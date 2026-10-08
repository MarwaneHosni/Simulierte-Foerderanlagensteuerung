# 08 – Testplan

## 1 Ziel

Ich möchte zeigen, dass meine Steuerung wirklich das tut, was sie soll – und
zwar unter normalen Bedingungen **und** bei Fehlern.

## 2 So teste ich

- **Automatisch** mit `tools/harness.py` und `tests/test_scenarios.py`.
- Jeder Test startet eine **frische** SPS (fester Takt, 20 ms) – so ist alles
  reproduzierbar.
- Fehler erzeuge ich absichtlich über **Injektionssignale** (z. B.
  `xSimInjectOverload`, `xSimInjectJam`).
- Die Ergebnisse werden **wirklich gemessen** und in `tests/results/` sowie in
  `09_Testprotokoll.md` festgehalten. Nichts wird erfunden.

Starten:

```text
python tests/test_scenarios.py
```

## 3 Meine Testfälle

| ID | Gruppe | Was ich teste | Erwartung |
| -- | ------ | ------------- | --------- |
| T01 | Grund | Startzustand | READY, keine Störung |
| T02 | Grund | Automatikstart durch Werkstück | Band startet |
| T03 | Grund | Stop und Start gleichzeitig | Motor aus (Stop gewinnt) |
| T04 | Grund | Reset ohne Störung | kein Start |
| T05 | Grund | Automatik: Transport + Zählen | Zähler ≥ 1 |
| T06 | Grund | Handbetrieb | RUNNING |
| T07 | Grund | Hand trotz Not-Halt | kein Start, EMERGENCY |
| T08 | Grund | Betriebsartwechsel | Band stoppt |
| T09 | Motor | Start mit Rückmeldung | RUNNING |
| T10 | Motor | Motor läuft nicht an | START-TIMEOUT |
| T11 | Motor | erfolgreicher Stop | Befehl/Rückmeldung AUS |
| T12 | Motor | Motor stoppt nicht | STOP-TIMEOUT |
| T13 | Motor | Überlast | UEBERLAST, Motor aus |
| T14 | Motor | Überlast blockiert Neustart | kein Start |
| T15 | Sensorik | Einlauf erkannt | B1 = 1 |
| T16 | Sensorik | Auslauf erkannt | B2 = 1 |
| T17 | Sensorik | nur einmal zählen | Zähler = 1 |
| T18 | Sensorik | Dauersignal | SENSOR-INKONSISTENZ |
| T19 | Sensorik | kein Fehlalarm im Normalbetrieb | keine Störung |
| T20 | Band | Transportzeit | ca. 140–260 Zyklen |
| T21 | Band | Stau | STAU |
| T22 | Band | Erholung nach Stau | läuft wieder |
| T23 | Band | keine vorzeitige Stau-Meldung | keine Störung |
| T24 | Sicherheit | Not-Halt im Stillstand | EMERGENCY |
| T25 | Sicherheit | Not-Halt während des Laufs | EMERGENCY, Motor aus |
| T26 | Sicherheit | kein Wiederanlauf ohne Quittung | gespeichert, Reset nötig |
| T27 | Sicherheit | Schütz fällt bei Not-Halt ab | Schütz aus |
| T28 | Wiederanlauf | Störung beheben + Reset | wieder bereit |
| T29 | Wiederanlauf | Neustart nach Störung | RUNNING |
| T30 | Wiederanlauf | First-out/Priorität | erste Störung bleibt |

Die genaue Zuordnung zu den Anforderungen steht in `02_Anforderungen.md`
(Abschnitt 7).

## 4 Regressionstest

Die komplette Testdatei ist gleichzeitig mein Regressionstest. Nach jeder
Änderung lasse ich alle Tests laufen. Erst bei **30/30 bestanden** ist der Stand
für mich „fertig“. Das Ergebnis steht in `09_Testprotokoll.md`.

## 5 Zusätzliche Tests der Runtime

`tests/test_interpreter.py` prüft die SoftPLC selbst (Lexer, Parser,
Standard-Bausteine). Das sind 14 Tests.
