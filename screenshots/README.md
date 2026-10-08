# Nachweise / Screenshots

Alle Bilder wurden aus **echten Simulationsläufen** der SoftPLC erzeugt
(`tools/gen_screenshots.py`, `tools/gen_schematic.py`). Keine retuschierten oder
erfundenen Zustände.

## HMI / Prozessvisualisierung

| Datei | Inhalt |
| ----- | ------ |
| `hmi_startup.png` | Anlage im Zustand READY |
| `hmi_manual.png` | Handbetrieb, Motor EIN |
| `hmi_running.png` | Automatik, Werkstück läuft auf dem Band |
| `hmi_workpiece_entry.png` | Werkstück am Einlauf (B1 aktiv) |
| `hmi_counter.png` | Werkstückzähler inkrementiert |
| `hmi_fault_overload.png` | Störung Überlast |
| `hmi_fault_start.png` | Störung Start-Timeout |
| `hmi_fault_jam.png` | Störung Stau |
| `hmi_emergency.png` | Not-Halt / EMERGENCY |

## Schaltpläne und I/O

| Datei | Inhalt |
| ----- | ------ |
| `schematic_power.png` | Stromlaufplan Leistungskreis |
| `schematic_control.png` | Stromlaufplan Steuerkreis |
| `io_overview.png` | I/O-Übersicht der SoftPLC |
| `zustandsautomat.png` | Zustandsübersicht der Anlage |
| `verriegelung.png` | Übersicht Verriegelungen/Freigaben |

Die Vektorversionen liegen unter `../electrical/schematics/`.

## Animationen

| Datei | Inhalt |
| ----- | ------ |
| `demo.gif` | START → Motor → Werkstück → Auslauf → Zähler → Stop |
| `fault_demo.gif` | Motor läuft → Überlast → Abschaltung |

## Test-Nachweise

Die Rohdaten der Tests liegen in `../tests/results/` (`results.csv` und
`trace_Txx.jsonl`). Das erzeugte Protokoll steht in
`../docs/09_Testprotokoll.md`.
