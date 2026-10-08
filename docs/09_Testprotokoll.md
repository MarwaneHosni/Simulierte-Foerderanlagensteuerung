# 09 - Testprotokoll

**Projekt:** Automatisierte Förderbandsteuerung mit SPS


> Diese Ergebnisse stammen aus **echten Testläufen** meiner SoftPLC (siehe `tests/results/`). Ich habe nichts erfunden. Ein Simulationszyklus dauert 20 ms.


## Zusammenfassung

- Testfälle: **30**
- bestanden: **30**
- fehlgeschlagen: **0**

Gesamtergebnis: **BESTANDEN**

## Ergebnisse

| ID | Gruppe | Titel | Erwartet | Ergebnis | Status |
| -- | ------ | ----- | -------- | -------- | ------ |
| T01 | Grundfunktionen | Startzustand READY | Zustand READY, keine Störung | Zustand READY, Störung - | PASS |
| T02 | Grundfunktionen | Automatikstart durch Werkstueck | Band startet automatisch (Schützbefehl EIN) | Schützbefehl EIN nach 202 Zyklen = True | PASS |
| T03 | Grundfunktionen | Stop hat Vorrang vor Start | Motor aus (Stop dominiert) | Schützbefehl = 0 | PASS |
| T04 | Grundfunktionen | Reset ohne Stoerung startet nicht | Kein Motorstart, keine Zaehleraenderung | Schützbefehl = 0, Zaehler = 0 | PASS |
| T05 | Grundfunktionen | Automatikbetrieb: Transport und Zaehlung | Werkstueck wird gezaehlt (Zaehler >= 1) | Zaehler = 1 nach 405 Zyklen | PASS |
| T06 | Grundfunktionen | Handbetrieb | Motor laeuft (RUNNING, Befehl und Rueckmeldung EIN) | Zustand RUNNING, Befehl 1, Rueckmeldung 1 | PASS |
| T07 | Grundfunktionen | Handbetrieb durch Not-Halt gesperrt | Kein Motorstart, Zustand EMERGENCY | Schützbefehl = 0, Zustand EMERGENCY | PASS |
| T08 | Grundfunktionen | Betriebsartwechsel stoppt das Band | Band wird gestoppt (kein automatischer Weiterlauf ohne Werkstueck) | Schützbefehl = 0 | PASS |
| T09 | Motor | Erfolgreicher Motorstart mit Rueckmeldung | Rueckmeldung EIN, Zustand RUNNING | Rueckmeldung 1, Zustand RUNNING | PASS |
| T10 | Motor | Motor laeuft nicht an (Start-Timeout) | Stoerung START-TIMEOUT | Stoerung START-TIMEOUT nach 103 Zyklen | PASS |
| T11 | Motor | Erfolgreicher Motorstop | Schützbefehl und Rueckmeldung AUS | Befehl 0, Rueckmeldung 0 | PASS |
| T12 | Motor | Motor stoppt nicht (Stop-Timeout) | Stoerung STOP-TIMEOUT | Stoerung STOP-TIMEOUT nach 121 Zyklen | PASS |
| T13 | Motor | Motorueberlast | Motor AUS, Stoerung UEBERLAST | Stoerung UEBERLAST, Schützbefehl 0 | PASS |
| T14 | Motor | Ueberlast blockiert Wiederanlauf | Kein Wiederanlauf (Stoerung verriegelt) | Schützbefehl = 0 | PASS |
| T15 | Sensorik | Einlaufsensor erkennt Werkstueck | Einlaufsensor B1 aktiv | B1 = 1, Zyklus 201 | PASS |
| T16 | Sensorik | Auslaufsensor erkennt Werkstueck | Auslaufsensor B2 aktiv | B2 = 1, Zyklus 404 | PASS |
| T17 | Sensorik | Zaehler zaehlt nur einmal je Werkstueck | Zaehler genau 1 (keine Mehrfachzaehlung) | Zaehler = 1 | PASS |
| T18 | Sensorik | Sensor-Inkonsistenz (Dauersignal) | Stoerung SENSOR-INKONSISTENZ | Stoerung SENSOR-INKONSISTENZ nach 29 Zyklen | PASS |
| T19 | Sensorik | Kein Fehlalarm bei normalem Transport | Keine Sensor-Inkonsistenz, Zaehler inkrementiert | Fehlalarm = False, Zaehler = 1 | PASS |
| T20 | Foerderband | Transportzeit im erwarteten Bereich | Transportzeit ca. 188 Zyklen (theoretisch) | 204 Zyklen (4.08 s) | PASS |
| T21 | Foerderband | Stauererkennung | Stoerung STAU | Stoerung STAU nach 602 Zyklen | PASS |
| T22 | Foerderband | Erholung nach Stau | Stoerung geloescht, Band laeuft wieder | Stoerung -, Schützbefehl 1 | PASS |
| T23 | Foerderband | Keine Stau-Stoerung vor Transportzeit | Noch keine Stau-Stoerung (Timeout 8 s = 400 Zyklen) | vorzeitige Stoerung = False | PASS |
| T24 | Sicherheit | Not-Halt im Stillstand | Zustand EMERGENCY, Motor aus | Zustand EMERGENCY, Schützbefehl 0 | PASS |
| T25 | Sicherheit | Not-Halt waehrend des Laufs | Zustand EMERGENCY, Motor sofort aus | Zustand EMERGENCY, Befehl 0, Rueckmeldung 0 | PASS |
| T26 | Sicherheit | Kein Wiederanlauf ohne Quittung nach Not-Halt | Vor Reset Stoerung gespeichert, nach Reset geloescht | vor Reset Stoerung=True, danach - | PASS |
| T27 | Sicherheit | Schuetz faellt bei Not-Halt ab | Schütz faellt ab (xSimContactor = 0), Motor aus | Schütz 0, Befehl 0 | PASS |
| T28 | Wiederanlauf | Stoerung beseitigen und quittieren | Stoerung geloescht, Anlage wieder bereit | Stoerung -, Zustand READY | PASS |
| T29 | Wiederanlauf | Neustart nach Stoerung | Motor startet wieder (RUNNING) | Befehl 1, Rueckmeldung 1, Zustand RUNNING | PASS |
| T30 | Wiederanlauf | First-out und Prioritaet der Stoerung | First-out bleibt START-TIMEOUT (2), Anzeige priorisiert 2 | first=2, danach first=2, aktiv=2 | PASS |

