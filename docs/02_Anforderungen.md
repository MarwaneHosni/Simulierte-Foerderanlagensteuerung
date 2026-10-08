# 02 – Anforderungen

Hier habe ich aufgeschrieben, was die Anlage können soll. Die Nummern (FR, SR,
DR, HR, NFR) helfen mir beim Testen: In `08_Testplan.md` steht, welcher Test zu
welcher Anforderung gehört.

## 1 Funktionale Anforderungen (FR)

Das sind die „normalen“ Aufgaben der Anlage.

| Nr. | Anforderung |
| --- | ----------- |
| FR-01 | Die Anlage hat die Zustände INIT, READY, RUNNING, STOPPED, FAULT, EMERGENCY. |
| FR-02 | Nach dem Start geht sie von INIT nach READY (wenn nichts stört). |
| FR-03 | Über einen Wahlschalter wählt man Hand oder Automatik. |
| FR-04 | In Automatik startet das Band, abhängig von Werkstück am Einlauf (oder als Dauerlauf). |
| FR-05 | In Hand fährt man das Band selbst mit Start/Stop. |
| FR-06 | Der Motorbefehl geht an das Schütz; der echte Lauf wird über die Rückmeldung geprüft. |
| FR-07 | Fertige Werkstücke werden gezählt (mit Flankenauswertung, keine Doppelzählung). |
| FR-08 | Einlauf- und Auslaufsensor erkennen Werkstücke. |
| FR-09 | Ein Stau wird erkannt, wenn der Auslauf nicht rechtzeitig erreicht wird. |
| FR-10 | Eine Störung schaltet den Motor ab und wird gemeldet. |
| FR-11 | Eine Störung bleibt gespeichert, bis die Ursache weg ist und quittiert wurde. |
| FR-12 | Ein Reset ohne Störung startet die Anlage nicht. |
| FR-13 | Start wirkt nicht, solange Stop, Not-Halt, Überlast oder eine Störung ansteht. |
| FR-14 | Es gibt Leuchten und eine Hupe für Meldungen. |

## 2 Sicherheits-/Verriegelungsanforderungen (SR)

Das sind die „Schutzregeln“.

| Nr. | Anforderung |
| --- | ----------- |
| SR-01 | Stop hat Vorrang vor Start. |
| SR-02 | Bei Not-Halt kann der Motor nicht laufen (Hand und Automatik). |
| SR-03 | Bei Überlast kann der Motor nicht laufen. |
| SR-04 | Der Motor läuft über eine Selbsthaltung; Stop/Störung setzen sie zurück. |
| SR-05 | Bei Überlast oder Not-Halt fällt das Schütz auch ohne die SPS ab. |
| SR-06 | Der Handbetrieb umgeht keine Schutz- oder Verriegelungsfunktion. |
| SR-07 | Unmögliche/widersprüchliche Sensorsignale werden erkannt und gemeldet. |
| SR-08 | Nach Not-Halt startet die Anlage nicht von selbst – erst Reset und Start. |

## 3 Diagnose-/Meldeanforderungen (DR)

Das sind die Fehlermeldungen.

| Nr. | Anforderung | Fehlercode |
| --- | ----------- | ---------- |
| DR-01 | Motorüberlast wird erkannt und gemeldet. | FAULT_OVERLOAD |
| DR-02 | „Motor läuft nicht an“ wird gemeldet. | FAULT_START_TIMEOUT |
| DR-03 | „Motor stoppt nicht“ wird gemeldet. | FAULT_STOP_TIMEOUT |
| DR-04 | Stau/Blockade wird gemeldet. | FAULT_JAM |
| DR-05 | Sensor-Inkonsistenz wird gemeldet. | FAULT_SENSOR_INCONSISTENCY |
| DR-06 | Not-Halt wird gemeldet. | FAULT_EMERGENCY |
| DR-07 | Die zuerst aufgetretene Störung bleibt erkennbar (First-out). | — |
| DR-08 | Störungen werden über rote Leuchte und Hupe angezeigt. | — |

## 4 Bedien-/HMI-Anforderungen (HR)

| Nr. | Anforderung |
| --- | ----------- |
| HR-01 | Das HMI zeigt den Zustand (READY/RUNNING/STOPPED/FAULT/EMERGENCY). |
| HR-02 | Das HMI zeigt Motorbefehl, Rückmeldung und Schutzstatus. |
| HR-03 | Das HMI zeigt den Werkstückzähler. |
| HR-04 | Das HMI zeigt die aktive Störung. |
| HR-05 | Das HMI zeigt das Band mit Werkstücken und die Sensoren. |
| HR-06 | Alle Anzeigen kommen aus echten Simulationsvariablen. |

## 5 Nicht-funktionale Anforderungen (NFR)

| Nr. | Anforderung |
| --- | ----------- |
| NFR-01 | Alles läuft auf dem PC, ohne zusätzliche Hardware. |
| NFR-02 | Die Steuerlogik ist in IEC 61131-3 ST und für CODESYS exportierbar. |
| NFR-03 | Die Simulation läuft mit festem Takt und ist reproduzierbar. |
| NFR-04 | Testergebnisse werden echt gemessen, nicht erfunden. |
| NFR-05 | Alles ist auf Deutsch beschrieben. |
| NFR-06 | I/O-Liste, ST-Adressen, Klemmenplan, Schaltplan und HMI passen zusammen. |
| NFR-07 | Es gibt keine falschen Angaben zu Inbetriebnahme oder Sicherheit. |

## 6 Was ich bewusst nicht mache

- Keine echte Hardware, keine echte Verdrahtung, keine echte Sicherheitsschaltung.
- Keine Auslegung echter Schutzkomponenten für eine reale Anlage.
- Keine detaillierte Motor-Physik (nur das, was für Steuerung/Diagnose nötig ist).
- Kein Umrichterantrieb, sondern eine klassische Schützsteuerung.
- Zuerst kein Rechts-/Linkslauf (nur eine Richtung).

## 7 Welcher Test prüft was (Traceability)

| Anforderung | Tests |
| ----------- | ----- |
| FR-01, FR-02 | T01 |
| FR-03 | T07, T08 |
| FR-04 | T02, T05, T20 |
| FR-05 | T06 |
| FR-06 | T09, T10, T11, T12 |
| FR-07 | T17 |
| FR-08 | T15, T16 |
| FR-09 | T21, T23 |
| FR-10 | T13, T21, T25 |
| FR-11 | T22, T28 |
| FR-12 | T04 |
| FR-13 | T03, T07, T14 |
| FR-14 | T02, T25 |
| SR-01 | T03 |
| SR-02 | T24, T25 |
| SR-03 | T13, T14 |
| SR-04 | T09, T11 |
| SR-05 | T27 |
| SR-06 | T07 |
| SR-07 | T18 |
| SR-08 | T26 |
| DR-01 | T13 |
| DR-02 | T10 |
| DR-03 | T12 |
| DR-04 | T21 |
| DR-05 | T18 |
| DR-06 | T24, T25 |
| DR-07 | T30 |
| HR-01…06 | HMI-Bilder |
