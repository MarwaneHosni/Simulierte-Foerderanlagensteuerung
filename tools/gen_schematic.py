"""Erzeugt die elektrischen Schaltplaene (SVG + PNG) und die I/O-Uebersicht.

Aufruf:
    python tools/gen_schematic.py

Es entstehen:
    electrical/schematics/power_circuit.(svg|png)
    electrical/schematics/control_circuit.(svg|png)
    electrical/schematics/io_overview.(svg|png)
    screenshots/schematic_power.png
    screenshots/schematic_control.png
    screenshots/io_overview.png
"""

from __future__ import annotations

import csv
import os
import shutil
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEM = os.path.join(ROOT, "electrical", "schematics")
SHOTS = os.path.join(ROOT, "screenshots")
os.makedirs(SCHEM, exist_ok=True)
os.makedirs(SHOTS, exist_ok=True)

C_WIRE = "#1b1b1b"
C_DEV = "#0d3b66"
C_ACC = "#b3261e"


def _save(fig, base):
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(SCHEM, f"{base}.{ext}"), dpi=150,
                    bbox_inches="tight", facecolor="white")
    fig.savefig(os.path.join(SHOTS, f"{base}.png"), dpi=150,
                bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  {base}.(svg|png)")


def wire(ax, pts, lw=1.6, color=C_WIRE):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="round", zorder=1)


def contact(ax, x, y, nc=False):
    """Kontakt-Symbol (Schliesser/Öffner) zwischen zwei Leiterenden."""
    ax.plot([x - 0.30, x - 0.10], [y, y], color=C_WIRE, lw=1.6, zorder=3)
    ax.plot([x + 0.12, x + 0.32], [y, y], color=C_WIRE, lw=1.6, zorder=3)
    ax.plot([x - 0.10, x + 0.12], [y, y + 0.26], color=C_DEV, lw=2.0, zorder=3)
    if nc:
        ax.plot([x + 0.12, x + 0.12], [y + 0.26, y + 0.26], color=C_DEV, lw=0)
        ax.plot([x + 0.02, x + 0.22], [y + 0.30, y + 0.22], color=C_DEV, lw=1.6, zorder=3)


def fuse(ax, x, y):
    ax.add_patch(Rectangle((x - 0.11, y - 0.26), 0.22, 0.52, fill=False,
                           edgecolor=C_DEV, lw=1.6, zorder=3))
    ax.plot([x, x], [y - 0.40, y + 0.40], color=C_WIRE, lw=1.4, zorder=2)


def overload(ax, x, y):
    ax.add_patch(Rectangle((x - 0.16, y - 0.30), 0.32, 0.60, fill=False,
                           edgecolor=C_DEV, lw=1.6, zorder=3))
    ax.text(x, y, "~", ha="center", va="center", color=C_DEV, fontsize=11, zorder=4)


def coil(ax, x, y, label):
    ax.add_patch(Rectangle((x - 0.28, y - 0.22), 0.56, 0.44, fill=False,
                           edgecolor=C_ACC, lw=1.8, zorder=3))
    ax.text(x, y, label, ha="center", va="center", color=C_ACC, fontsize=8, zorder=4)


def lamp(ax, x, y, label):
    ax.add_patch(Circle((x, y), 0.20, fill=False, edgecolor=C_ACC, lw=1.6, zorder=3))
    ax.plot([x - 0.14, x + 0.14], [y - 0.14, y + 0.14], color=C_ACC, lw=1.2, zorder=4)
    ax.plot([x - 0.14, x + 0.14], [y + 0.14, y - 0.14], color=C_ACC, lw=1.2, zorder=4)
    ax.text(x, y - 0.34, label, ha="center", va="top", color=C_ACC, fontsize=8)


def buzzer(ax, x, y):
    ax.add_patch(Arc((x, y), 0.5, 0.5, angle=0, theta1=90, theta2=270,
                     edgecolor=C_ACC, lw=1.6, zorder=3))
    ax.plot([x, x], [y - 0.25, y + 0.25], color=C_ACC, lw=1.6, zorder=3)


