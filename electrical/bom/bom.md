# Stückliste (Konzept)

**Projekt:** Simulierte Förderanlage mit Motorsteuerung, Schutz- und Fehlerdiagnose


> Dies ist eine **Konzept-Stückliste für die Simulation**. Es wurden keine Komponenten beschafft oder verdrahtet. Bemessungen sind in einer realen Anlage nach Typenschild und Normenlage zu wählen.

| Bezeichner | Komponente | Beschreibung | Menge | Bemerkung |
| ---------- | ---------- | ------------ | ----- | --------- |
| Q1 | Hauptschalter / Isolator, 3-polig | Freischaltung der Anlage | 1 | Konzept, Bemessung nach realer Anlage |
| F1 | Leitungsschutzsicherung | Schutz der Einspeisung/Steuerkreis | 1 | Bemessung nach realem Stromkreis |
| F2 | Motorschutzrelais, einstellbar | Überlastschutz Motor M1 | 1 | Annahme: Einstellbereich passend zu M1 |
| K1 | Schütz, 3 Hauptkontakte + Hilfskontakt | Schalten des Motorstroms | 1 | Spule 24 V DC (Annahme) |
| T1 | Netzteil 24 V DC | Steuerspannung | 1 | Leistung nach Verbrauchern |
| M1 | Drehstrommotor (Annahme 0,75 kW / 400 V) | Antrieb Förderband | 1 | Nur didaktische Annahme, kein reales Typenschild |
| S1 | Taster Schließer | Start | 1 |  |
| S2 | Taster Öffner | Stop | 1 |  |
| S3 | Not-Halt-Taster Öffner | Not-Halt (konzeptionell) | 1 |  |
| S4 | Taster Schließer | Reset | 1 |  |
| S5 | Wahlschalter | Hand/Auto | 1 |  |
| B1 | Lichtschranke | Werkstück Einlauf | 1 |  |
| B2 | Lichtschranke | Werkstück Auslauf | 1 |  |
| H1 | Meldeleuchte grün | Betrieb | 1 |  |
| H2 | Meldeleuchte rot | Störung | 1 |  |
| H3 | Hupe/Signalgeber | Störmeldung | 1 |  |
| H4 | Meldeleuchte gelb | Warnung | 1 | optional |
| X1-X6 | Reihenklemmen | Klemmen mit Zubehör | 1 | siehe Klemmenplan |

