"""HMI-/Prozessvisualisierung als Bild (Pillow).

Alle Anzeigewerte stammen aus echten Laufzeitvariablen der SoftPLC.
Es wird nichts gezeichnet, was nicht aus der Simulation stammt.

Verwendung:
    from hmi_render import state_from_runtime, render
    render(state_from_runtime(rt), "screenshots/hmi_running.png")
"""

from __future__ import annotations

import os

from PIL import Image, ImageDraw, ImageFont

STATE = {0: "INIT", 10: "READY", 20: "RUNNING", 30: "STOPPED", 40: "FAULT", 50: "EMERGENCY"}
FAULT = {
    0: "-", 1: "UEBERLAST", 2: "START-TIMEOUT", 3: "STOP-TIMEOUT",
    4: "STAU", 5: "SENSOR-INKONSISTENZ", 6: "NOT-HALT",
}
MODE = {0: "HAND", 1: "AUTO"}
PROC = {0: "IDLE", 1: "TRANSPORT", 2: "NACHLAUF"}

# Farben
BG = (26, 28, 34)
PANEL = (39, 42, 50)
PANEL2 = (48, 52, 62)
TXT = (232, 235, 240)
MUTED = (150, 156, 168)
GREEN = (46, 204, 113)
RED = (231, 76, 60)
YELLOW = (241, 196, 15)
BLUE = (52, 152, 219)
GREY = (110, 116, 128)
BELT = (70, 76, 88)

W, H = 940, 560

_FONT_DIRS = [r"C:\Windows\Fonts", "/usr/share/fonts/truetype/dejavu"]
_FONT_FILES = ["arial.ttf", "segoeui.ttf", "DejaVuSans.ttf"]
_FONTS: dict = {}


def _font(size: int, bold: bool = False):
    key = (size, bold)
    if key in _FONTS:
        return _FONTS[key]
    names = (["arialbd.ttf", "arial.ttf"] if bold else ["arial.ttf", "segoeui.ttf"]) + _FONT_FILES
    for d in _FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                try:
                    f = ImageFont.truetype(p, size)
                    _FONTS[key] = f
                    return f
                except Exception:
                    pass
    _FONTS[key] = ImageFont.load_default()
    return _FONTS[key]


def state_from_runtime(rt) -> dict:
    g = rt.get
    return {
        "state": STATE.get(g("eHmiState"), "?"),
        "fault": FAULT.get(g("eHmiActiveFault"), "-"),
        "first": FAULT.get(g("eHmiFirstFault"), "-"),
        "mode": MODE.get(g("eHmiMode"), "?"),
        "process": PROC.get(g("eHmiProcess"), "?"),
        "cmd": bool(g("xHmiMotorCmd")),
        "fb": bool(g("xHmiMotorFb")),
        "run": bool(g("xHmiMotorRun")),
        "overload": bool(g("xHmiOverload")),
        "emergency": bool(g("xHmiEmergency")),
        "entry": bool(g("xHmiEntry")),
        "exit": bool(g("xHmiExit")),
        "jam": bool(g("xHmiJam")),
        "count": int(g("diHmiCount")),
        "belt": list(g("aHmiBeltPos")),
        "lamp_red": bool(g("xHmiLampRed")),
        "buzzer": bool(g("xHmiBuzzer")),
        "contactor": bool(g("xSimContactor")),
    }


