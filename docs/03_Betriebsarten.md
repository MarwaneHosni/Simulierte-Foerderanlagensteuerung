# 03 – Betriebsarten

Es gibt zwei Betriebsarten. Umgeschaltet wird mit dem Wahlschalter S5
(`%IX0.7`).

## 1 Handbetrieb

- Ich starte das Band mit dem Start-Taster S1 und stoppe mit S2.
- Der Start wird als **Flanke** erkannt und setzt eine **Selbsthaltung** im
  Baustein `FB_MotorControl`. Stop wirkt als Rücksetzen (Kickout).
- **Alle Schutzregeln bleiben aktiv:**
  - Not-Halt verhindert jeden Start und stoppt sofort.
  - Überlast verhindert jeden Start und stoppt sofort.
  - Eine gespeicherte Störung verhindert den Start, bis ich quittiere.
- Im Handbetrieb hat der Einlaufsensor **keine** Startfunktion. Es läuft also
  kein automatischer Ablauf – ich fahre das Band selbst.

## 2 Automatikbetrieb

- Das Band folgt dem festen Ablauf (siehe `FB_ConveyorProcess`).
- Standard ist der **Bedarfsbetrieb** (`AUTO_CONTINUOUS = FALSE`):
  1. Ein Werkstück kommt am Einlauf B1 an.
  2. Die Steuerung startet das Band.
  3. Das Werkstück läuft zum Auslauf B2 und wird gezählt.
  4. Nachlauf (`T_RUN_ON`), danach Ruhe bis zum nächsten Werkstück.
- Alternativ gibt es den **Dauerlauf** (`AUTO_CONTINUOUS = TRUE`): Das Band
  läuft nach dem Einschalten der Automatik durchgehend.
- Auch hier gelten alle Schutz- und Verriegelungsregeln.

## 3 Wechsel der Betriebsart

- Beim Umschalten Hand ↔ Automatik stoppt das Band (einmaliger Stopimpuls).
- Danach muss neu gestartet werden (Hand) bzw. ein Werkstück kommen
  (Automatik). Ein selbsttätiger Wiederanlauf passiert **nicht**.
- Der Wahlschalter ist nur ein Bedienelement und hat **keine**
  Sicherheitsfunktion.

## 4 Vergleich

| Merkmal | Hand | Automatik |
| ------- | ---- | --------- |
| Start | Taster S1 | Werkstück am Einlauf (oder Dauerlauf) |
| Stop | Taster S2 | Nachlauf-Ende / Ablauf |
| Werkstückzählung | nicht nötig | am Auslauf B2 |
| Not-Halt wirkt | ja | ja |
| Überlast wirkt | ja | ja |
| Störungsspeicher | ja | ja |
| Automatischer Wiederanlauf | nein | nein |

## 5 Wann darf der Motor überhaupt laufen?

Nur wenn **alles** passt:

```text
keine Störung
+ Stop nicht gedrückt
+ Not-Halt nicht aktiv
+ keine Überlast
```

Erst dann kann ein Start wirksam werden.
