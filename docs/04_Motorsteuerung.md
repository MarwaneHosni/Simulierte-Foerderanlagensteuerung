# 04 – Motorsteuerung

Die Motorsteuerung ist der wichtigste Teil des Projekts. Sie steckt im Baustein
`plc/function_blocks/FB_MotorControl.st`.

Wichtig: Die Steuerung schaltet **nicht** direkt den Motor, sondern gibt nur
einen **Befehl an das Schütz**. Ob der Motor wirklich läuft, merkt sie über die
**Rückmeldung**. Das Schalten und Schützen übernimmt das simulierte
Elektrik-Modell (`FB_ContactorMotor`).

## 1 Die Grundidee

```text
Start (Flanke)  oder  Startimpuls aus der Automatik
        │
        ▼
 Sind alle Bedingungen erfüllt?
 (Freigabe, kein Stop, kein Not-Halt, keine Überlast)
        │ ja
        ▼
 Selbsthaltung wird gesetzt   →  Motor soll laufen
        │
        ▼
 Schützbefehl (zusätzlich gesichert)
        │
        ▼
 Rückmeldung wird erwartet   →  Motor läuft
```

Das Rücksetzen (Kickout) hat **immer Vorrang**:

```text
Stop ODER Not-Halt ODER Überlast ODER fehlende Freigabe ODER Automatik-Stop
        │
        ▼
 Selbsthaltung weg  →  Schützbefehl weg
```

## 2 Die Bedingungen im Detail

**Wann darf gestartet werden?**

```text
Start = (Startflanke OR Automatik-Start)
        AND Freigabe
        AND NOT Stop
        AND NOT Not-Halt
        AND NOT Überlast
```

**Wann wird zurückgesetzt (Kickout)?**

```text
Kickout = Stop OR Automatik-Stop OR Not-Halt OR Überlast OR NOT Freigabe
```

**Der Schützbefehl wird zusätzlich gesichert:**

```text
Schützbefehl = Selbsthaltung AND NOT Stop AND NOT Not-Halt AND NOT Überlast AND Freigabe
```

**Die Selbsthaltung:**

```text
WENN Kickout       DANN Selbsthaltung := AUS;
SONST WENN Start   DANN Selbsthaltung := EIN;
END_WENN;
```

## 3 Die Rückmeldung im Blick behalten

Der Motor gilt nur als „läuft“, wenn die **Rückmeldung** da ist – nicht schon,
weil der Befehl anliegt. Daraus entstehen zwei Diagnosen:

| Situation | Bedingung | Zeit | Störung |
| --------- | --------- | ---- | ------- |
| Läuft nicht an | Befehl EIN, aber Rückmeldung AUS | `T_MOTOR_START_TIMEOUT` | START-TIMEOUT |
| Stoppt nicht | Befehl AUS, aber Rückmeldung EIN | `T_MOTOR_STOP_TIMEOUT` | STOP-TIMEOUT |

```text
TON_start(IN := Schützbefehl AND NOT Rückmeldung, PT := T_MOTOR_START_TIMEOUT)
TON_stop (IN := NOT Schützbefehl AND Rückmeldung, PT := T_MOTOR_STOP_TIMEOUT)
```

Das ist ein schöner Denkfehler-Check: Der Befehl ist nur der *Wunsch*, die
Rückmeldung ist die *Wirklichkeit*. Passen beide längere Zeit nicht zusammen,
ist etwas faul.

## 4 Ein Beispiel (Handstart)

```text
Zyklus n    Start-Taster gedrückt (Flanke)
Zyklus n    alles frei  →  Selbsthaltung EIN, Schützbefehl EIN
Zyklus n+15 Schütz angezogen (T_CONTACTOR_PULL = 300 ms)  →  Rückmeldung EIN
ab n+15     Zustand RUNNING
Stop        Kickout  →  Schützbefehl AUS
            Rückmeldung fällt ab  →  Zustand STOPPED
```

## 5 Was ich bewusst weglasse

- Es gibt **keinen** Rechts-/Linkslauf. Ein Band in eine Richtung ist einfacher
  und ich kann es sauber testen (siehe `06_Verriegelungen.md`).
- Die Motorsteuerung ist die **Logik**. Die harte Schutzfunktion, die das Schütz
  ohne SPS abfallen lässt, steckt im Elektrik-Modell (siehe
  `05_Schutzkonzept.md`).
