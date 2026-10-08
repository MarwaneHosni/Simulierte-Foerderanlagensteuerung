# 07 – Fehlersuche

Wenn etwas nicht läuft, will ich wissen, **warum**. Genau das ist Fehlersuche
(Fehlersuche = systematisch auf die Ursache kommen). Dieses Kapitel beschreibt,
wie die Anlage Fehler erkennt und wie ich vorgehe.

## 1 Schnellübersicht: Symptom → Ursache → Maßnahme

| Symptom | Mögliche Ursache | Woran erkennt man es | Was tun |
| ------- | ---------------- | -------------------- | ------- |
| Motor startet nicht | Überlast / Motorschutz ausgelöst | `%IX0.3` = 0, Störung ÜBERLAST | Ursache beheben, Motorschutz zurückstellen, Reset |
| Motor startet nicht | Not-Halt aktiv | `%IX0.2` = 0, Zustand EMERGENCY | Not-Halt entriegeln, Reset, Start |
| Motor startet nicht | Störung nicht quittiert | `xAnyFault` = 1, keine Freigabe | Störung beheben, Reset |
| Motor startet nicht | Stop-Taster defekt/gedrückt | `%IX0.1` = 0 | Taster prüfen |
| Befehl EIN, keine Rückmeldung | Schütz zieht nicht / Rückmeldung defekt | START-TIMEOUT | Schütz, Rückmeldekontakt, Motorstromkreis prüfen |
| Motor bleibt nach Stop an | Rückmeldung hängt / Schütz klebt | STOP-TIMEOUT | Schütz/Rückmeldung prüfen, sicher freischalten |
| Band stoppt im Betrieb | Stau/Blockade | STAU nach `T_MAX_TRANSPORT` | Blockade entfernen, Reset |
| Sensor meldet dauerhaft | defekter/verschmutzter Sensor | SENSOR-INKONSISTENZ | Sensor reinigen/tauschen |
| Falschzählung | Sensor prellt / doppelte Erfassung | Zähler steigt ohne Werkstück | Sensor prüfen/montieren |
| kein Automatiklauf | kein Werkstück / Prozess in Ruhe | Einlauf B1 = 0 | Werkstückzufuhr prüfen |

## 2 Die Störungscodes

Die Codes stehen im Datentyp `E_FaultCode`.

| Code | Name | Bedeutung | Quittierbar, wenn … |
| ---- | ---- | --------- | ------------------- |
| 0 | `FAULT_NONE` | keine Störung | – |
| 1 | `FAULT_OVERLOAD` | Motorüberlast (F2) | Überlast weg |
| 2 | `FAULT_START_TIMEOUT` | Motor läuft nicht an | Startbedingung weg |
| 3 | `FAULT_STOP_TIMEOUT` | Motor stoppt nicht | Rückmeldung weg |
| 4 | `FAULT_JAM` | Stau/Blockade | Einlauf frei |
| 5 | `FAULT_SENSOR_INCONSISTENCY` | unplausibles Sensor-Signal | Signal weg |
| 6 | `FAULT_EMERGENCY` | Not-Halt | Not-Halt entriegelt |

## 3 So gehe ich vor

1. **Zustand ablesen:** READY / RUNNING / STOPPED / FAULT / EMERGENCY.
2. **Aktive Störung ablesen** (`eHmiActiveFault`).
3. **First-out beachten:** `eHmiFirstFault` zeigt die **erste** Störung. So
   erkenne ich die eigentliche Ursache, auch wenn danach noch etwas dazukommt.
4. **Freigaben prüfen:** Not-Halt (`%IX0.2`), Stop (`%IX0.1`), Überlast
   (`%IX0.3`).
5. **Befehl mit Rückmeldung vergleichen:** Befehl gegen `xHmiMotorFb`. Passt es
   nicht, stimmt etwas mit Schütz oder Rückmeldung nicht.
6. **Quittieren und neu starten:** erst wenn die Ursache weg ist. Ein Reset ohne
   Störung macht nichts.

## 4 Grenzen

- Die Diagnose arbeitet auf **Simulationssignalen**. In der Realität käme eine
  sichere Freischaltung und Messung dazu.
- Ein defekter Sensor kann – wie in echt – zu Fehlzählungen führen.
- Der Fehlerspeicher ist **kein** Diagnosesystem und **keine** Maschinensicherheit.