## Details

### T01 – Startzustand READY (Grundfunktionen)

- **Ausgangszustand:** Spannungsversorgung, keine Befehle
- **Aktion:** 5 Zyklen Initialisierung
- **Erwartet:** Zustand READY, keine Störung
- **Ergebnis:** Zustand READY, Störung -
- **Zyklen:** 7 (0.14 s simuliert)
- **Status:** PASS

### T02 – Automatikstart durch Werkstueck (Grundfunktionen)

- **Ausgangszustand:** Automatikbetrieb, keine Störung
- **Aktion:** Automatik + Werkstueckerzeugung aktiv
- **Erwartet:** Band startet automatisch (Schützbefehl EIN)
- **Ergebnis:** Schützbefehl EIN nach 202 Zyklen = True
- **Zyklen:** 202 (4.04 s simuliert)
- **Status:** PASS

### T03 – Stop hat Vorrang vor Start (Grundfunktionen)

- **Ausgangszustand:** Motor laeuft (Hand)
- **Aktion:** Start und Stop gleichzeitig
- **Erwartet:** Motor aus (Stop dominiert)
- **Ergebnis:** Schützbefehl = 0
- **Zyklen:** 24 (0.48 s simuliert)
- **Status:** PASS

### T04 – Reset ohne Stoerung startet nicht (Grundfunktionen)

