"""Erzeugt Klemmenplan und Stueckliste aus tools/electrical_data.py."""

from __future__ import annotations

import csv
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from electrical_data import TERMINALS, BOM  # noqa: E402


def gen_terminal_plan():
    d = os.path.join(ROOT, "electrical", "terminal_plan")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "terminal_plan.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["Klemme", "Signal", "Richtung", "Beschreibung"])
        for row in TERMINALS:
            w.writerow(row)
    lines = ["# Klemmenplan\n",
             "**Projekt:** Simulierte Förderanlage mit Motorsteuerung, Schutz- und Fehlerdiagnose\n",
             "**Art:** PC-basierte Simulation und elektrotechnische Konzeptplanung\n",
             "",
             "Die Klemmenzuordnung entspricht dem Stromlaufplan (`../schematics/`) und der "
             "I/O-Liste (`../io_list/io_list.md`). Richtungen: `DI` Eingang, `DO` Ausgang, "
             "`PWR` Versorgung/Leistung.",
             "",
             "| Klemme | Signal | Richtung | Beschreibung |",
             "| ------ | ------ | -------- | ------------ |"]
    for t, s, r, desc in TERMINALS:
        lines.append(f"| {t} | {s} | {r} | {desc} |")
    lines.append("")
    with open(os.path.join(d, "terminal_plan.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("  terminal_plan.(csv|md)")


def gen_bom():
    d = os.path.join(ROOT, "electrical", "bom")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "bom.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["Bezeichner", "Komponente", "Beschreibung", "Menge", "Bemerkung"])
        for row in BOM:
            w.writerow(row)
    lines = ["# Stückliste (Konzept)\n",
             "**Projekt:** Simulierte Förderanlage mit Motorsteuerung, Schutz- und Fehlerdiagnose\n",
             "",
             "> Dies ist eine **Konzept-Stückliste für die Simulation**. Es wurden keine "
             "Komponenten beschafft oder verdrahtet. Bemessungen sind in einer realen Anlage "
             "nach Typenschild und Normenlage zu wählen.",
             "",
             "| Bezeichner | Komponente | Beschreibung | Menge | Bemerkung |",
             "| ---------- | ---------- | ------------ | ----- | --------- |"]
    for b in BOM:
        lines.append(f"| {b[0]} | {b[1]} | {b[2]} | {b[3]} | {b[4]} |")
    lines.append("")
    with open(os.path.join(d, "bom.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("  bom.(csv|md)")


if __name__ == "__main__":
    print("Klemmenplan:")
    gen_terminal_plan()
    print("Stückliste:")
    gen_bom()
