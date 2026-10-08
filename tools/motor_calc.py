"""Technische Beispielrechnung Drehstrommotor (didaktisch).

ACHTUNG: Es handelt sich um ein HYPOTHETISCHES Beispiel. Kein reales
Typenschild. Die Werte dienen nur der Veranschaulichung des Zusammenhangs
zwischen mechanischer Leistung, Strom, Wirkungsgrad und Leistungsfaktor.
"""

from __future__ import annotations

import math

# Hypothetische Annahmen (bewusst als Annahme gekennzeichnet)
P_MECH_KW = 0.75          # mechanische Nennleistung [kW]
U_N = 400.0               # Außenleiterspannung [V]
COSPHI = 0.80             # Leistungsfaktor
ETA = 0.78                # Wirkungsgrad
F_N = 50.0                # Frequenz [Hz]
POLE_PAIRS = 2            # 4-polig -> 2 Polpaare

# Inrush-Faktor (typische Größenordnung für Käfigläufer, didaktisch)
INRUSH_FACTOR = 6.0


def main() -> None:
    P_mech = P_MECH_KW * 1000.0                     # W (Wellenleistung)
    I = P_mech / (math.sqrt(3) * U_N * COSPHI * ETA)  # A (aufgenommener Strom)
    S = math.sqrt(3) * U_N * I                       # Scheinleistung [VA]
    P_in = math.sqrt(3) * U_N * I * COSPHI           # aufgenommene Wirkleistung [W]
    Q = math.sqrt(max(S * S - P_in * P_in, 0.0))     # Blindleistung [var]
    n_sync = 120.0 * F_N / (2 * POLE_PAIRS)          # Synchrondrehzahl [1/min]

    print("Hypothetischer Drehstrommotor (didaktische Annahme)")
    print("--------------------------------------------------")
    print(f"Mechanische Nennleistung P   : {P_MECH_KW:.2f} kW")
    print(f"Außenleiterspannung U        : {U_N:.0f} V")
    print(f"Leistungsfaktor cos(phi)     : {COSPHI:.2f}")
    print(f"Wirkungsgrad eta             : {ETA:.2f}")
    print()
    print(f"Aufgenommener Strom I        : {I:.2f} A")
    print(f"  Formel: I = P / (sqrt(3) * U * cos(phi) * eta)")
    print(f"Scheinleistung S             : {S:.0f} VA")
    print(f"Aufgenommene Wirkleistung Pin: {P_in:.0f} W")
    print(f"Blindleistung Q              : {Q:.0f} var")
    print(f"Synchrondrehzahl (4-polig)   : {n_sync:.0f} 1/min")
    print()
    print("Didaktische Stromprofile (Simulation):")
    print(f"  Anlaufstrom (ca. {INRUSH_FACTOR:.0f}x)      : {I * INRUSH_FACTOR:.2f} A")
    print(f"  Nennstrom                 : {I:.2f} A")
    print(f"  Überlast (Annahme 1,5x)   : {I * 1.5:.2f} A")
    print()
    print("Hinweis: Schutzorgane sind in der Realität nach dem Typenschild")
    print("des Motors und der Normenlage zu bemessen - nicht nach diesem Beispiel.")


if __name__ == "__main__":
    main()
