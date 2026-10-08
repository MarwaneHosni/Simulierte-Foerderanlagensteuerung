"""Test-Harness fuer die simulierte Foerderanlagensteuerung.

Fuehrt die in tests/test_scenarios.py definierten Szenarien gegen die echte
SoftPLC-Runtime aus und schreibt echte Ergebnisse (keine erfundenen Werte):

    tests/results/results.csv
    tests/results/trace_Txx.jsonl
und daraus
    docs/09_Testprotokoll.md
"""

from __future__ import annotations

import csv
import json
import os
import sys
from dataclasses import dataclass, field, asdict
from typing import Callable, Dict, List, Optional

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "plc", "runtime"))

from softplc import load_project  # noqa: E402

PLC_DIR = os.path.join(ROOT, "plc")
RESULTS_DIR = os.path.join(ROOT, "tests", "results")

STATE = {0: "INIT", 10: "READY", 20: "RUNNING", 30: "STOPPED", 40: "FAULT", 50: "EMERGENCY"}
FAULT = {
    0: "-", 1: "UEBERLAST", 2: "START-TIMEOUT", 3: "STOP-TIMEOUT",
    4: "STAU", 5: "SENSOR-INKONSISTENZ", 6: "NOT-HALT",
}


@dataclass
class Case:
    id: str = ""
    group: str = ""
    title: str = ""
    initial: str = ""
    action: str = ""
    expected: str = ""
    actual: str = ""
    passed: bool = False
    cycles: int = 0


class Sim:
    def __init__(self):
        self.rt = load_project(PLC_DIR)
        self.cycle = 0
        self.trace: List[dict] = []
        self._trace_on = True
        self.scan(2)   # Einschaltinitialisierung abschliessen

    # -- Grundoperationen ------------------------------------------------ #
    def scan(self, n: int = 1) -> None:
        for _ in range(n):
            self.rt.scan()
            self.cycle += 1
            if self._trace_on:
                self.trace.append(self.snap())

    def run(self, n: int = 1) -> None:
        self.scan(n)

    def set(self, path: str, value) -> None:
        self.rt.set(path, value)

    def get(self, path: str):
        return self.rt.get(path)

    def snap(self) -> dict:
        g = self.rt.get
        return {
            "cycle": self.cycle,
            "state": g("eHmiState"),
            "fault": g("eHmiActiveFault"),
            "first": g("eHmiFirstFault"),
            "mode": g("eHmiMode"),
            "cmd": int(bool(g("xHmiMotorCmd"))),
            "run": int(bool(g("xHmiMotorRun"))),
            "fb": int(bool(g("xHmiMotorFb"))),
            "entry": int(bool(g("xHmiEntry"))),
            "exit": int(bool(g("xHmiExit"))),
            "count": g("diHmiCount"),
            "belt": g("aHmiBeltPos"),
        }

    # -- Bequeme Kurzformen --------------------------------------------- #
    @property
    def state(self) -> str:
        return STATE.get(self.rt.get("eHmiState"), "?")

    @property
    def fault(self) -> str:
        return FAULT.get(self.rt.get("eHmiActiveFault"), "?")

    @property
    def cmd(self) -> bool:
        return bool(self.rt.get("xHmiMotorCmd"))

    @property
    def fb(self) -> bool:
        return bool(self.rt.get("xHmiMotorFb"))

    @property
    def count(self) -> int:
        return int(self.rt.get("diHmiCount"))

    def start_manual(self, wait_feedback: bool = True) -> None:
        self.set("xStart", True)
        self.scan()
        self.set("xStart", False)
        if wait_feedback:
            self.run_until(lambda s: s.fb, 40)
            self.scan(2)   # Zustandsmodell nachziehen

    def press_stop(self) -> None:
        self.set("xStopNC", False)
        self.scan()
        self.set("xStopNC", True)

    def press_reset(self) -> None:
        self.set("xReset", True)
        self.scan()
        self.set("xReset", False)

    def run_until(self, pred: Callable[["Sim"], bool], max_cycles: int = 3000) -> bool:
        for _ in range(max_cycles):
            self.scan()
            if pred(self):
                return True
        return False


@dataclass
class TestDef:
    id: str
    group: str
    title: str
    func: Callable[[Sim], Case]


