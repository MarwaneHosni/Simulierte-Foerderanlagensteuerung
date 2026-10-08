# 05 – Schutzkonzept

> Das ist eine **Simulation auf dem PC**. Ich zeige hier, welche Aufgabe
> typische Schutzeinrichtungen haben. Es ist **keine** Auslegung für eine echte
> Anlage – so etwas muss man nach dem echten Typenschild und den Normen machen.

## 1 Leistungskreis und Steuerkreis

Der wichtigste Unterschied:

- **Leistungskreis:** versorgt und schaltet den Motor (3~ 400 V, Annahme).
- **Steuerkreis:** steuert die Schaltgeräte und die SPS (24 V, Annahme).

Das Schütz K1 verbindet beide: Seine Spule liegt im Steuerkreis, seine
Hauptkontakte im Leistungskreis.

```text
Leistungskreis                         Steuerkreis
Einspeisung 3~400V                     24 V Netzteil T1
   │                                      │
  Q1 Hauptschalter                      Not-Halt-/Steuerkette
   │                                      │
  F1 Leitungsschutz                     SPS
   │                                      │
  F2 Motorschutz (Überlast)             K1 Spule / Melder
   │
  K1 Hauptkontakte
   │
  M1 Drehstrommotor
```

## 2 Wer macht was?

| Bezeichner | Teil | Aufgabe |
| ---------- | ---- | ------- |
| Q1 | Hauptschalter | Anlage komplett freischalten |
| F1 | Leitungsschutz | schützt die Leitungen vor zu viel Strom |
| F2 | Motorschutzrelais | schützt den Motor vor **Überlast** |
| K1 | Schütz | schaltet den Motorstrom |
| T1 | Netzteil 24 V | liefert die Steuerspannung |
| S3 | Not-Halt (Öffner) | stoppt im Notfall |
| SPS | SoftPLC | Logik, Diagnose, Meldungen |
| X1–X6 | Klemmen | saubere Verdrahtung/Schnittstellen |

## 3 Warum es diese Teile gibt

- **Hauptschalter Q1:** trennt die Anlage bei Wartung komplett vom Netz.
- **Leitungsschutz F1:** schützt die Leitungen (Kurzschluss/Überstrom).
- **Motorschutz F2:** löst bei **anhaltender Überlast** zeitversetzt aus. Sein
  Öffner-Kontakt geht als `%IX0.3` an die SPS.
- **Schütz K1:** schaltet den Motor kontrolliert. Es schützt **nicht**, es
  schaltet nur.
- **Netzteil T1:** trennt die 24-V-Steuerebene vom Motorstrom.
- **Not-Halt-Kette S3:** unterbricht die Ansteuerung des Schützes.

## 4 Der harte Schutz (auch ohne SPS)

Im Modell `FB_ContactorMotor` gilt:

```text
Schütz zieht an = Befehl AND NOT Überlast AND NOT Not-Halt
```

Das heißt: **Auch wenn die SPS „EIN“ sagt, fällt das Schütz bei Überlast oder
Not-Halt ab.** Genau so wirkt eine echte Schutzeinrichtung direkt im
Leistungskreis. Die SPS merkt über die fehlende Rückmeldung, dass etwas nicht
stimmt, und meldet eine Störung. Das war für mich ein wichtiger Aha-Moment.

## 5 Was bei Überlast passiert

```text
Motor läuft  →  Überlast erkannt  →  F2 löst aus
             →  Schütz fällt ab
             →  keine Rückmeldung
             →  SPS: Störung ÜBERLAST, Motor AUS, FAULT
```

Die Störung bleibt gespeichert, bis Ursache weg ist **und** quittiert wurde.

## 6 Not-Halt (nur nachgebildet)

- Beim Drücken wird die Ansteuerung des Schützes unterbrochen; die Bewegung
  stoppt sofort.
- Der Zustand wird `EMERGENCY`, die Störung wird gemeldet.
- Danach muss ich **bewusst** Reset drücken und neu starten. Es gibt **keinen**
  automatischen Wiederanlauf.

> Der Not-Halt hier ist nur die **Nachbildung einer Steuerlogik**. Er ist
> **keine** zertifizierte Sicherheitsschaltung. Ein Not-Halt-Bit in der SPS
> allein macht noch keine sichere Maschine.

## 7 Zu den Werten

Alle elektrischen Werte sind **nur Annahmen zum Üben**. Die Beispielrechnung
steht in `11_Technische_Berechnung.md`. In der Realität wählt man F1, F2 und K1
nach dem echten Motor (Typenschild und Betriebsstrom) aus.
