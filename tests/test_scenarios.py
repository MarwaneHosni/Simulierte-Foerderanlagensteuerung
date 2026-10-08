"""30 Szenario-Testfaelle gegen die echte SoftPLC-Runtime.

Aufruf:
    python tools/harness.py
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

from harness import Sim, Case, test  # noqa: E402


def _c(sim, initial, action, expected, actual, passed):
    return Case(initial=initial, action=action, expected=expected,
                actual=actual, passed=passed)


# ============================================================================ #
#  Grundfunktionen
# ============================================================================ #
@test("T01", "Grundfunktionen", "Startzustand READY")
def t01(sim: Sim):
    sim.scan(5)
    ok = sim.state == "READY" and sim.fault == "-"
    return _c(sim, "Spannungsversorgung, keine Befehle", "5 Zyklen Initialisierung",
              "Zustand READY, keine Störung", f"Zustand {sim.state}, Störung {sim.fault}", ok)


@test("T02", "Grundfunktionen", "Automatikstart durch Werkstueck")
def t02(sim: Sim):
    sim.set("xModeAuto", True)
    sim.set("xSimGenerateWorkpieces", True)
    ok = sim.run_until(lambda s: s.cmd, 400)
    return _c(sim, "Automatikbetrieb, keine Störung", "Automatik + Werkstueckerzeugung aktiv",
              "Band startet automatisch (Schützbefehl EIN)",
              f"Schützbefehl EIN nach {sim.cycle} Zyklen = {ok}", ok and sim.cmd)


@test("T03", "Grundfunktionen", "Stop hat Vorrang vor Start")
def t03(sim: Sim):
    sim.start_manual()
    sim.set("xStart", True)
    sim.set("xStopNC", False)   # Stop gleichzeitig betaetigt
    sim.scan()
    sim.set("xStart", False)
    sim.set("xStopNC", True)
    sim.scan(3)
    ok = not sim.cmd
    return _c(sim, "Motor laeuft (Hand)", "Start und Stop gleichzeitig",
              "Motor aus (Stop dominiert)", f"Schützbefehl = {int(sim.cmd)}", ok)


@test("T04", "Grundfunktionen", "Reset ohne Stoerung startet nicht")
def t04(sim: Sim):
    sim.scan(5)
    sim.press_reset()
    sim.scan(3)
    ok = (not sim.cmd) and sim.count == 0
    return _c(sim, "Anlage READY, keine Stoerung", "Reset-Taster betaetigen",
              "Kein Motorstart, keine Zaehleraenderung",
              f"Schützbefehl = {int(sim.cmd)}, Zaehler = {sim.count}", ok)


@test("T05", "Grundfunktionen", "Automatikbetrieb: Transport und Zaehlung")
def t05(sim: Sim):
    sim.set("xModeAuto", True)
    sim.set("xSimGenerateWorkpieces", True)
    ok = sim.run_until(lambda s: s.count >= 1, 1200)
    return _c(sim, "Automatikbetrieb", "Werkstueck durchlaufen lassen",
              "Werkstueck wird gezaehlt (Zaehler >= 1)",
              f"Zaehler = {sim.count} nach {sim.cycle} Zyklen", ok)


@test("T06", "Grundfunktionen", "Handbetrieb")
def t06(sim: Sim):
    sim.start_manual()
    ok = sim.state == "RUNNING" and sim.cmd and sim.fb
    return _c(sim, "Handbetrieb, keine Stoerung", "Start-Taster betaetigen",
              "Motor laeuft (RUNNING, Befehl und Rueckmeldung EIN)",
              f"Zustand {sim.state}, Befehl {int(sim.cmd)}, Rueckmeldung {int(sim.fb)}", ok)


@test("T07", "Grundfunktionen", "Handbetrieb durch Not-Halt gesperrt")
def t07(sim: Sim):
    sim.set("xNotHaltNC", False)
    sim.start_manual(wait_feedback=False)
    sim.scan(10)
    ok = (not sim.cmd) and sim.state == "EMERGENCY"
    return _c(sim, "Not-Halt aktiv", "Start-Taster im Handbetrieb betaetigen",
              "Kein Motorstart, Zustand EMERGENCY",
              f"Schützbefehl = {int(sim.cmd)}, Zustand {sim.state}", ok)


@test("T08", "Grundfunktionen", "Betriebsartwechsel stoppt das Band")
def t08(sim: Sim):
    sim.start_manual()
    sim.set("xModeAuto", True)
    sim.scan(5)
    ok = not sim.cmd
    return _c(sim, "Motor laeuft im Handbetrieb", "Wechsel auf Automatik",
              "Band wird gestoppt (kein automatischer Weiterlauf ohne Werkstueck)",
              f"Schützbefehl = {int(sim.cmd)}", ok)


# ============================================================================ #
#  Motor
# ============================================================================ #
@test("T09", "Motor", "Erfolgreicher Motorstart mit Rueckmeldung")
def t09(sim: Sim):
    sim.start_manual()
    ok = sim.fb and sim.state == "RUNNING"
    return _c(sim, "Stillstand, keine Stoerung", "Start-Taster (Hand)",
              "Rueckmeldung EIN, Zustand RUNNING",
              f"Rueckmeldung {int(sim.fb)}, Zustand {sim.state}", ok)


@test("T10", "Motor", "Motor laeuft nicht an (Start-Timeout)")
def t10(sim: Sim):
    sim.set("xSimInjectFeedbackOpen", True)
    sim.start_manual(wait_feedback=False)
    ok = sim.run_until(lambda s: s.rt.get("eHmiActiveFault") == 2, 200)
    return _c(sim, "Rueckmeldung faellt aus (simulierter Defekt)", "Start-Taster",
              "Stoerung START-TIMEOUT", f"Stoerung {sim.fault} nach {sim.cycle} Zyklen", ok)


@test("T11", "Motor", "Erfolgreicher Motorstop")
def t11(sim: Sim):
    sim.start_manual()
    sim.press_stop()
    sim.scan(5)
    ok = (not sim.cmd) and (not sim.fb)
    return _c(sim, "Motor laeuft", "Stop-Taster",
              "Schützbefehl und Rueckmeldung AUS",
              f"Befehl {int(sim.cmd)}, Rueckmeldung {int(sim.fb)}", ok)


@test("T12", "Motor", "Motor stoppt nicht (Stop-Timeout)")
def t12(sim: Sim):
    sim.start_manual()
    sim.set("xSimInjectFeedbackStuck", True)
    sim.press_stop()
    ok = sim.run_until(lambda s: s.rt.get("eHmiActiveFault") == 3, 200)
    return _c(sim, "Rueckmeldung haengt EIN (simulierter Defekt)", "Stop-Taster",
              "Stoerung STOP-TIMEOUT", f"Stoerung {sim.fault} nach {sim.cycle} Zyklen", ok)


@test("T13", "Motor", "Motorueberlast")
def t13(sim: Sim):
    sim.start_manual()
    sim.set("xSimInjectOverload", True)
    ok = sim.run_until(lambda s: s.rt.get("eHmiActiveFault") == 1, 300)
    ok = ok and (not sim.cmd)
    return _c(sim, "Motor laeuft", "Ueberlast wird ausgeloest",
              "Motor AUS, Stoerung UEBERLAST",
              f"Stoerung {sim.fault}, Schützbefehl {int(sim.cmd)}", ok)


@test("T14", "Motor", "Ueberlast blockiert Wiederanlauf")
def t14(sim: Sim):
    sim.start_manual()
    sim.set("xSimInjectOverload", True)
    sim.run_until(lambda s: s.rt.get("eHmiActiveFault") == 1, 300)
    sim.set("xSimInjectOverload", False)
    sim.run(5)   # Ursache weg, aber nicht quittiert
    sim.set("xStart", True); sim.scan(); sim.set("xStart", False); sim.scan(3)
    ok = not sim.cmd
    return _c(sim, "Ueberlast gespeichert, nicht quittiert", "Start-Taster erneut",
              "Kein Wiederanlauf (Stoerung verriegelt)",
              f"Schützbefehl = {int(sim.cmd)}", ok)


# ============================================================================ #
#  Sensorik
# ============================================================================ #
@test("T15", "Sensorik", "Einlaufsensor erkennt Werkstueck")
def t15(sim: Sim):
    sim.set("xModeAuto", True)
    sim.set("xSimGenerateWorkpieces", True)
    ok = sim.run_until(lambda s: bool(s.rt.get("xHmiEntry")), 400)
    return _c(sim, "Automatikbetrieb", "Werkstueck am Einlauf",
              "Einlaufsensor B1 aktiv", f"B1 = {int(bool(sim.rt.get('xHmiEntry')))}, "
              f"Zyklus {sim.cycle}", ok)


@test("T16", "Sensorik", "Auslaufsensor erkennt Werkstueck")
def t16(sim: Sim):
    sim.set("xModeAuto", True)
    sim.set("xSimGenerateWorkpieces", True)
    ok = sim.run_until(lambda s: bool(s.rt.get("xHmiExit")), 800)
    return _c(sim, "Automatikbetrieb", "Werkstueck am Auslauf",
              "Auslaufsensor B2 aktiv", f"B2 = {int(bool(sim.rt.get('xHmiExit')))}, "
              f"Zyklus {sim.cycle}", ok)


@test("T17", "Sensorik", "Zaehler zaehlt nur einmal je Werkstueck")
def t17(sim: Sim):
    sim.set("xModeAuto", True)
    sim.set("xSimGenerateWorkpieces", True)
    sim.run_until(lambda s: bool(s.rt.get("xHmiEntry")), 400)
    sim.set("xSimGenerateWorkpieces", False)   # nur dieses eine Werkstueck
    sim.run_until(lambda s: s.count >= 1, 600)
    sim.run(300)
    ok = sim.count == 1
    return _c(sim, "Ein Werkstueck auf dem Band", "Durchlauf bis Auslauf",
              "Zaehler genau 1 (keine Mehrfachzaehlung)",
              f"Zaehler = {sim.count}", ok)


@test("T18", "Sensorik", "Sensor-Inkonsistenz (Dauersignal)")
def t18(sim: Sim):
    sim.set("xSimInjectSensorInconsistency", True)
    ok = sim.run_until(lambda s: s.rt.get("eHmiActiveFault") == 5, 80)
    return _c(sim, "Anlage steht, kein Transport", "Auslaufsensor liefert Dauersignal",
              "Stoerung SENSOR-INKONSISTENZ",
              f"Stoerung {sim.fault} nach {sim.cycle} Zyklen", ok)


@test("T19", "Sensorik", "Kein Fehlalarm bei normalem Transport")
def t19(sim: Sim):
    sim.set("xModeAuto", True)
    sim.set("xSimGenerateWorkpieces", True)
    bad = False
    for _ in range(800):
        sim.scan()
        if sim.rt.get("eHmiActiveFault") == 5:
            bad = True
        if sim.count >= 1:
            break
    ok = (not bad) and sim.count >= 1
    return _c(sim, "Automatikbetrieb", "Normales Werkstueck transportieren",
              "Keine Sensor-Inkonsistenz, Zaehler inkrementiert",
              f"Fehlalarm = {bad}, Zaehler = {sim.count}", ok)


# ============================================================================ #
#  Foerderband
# ============================================================================ #
@test("T20", "Foerderband", "Transportzeit im erwarteten Bereich")
def t20(sim: Sim):
    sim.set("xModeAuto", True)
    sim.set("xSimGenerateWorkpieces", True)
    sim.run_until(lambda s: bool(s.rt.get("xHmiEntry")), 400)
    sim.set("xSimGenerateWorkpieces", False)
    t_entry = sim.cycle
    sim.run_until(lambda s: s.count >= 1, 600)
    dt = sim.cycle - t_entry
    ok = 140 <= dt <= 260 and sim.count == 1
    return _c(sim, "Werkstueck am Einlauf", "Transport bis Auslauf",
              "Transportzeit ca. 188 Zyklen (theoretisch)",
              f"{dt} Zyklen ({dt * 0.02:.2f} s)", ok)


@test("T21", "Foerderband", "Stauererkennung")
def t21(sim: Sim):
    sim.set("xModeAuto", True)
    sim.set("xSimGenerateWorkpieces", True)
    sim.set("xSimInjectJam", True)
    ok = sim.run_until(lambda s: s.rt.get("eHmiActiveFault") == 4, 1200)
    return _c(sim, "Automatikbetrieb", "Blockade in Bandmitte",
              "Stoerung STAU", f"Stoerung {sim.fault} nach {sim.cycle} Zyklen", ok)


@test("T22", "Foerderband", "Erholung nach Stau")
def t22(sim: Sim):
    sim.set("xModeAuto", True)
    sim.set("xSimGenerateWorkpieces", True)
    sim.set("xSimInjectJam", True)
    sim.run_until(lambda s: s.rt.get("eHmiActiveFault") == 4, 1200)
    sim.set("xSimInjectJam", False)
    sim.press_reset()
    ok = sim.run_until(lambda s: (not sim.rt.get("eHmiActiveFault")) and s.cmd, 800)
    return _c(sim, "Stau quittiert, Blockade entfernt", "Reset und Weiterbetrieb",
              "Stoerung geloescht, Band laeuft wieder",
              f"Stoerung {sim.fault}, Schützbefehl {int(sim.cmd)}", ok)


@test("T23", "Foerderband", "Keine Stau-Stoerung vor Transportzeit")
def t23(sim: Sim):
    sim.set("xModeAuto", True)
    sim.set("xSimGenerateWorkpieces", True)
    sim.set("xSimInjectJam", True)
    sim.run_until(lambda s: bool(s.rt.get("xHmiEntry")), 400)
    premature = False
    for _ in range(300):   # < T_MAX_TRANSPORT (400 Zyklen)
        sim.scan()
        if sim.rt.get("eHmiActiveFault") == 4:
            premature = True
    return _c(sim, "Werkstueck laeuft an, Blockade", "300 Zyklen beobachten",
              "Noch keine Stau-Stoerung (Timeout 8 s = 400 Zyklen)",
              f"vorzeitige Stoerung = {premature}", not premature)


# ============================================================================ #
#  Sicherheit
# ============================================================================ #
@test("T24", "Sicherheit", "Not-Halt im Stillstand")
def t24(sim: Sim):
    sim.set("xNotHaltNC", False)
    sim.scan(3)
    ok = sim.state == "EMERGENCY" and (not sim.cmd)
    return _c(sim, "Anlage steht (READY)", "Not-Halt-Taster betaetigen",
              "Zustand EMERGENCY, Motor aus",
              f"Zustand {sim.state}, Schützbefehl {int(sim.cmd)}", ok)


@test("T25", "Sicherheit", "Not-Halt waehrend des Laufs")
def t25(sim: Sim):
    sim.start_manual()
    sim.set("xNotHaltNC", False)
    sim.scan(3)
    ok = sim.state == "EMERGENCY" and (not sim.cmd) and (not sim.fb)
    return _c(sim, "Motor laeuft", "Not-Halt-Taster betaetigen",
              "Zustand EMERGENCY, Motor sofort aus",
              f"Zustand {sim.state}, Befehl {int(sim.cmd)}, Rueckmeldung {int(sim.fb)}", ok)


@test("T26", "Sicherheit", "Kein Wiederanlauf ohne Quittung nach Not-Halt")
def t26(sim: Sim):
    sim.start_manual()
    sim.set("xNotHaltNC", False); sim.scan(3)
    sim.set("xNotHaltNC", True); sim.scan(20)   # freigegeben, aber nicht quittiert
    before = (sim.fault == "NOT-HALT") and (not sim.cmd)
    sim.press_reset(); sim.scan(5)
    ok = before and sim.fault == "-" and sim.state in ("READY", "STOPPED")
    return _c(sim, "Not-Halt war aktiv, Taster wieder freigegeben",
              "Zuerst ohne Quittung beobachten, dann Reset",
              "Vor Reset Stoerung gespeichert, nach Reset geloescht",
              f"vor Reset Stoerung={before}, danach {sim.fault}", ok)


@test("T27", "Sicherheit", "Schuetz faellt bei Not-Halt ab")
def t27(sim: Sim):
    sim.start_manual()
    sim.set("xNotHaltNC", False)
    sim.scan(1)
    ok = (not bool(sim.rt.get("xSimContactor"))) and (not sim.cmd)
    return _c(sim, "Motor laeuft (Schütz angezogen)", "Not-Halt betaetigen",
              "Schütz faellt ab (xSimContactor = 0), Motor aus",
              f"Schütz {int(bool(sim.rt.get('xSimContactor')))}, Befehl {int(sim.cmd)}", ok)


# ============================================================================ #
#  Wiederanlauf
# ============================================================================ #
@test("T28", "Wiederanlauf", "Stoerung beseitigen und quittieren")
def t28(sim: Sim):
    sim.set("xSimInjectFeedbackOpen", True)
    sim.start_manual(wait_feedback=False)
    sim.run_until(lambda s: s.rt.get("eHmiActiveFault") == 2, 200)
    sim.set("xSimInjectFeedbackOpen", False)
    sim.run(3)
    sim.press_reset()
    sim.scan(5)
    ok = sim.fault == "-" and sim.state in ("READY", "STOPPED")
    return _c(sim, "Start-Timeout gespeichert", "Defekt behoben und Reset",
              "Stoerung geloescht, Anlage wieder bereit",
              f"Stoerung {sim.fault}, Zustand {sim.state}", ok)


@test("T29", "Wiederanlauf", "Neustart nach Stoerung")
def t29(sim: Sim):
    sim.set("xSimInjectFeedbackOpen", True)
    sim.start_manual(wait_feedback=False)
    sim.run_until(lambda s: s.rt.get("eHmiActiveFault") == 2, 200)
    sim.set("xSimInjectFeedbackOpen", False)
    sim.run(3); sim.press_reset(); sim.scan(5)
    sim.start_manual()
    ok = sim.cmd and sim.fb and sim.state == "RUNNING"
    return _c(sim, "Stoerung quittiert", "Start-Taster erneut",
              "Motor startet wieder (RUNNING)",
              f"Befehl {int(sim.cmd)}, Rueckmeldung {int(sim.fb)}, Zustand {sim.state}", ok)


@test("T30", "Wiederanlauf", "First-out und Prioritaet der Stoerung")
def t30(sim: Sim):
    sim.set("xSimInjectFeedbackOpen", True)
    sim.start_manual(wait_feedback=False)
    sim.run_until(lambda s: s.rt.get("eHmiActiveFault") == 2, 200)
    first1 = sim.rt.get("eHmiFirstFault")
    sim.set("xSimInjectFeedbackOpen", False)
    sim.set("xSimInjectFeedbackStuck", True)
    sim.run_until(lambda s: bool(s.rt.get("fbAlarm.xStopLatched")), 250)
    active = sim.rt.get("eHmiActiveFault")
    first2 = sim.rt.get("eHmiFirstFault")
    ok = (first1 == 2) and (first2 == 2) and (active == 2)
    return _c(sim, "Start-Timeout gespeichert", "Zusaetzlich Stop-Timeout erzeugen",
              "First-out bleibt START-TIMEOUT (2), Anzeige priorisiert 2",
              f"first={first1}, danach first={first2}, aktiv={active}", ok)


if __name__ == "__main__":
    from harness import run_all
    result = run_all(write=True)
    ok = sum(1 for c in result if c.passed)
    for c in result:
        print(f"[{'PASS' if c.passed else 'FAIL'}] {c.id:<4} {c.title:<48} -> {c.actual}")
    print(f"\n{ok}/{len(result)} Tests bestanden")
