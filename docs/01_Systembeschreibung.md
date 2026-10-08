# 01 – Systembeschreibung

Hier erkläre ich kurz und einfach, worum es in diesem Projekt geht.

> Alles in diesem Projekt ist eine **Simulation auf dem PC**. Ich habe keine
> echte Anlage gebaut und nichts verdrahtet. Es geht darum, industrielle
> Steuerungstechnik zu verstehen und auszuprobieren.

## Worum geht es?

Eine kleine Förderanlage soll Werkstücke transportieren. Ein Motor treibt ein
Förderband. Über eine SPS (speicherprogrammierbare Steuerung) wird der Motor
gestartet und gestoppt. Sensoren erkennen die Werkstücke, ein Zähler zählt sie,
und bei einer Störung (z. B. Überlast oder Stau) schaltet die Anlage sicher ab.

## Was die Anlage können soll

- sicher starten und stoppen,
- Werkstücke erkennen und zählen,
- einen Stau (Blockade) erkennen,
- auf Überlast des Motors reagieren,
- bei Not-Halt sofort stoppen,
- im Handbetrieb und im Automatikbetrieb laufen,
- Störungen speichern und erst nach Quittung freigeben,
- den aktuellen Zustand auf einem Bildschirm (HMI) anzeigen.

## So ist alles aufgebaut

```text
 Bedienelemente (Start, Stop, Not-Halt, Reset, Hand/Auto)
             │
             ▼
        ┌─────────┐
        │  SPS    │   ← hier steckt die Steuerlogik
        └──┬───┬──┘
   Sensorik │   │ Aktorik / Melder
            ▼   ▼
   B1/B2, Rückmeldung,     Schützbefehl K1, Leuchten, Hupe
   Motorschutz F2
             │
             ▼
   „Elektrik“ (simuliert)
   Schütz K1  →  Motor M1  →  Förderband
```

## Steuerung und Elektrik sind getrennt

Das ist ein wichtiger Punkt, den ich lernen wollte:

- Die **SPS** entscheidet, *was* passieren soll (Logik).
- Die **Elektrik** (simuliert) stellt dar, *wie* der Motor geschaltet und
  geschützt würde.

Deshalb gibt es eine Besonderheit: Wenn eine Überlast oder ein Not-Halt
ansteht, fällt das Schütz **auch ohne die SPS** ab. Die SPS merkt das über die
fehlende Rückmeldung und meldet eine Störung. Genauso ist es auch in der echten
Welt.

## Welche Teile benutzt werden

**Bedienung**
| Bezeichner | Teil | Aufgabe |
| ---------- | ---- | ------- |
| S1 | Start-Taster | Motor starten |
| S2 | Stop-Taster | Motor stoppen (hat Vorrang) |
| S3 | Not-Halt-Taster | Sicherheit, stoppt sofort |
| S4 | Reset-Taster | Störung quittieren |
| S5 | Wahlschalter | Hand oder Automatik |

**Sensorik**
| Bezeichner | Teil | Aufgabe |
| ---------- | ---- | ------- |
| B1 | Lichtschranke Einlauf | erkennt ankommende Werkstücke |
| B2 | Lichtschranke Auslauf | erkennt fertige Werkstücke |
| — | Motor-Rückmeldung | meldet, ob der Motor wirklich läuft |
| F2 | Motorschutzrelais | meldet Überlast |

**Aktorik / Melder**
| Bezeichner | Teil |
| ---------- | ---- |
| M1 | Drehstrommotor (Förderband) |
| K1 | Schütz (schaltet den Motor) |
| H1 | Leuchte grün (Betrieb) |
| H2 | Leuchte rot (Störung) |
| H3 | Hupe (Störung) |
| H4 | Leuchte gelb (Warnung) |

## Betriebsarten

- **Automatik:** Die Anlage läuft selbstständig, sobald ein Werkstück am Einlauf
  ankommt.
- **Hand:** Der Mensch startet und stoppt das Band selbst. Die
  Sicherheitsregeln bleiben aber immer aktiv.

Mehr dazu in `03_Betriebsarten.md`.

## Die Zustände der Anlage

```text
INIT ──► READY ──(Start)──► RUNNING
           ▲                  │
           │◄────(Stop)───────┘
           │
           └──(Störung/Not-Halt)──► FAULT / EMERGENCY
                                        │
                                        └──(Reset)──► READY
```

## Wörterbuch (kurz erklärt)

| Begriff | Einfach erklärt |
| ------- | --------------- |
| Leistungskreis | der Teil, der den Motor mit Strom versorgt |
| Steuerkreis | der Teil mit 24 V, der die Schaltgeräte steuert |
| Schütz | ein großes Relais, das den Motor ein/aus schaltet |
| Motorschutz | schützt den Motor vor Überlast |
| Überlast | der Motor muss zu schwer arbeiten |
| Rückmeldung | das echte Signal, ob der Motor läuft |
| Verriegelung | eine Regel, die etwas verbietet |
| Freigabe | eine Bedingung, damit etwas erlaubt ist |
| Not-Halt | sofortiges Stillsetzen im Notfall |
| Störung | ein Fehler, der gemeldet wird |
| Fehlersuche | das systematische Suchen eines Fehlers |

## Womit ich das gebaut habe

- **SPS-Programm:** in **Structured Text** (IEC 61131-3), liegt in `plc/`.
- **Ausführen ohne CODESYS:** mit einer kleinen, selbst gebauten
  Python-SoftPLC (`plc/runtime/`), damit alles auf dem PC läuft.
- **Elektro-Dokumentation:** Schaltpläne als Bild (SVG/PNG) sowie eine
  QElectroTech-Datei.
- **Hilfswerkzeuge:** Python für HMI, Tests und die Bilder.
