"""Laufzeit der SoftPLC.

Wertet die geparsten ST-POUs zyklisch aus. Es wird nur die Teilmenge der
IEC-61131-3-Sprache unterstuetzt, die in diesem Projekt verwendet wird.
"""

from __future__ import annotations

import glob
import os
from typing import Dict, List, Optional, Tuple

from .errors import RuntimeError_
from .parser import (
    Assign, Binary, Case, Expr, FBCall, For, If, Literal, Name, POU,
    Return, Stmt, Unary, VarDecl, While, EnumDef, parse_source,
)

BUILTIN_FB = {
    "TON", "TOF", "TP", "R_TRIG", "F_TRIG",
    "SR", "RS", "CTU", "CTD", "CTUD",
}

_BOOL_TYPES = {"BOOL"}
_INT_TYPES = {"SINT", "INT", "DINT", "LINT", "USINT", "UINT", "UDINT", "ULINT", "BYTE", "WORD", "DWORD", "LWORD"}
_REAL_TYPES = {"REAL", "LREAL"}
_TIME_TYPES = {"TIME", "LTIME", "TOD", "DATE"}


# --------------------------------------------------------------------------- #
#  Werte
# --------------------------------------------------------------------------- #
class ArrayVal:
    def __init__(self, low: int, high: int, values: Optional[List] = None):
        self.low = low
        self.high = high
        self.data = list(values) if values is not None else [None] * (high - low + 1)

    def get(self, idx: int):
        return self.data[idx - self.low]

    def set(self, idx: int, value) -> None:
        self.data[idx - self.low] = value

    def fill(self, value) -> None:
        self.data = [value] * len(self.data)

    def to_list(self) -> List:
        return list(self.data)

    def __repr__(self) -> str:  # pragma: no cover
        return f"ArrayVal{self.data!r}"


class BuiltinInstance:
    """Standard-Funktionsbaustein (Timer, Flanken, Zaehler, ...)."""

    def __init__(self, kind: str):
        self.kind = kind.upper()
        self.mem: Dict[str, object] = {}
        if self.kind in ("TON", "TOF", "TP"):
            self.mem.update({"IN": False, "PT": 0, "Q": False, "ET": 0, "_prev": False})
        elif self.kind in ("R_TRIG", "F_TRIG"):
            self.mem.update({"CLK": False, "Q": False, "_prev": False})
        elif self.kind == "SR":
            self.mem.update({"S1": False, "R": False, "Q1": False})
        elif self.kind == "RS":
            self.mem.update({"S": False, "R1": False, "Q1": False})
        elif self.kind == "CTU":
            self.mem.update({"CU": False, "R": False, "PV": 0, "Q": False, "CV": 0, "_prev": False})
        elif self.kind == "CTD":
            self.mem.update({"CD": False, "LD": False, "PV": 0, "Q": False, "CV": 0, "_prev": False})
        elif self.kind == "CTUD":
            self.mem.update({"CU": False, "CD": False, "R": False, "LD": False,
                             "PV": 0, "QU": False, "QD": False, "CV": 0,
                             "_prev_cu": False, "_prev_cd": False})

    def update(self, dt_ms: int) -> None:
        m = self.mem
        if self.kind == "TON":
            if self._rising("IN"):
                m["ET"] = 0
            elif m["IN"]:
                m["ET"] = min(int(m["ET"]) + dt_ms, int(m["PT"]))
            if m["IN"]:
                m["Q"] = int(m["ET"]) >= int(m["PT"])
            else:
                m["Q"] = False
                m["ET"] = 0
        elif self.kind == "TOF":
            if m["IN"]:
                m["Q"] = True
                m["ET"] = 0
            elif m["_prev"]:
                m["ET"] = min(int(m["ET"]) + dt_ms, int(m["PT"]))
                m["Q"] = int(m["ET"]) < int(m["PT"])
            else:
                m["ET"] = 0
                m["Q"] = False
        elif self.kind == "TP":
            if self._rising("IN"):
                m["Q"] = True
                m["ET"] = 0
            elif m["Q"]:
                m["ET"] = min(int(m["ET"]) + dt_ms, int(m["PT"]))
                if int(m["ET"]) >= int(m["PT"]):
                    m["Q"] = False
        elif self.kind == "R_TRIG":
            m["Q"] = bool(m["CLK"]) and not bool(m["_prev"])
        elif self.kind == "F_TRIG":
            m["Q"] = (not bool(m["CLK"])) and bool(m["_prev"])
        elif self.kind == "SR":
            m["Q1"] = bool(m["S1"]) or (bool(m["Q1"]) and not bool(m["R"]))
        elif self.kind == "RS":
            m["Q1"] = (not bool(m["R1"])) and (bool(m["S"]) or bool(m["Q1"]))
        elif self.kind == "CTU":
            if self._rising("CU"):
                m["CV"] = int(m["CV"]) + 1
            if m["R"]:
                m["CV"] = 0
            m["Q"] = int(m["CV"]) >= int(m["PV"])
        elif self.kind == "CTD":
            if m["LD"]:
                m["CV"] = int(m["PV"])
            elif self._rising("CD"):
                m["CV"] = int(m["CV"]) - 1
            m["Q"] = int(m["CV"]) <= 0
        elif self.kind == "CTUD":
            if self._rising("CU"):
                m["CV"] = int(m["CV"]) + 1
            if self._rising("CD"):
                m["CV"] = int(m["CV"]) - 1
            if m["R"]:
                m["CV"] = 0
            if m["LD"]:
                m["CV"] = int(m["PV"])
            m["QU"] = int(m["CV"]) >= int(m["PV"])
            m["QD"] = int(m["CV"]) <= 0

        if "_prev" in m:
            m["_prev"] = bool(m[[k for k in ("IN", "CLK", "CU", "CD") if k in m][0]])
        if self.kind == "CTUD":
            m["_prev_cu"] = bool(m["CU"])
            m["_prev_cd"] = bool(m["CD"])

    def _rising(self, key: str) -> bool:
        m = self.mem
        if key == "CU" and self.kind == "CTUD":
            rising = bool(m["CU"]) and not bool(m["_prev_cu"])
            return rising
        if key == "CD" and self.kind == "CTUD":
            return bool(m["CD"]) and not bool(m["_prev_cd"])
        return bool(m[key]) and not bool(m["_prev"])


