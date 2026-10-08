"""Live-HMI der SoftPLC (Tkinter, optional).

Startet die SoftPLC im Prozess und stellt den Anlagenzustand in Echtzeit dar.
Bedienung und Fehlerinjektion erfolgen ueber Schaltflaechen.

Aufruf:
    python tools/hmi.py
"""

from __future__ import annotations

import os
import sys
import tkinter as tk

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "plc", "runtime"))

from softplc import load_project  # noqa: E402

STATE = {0: "INIT", 10: "READY", 20: "RUNNING", 30: "STOPPED", 40: "FAULT", 50: "EMERGENCY"}
FAULT = {
    0: "-", 1: "UEBERLAST", 2: "START-TIMEOUT", 3: "STOP-TIMEOUT",
    4: "STAU", 5: "SENSOR-INKONSISTENZ", 6: "NOT-HALT",
}
MODE = {0: "HAND", 1: "AUTO"}
BG = "#1a1c22"
PANEL = "#272a32"
TXT = "#e8ebf0"
MUTED = "#969ca8"
GREEN = "#2ecc71"
RED = "#e74c3c"
YELLOW = "#f1c40f"
BLUE = "#3498db"
GREY = "#6e7480"


class HmiApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.rt = load_project(os.path.join(ROOT, "plc"))
        self.rt.run(3)
        self.auto = tk.BooleanVar(value=False)
        root.title("Förderanlage – SoftPLC HMI (Simulation)")
        root.configure(bg=BG)

        self._build_controls()
        self.canvas = tk.Canvas(root, width=940, height=470, bg=BG, highlightthickness=0)
        self.canvas.pack()
        self.tick()

    # ---------------------------------------------------------------- Controls
    def _build_controls(self):
        bar = tk.Frame(self.root, bg=BG)
        bar.pack(fill="x", padx=8, pady=6)

        def btn(text, cmd, color="#3a3f4b"):
            b = tk.Button(bar, text=text, command=cmd, bg=color, fg=TXT,
                          activebackground="#50576a", relief="flat", padx=8, pady=4)
            b.pack(side="left", padx=3)
            return b

        def pulse(path):
            self.rt.set(path, True)
            self.root.after(120, lambda: self.rt.set(path, False))

        self.mode_btn = btn("Hand/Auto umschalten", self._toggle_mode)
        btn("Start", lambda: pulse("xStart"), "#1f6f43")

        def stop_pulse():
            self.rt.set("xStopNC", False)
            self.root.after(150, lambda: self.rt.set("xStopNC", True))
        btn("Stop", stop_pulse, "#7a2b28")
        btn("Reset", lambda: pulse("xReset"))
        btn("Not-Halt (halten)", self._not_halt_toggle, "#8a6d1a")
        self.gen = tk.BooleanVar(value=False)
        tk.Checkbutton(bar, text="Werkstücke erzeugen", variable=self.gen,
                       command=lambda: self.rt.set("xSimGenerateWorkpieces", self.gen.get()),
                       bg=BG, fg=TXT, selectcolor=PANEL, activebackground=BG).pack(side="left", padx=6)

        bar2 = tk.Frame(self.root, bg=BG)
        bar2.pack(fill="x", padx=8)

        def inj(label, path):
            var = tk.BooleanVar(value=False)

            def cb():
                self.rt.set(path, var.get())
            tk.Checkbutton(bar2, text=label, variable=var, command=cb,
                           bg=BG, fg=MUTED, selectcolor=PANEL, activebackground=BG).pack(side="left", padx=4)
        tk.Label(bar2, text="Fehlerinjektion:", bg=BG, fg=MUTED).pack(side="left")
        inj("Überlast", "xSimInjectOverload")
        inj("Stau", "xSimInjectJam")
        inj("Sensorfehler", "xSimInjectSensorInconsistency")
        inj("Rückm. aus", "xSimInjectFeedbackOpen")
        inj("Rückm. hängt", "xSimInjectFeedbackStuck")

    def _toggle_mode(self):
        self.auto.set(not self.auto.get())
        self.rt.set("xModeAuto", self.auto.get())

    def _not_halt_toggle(self):
        cur = bool(self.rt.get("xNotHaltNC"))
        self.rt.set("xNotHaltNC", not cur)

    # ----------------------------------------------------------------- Tick
    def tick(self):
        self.rt.scan()
        self._redraw()
        self.root.after(20, self.tick)

    def _redraw(self):
        g = self.rt.get
        c = self.canvas
        c.delete("all")
        state = STATE.get(g("eHmiState"), "?")
        fault = FAULT.get(g("eHmiActiveFault"), "-")

        # Förderband
        bx0, bx1, by, bh = 30, 560, 250, 60
        c.create_rectangle(bx0 - 8, by - 8, bx1 + 8, by + bh + 8, fill=PANEL, outline="")
        c.create_rectangle(bx0, by, bx1, by + bh, fill="#464c58", outline="#5a6270", width=2)
        ex, xx = bx0 + 0.03 * (bx1 - bx0), bx0 + 0.96 * (bx1 - bx0)
        c.create_polygon(ex, by - 26, ex - 10, by - 44, ex + 10, by - 44,
                         fill=(GREEN if g("xHmiEntry") else GREY))
        c.create_polygon(xx, by - 26, xx - 10, by - 44, xx + 10, by - 44,
                         fill=(GREEN if g("xHmiExit") else GREY))
        c.create_text(ex, by - 56, text="B1", fill=MUTED)
        c.create_text(xx, by - 56, text="B2", fill=MUTED)
        for pos in g("aHmiBeltPos"):
            if pos is not None and pos >= 0.0:
                px = bx0 + max(0.0, min(100.0, pos)) / 100.0 * (bx1 - bx0)
                c.create_rectangle(px - 15, by - 36, px + 15, by - 6,
                                   fill=BLUE, outline="#eaf2ff", width=2)
        mx, my = (bx0 + bx1) // 2, by - 96
        m_col = GREEN if g("xHmiMotorRun") else (YELLOW if g("xHmiMotorCmd") else GREY)
        c.create_oval(mx - 26, my - 26, mx + 26, my + 26, fill=PANEL, outline=m_col, width=4)
        c.create_text(mx, my, text="M1", fill=m_col, font=("Segoe UI", 14, "bold"))
        c.create_line(mx, by, mx, my + 26, fill=m_col, width=2)

        # Statuspanel
        px, pw = 600, 320
        c.create_rectangle(px, 60, px + pw, 190, fill=PANEL, outline="")
        c.create_text(px + 14, 78, anchor="w", text="Systemstatus", fill=TXT,
                      font=("Segoe UI", 14, "bold"))
        scol = {"RUNNING": GREEN, "READY": BLUE, "STOPPED": MUTED,
                "FAULT": RED, "EMERGENCY": YELLOW}.get(state, TXT)
        c.create_text(px + 14, 118, anchor="w", text=state, fill=scol,
                      font=("Segoe UI", 26, "bold"))
        c.create_text(px + 14, 158, anchor="w",
                      text=f"Betriebsart: {MODE.get(g('eHmiMode'))}", fill=TXT)
        c.create_text(px + pw - 14, 158, anchor="e",
                      text=f"Störung: {fault}", fill=(RED if fault != "-" else MUTED))

        c.create_rectangle(px, 200, px + pw, 310, fill=PANEL, outline="")
        c.create_text(px + 14, 216, anchor="w", text="Motor / Schutz", fill=TXT,
                      font=("Segoe UI", 13, "bold"))
        rows = [("Befehl (K1)", g("xHmiMotorCmd")),
                ("Rückmeldung", g("xHmiMotorFb")),
                ("Motorschutz", not g("xHmiOverload") and not g("xHmiEmergency"))]
        for i, (k, v) in enumerate(rows):
            y = 246 + i * 24
            c.create_text(px + 14, y, anchor="w", text=k, fill=MUTED)
            c.create_text(px + pw - 14, y, anchor="e",
                          text="EIN" if v else "AUS", fill=(GREEN if v else MUTED))

        c.create_rectangle(px, 320, px + pw, 400, fill=PANEL, outline="")
        c.create_text(px + 14, 336, anchor="w", text="Bearbeitete Werkstücke", fill=TXT)
        c.create_text(px + pw / 2, 372, text=str(g("diHmiCount")), fill=BLUE,
                      font=("Segoe UI", 30, "bold"))

        c.create_rectangle(px, 410, px + pw, 470, fill=PANEL, outline="")
        c.create_text(px + 14, 426, anchor="w", text="Meldeorgane", fill=TXT)
        c.create_oval(px + 16, 444, px + 40, 468,
                      fill=(GREEN if state in ("READY", "RUNNING") else GREY), outline="#141418")
        c.create_oval(px + 96, 444, px + 120, 468,
                      fill=(RED if g("xHmiLampRed") else GREY), outline="#141418")
        c.create_oval(px + 176, 444, px + 200, 468,
                      fill=(YELLOW if g("xHmiBuzzer") else GREY), outline="#141418")
        c.create_text(px + 210, 456, anchor="w", text="H3 Hupe", fill=MUTED)


def main():
    root = tk.Tk()
    HmiApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