- **Ausgangszustand:** Anlage READY, keine Stoerung
- **Aktion:** Reset-Taster betaetigen
- **Erwartet:** Kein Motorstart, keine Zaehleraenderung
- **Ergebnis:** Schützbefehl = 0, Zaehler = 0
- **Zyklen:** 11 (0.22 s simuliert)
- **Status:** PASS

### T05 – Automatikbetrieb: Transport und Zaehlung (Grundfunktionen)

- **Ausgangszustand:** Automatikbetrieb
- **Aktion:** Werkstueck durchlaufen lassen
- **Erwartet:** Werkstueck wird gezaehlt (Zaehler >= 1)
- **Ergebnis:** Zaehler = 1 nach 405 Zyklen
- **Zyklen:** 405 (8.10 s simuliert)
- **Status:** PASS

### T06 – Handbetrieb (Grundfunktionen)

- **Ausgangszustand:** Handbetrieb, keine Stoerung
- **Aktion:** Start-Taster betaetigen
- **Erwartet:** Motor laeuft (RUNNING, Befehl und Rueckmeldung EIN)
- **Ergebnis:** Zustand RUNNING, Befehl 1, Rueckmeldung 1
- **Zyklen:** 20 (0.40 s simuliert)
- **Status:** PASS

### T07 – Handbetrieb durch Not-Halt gesperrt (Grundfunktionen)

- **Ausgangszustand:** Not-Halt aktiv
- **Aktion:** Start-Taster im Handbetrieb betaetigen
- **Erwartet:** Kein Motorstart, Zustand EMERGENCY
- **Ergebnis:** Schützbefehl = 0, Zustand EMERGENCY
- **Zyklen:** 13 (0.26 s simuliert)
- **Status:** PASS

### T08 – Betriebsartwechsel stoppt das Band (Grundfunktionen)

- **Ausgangszustand:** Motor laeuft im Handbetrieb
- **Aktion:** Wechsel auf Automatik
- **Erwartet:** Band wird gestoppt (kein automatischer Weiterlauf ohne Werkstueck)
- **Ergebnis:** Schützbefehl = 0
- **Zyklen:** 25 (0.50 s simuliert)
- **Status:** PASS

### T09 – Erfolgreicher Motorstart mit Rueckmeldung (Motor)

- **Ausgangszustand:** Stillstand, keine Stoerung
- **Aktion:** Start-Taster (Hand)
- **Erwartet:** Rueckmeldung EIN, Zustand RUNNING
- **Ergebnis:** Rueckmeldung 1, Zustand RUNNING
- **Zyklen:** 20 (0.40 s simuliert)
- **Status:** PASS

### T10 – Motor laeuft nicht an (Start-Timeout) (Motor)

- **Ausgangszustand:** Rueckmeldung faellt aus (simulierter Defekt)
- **Aktion:** Start-Taster
- **Erwartet:** Stoerung START-TIMEOUT
- **Ergebnis:** Stoerung START-TIMEOUT nach 103 Zyklen
- **Zyklen:** 103 (2.06 s simuliert)
- **Status:** PASS

### T11 – Erfolgreicher Motorstop (Motor)

- **Ausgangszustand:** Motor laeuft
- **Aktion:** Stop-Taster
- **Erwartet:** Schützbefehl und Rueckmeldung AUS
- **Ergebnis:** Befehl 0, Rueckmeldung 0
- **Zyklen:** 26 (0.52 s simuliert)
- **Status:** PASS

### T12 – Motor stoppt nicht (Stop-Timeout) (Motor)

- **Ausgangszustand:** Rueckmeldung haengt EIN (simulierter Defekt)
- **Aktion:** Stop-Taster
- **Erwartet:** Stoerung STOP-TIMEOUT
- **Ergebnis:** Stoerung STOP-TIMEOUT nach 121 Zyklen
- **Zyklen:** 121 (2.42 s simuliert)
- **Status:** PASS