REGISTRY: List[TestDef] = []


def test(id: str, group: str, title: str):
    def deco(func):
        REGISTRY.append(TestDef(id, group, title, func))
        return func
    return deco


def run_all(write: bool = True) -> List[Case]:
    cases: List[Case] = []
    os.makedirs(RESULTS_DIR, exist_ok=True)
    for td in REGISTRY:
        sim = Sim()
        try:
            case = td.func(sim)
        except Exception as exc:  # Testfehler nicht verschleiern
            case = Case(id=td.id, group=td.group, title=td.title,
                        expected="Test laeuft fehlerfrei", actual=f"Exception: {exc}",
                        passed=False, cycles=sim.cycle)
        case.id = td.id
        case.group = td.group
        case.title = td.title
        case.cycles = sim.cycle
        cases.append(case)
        with open(os.path.join(RESULTS_DIR, f"trace_{td.id}.jsonl"), "w", encoding="utf-8") as fh:
            for row in sim.trace:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    if write:
        _write_csv(cases)
        _write_protokoll(cases)
    return cases


def _write_csv(cases: List[Case]) -> None:
    path = os.path.join(RESULTS_DIR, "results.csv")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["ID", "Gruppe", "Titel", "Ausgangszustand", "Aktion",
                    "Erwartet", "Ergebnis", "Status", "Zyklen"])
        for c in cases:
            w.writerow([c.id, c.group, c.title, c.initial, c.action,
                        c.expected, c.actual, "PASS" if c.passed else "FAIL", c.cycles])


def _write_protokoll(cases: List[Case]) -> None:
    passed = sum(1 for c in cases if c.passed)
    total = len(cases)
    lines: List[str] = []
    lines.append("# 09 - Testprotokoll\n")
    lines.append("**Projekt:** Automatisierte Förderbandsteuerung mit SPS\n")
    lines.append("")
    lines.append("> Diese Ergebnisse stammen aus **echten Testläufen** meiner SoftPLC "
                 "(siehe `tests/results/`). Ich habe nichts erfunden. Ein "
                 "Simulationszyklus dauert 20 ms.\n")
    lines.append("")
    lines.append(f"## Zusammenfassung\n")
    lines.append(f"- Testfälle: **{total}**")
    lines.append(f"- bestanden: **{passed}**")
    lines.append(f"- fehlgeschlagen: **{total - passed}**")
    lines.append("")
    lines.append(f"Gesamtergebnis: **{'BESTANDEN' if passed == total else 'NICHT BESTANDEN'}**")
    lines.append("")
    lines.append("## Ergebnisse\n")
    lines.append("| ID | Gruppe | Titel | Erwartet | Ergebnis | Status |")
    lines.append("| -- | ------ | ----- | -------- | -------- | ------ |")
    for c in cases:
        lines.append(f"| {c.id} | {c.group} | {c.title} | {_esc(c.expected)} | "
                     f"{_esc(c.actual)} | {'PASS' if c.passed else 'FAIL'} |")
    lines.append("")
    lines.append("## Details\n")
    for c in cases:
        lines.append(f"### {c.id} – {c.title} ({c.group})\n")
        lines.append(f"- **Ausgangszustand:** {c.initial}")
        lines.append(f"- **Aktion:** {c.action}")
        lines.append(f"- **Erwartet:** {c.expected}")
        lines.append(f"- **Ergebnis:** {c.actual}")
        lines.append(f"- **Zyklen:** {c.cycles} ({c.cycles * 0.02:.2f} s simuliert)")
        lines.append(f"- **Status:** {'PASS' if c.passed else 'FAIL'}")
        lines.append("")
    with open(os.path.join(ROOT, "docs", "09_Testprotokoll.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def _esc(text: str) -> str:
    return str(text).replace("|", "\\|")


if __name__ == "__main__":
    import test_scenarios  # noqa: F401  (registriert die Tests)
    result = run_all(write=True)
    ok = sum(1 for c in result if c.passed)
    for c in result:
        print(f"[{'PASS' if c.passed else 'FAIL'}] {c.id:<4} {c.title:<45} -> {c.actual}")
    print(f"\n{ok}/{len(result)} Tests bestanden")
