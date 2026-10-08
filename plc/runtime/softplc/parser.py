"""AST und Parser fuer die verwendete ST-Teilmenge.

Die Parser-Ergebnisse werden von runtime.py ausgefuehrt.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .errors import ParseError
from .lexer import Token, Lexer

# --------------------------------------------------------------------------- #
#  AST-Knoten
# --------------------------------------------------------------------------- #


@dataclass
class VarDecl:
    name: str
    type_name: str
    is_array: bool = False
    array_low: int = 0
    array_high: int = 0
    init: Optional["Expr"] = None
    section: str = "VAR"   # VAR | VAR_INPUT | VAR_OUTPUT | VAR_IN_OUT | VAR_GLOBAL ...
    address: Optional[str] = None


@dataclass
class EnumDef:
    name: str
    members: List[Tuple[str, int]]


@dataclass
class POU:
    kind: str              # PROGRAM | FUNCTION_BLOCK
    name: str
    var_sections: Dict[str, List[VarDecl]] = field(default_factory=dict)
    body: List["Stmt"] = field(default_factory=list)

    def all_vars(self) -> List[VarDecl]:
        out: List[VarDecl] = []
        for decls in self.var_sections.values():
            out.extend(decls)
        return out


# --- Statements ---
@dataclass
class Stmt:
    pass


@dataclass
class Assign(Stmt):
    target: "Expr"
    value: "Expr"


@dataclass
class FBCall(Stmt):
    name: str
    args: List[Tuple[str, "Expr"]]


@dataclass
class If(Stmt):
    cond: "Expr"
    then_body: List[Stmt]
    elifs: List[Tuple["Expr", List[Stmt]]]
    else_body: List[Stmt]


@dataclass
class Case(Stmt):
    expr: "Expr"
    cases: List[Tuple[List["Expr"], List[Stmt]]]
    else_body: List[Stmt]


@dataclass
class For(Stmt):
    var: str
    start: "Expr"
    end: "Expr"
    step: Optional["Expr"]
    body: List[Stmt]


@dataclass
class While(Stmt):
    cond: "Expr"
    body: List[Stmt]


@dataclass
class Return(Stmt):
    pass


# --- Expressions ---
@dataclass
class Expr:
    pass


@dataclass
class Literal(Expr):
    value: object
    type_name: str = ""


@dataclass
class Name(Expr):
    parts: List[Tuple[str, List[Expr]]]


@dataclass
class Unary(Expr):
    op: str
    operand: Expr


@dataclass
class Binary(Expr):
    op: str
    left: Expr
    right: Expr


# --------------------------------------------------------------------------- #
#  Parser
# --------------------------------------------------------------------------- #

_KEYWORDS = {
    "PROGRAM", "END_PROGRAM", "FUNCTION_BLOCK", "END_FUNCTION_BLOCK",
    "FUNCTION", "END_FUNCTION", "VAR", "VAR_INPUT", "VAR_OUTPUT",
    "VAR_IN_OUT", "VAR_GLOBAL", "VAR_TEMP", "VAR_EXTERNAL", "END_VAR",
    "CONSTANT", "RETAIN", "NON_RETAIN", "PERSISTENT", "TYPE", "END_TYPE",
    "STRUCT", "END_STRUCT", "ARRAY", "OF", "IF", "THEN", "ELSIF", "ELSE",
    "END_IF", "CASE", "END_CASE", "FOR", "TO", "BY", "DO", "END_FOR",
    "WHILE", "END_WHILE", "REPEAT", "UNTIL", "END_REPEAT", "RETURN", "AT",
    "TRUE", "FALSE", "AND", "OR", "XOR", "NOT", "MOD",
}

_VAR_BLOCK_KEYWORDS = {
    "VAR", "VAR_INPUT", "VAR_OUTPUT", "VAR_IN_OUT", "VAR_GLOBAL",
    "VAR_TEMP", "VAR_EXTERNAL",
}


class Parser:
    def __init__(self, tokens: List[Token], filename: str = "<st>"):
        self.toks = tokens
        self.i = 0
        self.filename = filename

    # ---- Token-Helfer ------------------------------------------------- #
    def _cur(self) -> Token:
        return self.toks[self.i]

    def _peek(self, off: int = 1) -> Token:
        j = self.i + off
        if j >= len(self.toks):
            return self.toks[-1]
        return self.toks[j]

    def _advance(self) -> Token:
        tok = self.toks[self.i]
        if self.i < len(self.toks) - 1:
            self.i += 1
        return tok

    def _error(self, msg: str, tok: Optional[Token] = None) -> ParseError:
        tok = tok or self._cur()
        return ParseError(f"{self.filename}:{tok.line}:{tok.col}: {msg} (bei {tok.value!r})")

    def _is_kw(self, word: str, off: int = 0) -> bool:
        tok = self._peek(off) if off else self._cur()
        return tok.kind == "id" and tok.value.upper() == word

    def _is_op(self, op: str, off: int = 0) -> bool:
        tok = self._peek(off) if off else self._cur()
        return tok.kind == "op" and tok.value == op

    def _expect_op(self, op: str) -> None:
        if not self._is_op(op):
            raise self._error(f"Erwartet '{op}'")
        self._advance()

    def _expect_kw(self, word: str) -> None:
        if not self._is_kw(word):
            raise self._error(f"Erwartet Schluesselwort {word}")
        self._advance()

    def _expect_id(self) -> str:
        tok = self._cur()
        if tok.kind != "id":
            raise self._error("Erwartet Bezeichner")
        self._advance()
        return tok.value

    # ---- Top-Level ---------------------------------------------------- #
    def parse(self) -> Tuple[List[VarDecl], List[EnumDef], Dict[str, POU]]:
        globals_: List[VarDecl] = []
        types: List[EnumDef] = []
        pous: Dict[str, POU] = {}

        while self._cur().kind != "eof":
            if self._is_kw("TYPE"):
                types.extend(self._parse_type_block())
            elif self._is_kw("VAR_GLOBAL"):
                globals_.extend(self._parse_var_block())
            elif self._is_kw("PROGRAM") or self._is_kw("FUNCTION_BLOCK") or self._is_kw("FUNCTION"):
                pou = self._parse_pou()
                pous[pou.name.upper()] = pou
            else:
                raise self._error("Unerwartetes Konstrukt auf oberster Ebene")
        return globals_, types, pous

    # ---- Typen -------------------------------------------------------- #
    def _parse_type_block(self) -> List[EnumDef]:
        self._expect_kw("TYPE")
        defs: List[EnumDef] = []
        while not self._is_kw("END_TYPE"):
            name = self._expect_id()
            self._expect_op(":")
            if self._is_kw("STRUCT"):
                self._error("STRUCT-Typen werden in diesem Projekt nicht verwendet")
            members = self._parse_enum_members()
            self._expect_op(";")
            defs.append(EnumDef(name.upper(), members))
        self._expect_kw("END_TYPE")
        return defs

    def _parse_enum_members(self) -> List[Tuple[str, int]]:
        self._expect_op("(")
        members: List[Tuple[str, int]] = []
        nxt = 0
        while True:
            mname = self._expect_id()
            if self._is_op(":="):
                self._advance()
                sign = 1
                if self._is_op("-"):
                    self._advance()
                    sign = -1
                tok = self._cur()
                if tok.kind != "int":
                    raise self._error("Erwartet Ganzzahl fuer Enum-Wert")
                nxt = sign * int(tok.value)
                self._advance()
            members.append((mname.upper(), nxt))
            nxt += 1
            if self._is_op(","):
                self._advance()
                continue
            break
        self._expect_op(")")
        return members

    # ---- Variablenbloecke --------------------------------------------- #
    def _parse_var_block(self) -> List[VarDecl]:
        tok = self._cur()
        section = tok.value.upper()
        self._advance()
        # optionale Qualifier (CONSTANT, RETAIN, ...) ignorieren
        while self._cur().kind == "id" and self._cur().value.upper() in (
            "CONSTANT", "RETAIN", "NON_RETAIN", "PERSISTENT", "RETAIN",
        ):
            self._advance()
        decls: List[VarDecl] = []
        while not self._is_kw("END_VAR"):
            decl = self._parse_var_decl(section)
            decls.extend(decl)
        self._expect_kw("END_VAR")
        return decls

    def _parse_var_decl(self, section: str) -> List[VarDecl]:
        names = [self._expect_id()]
        while self._is_op(","):
            self._advance()
            names.append(self._expect_id())
        address = None
        if self._is_kw("AT"):
            self._advance()
            atok = self._cur()
            if atok.kind != "addr":
                raise self._error("Erwartet Hardwareadresse nach AT")
            address = atok.value
            self._advance()
        self._expect_op(":")
        is_array = False
        low = high = 0
        if self._is_kw("ARRAY"):
            self._advance()
            is_array = True
            self._expect_op("[")
            low = self._parse_int_literal()
            self._expect_op("..")
            high = self._parse_int_literal()
            self._expect_op("]")
            self._expect_kw("OF")
        type_name = self._expect_id()
        init = None
        if self._is_op(":="):
            self._advance()
            init = self._parse_expr()
        self._expect_op(";")
        out = []
        for n in names:
            out.append(VarDecl(name=n.upper(), type_name=type_name.upper(),
                               is_array=is_array, array_low=low, array_high=high,
                               init=init, section=section, address=address))
        return out

    def _parse_int_literal(self) -> int:
        sign = 1
        if self._is_op("-"):
            self._advance()
            sign = -1
        tok = self._cur()
        if tok.kind != "int":
            raise self._error("Erwartet Ganzzahl")
        self._advance()
        return sign * int(tok.value)

    # ---- POU ---------------------------------------------------------- #
    def _parse_pou(self) -> POU:
        kind = self._cur().value.upper()
        self._advance()
        name = self._expect_id()
        pou = POU(kind=kind, name=name.upper())

        while self._cur().kind == "id" and self._cur().value.upper() in _VAR_BLOCK_KEYWORDS:
            section = self._cur().value.upper()
            decls = self._parse_var_block()
            for d in decls:
                d.section = section
            pou.var_sections.setdefault(section, []).extend(decls)

        end_kw = {"PROGRAM": "END_PROGRAM",
                  "FUNCTION_BLOCK": "END_FUNCTION_BLOCK",
                  "FUNCTION": "END_FUNCTION"}[kind]
        pou.body = self._parse_stmt_list((end_kw,))
        self._expect_kw(end_kw)
        return pou

    # ---- Statements --------------------------------------------------- #
    _BLOCK_END = (
        "END_IF", "END_CASE", "END_FOR", "END_WHILE", "END_REPEAT",
        "ELSIF", "ELSE", "UNTIL",
        "END_PROGRAM", "END_FUNCTION_BLOCK", "END_FUNCTION",
    )

    def _parse_stmt_list(self, terminators: Tuple[str, ...], stop_pred=None) -> List[Stmt]:
        stmts: List[Stmt] = []
        while True:
            tok = self._cur()
            if tok.kind == "eof":
                break
            if tok.kind == "id" and tok.value.upper() in terminators:
                break
            if stop_pred is not None and stop_pred():
                break
            if self._is_op(";"):
                self._advance()
                continue
            stmts.append(self._parse_stmt())
        return stmts

    def _looks_like_case_label(self) -> bool:
        """Prueft (ohne zu konsumieren), ob an der aktuellen Position ein
        CASE-Label (Ausdruck(sliste) gefolgt von ':') beginnt."""
        save = self.i
        try:
            self._parse_expr()
            while self._is_op(","):
                self._advance()
                self._parse_expr()
            ok = self._is_op(":")
        except Exception:
            ok = False
        self.i = save
        return ok

    def _parse_stmt(self) -> Stmt:
        if self._is_kw("IF"):
            return self._parse_if()
        if self._is_kw("CASE"):
            return self._parse_case()
        if self._is_kw("FOR"):
            return self._parse_for()
        if self._is_kw("WHILE"):
            return self._parse_while()
        if self._is_kw("RETURN"):
            self._advance()
            self._expect_op(";")
            return Return()
        # Zuweisung oder FB-Aufruf
        if self._cur().kind == "id" and self._peek(1).kind == "op" and self._peek(1).value == "(":
            return self._parse_fb_call()
        return self._parse_assignment()

    def _parse_assignment(self) -> Stmt:
        target = self._parse_expr()
        self._expect_op(":=")
        value = self._parse_expr()
        self._expect_op(";")
        return Assign(target, value)

    def _parse_fb_call(self) -> Stmt:
        name = self._expect_id()
        self._expect_op("(")
        args: List[Tuple[str, Expr]] = []
        if not self._is_op(")"):
            while True:
                pname = self._expect_id()
                self._expect_op(":=")
                val = self._parse_expr()
                args.append((pname.upper(), val))
                if self._is_op(","):
                    self._advance()
                    continue
                break
        self._expect_op(")")
        self._expect_op(";")
        return FBCall(name.upper(), args)

    def _parse_if(self) -> Stmt:
        self._expect_kw("IF")
        cond = self._parse_expr()
        self._expect_kw("THEN")
        then_body = self._parse_stmt_list(("ELSIF", "ELSE", "END_IF"))
        elifs: List[Tuple[Expr, List[Stmt]]] = []
        while self._is_kw("ELSIF"):
            self._advance()
            econd = self._parse_expr()
            self._expect_kw("THEN")
            ebody = self._parse_stmt_list(("ELSIF", "ELSE", "END_IF"))
            elifs.append((econd, ebody))
        else_body: List[Stmt] = []
        if self._is_kw("ELSE"):
            self._advance()
            else_body = self._parse_stmt_list(("END_IF",))
        self._expect_kw("END_IF")
        self._expect_op(";")
        return If(cond, then_body, elifs, else_body)

    def _parse_case(self) -> Stmt:
        self._expect_kw("CASE")
        expr = self._parse_expr()
        self._expect_kw("OF")
        cases: List[Tuple[List[Expr], List[Stmt]]] = []
        while not self._is_kw("ELSE") and not self._is_kw("END_CASE"):
            labels: List[Expr] = [self._parse_expr()]
            while self._is_op(","):
                self._advance()
                labels.append(self._parse_expr())
            self._expect_op(":")
            body = self._parse_stmt_list(("ELSE", "END_CASE"),
                                         stop_pred=self._looks_like_case_label)
            # optionale Leeranweisung vor naechstem Label
            cases.append((labels, body))
        else_body: List[Stmt] = []
        if self._is_kw("ELSE"):
            self._advance()
            else_body = self._parse_stmt_list(("END_CASE",))
        self._expect_kw("END_CASE")
        self._expect_op(";")
        return Case(expr, cases, else_body)

    def _parse_for(self) -> Stmt:
        self._expect_kw("FOR")
        var = self._expect_id()
        self._expect_op(":=")
        start = self._parse_expr()
        self._expect_kw("TO")
        end = self._parse_expr()
        step = None
        if self._is_kw("BY"):
            self._advance()
            step = self._parse_expr()
        self._expect_kw("DO")
        body = self._parse_stmt_list(("END_FOR",))
        self._expect_kw("END_FOR")
        self._expect_op(";")
        return For(var.upper(), start, end, step, body)

    def _parse_while(self) -> Stmt:
        self._expect_kw("WHILE")
        cond = self._parse_expr()
        self._expect_kw("DO")
        body = self._parse_stmt_list(("END_WHILE",))
        self._expect_kw("END_WHILE")
        self._expect_op(";")
        return While(cond, body)

    # ---- Expressions (Precedence Climbing) ---------------------------- #
    def _parse_expr(self) -> Expr:
        return self._parse_or()

    def _parse_or(self) -> Expr:
        left = self._parse_xor()
        while self._is_kw("OR"):
            self._advance()
            left = Binary("OR", left, self._parse_xor())
        return left

    def _parse_xor(self) -> Expr:
        left = self._parse_and()
        while self._is_kw("XOR"):
            self._advance()
            left = Binary("XOR", left, self._parse_and())
        return left

    def _parse_and(self) -> Expr:
        left = self._parse_compare_eq()
        while self._is_kw("AND"):
            self._advance()
            left = Binary("AND", left, self._parse_compare_eq())
        return left

    def _parse_compare_eq(self) -> Expr:
        left = self._parse_compare_rel()
        while self._is_op("=") or self._is_op("<>"):
            op = self._advance().value
            left = Binary(op, left, self._parse_compare_rel())
        return left

    def _parse_compare_rel(self) -> Expr:
        left = self._parse_add()
        while self._is_op("<") or self._is_op(">") or self._is_op("<=") or self._is_op(">="):
            op = self._advance().value
            left = Binary(op, left, self._parse_add())
        return left

    def _parse_add(self) -> Expr:
        left = self._parse_mul()
        while self._is_op("+") or self._is_op("-"):
            op = self._advance().value
            left = Binary(op, left, self._parse_mul())
        return left

    def _parse_mul(self) -> Expr:
        left = self._parse_unary()
        while self._is_op("*") or self._is_op("/") or self._is_kw("MOD"):
            op = self._advance().value.upper()
            left = Binary(op, left, self._parse_unary())
        return left

    def _parse_unary(self) -> Expr:
        if self._is_kw("NOT"):
            self._advance()
            return Unary("NOT", self._parse_unary())
        if self._is_op("-"):
            self._advance()
            return Unary("-", self._parse_unary())
        return self._parse_primary()

    def _parse_primary(self) -> Expr:
        tok = self._cur()
        if tok.kind == "int":
            self._advance()
            return Literal(tok.value, "INT")
        if tok.kind == "real":
            self._advance()
            return Literal(tok.value, "REAL")
        if tok.kind == "time":
            self._advance()
            return Literal(tok.value, "TIME")
        if tok.kind == "id" and tok.value.upper() == "TRUE":
            self._advance()
            return Literal(True, "BOOL")
        if tok.kind == "id" and tok.value.upper() == "FALSE":
            self._advance()
            return Literal(False, "BOOL")
        if tok.kind == "op" and tok.value == "(":
            self._advance()
            expr = self._parse_expr()
            self._expect_op(")")
            return expr
        if tok.kind == "id":
            return self._parse_name()
        raise self._error("Erwartet Ausdruck")

    def _parse_name(self) -> Expr:
        parts: List[Tuple[str, List[Expr]]] = []
        first = self._expect_id()
        indices = self._parse_indices()
        parts.append((first.upper(), indices))
        while self._is_op("."):
            self._advance()
            ident = self._expect_id()
            idx = self._parse_indices()
            parts.append((ident.upper(), idx))
        return Name(parts)

    def _parse_indices(self) -> List[Expr]:
        idx: List[Expr] = []
        while self._is_op("["):
            self._advance()
            idx.append(self._parse_expr())
            self._expect_op("]")
        return idx


def parse_source(src: str, filename: str = "<st>") -> Tuple[List[VarDecl], List[EnumDef], Dict[str, POU]]:
    tokens = Lexer(src, filename).tokenize()
    return Parser(tokens, filename).parse()