### T13 – Motorueberlast (Motor)

- **Ausgangszustand:** Motor laeuft
- **Aktion:** Ueberlast wird ausgeloest
- **Erwartet:** Motor AUS, Stoerung UEBERLAST
- **Ergebnis:** Stoerung UEBERLAST, Schützbefehl 0
- **Zyklen:** 172 (3.44 s simuliert)
- **Status:** PASS

### T14 – Ueberlast blockiert Wiederanlauf (Motor)

- **Ausgangszustand:** Ueberlast gespeichert, nicht quittiert
- **Aktion:** Start-Taster erneut
- **Erwartet:** Kein Wiederanlauf (Stoerung verriegelt)
- **Ergebnis:** Schützbefehl = 0
- **Zyklen:** 181 (3.62 s simuliert)
- **Status:** PASS

### T15 – Einlaufsensor erkennt Werkstueck (Sensorik)

- **Ausgangszustand:** Automatikbetrieb
- **Aktion:** Werkstueck am Einlauf
- **Erwartet:** Einlaufsensor B1 aktiv
- **Ergebnis:** B1 = 1, Zyklus 201
- **Zyklen:** 201 (4.02 s simuliert)
- **Status:** PASS

### T16 – Auslaufsensor erkennt Werkstueck (Sensorik)

- **Ausgangszustand:** Automatikbetrieb
- **Aktion:** Werkstueck am Auslauf
- **Erwartet:** Auslaufsensor B2 aktiv
- **Ergebnis:** B2 = 1, Zyklus 404
- **Zyklen:** 404 (8.08 s simuliert)
- **Status:** PASS

### T17 – Zaehler zaehlt nur einmal je Werkstueck (Sensorik)

- **Ausgangszustand:** Ein Werkstueck auf dem Band
- **Aktion:** Durchlauf bis Auslauf
- **Erwartet:** Zaehler genau 1 (keine Mehrfachzaehlung)
- **Ergebnis:** Zaehler = 1
- **Zyklen:** 705 (14.10 s simuliert)
- **Status:** PASS

### T18 – Sensor-Inkonsistenz (Dauersignal) (Sensorik)

- **Ausgangszustand:** Anlage steht, kein Transport
- **Aktion:** Auslaufsensor liefert Dauersignal
- **Erwartet:** Stoerung SENSOR-INKONSISTENZ
- **Ergebnis:** Stoerung SENSOR-INKONSISTENZ nach 29 Zyklen
- **Zyklen:** 29 (0.58 s simuliert)
- **Status:** PASS

### T19 – Kein Fehlalarm bei normalem Transport (Sensorik)

- **Ausgangszustand:** Automatikbetrieb
- **Aktion:** Normales Werkstueck transportieren
- **Erwartet:** Keine Sensor-Inkonsistenz, Zaehler inkrementiert
- **Ergebnis:** Fehlalarm = False, Zaehler = 1
- **Zyklen:** 405 (8.10 s simuliert)
- **Status:** PASS

### T20 – Transportzeit im erwarteten Bereich (Foerderband)

- **Ausgangszustand:** Werkstueck am Einlauf
- **Aktion:** Transport bis Auslauf
- **Erwartet:** Transportzeit ca. 188 Zyklen (theoretisch)
- **Ergebnis:** 204 Zyklen (4.08 s)
- **Zyklen:** 405 (8.10 s simuliert)
- **Status:** PASS

### T21 – Stauererkennung (Foerderband)

- **Ausgangszustand:** Automatikbetrieb
- **Aktion:** Blockade in Bandmitte
- **Erwartet:** Stoerung STAU
- **Ergebnis:** Stoerung STAU nach 602 Zyklen
- **Zyklen:** 602 (12.04 s simuliert)
- **Status:** PASS

### T22 – Erholung nach Stau (Foerderband)

