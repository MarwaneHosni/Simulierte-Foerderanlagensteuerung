"""Erzeugt HMI-Screenshots und GIF-Demos aus echten Simulationslaeufen.

Aufruf:
    python tools/gen_screenshots.py
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "plc", "runtime"))

from harness import Sim  # noqa: E402
from hmi_render import render, state_from_runtime  # noqa: E402

SHOTS = os.path.join(ROOT, "screenshots")
os.makedirs(SHOTS, exist_ok=True)


def save(sim: Sim, name: str, caption: str = "") -> None:
    render(state_from_runtime(sim.rt), os.path.join(SHOTS, name), caption)
    print(f"  {name}")


def find_workpiece(sim: Sim, lo: float, hi: float, max_cycles: int = 900) -> bool:
    for _ in range(max_cycles):
        sim.scan()
        pos = sim.rt.get("aHmiBeltPos")
        if any(lo <= p <= hi for p in pos):
            return True
    return False


# ---------------------------------------------------------------- Einzelbilder
def shot_startup():
    sim = Sim()
    sim.scan(3)
    save(sim, "hmi_startup.png", "READY / Stillstand")


def shot_manual():
    sim = Sim()
    sim.start_manual()
    sim.scan(20)
    save(sim, "hmi_manual.png", "Handbetrieb / Motor EIN")


def shot_running():
    sim = Sim()
    sim.set("xModeAuto", True)
    sim.set("xSimGenerateWorkpieces", True)
    if find_workpiece(sim, 30.0, 70.0):
        save(sim, "hmi_running.png", "Automatik / Werkstück läuft")
    else:
        save(sim, "hmi_running.png", "Automatik / Werkstück läuft")


def shot_entry():
    sim = Sim()
    sim.set("xModeAuto", True)
    sim.set("xSimGenerateWorkpieces", True)
    sim.run_until(lambda s: bool(s.rt.get("xHmiEntry")), 400)
    save(sim, "hmi_workpiece_entry.png", "Werkstück am Einlauf B1")


def shot_counter():
    sim = Sim()
    sim.set("xModeAuto", True)
    sim.set("xSimGenerateWorkpieces", True)
    sim.run_until(lambda s: s.count >= 1, 1200)
    save(sim, "hmi_counter.png", f"Zähler = {sim.count}")


def shot_overload():
    sim = Sim()
    sim.start_manual()
    sim.set("xSimInjectOverload", True)
    sim.run_until(lambda s: s.rt.get("eHmiActiveFault") == 1, 300)
    save(sim, "hmi_fault_overload.png", "Störung: Überlast")


def shot_start_timeout():
    sim = Sim()
    sim.set("xSimInjectFeedbackOpen", True)
    sim.start_manual(wait_feedback=False)
    sim.run_until(lambda s: s.rt.get("eHmiActiveFault") == 2, 200)
    save(sim, "hmi_fault_start.png", "Störung: Motor startet nicht")


def shot_jam():
    sim = Sim()
    sim.set("xModeAuto", True)
    sim.set("xSimGenerateWorkpieces", True)
    sim.set("xSimInjectJam", True)
    sim.run_until(lambda s: s.rt.get("eHmiActiveFault") == 4, 1200)
    save(sim, "hmi_fault_jam.png", "Störung: Stau")


def shot_emergency():
    sim = Sim()
    sim.start_manual()
    sim.set("xNotHaltNC", False)
    sim.scan(3)
    save(sim, "hmi_emergency.png", "Not-Halt / EMERGENCY")


# ------------------------------------------------------------------------- GIF
def _frames_dir():
    d = os.path.join(SHOTS, "_frames")
    os.makedirs(d, exist_ok=True)
    return d


def _save_frame(sim: Sim, caption: str, idx: int) -> str:
    p = os.path.join(_frames_dir(), f"frame_{idx:04d}.png")
    render(state_from_runtime(sim.rt), p, caption)
    return p


def gif_demo():
    sim = Sim()
    sim.set("xModeAuto", True)
    sim.set("xSimGenerateWorkpieces", True)
    frames = []
    idx = 0
    for i in range(900):
        sim.scan()
        if i % 10 == 0:
            frames.append(_save_frame(sim, "Automatikbetrieb", idx)); idx += 1
        if sim.count >= 1:
            break
    sim.set("xModeAuto", False)
    for k in range(60):
        sim.scan()
        if k % 6 == 0:
            frames.append(_save_frame(sim, "STOP", idx)); idx += 1
    _assemble_gif(frames, os.path.join(SHOTS, "demo.gif"))
    print(f"  demo.gif ({len(frames)} frames, count={sim.count})")


def gif_fault():
    sim = Sim()
    sim.start_manual()
    frames = []
    idx = 0
    for i in range(40):
        sim.scan()
        if i % 5 == 0:
            frames.append(_save_frame(sim, "Motor läuft", idx)); idx += 1
    sim.set("xSimInjectOverload", True)
    for i in range(170):
        sim.scan()
        if i % 8 == 0:
            frames.append(_save_frame(sim, "Überlast", idx)); idx += 1
    _assemble_gif(frames, os.path.join(SHOTS, "fault_demo.gif"))
    print(f"  fault_demo.gif ({len(frames)} frames)")


def _assemble_gif(frames_paths, out_path):
    from PIL import Image
    imgs = [Image.open(p).convert("RGB") for p in frames_paths]
    if not imgs:
        return
    imgs[0].save(out_path, save_all=True, append_images=imgs[1:],
                 duration=140, loop=0, optimize=True)
    for p in frames_paths:
        try:
            os.remove(p)
        except OSError:
            pass


def main():
    print("Erzeuge HMI-Screenshots:")
    shot_startup()
    shot_manual()
    shot_running()
    shot_entry()
    shot_counter()
    shot_overload()
    shot_start_timeout()
    shot_jam()
    shot_emergency()
    print("Erzeuge GIF-Demos:")
    gif_demo()
    gif_fault()
    print("Fertig.")


if __name__ == "__main__":
    main()
