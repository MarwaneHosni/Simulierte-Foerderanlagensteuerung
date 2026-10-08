"""Kommandozeilen-Einstieg zur SoftPLC.

Beispiele:
    python run.py --cycles 100
    python run.py --cycles 500 --auto --generate
    python run.py --interactive
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from softplc import load_project  # noqa: E402

PLC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

_STATE_NAMES = {
    0: "INIT", 10: "READY", 20: "RUNNING", 30: "STOPPED", 40: "FAULT", 50: "EMERGENCY",
}
_FAULT_NAMES = {
    0: "-", 1: "UEBERLAST", 2: "START-TIMEOUT", 3: "STOP-TIMEOUT",
    4: "STAU", 5: "SENSOR-INKONSISTENZ", 6: "NOT-HALT",
}


def _print_status(rt, cycle: int) -> None:
    state = _STATE_NAMES.get(rt.get("eHmiState"), "?")
    fault = _FAULT_NAMES.get(rt.get("eHmiActiveFault"), "?")
    print(
        f"zyklus={cycle:5d}  zustand={state:<9} "
        f"motor_cmd={int(bool(rt.get('xHmiMotorCmd')))} "
        f"motor_fb={int(bool(rt.get('xHmiMotorFb')))} "
        f"stueck={rt.get('diHmiCount')} "
        f"stoerung={fault}"
    )


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="SoftPLC der simulierten Foerderanlage")
    ap.add_argument("--cycles", type=int, default=50, help="Anzahl Simulationszyklen")
    ap.add_argument("--auto", action="store_true", help="Betriebsart Automatik")
    ap.add_argument("--generate", action="store_true", help="Werkstuecke erzeugen")
    ap.add_argument("--start", action="store_true", help="Start-Taster betaetigen")
    ap.add_argument("--interactive", action="store_true", help="Status je Zyklus ausgeben")
    args = ap.parse_args(argv)

    rt = load_project(PLC_DIR)
    rt.set("xModeAuto", bool(args.auto))
    rt.set("xSimGenerateWorkpieces", bool(args.generate))
    rt.run(20)

    for c in range(args.cycles):
        if args.start and c == 1:
            rt.set("xStart", True)
        elif args.start and c == 2:
            rt.set("xStart", False)
        rt.scan()
        if args.interactive or c % max(1, args.cycles // 10) == 0 or c == args.cycles - 1:
            _print_status(rt, c + 1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
