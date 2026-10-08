# Werkzeuge (tools)

Hilfsskripte rund um Simulation, Test und Dokumentationserzeugung.
Die SPS-Steuerlogik liegt in `../plc/` (IEC 61131-3 Structured Text) und ist die
maßgebliche Quelle; diese Skripte führen sie aus bzw. erzeugen Nachweise.

| Skript | Zweck | Phase |
| ------ | ----- | ----- |
| `motor_calc.py`             | Technische Beispielrechnung Drehstrommotor | 11 |
| `gen_schematic.py`          | Stromlaufplan (Leistung/Steuerung) als SVG + PNG | 8 |
| `gen_qet.py`                | QElectroTech-Projektdatei (`.qet`) | 8 |
| `gen_terminal_io.py`        | Klemmenplan & I/O-Liste als CSV/Markdown | 3, 8 |
| `gen_diagrams.py`           | Architektur-/Ablaufdiagramme | 11 |
| `hmi.py`                    | Live-HMI (Tkinter) auf der SoftPLC-Runtime | 7 |
| `render_hmi.py`             | Deterministische HMI-Screenshots aus aufgezeichneten Zuständen | 7 |
| `gen_animation.py`          | GIF-Demo aus realen Zustandsfolgen | 12 |
| `consistency_check.py`      | Konsistenzprüfung I/O / Klemmen / HMI / Schaltplan | 12 |
| `run_tests.ps1`             | Testsuite ausführen | 9 |

Gemeinsame Konvention: Diese Skripte **erzeugen** nichts, was nicht aus der
Simulation/den ST-Quellen ableitbar ist. Keine erfundenen Messwerte.