def _rounded(d, box, r, fill, outline=None, width=1):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def render(st: dict, path: str, caption: str = "") -> None:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    f_title = _font(22, True)
    f_h = _font(16, True)
    f = _font(15)
    f_sm = _font(13)
    f_big = _font(46, True)

    d.text((24, 16), "Förderanlage – Steuerung & Diagnose (Simulation)", font=f_title, fill=TXT)
    d.text((24, 46), "PC-basierte Simulation und elektrotechnische Konzeptplanung",
           font=f_sm, fill=MUTED)
    if caption:
        d.text((W - 24, 24), caption, font=f_h, fill=YELLOW, anchor="ra")

    # ---------------- Förderband ----------------
    bx0, bx1, by, bh = 30, 560, 300, 60
    _rounded(d, (bx0 - 8, by - 8, bx1 + 8, by + bh + 8), 10, PANEL)
    d.rectangle((bx0, by, bx1, by + bh), fill=BELT, outline=(90, 96, 110), width=2)
    for x in range(bx0 + 6, bx1, 18):
        d.line((x, by + bh, x + 10, by), fill=(52, 56, 66), width=1)

    # Sensoren
    ex = bx0 + 0.03 * (bx1 - bx0)
    xx = bx0 + 0.96 * (bx1 - bx0)
    e_col = GREEN if st["entry"] else GREY
    x_col = GREEN if st["exit"] else GREY
    d.polygon([(ex, by - 26), (ex - 10, by - 44), (ex + 10, by - 44)], fill=e_col)
    d.text((ex, by - 66), "B1", font=f_sm, fill=e_col, anchor="ma")
    d.text((ex, by - 66 - 0), "", font=f_sm, fill=e_col)
    d.polygon([(xx, by - 26), (xx - 10, by - 44), (xx + 10, by - 44)], fill=x_col)
    d.text((xx, by - 66), "B2", font=f_sm, fill=x_col, anchor="ma")
    d.text((ex, by + bh + 4), "Einlauf", font=f_sm, fill=MUTED, anchor="ma")
    d.text((xx, by + bh + 4), "Auslauf", font=f_sm, fill=MUTED, anchor="ma")

    # Werkstücke
    wsq = 30
    for pos in st["belt"]:
        if pos is not None and pos >= 0.0:
            cx = bx0 + max(0.0, min(100.0, pos)) / 100.0 * (bx1 - bx0)
            d.rectangle((cx - wsq / 2, by - wsq - 6, cx + wsq / 2, by - 6),
                        fill=BLUE, outline=(230, 240, 255), width=2)

    # Motor
    mx, my, mr = (bx0 + bx1) // 2, by - 96, 26
    m_col = GREEN if st["run"] else (GREY if not st["cmd"] else YELLOW)
    d.ellipse((mx - mr, my - mr, mx + mr, my + mr), fill=PANEL2, outline=m_col, width=4)
    d.text((mx, my - 8), "M1", font=f_h, fill=m_col, anchor="mm")
    d.text((mx, my + 10), "Motor", font=f_sm, fill=MUTED, anchor="mm")
    d.line((mx, by, mx, my + mr), fill=m_col, width=2)
    d.text((mx + 34, by + bh / 2), f"Rückmeldung: {'EIN' if st['fb'] else 'AUS'}",
           font=f_sm, fill=(GREEN if st["fb"] else MUTED), anchor="lm")

    # Legende
    d.text((30, by + bh + 26), "Sensoren: B1 Lichtschranke Einlauf   B2 Lichtschranke Auslauf   "
                              "■ Werkstück", font=f_sm, fill=MUTED)

    # ---------------- Rechte Spalte ----------------
    px = 590
    pw = W - px - 26

    # Systemstatus
    _rounded(d, (px, 90, px + pw, 210), 12, PANEL)
    d.text((px + 16, 100), "Systemstatus", font=f_h, fill=TXT)
    s_col = {
        "RUNNING": GREEN, "READY": BLUE, "STOPPED": MUTED,
        "FAULT": RED, "EMERGENCY": YELLOW, "INIT": MUTED,
    }.get(st["state"], TXT)
    d.text((px + 16, 128), st["state"], font=_font(30, True), fill=s_col)
    d.text((px + 16, 172), f"Betriebsart: {st['mode']}", font=f, fill=TXT)
    d.text((px + 16, 190), f"Prozess: {st['process']}", font=f, fill=TXT)
    d.text((px + pw - 16, 172), f"First-out: {st['first']}", font=f_sm, fill=MUTED, anchor="ra")
    fault_col = RED if st["fault"] != "-" else MUTED
    d.text((px + pw - 16, 190), f"Störung: {st['fault']}", font=f, fill=fault_col, anchor="ra")

    # Motor
    _rounded(d, (px, 220, px + pw, 330), 12, PANEL)
    d.text((px + 16, 230), "Motor / Schutz", font=f_h, fill=TXT)
    prot_ok = (not st["overload"]) and (not st["emergency"])
    rows = [
        ("Befehl (K1)", "EIN" if st["cmd"] else "AUS", GREEN if st["cmd"] else MUTED),
        ("Rückmeldung", "EIN" if st["fb"] else "AUS", GREEN if st["fb"] else MUTED),
        ("Motorschutz", "OK" if prot_ok else "STÖRUNG", GREEN if prot_ok else RED),
    ]
    for i, (k, v, c) in enumerate(rows):
        yy = 260 + i * 24
        d.text((px + 16, yy), k, font=f, fill=MUTED)
        d.text((px + pw - 16, yy), v, font=f_h, fill=c, anchor="ra")

    # Zähler
    _rounded(d, (px, 340, px + pw, 430), 12, PANEL)
    d.text((px + 16, 350), "Bearbeitete Werkstücke", font=f_h, fill=TXT)
    d.text((px + pw / 2, 405), f"{st['count']}", font=f_big, fill=BLUE, anchor="mm")

    # Meldeorgane
    _rounded(d, (px, 440, px + pw, 520), 12, PANEL)
    d.text((px + 16, 450), "Meldeorgane", font=f_h, fill=TXT)
    lamp_y = 495
    lamps = [
        ("H1", GREEN if st["state"] in ("READY", "RUNNING") else GREY, 16),
        ("H2", RED if st["lamp_red"] else GREY, 90),
        ("H4", YELLOW if st["jam"] or st["fault"] == "SENSOR-INKONSISTENZ" else GREY, 164),
    ]
    for name, col, dx in lamps:
        d.ellipse((px + dx, lamp_y - 12, px + dx + 24, lamp_y + 12), fill=col, outline=(20, 20, 24))
        d.text((px + dx + 12, lamp_y + 20), name, font=f_sm, fill=MUTED, anchor="ma")
    d.text((px + pw - 16, lamp_y - 10), "Hupe H3", font=f, fill=MUTED, anchor="ra")
    d.text((px + pw - 16, lamp_y + 10), "EIN" if st["buzzer"] else "AUS",
           font=f_h, fill=(YELLOW if st["buzzer"] else MUTED), anchor="ra")

    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    img.save(path)


if __name__ == "__main__":  # pragma: no cover - manueller Test
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "plc", "runtime"))
    from softplc import load_project
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rt = load_project(os.path.join(root, "plc"))
    rt.run(10)
    render(state_from_runtime(rt), os.path.join(root, "screenshots", "_probe_hmi.png"))
    print("ok")