# ---------------------------------------------------------------- Leistungskreis
def power_circuit():
    fig, ax = plt.subplots(figsize=(11, 8.5))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis("off")
    ax.set_title("Stromlaufplan – Leistungskreis (Konzept, simuliert)\n"
                 "Einspeisung 3~ 400 V AC / 50 Hz (Annahme)", fontsize=13, color=C_DEV)

    xs = [4.0, 5.0, 6.0]
    top, bot = 11.0, 2.6
    for i, x in enumerate(xs):
        wire(ax, [(x, top), (x, bot)])
        ax.text(x, top + 0.2, f"L{i + 1}", ha="center", color=C_WIRE, fontsize=11)

    y_q1, y_f1, y_f2, y_k1 = 9.6, 8.3, 7.0, 5.6
    for x in xs:
        contact(ax, x, y_q1)
        fuse(ax, x, y_f1)
        overload(ax, x, y_f2)
        contact(ax, x, y_k1)

    ax.text(2.5, y_q1, "Q1\nHauptschalter", ha="right", va="center", color=C_DEV, fontsize=9)
    ax.text(2.5, y_f1, "F1\nLeitungsschutz", ha="right", va="center", color=C_DEV, fontsize=9)
    ax.text(2.5, y_f2, "F2\nMotorschutz", ha="right", va="center", color=C_DEV, fontsize=9)
    ax.text(2.5, y_k1, "K1\nSchütz (3 Hauptkontakte)", ha="right", va="center",
            color=C_DEV, fontsize=9)

    # Motor
    cx, cy, r = 5.0, 2.0, 0.85
    for x in xs:
        wire(ax, [(x, bot), (x, cy + 0.5) if abs(x - cx) < 0.1 else (x, cy)])
    # einzelne Anschluesse zum Motor
    ax.plot([4.0, 4.0], [bot, cy + 0.45], color=C_WIRE, lw=1.6)
    ax.plot([5.0, 5.0], [bot, cy + r], color=C_WIRE, lw=1.6)
    ax.plot([6.0, 6.0], [bot, cy + 0.45], color=C_WIRE, lw=1.6)
    ax.add_patch(Circle((cx, cy), r, fill=False, edgecolor=C_DEV, lw=2.0, zorder=3))
    ax.text(cx, cy + 0.1, "M1", ha="center", va="center", color=C_DEV, fontsize=11)
    ax.text(cx, cy - 0.28, "3~", ha="center", va="center", color=C_DEV, fontsize=10)
    ax.text(4.0, cy - 0.9, "U", ha="center", color=C_MUTED_TEXT, fontsize=9)
    ax.text(5.0, cy - 1.1, "V", ha="center", color=C_MUTED_TEXT, fontsize=9)
    ax.text(6.0, cy - 0.9, "W", ha="center", color=C_MUTED_TEXT, fontsize=9)

    # PE
    xpe = 7.4
    wire(ax, [(xpe, top), (xpe, 2.6)])
    ax.plot([xpe - 0.35, xpe + 0.35], [2.6, 2.6], color=C_DEV, lw=2)
    ax.plot([xpe - 0.22, xpe + 0.22], [2.4, 2.4], color=C_DEV, lw=2)
    ax.plot([xpe - 0.10, xpe + 0.10], [2.2, 2.2], color=C_DEV, lw=2)
    ax.text(xpe + 0.15, top + 0.2, "PE", ha="left", color=C_WIRE, fontsize=11)
    wire(ax, [(6.0, cy), (xpe, cy)], color=C_WIRE, lw=1.2)
    ax.text(xpe, cy + 0.2, "PE", ha="center", color=C_MUTED_TEXT, fontsize=9)

    ax.text(0.3, 0.6,
            "Hinweis: Konzeptdarstellung zur Simulation. Keine reale Auslegung – Schutzeinrichtungen "
            "sind nach realem Typenschild und Normenlage zu bemessen.",
            fontsize=8.5, color=C_ACC)
    _save(fig, "power_circuit")


