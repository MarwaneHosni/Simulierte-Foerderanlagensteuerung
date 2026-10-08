# 10 – Grenzen und Annahmen

> Kurz gesagt: Das hier ist ein **Lernprojekt** und eine **Simulation auf dem
> PC**. Ich habe keine echte Anlage gebaut, nichts verdrahtet und nichts
> gemessen.

## 1 Was das Projekt nicht ist

- Keine echte Hardware, keine echte Verdrahtung, keine Messungen.
- Keine echte Inbetriebnahme und keine echte Fehlersuche an Geräten.
- Der Not-Halt ist nur die **Nachbildung einer Steuerlogik** – keine
  zertifizierte Sicherheitsschaltung und keine funktionale Sicherheit.
- Ich behaupte keine Zertifizierungen. Es ist ein Lernprojekt, kein Beruf.

## 2 Annahmen in der Simulation

| Größe | Wert | Was es bedeutet |
| ----- | ---- | --------------- |
| Zykluszeit | 20 ms | fester Simulationsschritt |
| `T_CONTACTOR_PULL` | 300 ms | Anzugsverzögerung Schütz |
| `T_OVERLOAD_TRIP` | 3000 ms | Auslöseverzögerung Motorschutz |
| `T_MOTOR_START_TIMEOUT` | 2000 ms | Überwachung „läuft nicht an“ |
| `T_MOTOR_STOP_TIMEOUT` | 2000 ms | Überwachung „stoppt nicht“ |
| `T_MAX_TRANSPORT` | 8000 ms | zulässige Transportzeit (Stau) |
| `T_RUN_ON` | 1500 ms | Nachlauf nach dem Auslauf |
| `T_DEBOUNCE` | 500 ms | Entprell-/Plausibilitätszeit |
| Bandlänge | 100 % | normiertes Modell |
| Bandgeschwindigkeit | 25 %/s | Annahme |
| Werkstückintervall | 4000 ms | Annahme (Automatik) |

Diese Werte habe ich **frei gewählt** – es sind keine echten Anlagendaten.

## 3 Der Motor

- Der Motor ist ein **erfundener** Drehstrommotor (0,75 kW / 400 V) nur zum
  Rechnen und Erklären (siehe `11_Technische_Berechnung.md`).
- Ich simuliere **keine** genaue Motor-Physik. Nur das, was für Steuerung und
  Diagnose nötig ist (läuft / Rückmeldung / Überlast).

## 4 Die elektrische Doku

- Die Schaltpläne sind **Übersichts-/Konzeptbilder**, keine vollständigen
  Werkstattzeichnungen.
- Die QElectroTech-Datei ist ein **Ausgangsgerüst**, weil die
  QElectroTech-Bibliothek auf meinem Rechner nicht installiert war. Gut lesbar
  sind die SVG-/PNG-Pläne (siehe `electrical/qelectrotech/README.md`).
- Die Schutzwerte sind **nicht** für eine echte Anlage gültig.

## 5 SPS und Software

- CODESYS lief in meiner Umgebung nicht. Deshalb habe ich die Steuerlogik in
  **IEC-61131-3-Structured-Text** geschrieben und führe sie mit einer **selbst
  gebauten Python-SoftPLC** aus.
- Es gibt einen PLCopen-Export (`plc/export/`) für den Fall, dass ich den Code
  später in CODESYS übernehme. Wichtig bleiben aber die `.st`-Dateien.
- Meine Python-SoftPLC kann nur die **Sprachmittel, die ich auch benutze** –
  nicht den ganzen IEC-61131-3-Umfang.

## 6 Diagnose

- Störungen werden aus **Simulationssignalen** erkannt. Echte Fehler (z. B. ein
  Kabelfehler) habe ich durch Injektionssignale nachgebildet.
- Ein defekter Sensor kann wie in echt zu Fehlzählungen führen.

## 7 Fazit

Das Projekt zeigt, dass ich mich mit Motorsteuerung, Schutz, Verriegelungen,
Sensorik, SPS-Logik und Fehlersuche beschäftigt habe – als **Simulation und
Übung**, nicht als echte Anlage. Es hat mir viel Spaß gemacht und ich habe eine
Menge dabei gelernt.
