"""Konsistenzpruefung ueber alle Artefakte.

Prueft u. a.:
  - SPS-Adressen (GVL_IO) == I/O-Liste
  - HMI-Variablen existieren im Projekt
  - Fehlercodes sind dokumentiert
  - Klemmenplan deckt die I/O ab
  - Bauteilbezeichner aus der Stueckliste erscheinen im Schaltplan

Rueckgabecode 0 = alle Pruefungen bestanden.
"""

from __future__ import annotations

import csv
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "plc", "runtime"))
from softplc.parser import parse_source  # noqa: E402

PLC = os.path.join(ROOT, "plc")
SUBDIRS = ("standard", "application", "function_blocks", "simulation", "visualization")

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"[{'OK  ' if ok else 'FAIL'}] {name}" + (f"  -> {detail}" if detail else ""))


def read_all_st():
    items = []
    for sub in SUBDIRS:
        d = os.path.join(PLC, sub)
        for fn in sorted(os.listdir(d)):
            if fn.endswith(".st"):
                with open(os.path.join(d, fn), encoding="utf-8") as fh:
                    items.append((f"{sub}/{fn}", fh.read()))
    return items


def collect_globals():
    names = set()
    addrs = {}
    hmi = set()
    for path, src in read_all_st():
        g, t, p = parse_source(src, path)
        for d in g:
            names.add(d.name)
            if d.address:
                addrs[d.name] = d.address
            if "HMI" in path:
                hmi.add(d.name)
    return names, addrs, hmi


def io_list_rows():
    with open(os.path.join(ROOT, "electrical", "io_list", "io_list.csv"), encoding="utf-8") as fh:
        return list(csv.reader(fh, delimiter=";"))[1:]


def main():
    names, addrs, hmi = collect_globals()
    rows = io_list_rows()

    io_addrs = {r[0] for r in rows}
    gvl_addrs = set(addrs.values())

    check("I/O-Adressen: GVL_IO == I/O-Liste",
          io_addrs == gvl_addrs,
          f"nur in IO-Liste: {sorted(io_addrs - gvl_addrs)}; "
          f"nur in GVL_IO: {sorted(gvl_addrs - io_addrs)}")

    # Adressrichtungen
    io_in = {a for a in io_addrs if a.startswith("%I")}
    io_out = {a for a in io_addrs if a.startswith("%Q")}
    gvl_in = {a for a in gvl_addrs if a.startswith("%I")}
    gvl_out = {a for a in gvl_addrs if a.startswith("%Q")}
    check("Eingaenge konsistent", io_in == gvl_in, f"IN={len(io_in)}")
    check("Ausgaenge konsistent", io_out == gvl_out, f"OUT={len(io_out)}")

    # HMI-Variablen existieren
    used = {
        "eHmiState", "eHmiMode", "eHmiProcess", "eHmiActiveFault", "eHmiFirstFault",
        "xHmiMotorCmd", "xHmiMotorRun", "xHmiMotorFb", "xHmiOverload", "xHmiEmergency",
        "xHmiEntry", "xHmiExit", "xHmiJam", "xHmiLampRed", "xHmiBuzzer",
        "diHmiCount", "aHmiBeltPos",
    }
    missing = sorted(v for v in used if v.upper() not in names)
    check("HMI-Variablen vorhanden", not missing, f"fehlend: {missing}")

    # Fehlercodes dokumentiert
    fault_names = []
    for path, src in read_all_st():
        _, t, _ = parse_source(src, path)
        for td in t:
            if td.name == "E_FAULTCODE":
                fault_names = [m for m, _ in td.members]
    doc07 = open(os.path.join(ROOT, "docs", "07_Fehlersuche.md"), encoding="utf-8").read()
    undoc = [f for f in fault_names if f not in doc07]
    check("Fehlercodes dokumentiert", not undoc, f"undokumentiert: {undoc}")

    # Klemmenplan deckt I/O ab
    with open(os.path.join(ROOT, "electrical", "terminal_plan", "terminal_plan.csv"),
              encoding="utf-8") as fh:
        trows = list(csv.reader(fh, delimiter=";"))[1:]
    t_di = sum(1 for r in trows if r[2] == "DI")
    t_do = sum(1 for r in trows if r[2] == "DO")
    io_di = sum(1 for r in rows if r[2] == "DI" and not r[0].startswith("%IX1.1"))
    io_do = sum(1 for r in rows if r[2] == "DO")
    check("Klemmenplan deckt Eingaenge", t_di == io_di, f"Klemmen DI={t_di}, IO DI={io_di}")
    check("Klemmenplan deckt Ausgaenge", t_do == io_do, f"Klemmen DO={t_do}, IO DO={io_do}")

    # Bauteilbezeichner im Schaltplan
    with open(os.path.join(ROOT, "electrical", "bom", "bom.csv"), encoding="utf-8") as fh:
        bom = list(csv.reader(fh, delimiter=";"))[1:]
    svg = ""
    for f in ("power_circuit.svg", "control_circuit.svg"):
        svg += open(os.path.join(ROOT, "electrical", "schematics", f), encoding="utf-8").read()
    single = [b[0] for b in bom if b[0].startswith(("Q", "F", "K", "M", "T"))]
    missing_dev = [d for d in single if d not in svg]
    check("Bauteilbezeichner im Schaltplan", not missing_dev, f"fehlend: {missing_dev}")

    # TESTPROTOKOLL vorhanden und 30 Tests
    proto = os.path.join(ROOT, "docs", "09_Testprotokoll.md")
    if os.path.exists(proto):
        txt = open(proto, encoding="utf-8").read()
        m = re.search(r"Testfälle: \*\*(\d+)\*\*", txt)
        n = int(m.group(1)) if m else 0
        passed = "NICHT BESTANDEN" not in txt and "fehlgeschlagen: **0**" in txt
        check("Testprotokoll: 30 Tests, alle bestanden", n >= 30 and passed, f"n={n}")
    else:
        check("Testprotokoll vorhanden", False, "09_Testprotokoll.md fehlt")

    failed = [r for r in results if not r[1]]
    print()
    print(f"Ergebnis: {len(results) - len(failed)}/{len(results)} Pruefungen bestanden")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
