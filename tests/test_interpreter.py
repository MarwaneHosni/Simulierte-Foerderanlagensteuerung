"""Unit-Tests der SoftPLC-Runtime (Parser und Ausfuehrung).

Aufruf:
    python -m unittest discover -s tests -t .
oder:
    python tests/test_interpreter.py
"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "plc", "runtime"))

from softplc import load_project  # noqa: E402
from softplc.lexer import Lexer  # noqa: E402
from softplc.parser import parse_source  # noqa: E402
from softplc.runtime import BuiltinInstance, Runtime  # noqa: E402

PLC_DIR = os.path.join(ROOT, "plc")


def _tokens(src):
    return Lexer(src).tokenize()


class LexerTests(unittest.TestCase):
    def test_time_literals(self):
        toks = _tokens("T#20ms TIME#2s t#1m")
        kinds = [t.kind for t in toks]
        self.assertEqual(kinds[:3], ["time", "time", "time"])
        self.assertEqual(toks[0].value, 20)
        self.assertEqual(toks[1].value, 2000)
        self.assertEqual(toks[2].value, 60000)

    def test_address_and_comment(self):
        toks = _tokens("(* x *) %IX0.0 (* y *)")
        self.assertEqual(toks[0].kind, "addr")
        self.assertEqual(toks[0].value, "%IX0.0")

    def test_real_and_int(self):
        toks = _tokens("25.0 3")
        self.assertEqual(toks[0].kind, "real")
        self.assertEqual(toks[1].kind, "int")

    def test_range_operator(self):
        toks = _tokens("ARRAY[0..4]")
        ops = [t.value for t in toks if t.kind == "op"]
        self.assertIn("..", ops)


class ParserTests(unittest.TestCase):
    def test_enum_values(self):
        src = "TYPE E_X : (A := 0, B := 5, C) ; END_TYPE"
        _, types, _ = parse_source(src)
        self.assertEqual(types[0].members, [("A", 0), ("B", 5), ("C", 6)])

    def test_project_parses(self):
        rt = load_project(PLC_DIR)
        self.assertIn("PLC_PRG", rt.pous)
        self.assertIn("FB_MOTORCONTROL", rt.pous)
        self.assertIn("E_FAULTCODE", rt.type_defs)

    def test_case_and_fb_call(self):
        src = """
        FUNCTION_BLOCK FB_T
        VAR_INPUT x : BOOL; END_VAR
        VAR_OUTPUT y : INT; END_VAR
        VAR t : TON; END_VAR
            t(IN := x, PT := T#1s);
            CASE y OF
                0 : y := 1;
                1 : y := 2;
            ELSE
                y := 9;
            END_CASE;
        END_FUNCTION_BLOCK
        """
        _, _, pous = parse_source(src)
        self.assertIn("FB_T", pous)


class BuiltinFbTests(unittest.TestCase):
    def test_ton(self):
        ton = BuiltinInstance("TON")
        ton.mem["IN"] = True
        ton.mem["PT"] = 100
        ton.update(20)
        self.assertFalse(ton.mem["Q"])
        for _ in range(5):
            ton.update(20)
        self.assertTrue(ton.mem["Q"])
        ton.mem["IN"] = False
        ton.update(20)
        self.assertFalse(ton.mem["Q"])
        self.assertEqual(ton.mem["ET"], 0)

    def test_r_trig(self):
        rt = BuiltinInstance("R_TRIG")
        rt.mem["CLK"] = False
        rt.update(20)
        self.assertFalse(rt.mem["Q"])
        rt.mem["CLK"] = True
        rt.update(20)
        self.assertTrue(rt.mem["Q"])
        rt.update(20)
        self.assertFalse(rt.mem["Q"])


class ProjectBehaviourTests(unittest.TestCase):
    def setUp(self):
        self.rt = load_project(PLC_DIR)
        self.rt.run(5)

    def _bool(self, path):
        return bool(self.rt.get(path))

    def test_startup_ready(self):
        self.assertEqual(self.rt.get("eHmiState"), 10)  # READY

    def test_manual_start_sequence(self):
        self.rt.set("xStart", True)
        self.rt.scan()
        self.rt.set("xStart", False)
        self.rt.scan()
        self.assertTrue(self._bool("xHmiMotorCmd"))
        # Rueckmeldung erst nach Anzugsverzoegerung (T_CONTACTOR_PULL = 300 ms)
        self.rt.run(20)
        self.assertTrue(self._bool("xHmiMotorFb"))
        self.assertEqual(self.rt.get("eHmiState"), 20)  # RUNNING

    def test_stop_priority(self):
        self.rt.set("xStart", True); self.rt.scan(); self.rt.set("xStart", False)
        self.rt.run(20)
        self.rt.set("xStopNC", False)  # Stop betaetigt
        self.rt.scan()
        self.assertFalse(self._bool("xHmiMotorCmd"))

    def test_emergency_blocks_start(self):
        self.rt.set("xNotHaltNC", False)
        self.rt.set("xStart", True); self.rt.scan(); self.rt.set("xStart", False)
        self.rt.run(5)
        self.assertFalse(self._bool("xHmiMotorCmd"))
        self.assertEqual(self.rt.get("eHmiState"), 50)  # EMERGENCY

    def test_contactor_hard_dropout_on_overload(self):
        # Schütz darf bei Überlast unabhaengig von der SPS abfallen:
        # Befehl wird zunaechst gesetzt, dann Ueberlast aktiv, ohne Ablauf der SPS-Überwachung.
        self.rt.set("xStart", True); self.rt.scan(); self.rt.set("xStart", False)
        self.rt.run(20)
        self.assertTrue(self._bool("xSimContactor"))
        self.rt.set("xSimInjectOverload", True)
        self.rt.run(160)  # > T_OVERLOAD_TRIP
        self.assertTrue(self._bool("xSimOverloadTrip"))
        self.assertFalse(self._bool("xSimContactor"))
        self.assertEqual(self.rt.get("eHmiActiveFault"), 1)  # FAULT_OVERLOAD


if __name__ == "__main__":
    unittest.main(verbosity=2)