class FBInstance:
    def __init__(self, pou: POU, frame: Dict[str, object]):
        self.pou = pou
        self.frame = frame


# --------------------------------------------------------------------------- #
#  Laufzeit
# --------------------------------------------------------------------------- #
class Ctx:
    def __init__(self, rt: "Runtime", frame: Dict[str, object]):
        self.rt = rt
        self.frame = frame

    def read_var(self, name: str):
        if name in self.frame:
            return self.frame[name]
        if name in self.rt.globals:
            return self.rt.globals[name]
        raise RuntimeError_(f"Unbekannte Variable '{name}'")

    def write_var(self, name: str, value) -> None:
        if name in self.frame:
            self.frame[name] = value
        elif name in self.rt.globals:
            self.rt.globals[name] = value
        else:
            raise RuntimeError_(f"Zuweisung an unbekannte Variable '{name}'")


class Runtime:
    def __init__(self, globals_decls: List[VarDecl], type_defs: List[EnumDef],
                 pous: Dict[str, POU]):
        self.type_defs = {t.name: t for t in type_defs}
        self.pous = pous
        self.globals: Dict[str, object] = {}
        self.dt_ms = 20
        self.program_frame: Dict[str, object] = {}
        self.program: Optional[POU] = None
        self._init_globals(globals_decls)
        self._init_program()
        self.scan_count = 0

    # ---- Initialisierung --------------------------------------------- #
    def value_default(self, type_name: str):
        t = type_name.upper()
        if t in _BOOL_TYPES:
            return False
        if t in _INT_TYPES:
            return 0
        if t in _REAL_TYPES:
            return 0.0
        if t in _TIME_TYPES:
            return 0
        if t in self.type_defs:
            return self.type_defs[t].members[0][1]
        return 0

    def _init_globals(self, decls: List[VarDecl]) -> None:
        for d in decls:
            if d.is_array:
                self.globals[d.name] = ArrayVal(d.array_low, d.array_high)
                self.globals[d.name].fill(self.value_default(d.type_name))
            else:
                self.globals[d.name] = self.value_default(d.type_name)
        # zweiter Durchlauf: Initialisierungswerte
        ctx = Ctx(self, {})
        for d in decls:
            if d.init is not None:
                value = eval_expr(d.init, ctx)
                if d.is_array:
                    self.globals[d.name].fill(value)
                else:
                    self.globals[d.name] = value
        if "T_ZYKLUS" in self.globals and isinstance(self.globals["T_ZYKLUS"], int) and self.globals["T_ZYKLUS"] > 0:
            self.dt_ms = self.globals["T_ZYKLUS"]

    def make_frame(self, decls: List[VarDecl]) -> Dict[str, object]:
        frame: Dict[str, object] = {}
        for d in decls:
            if d.is_array:
                arr = ArrayVal(d.array_low, d.array_high)
                arr.fill(self.value_default(d.type_name))
                frame[d.name] = arr
            elif d.type_name in BUILTIN_FB:
                frame[d.name] = BuiltinInstance(d.type_name)
            elif d.type_name in self.pous and self.pous[d.type_name].kind == "FUNCTION_BLOCK":
                sub = self.make_frame(self.pous[d.type_name].all_vars())
                frame[d.name] = FBInstance(self.pous[d.type_name], sub)
            else:
                frame[d.name] = self.value_default(d.type_name)
        # lokale Initialisierungswerte
        ctx = Ctx(self, frame)
        for d in decls:
            if d.init is not None:
                frame[d.name] = eval_expr(d.init, ctx)
        return frame

    def _init_program(self) -> None:
        self.program = self.pous.get("PLC_PRG")
        if self.program is None:
            raise RuntimeError_("PROGRAM 'PLC_PRG' nicht gefunden")
        self.program_frame = self.make_frame(self.program.all_vars())

    # ---- Ausfuehrung -------------------------------------------------- #
    def scan(self) -> None:
        ctx = Ctx(self, self.program_frame)
        exec_block(self.program.body, ctx)
        self.scan_count += 1

    def run(self, cycles: int = 1) -> None:
        for _ in range(cycles):
            self.scan()

    # ---- Variablenzugriff --------------------------------------------- #
    def get(self, path: str):
        parts = path.split(".")
        base = parts[0].upper()
        if base in self.program_frame:
            val = self.program_frame[base]
        elif base in self.globals:
            val = self.globals[base]
        else:
            raise RuntimeError_(f"Variable '{path}' nicht gefunden")
        for p in parts[1:]:
            val = get_member(val, p.upper())
        return unwrap(val)

    def set(self, path: str, value) -> None:
        parts = path.split(".")
        base = parts[0].upper()
        if base in self.globals:
            target = self.globals
        elif base in self.program_frame:
            target = self.program_frame
        else:
            raise RuntimeError_(f"Variable '{path}' nicht gefunden")
        if len(parts) == 1:
            target[base] = value
            return
        val = target[base]
        for p in parts[1:-1]:
            val = get_member(val, p.upper())
        last = parts[-1].upper()
        if isinstance(val, FBInstance):
            val.frame[last] = value
        elif isinstance(val, BuiltinInstance):
            val.mem[last] = value
        elif isinstance(val, dict):
            val[last] = value
        else:
            raise RuntimeError_(f"Kein beschreibbares Ziel: {path}")

    def enum_name(self, type_name: str, value) -> str:
        td = self.type_defs.get(type_name.upper())
        if td is None:
            return str(value)
        for name, val in td.members:
            if val == value:
                return name
        return str(value)