# ---------------------------------------------------------------- Steuerkreis
def control_circuit():
    fig, ax = plt.subplots(figsize=(11, 8.5))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis("off")
    ax.set_title("Stromlaufplan – Steuerkreis (Konzept, simuliert)\n"
                 "Steuerspannung 24 V DC (Annahme)", fontsize=13, color=C_DEV)

    xp, x0 = 1.3, 14.8
    wire(ax, [(xp, 10.6), (xp, 1.2)], lw=2)
    wire(ax, [(x0, 10.6), (x0, 1.2)], lw=2)
    ax.text(xp, 10.8, "+24 V", ha="center", color=C_WIRE, fontsize=11)
    ax.text(x0, 10.8, "0 V", ha="center", color=C_WIRE, fontsize=11)
    ax.text(xp - 0.1, 11.2, "T1 Netzteil 24 V DC", ha="left", color=C_DEV, fontsize=9)

    # SPS
    px0, px1, py0, py1 = 6.2, 9.2, 2.2, 10.2
    ax.add_patch(Rectangle((px0, py0), px1 - px0, py1 - py0, fill=True,
                           facecolor="#eef3f9", edgecolor=C_DEV, lw=2, zorder=2))
    ax.text((px0 + px1) / 2, py1 - 0.35, "SPS (SoftPLC)", ha="center",
            color=C_DEV, fontsize=11, zorder=3)
    ax.text((px0 + px1) / 2, py1 - 0.7, "24 V DC", ha="center",
            color=C_MUTED_TEXT, fontsize=8, zorder=3)

    inputs = [
        ("S3 NC", "%IX0.2 Not-Halt", True),
        ("S2 NC", "%IX0.1 Stop", True),
        ("S1 NO", "%IX0.0 Start", False),
        ("S4 NO", "%IX1.0 Reset", False),
        ("S5", "%IX0.7 Hand/Auto", False),
        ("B1", "%IX0.4 Sensor Einlauf", False),
        ("B2", "%IX0.5 Sensor Auslauf", False),
        ("K1", "%IX0.6 Motor-Rückmeldung", False),
        ("F2 NC", "%IX0.3 Motorschutz", True),
    ]
    ys = [9.6 - i * 0.78 for i in range(len(inputs))]
    for (dev, addr, nc), y in zip(inputs, ys):
        wire(ax, [(xp, y), (px0, y)])
        contact(ax, 3.4, y, nc=nc)
        ax.text(3.4, y + 0.38, dev, ha="center", color=C_ACC, fontsize=8)
        ax.text(px0 - 0.15, y, addr, ha="right", va="center", color=C_DEV, fontsize=8)

    outputs = [
        ("K1", "%QX0.0 Schütz", "coil"),
        ("H1", "%QX0.1 grün", "lamp"),
        ("H2", "%QX0.2 rot", "lamp"),
        ("H3", "%QX0.3 Hupe", "buzzer"),
        ("H4", "%QX0.4 gelb", "lamp"),
    ]
    oy = [9.0 - i * 0.95 for i in range(len(outputs))]
    for (dev, addr, kind), y in zip(outputs, oy):
        wire(ax, [(px1, y), (x0, y)])
        ax.text(px1 + 0.15, y, addr, ha="left", va="center", color=C_DEV, fontsize=8)
        if kind == "coil":
            coil(ax, 11.6, y, "K1")
        elif kind == "lamp":
            lamp(ax, 11.6, y, dev)
        else:
            buzzer(ax, 11.6, y)
            ax.text(11.6, y - 0.34, dev, ha="center", color=C_ACC, fontsize=8)

    ax.text(0.3, 0.6,
            "Hinweis: Konzeptdarstellung. Der Not-Halt-Steuerkreis ist eine Simulation und "
            "ersetzt keine zertifizierte Sicherheitsschaltung.",
            fontsize=8.5, color=C_ACC)
    _save(fig, "control_circuit")


# ---------------------------------------------------------------- I/O-Uebersicht
def io_overview():
    path = os.path.join(ROOT, "electrical", "io_list", "io_list.csv")
    rows = []
    with open(path, encoding="utf-8") as fh:
        for r in csv.reader(fh, delimiter=";"):
            rows.append(r)
    header = rows[0]
    body = rows[1:]
    body = [r for r in body if not r[0].startswith("%IX1.1")]  # Reserve ausblenden

    fig, ax = plt.subplots(figsize=(11, 8.5))
    ax.axis("off")
    ax.set_title("I/O-Übersicht der SoftPLC\n"
                 "Adressen konsistent mit ST (GVL_IO), Klemmenplan und Schaltplan",
                 fontsize=13, color=C_DEV)
    keep = [0, 1, 2, 4, 7]
    table_rows = [[r[i] for i in keep] for r in body]
    tbl = ax.table(cellText=table_rows,
                   colLabels=[header[i] for i in keep],
                   loc="center", cellLoc="left", colLoc="left")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8.5)
    tbl.scale(1.0, 1.5)
    for (row, col), cell in tbl.get_celld().items():
        cell.set_edgecolor("#c8cdd6")
        if row == 0:
            cell.set_facecolor("#dbe4f0")
            cell.set_text_props(color=C_DEV)
        elif cell.get_text().get_text().startswith("%Q"):
            cell.set_facecolor("#fbecec")
        elif cell.get_text().get_text().startswith("%I"):
            cell.set_facecolor("#eef7ee")
    _save(fig, "io_overview")


C_MUTED_TEXT = "#666666"

if __name__ == "__main__":
    print("Schaltpläne:")
    power_circuit()
    control_circuit()
    io_overview()
    # Screenshot-Aliase mit gewuenschten Namen
    for src, dst in (("power_circuit", "schematic_power"),
                     ("control_circuit", "schematic_control")):
        shutil.copyfile(os.path.join(SCHEM, f"{src}.png"), os.path.join(SHOTS, f"{dst}.png"))
    print("Fertig.")
