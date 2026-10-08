# I/O-Liste (Ein-/Ausgänge)

**Projekt:** Simulierte Förderanlage mit Motorsteuerung, Schutz- und Fehlerdiagnose
**Steuerung:** SoftPLC (IEC 61131-3 ST), fester Zyklus
**Stand:** eingefroren (Phase 3) – Adressen sind verbindlich für ST, Klemmenplan und Schaltplan.

## Legende

- **Typ:** `DI` = digitaler Eingang, `DO` = digitaler Ausgang.
- **Polarität:** Für sicherheitsrelevante Signale (Stop, Not-Halt, Überlast) ist eine
  **Öffner-Verdrahtung (NC, fail-safe)** angenommen: Signal = `1` bei geschlossener
  Kette / gesundem Zustand, `0` bei Betätigung bzw. Störung.
- **Ruhezustand:** Pegel im unbetätigten/gesunden Zustand.

## Eingänge (%I)

| Adresse | Signal | Typ | Bezeichner | Gerät | Polarität | Ruhezustand | Beschreibung |
| ------- | ------ | --- | ---------- | ----- | --------- | ----------- | ------------ |
| `%IX0.0` | Start | DI | S1 | Taster (Schließer) | NO | 0 | Start des Motors anfordern |
| `%IX0.1` | Stop | DI | S2 | Taster (Öffner) | NC | 1 | Stop, hat Vorrang vor Start |
| `%IX0.2` | Not-Halt | DI | S3 | Not-Halt-Taster (Öffner) | NC | 1 | Sicherheitskette geschlossen |
| `%IX0.3` | Überlast | DI | F2 | Motorschutzrelais (Öffner-Hilfskontakt) | NC | 1 | Motorschutz in Ordnung |
| `%IX0.4` | Sensor Einlauf | DI | B1 | Lichtschranke Einlauf | — | 0 | Werkstück am Einlauf erfasst |
| `%IX0.5` | Sensor Auslauf | DI | B2 | Lichtschranke Auslauf | — | 0 | Werkstück am Auslauf erfasst |
| `%IX0.6` | Motor-Rückmeldung | DI | K1/M1 | Hilfskontakt Schütz / Stromrelais | — | 0 | Motor läuft / Schütz angezogen |
| `%IX0.7` | Betriebsart Auto | DI | S5 | Wahlschalter Hand/Auto | — | 0 | 1 = Automatik, 0 = Hand |
| `%IX1.0` | Reset | DI | S4 | Taster (Schließer) | NO | 0 | Störung quittieren |
| `%IX1.1` | (reserviert) | DI | — | — | — | 0 | Reserve (z. B. Bandgeschwindigkeit, optional) |

## Ausgänge (%Q)

| Adresse | Signal | Typ | Bezeichner | Gerät | Beschreibung |
| ------- | ------ | --- | ---------- | ----- | ------------ |
| `%QX0.0` | Schützansteuerung | DO | K1 | Schütz (Spule) | Motor einschalten |
| `%QX0.1` | Meldeleuchte grün | DO | H1 | Leuchte | Betrieb/READY |
| `%QX0.2` | Meldeleuchte rot | DO | H2 | Leuchte | Störung |
| `%QX0.3` | Hupe | DO | H3 | Signalgeber | Störmeldung |
| `%QX0.4` | Meldeleuchte gelb | DO | H4 | Leuchte | Warnung (optional) |

## Hinweise zur Signalwahl

- **Stop/Not-Halt/Überlast als Öffner:** Bei Drahtbruch oder Ausfall fällt das Signal
  auf `0` und wirkt damit im Sinne der Sicherheit (fail-safe). Die Software wertet
  „Kette geschlossen = 1“ aus.
- **Betriebsartwahl:** Ein Schalter mit einer Signalleitung (0 = Hand, 1 = Auto).
- **Rückmeldung:** dient der Überwachung des tatsächlichen Motorzustands
  (nicht nur des Befehls) und ermöglicht die Diagnose „läuft nicht an“ /
  „stoppt nicht“.

Diese Liste ist die Referenz für `../../plc/standard/GVL_IO.st`.