# --------------------------------------------------------------------------- #
#  Auswertung von Ausdruecken
# --------------------------------------------------------------------------- #
def unwrap(value):
    if isinstance(value, ArrayVal):
        return value.to_list()
    return value


def index_if(value, idx_exprs: List[Expr], ctx: Ctx):
    if not idx_exprs:
        return value
    idx = eval_expr(idx_exprs[0], ctx)
    if not isinstance(value, ArrayVal):
        raise RuntimeError_("Indexierung auf Nicht-Array")
    return value.get(int(idx))


def get_member(container, name: str):
    if isinstance(container, FBInstance):
        if name in container.frame:
            return container.frame[name]
        raise RuntimeError_(f"Unbekanntes FB-Element '{name}'")
    if isinstance(container, BuiltinInstance):
        if name in container.mem:
            return container.mem[name]
        raise RuntimeError_(f"Unbekanntes FB-Element '{name}'")
    if isinstance(container, dict):
        if name in container:
            return container[name]
        raise RuntimeError_(f"Unbekanntes Strukturfeld '{name}'")
    raise RuntimeError_(f"Kein Zugriff auf Element '{name}'")


def set_member(container, name: str, value) -> None:
    if isinstance(container, FBInstance):
        container.frame[name] = value
    elif isinstance(container, BuiltinInstance):
        container.mem[name] = value
    elif isinstance(container, dict):
        container[name] = value
    else:
        raise RuntimeError_(f"Kein beschreibbares Element '{name}'")


