"""Erzeugt eine QElectroTech-Projektdatei (.qet) als Gerüst.

Die eigentlichen, lesbaren Stromlaufpläne liegen als SVG/PNG in
../schematics/. QElectroTech platziert Symbole aus seiner Bauteilbibliothek;
diese Bibliothek ist hier nicht installiert. Daher enthält die .qet-Datei
zwei Folios (Leistungs-/Steuerkreis) mit Titelblock und Hinweistext, die in
QElectroTech geöffnet und mit Symbolen aus der Standardbibliothek ergänzt
werden können.
"""

from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "electrical", "qelectrotech")
os.makedirs(OUT, exist_ok=True)


def _prop(parent, name, value, show="1"):
    p = ET.SubElement(parent, "property", {"name": name, "show": show})
    p.text = value


def build():
    project = ET.Element("project", {
        "version": "0.80",
        "title": "Simulierte Förderanlage mit Motorsteuerung",
    })

    props = ET.SubElement(project, "properties")
    _prop(props, "title", "Simulierte Förderanlage – Motorsteuerung, Schutz- und Fehlerdiagnose")
    _prop(props, "author", "Eigenes technisches Simulationsprojekt")
    _prop(props, "date", "2026")

    nd = ET.SubElement(project, "newdiagrams")
    ET.SubElement(nd, "border", {"cols": "17", "rows": "8", "displaycols": "1", "displayrows": "1"})
    ET.SubElement(nd, "conductors", {"type": "simple", "num": "1"})

    def diagram(title, order, note):
        dg = ET.SubElement(project, "diagram", {"title": title, "order": str(order)})
        dprops = ET.SubElement(dg, "properties")
        _prop(dprops, "title", title)
        ET.SubElement(dg, "elements")
        ET.SubElement(dg, "conductors")
        ET.SubElement(dg, "inputs")
        shapes = ET.SubElement(dg, "shapes")
        txt = ET.SubElement(shapes, "dynamic_text", {"x": "60", "y": "60"})
        txt.text = note
        return dg

    diagram("01 – Leistungskreis", 1,
            "Leistungskreis: Einspeisung 3~400V -> Q1 -> F1 -> F2 -> K1 -> M1. "
            "Siehe electrical/schematics/power_circuit.svg")
    diagram("02 – Steuerkreis", 2,
            "Steuerkreis 24V DC -> Not-Halt-Kette -> SPS -> Schütz K1 / Meldeorgane. "
            "Siehe electrical/schematics/control_circuit.svg")

    ET.SubElement(project, "collection")

    xml_bytes = ET.tostring(project, encoding="utf-8")
    pretty = minidom.parseString(xml_bytes).toprettyxml(indent="  ", encoding="UTF-8")
    path = os.path.join(OUT, "foerderanlage.qet")
    with open(path, "wb") as fh:
        fh.write(pretty)
    print(f"  {os.path.relpath(path, ROOT)}")


if __name__ == "__main__":
    build()
