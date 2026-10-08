# 06 – Verriegelungen und Freigaben

Verriegelungen sind Regeln, die gefährliche oder unsinnige Zustände verhindern.
Ich habe sie an zwei Stellen umgesetzt: in der **SPS-Logik** und **hart am
Schütz** (im Modell).

## 1 Übersicht

| Nr. | Regel | Wie umgesetzt | Wozu |
| --- | ----- | ------------- | ---- |
| V1 | Stop hat Vorrang vor Start | Kickout vor Start | kein „Start über Stop hinweg“ |
| V2 | Not-Halt sperrt alles | `xEmergencyActive` überall geprüft | sofort stoppen |
| V3 | Überlast sperrt alles | `xOverloadActive` | Motorschutz |
| V4 | Selbsthaltung + Kickout | Latch im `FB_MotorControl` | kein ungewollter Dauerlauf |
| V5 | gespeicherte Störung sperrt Start | `xPermissive = NOT xAnyFault` | erst quittieren |
| V6 | Betriebsartwechsel stoppt | `xModeChange` als Stop | kein unkontrollierter Wechsel |
| V7 | kein Wiederanlauf nach Not-Halt | Not-Halt wird gespeichert | bewusster Reset nötig |
| V8 | Sensor-Plausibilität | Auslauf ohne Transport → Störung | defekter Sensor wird erkannt |
| V9 | harte Verriegelung am Schütz | `Befehl AND NOT Überlast AND NOT Not-Halt` | Schutz wirkt ohne SPS |
| V10 | Hand umgeht keine Regel | gleiche Freigabekette | Bedienung ≠ Sicherheit |

## 2 Stop-Vorrang (V1)

```text
WENN Kickout DANN Selbsthaltung := AUS;
SONST WENN Start DANN Selbsthaltung := EIN;
END_WENN;
```

So kann ein gleichzeitiges Start- und Stop-Signal den Motor nicht einschalten.

## 3 Soft- und Hart-Verriegelung (V9)

- **Soft (SPS):** Der Schützbefehl wird schon in der Logik verriegelt.
- **Hart (Elektrik):** Die Schützspule zieht nur an, wenn zusätzlich keine
  Überlast und kein Not-Halt ansteht. So bleibt der Schutz wirksam, auch wenn
  die Software „EIN“ sagt.

## 4 Sensor-Plausibilität (V8)

Der Auslaufsensor B2 darf nur aktiv sein, wenn ein Transport läuft oder gerade
endet. Meldet B2 dauerhaft ein Werkstück, obwohl kein Transport läuft und der
Motor steht, wird nach der Entprellzeit `T_DEBOUNCE` die Störung
**SENSOR-INKONSISTENZ** gesetzt. Ein defekter Sensor fällt so auf.

## 5 Betriebsartenwechsel (V6)

Der Wechsel Hand ↔ Automatik wird als Flanke erkannt und dem Motorbaustein als
Stop gegeben. Das Band stoppt, ein automatischer Wiederanlauf ist ausgeschlossen.

## 6 Rechts-/Linkslauf? Bewusst nicht.

Ich habe mich gegen einen Wendebetrieb entschieden. Dafür bräuchte man:

- zwei Schütze (vorwärts/rückwärts),
- eine **gegenseitige Verriegelung** (der eine schließt den anderen aus) – in
  der Elektrik **und** in der Logik,
- eine Umschaltpause zum Schutz des Motors.

Ein halb richtiger Wendebetrieb wäre schlechter als ein sauberer Betrieb in eine
Richtung. Deshalb bleibt das Band **eindirektional** und ist dadurch vollständig
testbar.