def eval_expr(expr: Expr, ctx: Ctx):
    if isinstance(expr, Literal):
        return expr.value
    if isinstance(expr, Name):
        return eval_name(expr, ctx)
    if isinstance(expr, Unary):
        v = eval_expr(expr.operand, ctx)
        if expr.op == "NOT":
            return not bool(v)
        if expr.op == "-":
            return -v
        raise RuntimeError_(f"Unbekannter unarer Operator {expr.op}")
    if isinstance(expr, Binary):
        return eval_binary(expr, ctx)
    raise RuntimeError_(f"Unbekannter Ausdruck {type(expr).__name__}")


def eval_name(name: Name, ctx: Ctx):
    parts = name.parts
    first, first_idx = parts[0]
    if first in ctx.rt.type_defs:
        if len(parts) < 2:
            raise RuntimeError_(f"Enum-Typ '{first}' ohne Element")
        member = parts[1][0]
        for mname, mval in ctx.rt.type_defs[first].members:
            if mname == member:
                return mval
        raise RuntimeError_(f"Unbekanntes Enum-Element {first}.{member}")
    val = ctx.read_var(first)
    val = index_if(val, first_idx, ctx)
    for pname, pidx in parts[1:]:
        val = get_member(val, pname)
        val = index_if(val, pidx, ctx)
    return val


def eval_binary(expr: Binary, ctx: Ctx):
    op = expr.op
    left = eval_expr(expr.left, ctx)
    if op == "AND":
        return bool(left) and bool(eval_expr(expr.right, ctx))
    if op == "OR":
        return bool(left) or bool(eval_expr(expr.right, ctx))
    if op == "XOR":
        return bool(left) != bool(eval_expr(expr.right, ctx))
    right = eval_expr(expr.right, ctx)
    if op == "+":
        return left + right
    if op == "-":
        return left - right
    if op == "*":
        return left * right
    if op == "/":
        return left / right
    if op == "MOD":
        return int(left) % int(right)
    if op == "=":
        return left == right
    if op == "<>":
        return left != right
    if op == "<":
        return left < right
    if op == ">":
        return left > right
    if op == "<=":
        return left <= right
    if op == ">=":
        return left >= right
    raise RuntimeError_(f"Unbekannter Operator {op}")


# --------------------------------------------------------------------------- #
#  Ausfuehrung von Anweisungen
# --------------------------------------------------------------------------- #
class _ReturnSignal(Exception):
    pass


def exec_block(stmts: List[Stmt], ctx: Ctx) -> None:
    try:
        for stmt in stmts:
            exec_stmt(stmt, ctx)
    except _ReturnSignal:
        pass


