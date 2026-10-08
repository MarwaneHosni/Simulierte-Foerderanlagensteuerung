"""Erzeugt einfache Uebersichtsdiagramme fuer das README (Pillow/matplotlib).

Ergebnis:
    screenshots/zustandsautomat.png
    screenshots/verriegelung.png
"""

from __future__ import annotations

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "screenshots")
os.makedirs(OUT, exist_ok=True)

BG = "#ffffff"
TXT = "#1b2430"
LINE = "#2b3a4a"
C_READY = "#3498db"
C_RUN = "#2ecc71"
C_STOP = "#95a5a6"
C_FAULT = "#e74c3c"
C_EM = "#f1c40f"


def box(ax, x, y, w, h, text, color, fsize=11):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                boxstyle="round,pad=0.08,rounding_size=0.12",
                                linewidth=2, edgecolor=color, facecolor="white", zorder=2))
    ax.text(x, y, text, ha="center", va="center", fontsize=fsize, color=TXT, zorder=3)


def arrow(ax, p1, p2, label="", rad=0.0):
    ax.annotate("", xy=p2, xytext=p1,
                arrowprops=dict(arrowstyle="-|>", color=LINE, lw=1.8,
                                connectionstyle=f"arc3,rad={rad}"), zorder=1)
    if label:
        mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
        ax.text(mx, my, f" {label} ", ha="center", va="center", fontsize=9,
                color=LINE, bbox=dict(fc="white", ec="none", pad=1), zorder=4)


def zustandsautomat():
    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("Zustandsautomat der Förderanlage (Übersicht)", fontsize=13, color=TXT)

    box(ax, 8, 8.4, 3.2, 1.2, "READY", C_READY)
    box(ax, 13, 8.4, 3.4, 1.2, "RUNNING", C_RUN)
    box(ax, 13, 4.6, 3.4, 1.2, "STOPPED", C_STOP)
    box(ax, 8, 4.6, 3.2, 1.2, "FAULT", C_FAULT)
    box(ax, 3, 4.6, 3.6, 1.2, "EMERGENCY", C_EM)

    arrow(ax, (9.6, 8.4), (11.3, 8.4), "Start")
    arrow(ax, (13, 7.8), (13, 5.2), "Stop")
    arrow(ax, (11.3, 7.9), (9.6, 7.9), "Start", rad=0.35)
    arrow(ax, (13, 5.2), (11.3, 5.2), "", rad=0)
    arrow(ax, (11.3, 4.6), (9.6, 4.6), "Störung")
    arrow(ax, (8, 7.8), (8, 5.2), "", rad=0)
    arrow(ax, (6.4, 4.6), (4.8, 4.6), "Not-Halt")
    arrow(ax, (8, 5.2), (3.0, 5.2), "Not-Halt", rad=0.25)
    arrow(ax, (3, 5.2), (6.4, 8.0), "Reset", rad=-0.35)
    arrow(ax, (6.4, 5.2), (6.4, 8.0), "Reset", rad=0.0)

    plt.tight_layout()
    p = os.path.join(OUT, "zustandsautomat.png")
    fig.savefig(p, dpi=150, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    print(f"  zustandsautomat.png")


def verriegelung():
    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 11)
    ax.axis("off")
    ax.set_title("Verriegelung und Freigaben der Motorsteuerung (Übersicht)", fontsize=13, color=TXT)

    conds = ["Start-Taster\n(Flanke)", "kein Stop", "kein Not-Halt",
             "keine Überlast", "keine Störung"]
    ys = [9.2, 7.9, 6.6, 5.3, 4.0]
    for text, y in zip(conds, ys):
        box(ax, 3.2, y, 4.2, 1.0, text, "#2b3a4a", 9)
        arrow(ax, (5.3, y), (7.6, 6.6))

    box(ax, 9.3, 6.6, 3.0, 2.2, "UND\n(Freigaben\nerfüllt)", C_RUN, 10)
    box(ax, 13.4, 6.6, 3.4, 1.4, "Selbsthaltung\n(Latch / Speicher)", C_READY, 10)
    box(ax, 17.6, 6.6, 3.6, 1.4, "Schützbefehl K1\n(Motor ein)", C_RUN, 10)
    arrow(ax, (10.8, 6.6), (11.7, 6.6))
    arrow(ax, (15.1, 6.6), (15.8, 6.6))

    box(ax, 13.4, 2.6, 6.2, 1.4, "Stop / Not-Halt / Überlast / Störung\n→ Rücksetzen (Kickout)", C_FAULT, 9)
    arrow(ax, (13.4, 3.3), (13.4, 5.8), "Vorrang", rad=0.0)

    ax.text(0.3, 0.5, "Stop und Störungen haben immer Vorrang – der Motor kann nicht „über“ sie hinweg gestartet werden.",
            fontsize=9, color="#b3261e")
    plt.tight_layout()
    p = os.path.join(OUT, "verriegelung.png")
    fig.savefig(p, dpi=150, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    print(f"  verriegelung.png")


if __name__ == "__main__":
    print("Diagramme:")
    zustandsautomat()
    verriegelung()
