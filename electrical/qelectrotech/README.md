# QElectroTech-Projekt

`foerderanlage.qet` ist eine **generierte** QElectroTech-Projektdatei (Format
0.80) mit zwei Folios:

1. **Leistungskreis** (Einspeisung → Q1 → F1 → F2 → K1 → M1)
2. **Steuerkreis** (24 V DC → Not-Halt-Kette → SPS → Schütz/Meldeorgane)

## Hinweis zur Nutzung

QElectroTech platzierte Symbole stammen aus seiner Bauteilbibliothek. Diese
Bibliothek ist auf dem Erstellungssystem **nicht installiert**, daher enthält die
`.qet`-Datei die Folios mit Titelblock und Hinweistext, aber **keine
vorplatzierten Symbole**. Zum Weiterarbeiten:

1. QElectroTech installieren und `foerderanlage.qet` öffnen.
2. Symbole aus der Standardbibliothek platzieren (Schütz, Motorschutz, Motor,
   Taster, Leuchten, Klemmen, SPS-Ein-/Ausgänge).
3. Verbindungen gemäß den gerenderten Plänen ziehen.

## Maßgebliche, lesbare Schaltpläne

Die inhaltlich vollständigen und direkt lesbaren Stromlaufpläne sind:

- `../schematics/power_circuit.svg` / `.png` – Leistungskreis
- `../schematics/control_circuit.svg` / `.png` – Steuerkreis
- `../schematics/io_overview.svg` / `.png` – I/O-Übersicht

Diese Pläne sind mit den Klemmen (`../terminal_plan/`), der I/O-Liste
(`../io_list/`) und dem ST-Programm (`../../plc/`) konsistent und wurden mit
`tools/gen_schematic.py` aus derselben Datenbasis erzeugt.

> Die `.qet`-Datei ist ein **Ausgangsgerüst**; sie erhebt keinen Anspruch auf
> eine fertig verdrahtete, normgerechte QElectroTech-Zeichnung.