def exec_stmt(stmt: Stmt, ctx: Ctx) -> None:
    if isinstance(stmt, Assign):
        assign_name(stmt.target, eval_expr(stmt.value, ctx), ctx)
    elif isinstance(stmt, FBCall):
        exec_fb_call(stmt, ctx)
    elif isinstance(stmt, If):
        if bool(eval_expr(stmt.cond, ctx)):
            exec_block(stmt.then_body, ctx)
            return
        for econd, ebody in stmt.elifs:
            if bool(eval_expr(econd, ctx)):
                exec_block(ebody, ctx)
                return
        exec_block(stmt.else_body, ctx)
    elif isinstance(stmt, Case):
        sel = eval_expr(stmt.expr, ctx)
        matched = False
        for labels, body in stmt.cases:
            for lab in labels:
                if eval_expr(lab, ctx) == sel:
                    exec_block(body, ctx)
                    matched = True
                    break
            if matched:
                break
        if not matched:
            exec_block(stmt.else_body, ctx)
    elif isinstance(stmt, For):
        start = int(eval_expr(stmt.start, ctx))
        end = int(eval_expr(stmt.end, ctx))
        step = int(eval_expr(stmt.step, ctx)) if stmt.step is not None else 1
        i = start
        while (step > 0 and i <= end) or (step < 0 and i >= end):
            ctx.write_var(stmt.var, i)
            exec_block(stmt.body, ctx)
            i += step
    elif isinstance(stmt, While):
        guard = 0
        while bool(eval_expr(stmt.cond, ctx)):
            exec_block(stmt.body, ctx)
            guard += 1
            if guard > 1000000:
                raise RuntimeError_("WHILE-Schleife ohne Ende")
    elif isinstance(stmt, Return):
        raise _ReturnSignal()
    else:
        raise RuntimeError_(f"Unbekannte Anweisung {type(stmt).__name__}")


def assign_name(target: Expr, value, ctx: Ctx) -> None:
    if not isinstance(target, Name):
        raise RuntimeError_("Ungueltiges Zuweisungsziel")
    parts = target.parts

    if len(parts) == 1:
        name, idx = parts[0]
        if not idx:
            ctx.write_var(name, value)
            return
        arr = ctx.read_var(name)
        arr.set(int(eval_expr(idx[0], ctx)), value)
        return

    container = ctx.read_var(parts[0][0])
    container = index_if(container, parts[0][1], ctx)
    for pname, pidx in parts[1:-1]:
        container = get_member(container, pname)
        container = index_if(container, pidx, ctx)

    last_name, last_idx = parts[-1]
    if not last_idx:
        set_member(container, last_name, value)
    else:
        arr = get_member(container, last_name)
        arr.set(int(eval_expr(last_idx[0], ctx)), value)


def exec_fb_call(call: FBCall, ctx: Ctx) -> None:
    inst = ctx.read_var(call.name)
    if isinstance(inst, BuiltinInstance):
        for pname, pexpr in call.args:
            if pname not in inst.mem:
                raise RuntimeError_(f"Unbekannter Parameter '{pname}' fuer {inst.kind}")
            inst.mem[pname] = eval_expr(pexpr, ctx)
        inst.update(ctx.rt.dt_ms)
    elif isinstance(inst, FBInstance):
        for pname, pexpr in call.args:
            inst.frame[pname] = eval_expr(pexpr, ctx)
        sub_ctx = Ctx(ctx.rt, inst.frame)
        exec_block(inst.pou.body, sub_ctx)
    else:
        raise RuntimeError_(f"'{call.name}' ist kein Funktionsbaustein")


# --------------------------------------------------------------------------- #
#  Projekt laden
# --------------------------------------------------------------------------- #
def _read_st_files(plc_dir: str) -> List[Tuple[str, str]]:
    files: List[Tuple[str, str]] = []
    for sub in ("standard", "application", "function_blocks", "simulation", "visualization"):
        pattern = os.path.join(plc_dir, sub, "*.st")
        for path in sorted(glob.glob(pattern)):
            with open(path, "r", encoding="utf-8") as fh:
                files.append((path, fh.read()))
    return files


def load_project(plc_dir: str) -> Runtime:
    globals_decls: List[VarDecl] = []
    type_defs: List[EnumDef] = []
    pous: Dict[str, POU] = {}

    for path, src in _read_st_files(plc_dir):
        g, t, p = parse_source(src, os.path.basename(path))
        globals_decls.extend(g)
        type_defs.extend(t)
        for name, pou in p.items():
            if name in pous:
                raise RuntimeError_(f"Doppelte POU '{name}'")
            pous[name] = pou

    return Runtime(globals_decls, type_defs, pous)