- **Ausgangszustand:** Stau quittiert, Blockade entfernt
- **Aktion:** Reset und Weiterbetrieb
- **Erwartet:** Stoerung geloescht, Band laeuft wieder
- **Ergebnis:** Stoerung -, Schützbefehl 1
- **Zyklen:** 606 (12.12 s simuliert)
- **Status:** PASS

### T23 – Keine Stau-Stoerung vor Transportzeit (Foerderband)

- **Ausgangszustand:** Werkstueck laeuft an, Blockade
- **Aktion:** 300 Zyklen beobachten
- **Erwartet:** Noch keine Stau-Stoerung (Timeout 8 s = 400 Zyklen)
- **Ergebnis:** vorzeitige Stoerung = False
- **Zyklen:** 501 (10.02 s simuliert)
- **Status:** PASS

### T24 – Not-Halt im Stillstand (Sicherheit)

- **Ausgangszustand:** Anlage steht (READY)
- **Aktion:** Not-Halt-Taster betaetigen
- **Erwartet:** Zustand EMERGENCY, Motor aus
- **Ergebnis:** Zustand EMERGENCY, Schützbefehl 0
- **Zyklen:** 5 (0.10 s simuliert)
- **Status:** PASS

### T25 – Not-Halt waehrend des Laufs (Sicherheit)

- **Ausgangszustand:** Motor laeuft
- **Aktion:** Not-Halt-Taster betaetigen
- **Erwartet:** Zustand EMERGENCY, Motor sofort aus
- **Ergebnis:** Zustand EMERGENCY, Befehl 0, Rueckmeldung 0
- **Zyklen:** 23 (0.46 s simuliert)
- **Status:** PASS

### T26 – Kein Wiederanlauf ohne Quittung nach Not-Halt (Sicherheit)

- **Ausgangszustand:** Not-Halt war aktiv, Taster wieder freigegeben
- **Aktion:** Zuerst ohne Quittung beobachten, dann Reset
- **Erwartet:** Vor Reset Stoerung gespeichert, nach Reset geloescht
- **Ergebnis:** vor Reset Stoerung=True, danach -
- **Zyklen:** 49 (0.98 s simuliert)
- **Status:** PASS

### T27 – Schuetz faellt bei Not-Halt ab (Sicherheit)

- **Ausgangszustand:** Motor laeuft (Schütz angezogen)
- **Aktion:** Not-Halt betaetigen
- **Erwartet:** Schütz faellt ab (xSimContactor = 0), Motor aus
- **Ergebnis:** Schütz 0, Befehl 0
- **Zyklen:** 21 (0.42 s simuliert)
- **Status:** PASS

### T28 – Stoerung beseitigen und quittieren (Wiederanlauf)

- **Ausgangszustand:** Start-Timeout gespeichert
- **Aktion:** Defekt behoben und Reset
- **Erwartet:** Stoerung geloescht, Anlage wieder bereit
- **Ergebnis:** Stoerung -, Zustand READY
- **Zyklen:** 112 (2.24 s simuliert)
- **Status:** PASS

### T29 – Neustart nach Stoerung (Wiederanlauf)

- **Ausgangszustand:** Stoerung quittiert
- **Aktion:** Start-Taster erneut
- **Erwartet:** Motor startet wieder (RUNNING)
- **Ergebnis:** Befehl 1, Rueckmeldung 1, Zustand RUNNING
- **Zyklen:** 130 (2.60 s simuliert)
- **Status:** PASS

### T30 – First-out und Prioritaet der Stoerung (Wiederanlauf)

- **Ausgangszustand:** Start-Timeout gespeichert
- **Aktion:** Zusaetzlich Stop-Timeout erzeugen
- **Erwartet:** First-out bleibt START-TIMEOUT (2), Anzeige priorisiert 2
- **Ergebnis:** first=2, danach first=2, aktiv=2
- **Zyklen:** 205 (4.10 s simuliert)
- **Status:** PASS

