# 11 – Technische Berechnung (zum Üben)

> Achtung: Die Werte unten gehören zu einem **erfundenen Beispielmotor**. Das ist
> **kein** echtes Typenschild und **keine** Auslegung für eine echte Anlage. In
> der Praxis wählt man Schutzorgane nach dem echten Motor aus.

Die Rechnung kann ich mit `tools/motor_calc.py` selbst nachrechnen.

## 1 Meine Annahmen

| Größe | Symbol | Wert |
| ----- | ------ | ---- |
| Mechanische Leistung | P | 0,75 kW |
| Spannung | U | 400 V |
| Leistungsfaktor | cos φ | 0,80 |
| Wirkungsgrad | η | 0,78 |
| Frequenz | f | 50 Hz |
| Polpaare | p | 2 (4-polig) |

## 2 Den Strom ausrechnen

Für einen Drehstrommotor gilt ungefähr:

```text
I = P / (√3 · U · cos φ · η)
```

Einsetzen:

```text
I = 750 W / (1,732 · 400 V · 0,80 · 0,78)
I ≈ 1,73 A
```

## 3 Die Leistungen

| Größe | Formel | Ergebnis |
| ----- | ------ | -------- |
| Scheinleistung S | S = √3 · U · I | ≈ 1 202 VA |
| Wirkleistung P_auf | P_auf = √3 · U · I · cos φ | ≈ 962 W |
| Blindleistung Q | Q = √(S² − P_auf²) | ≈ 721 var |
| Wellenleistung P_ab | P_ab = P | 750 W |
| Wirkungsgrad | η = P_ab / P_auf | ≈ 0,78 |

## 4 Was das bedeutet

- **Wirkungsgrad η** = wie viel von der elektrischen Leistung wirklich als
  mechanische Leistung rauskommt. Der Rest sind Verluste.
- **Leistungsfaktor cos φ** = Verhältnis von Wirk- zu Scheinleistung. Kleiner
  cos φ bedeutet mehr Blindstrom und mehr Belastung der Leitungen.
- **Schein- vs. Wirkleistung:** Für Leitungen und Schutz ist der **Strom**
  entscheidend.
- **Anlaufstrom:** Beim Anlauf zieht ein Motor ein Vielfaches (hier ca. 6-fach
  ≈ 10,4 A). Deshalb müssen Schütz und Motorschutz dazu passen.

## 5 Stromwerte (Annahme)

| Betrieb | Strom |
| ------- | ----- |
| Anlauf (ca. 6×) | ≈ 10,4 A |
| Nennbetrieb | ≈ 1,73 A |
| Überlast (1,5×) | ≈ 2,6 A |

## 6 Warum man nach dem Typenschild auswählt

Der Motorschutz muss den **Nennstrom** des echten Motors dauerhaft führen, aber
bei **anhaltender Überlast** auslösen. Das Schütz muss den **Anlaufstrom**
aushalten. Leitungsschutz und Leiterquerschnitt richten sich nach dem echten
Strom und der Verlegung. Mein Projekt zeigt das nur als **Konzept**.
