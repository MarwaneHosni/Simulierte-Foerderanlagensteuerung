"""Erzeugt einen portablen PLCopen-/TC6-orientierten Export der ST-Quellen.

Die maßgebliche Quelle bleiben die .st-Dateien. Dieser Export bildet die
POU-Struktur ab und bettet die ST-Quelltexte ein, damit sie in eine
IEC-61131-3-Umgebung (z. B. CODESYS) übernommen werden können.
"""

from __future__ import annotations

import datetime
import os
import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "plc", "runtime"))
from softplc.parser import parse_source  # noqa: E402

PLC = os.path.join(ROOT, "plc")
OUT = os.path.join(PLC, "export")
os.makedirs(OUT, exist_ok=True)

SUBDIRS = ("standard", "application", "function_blocks", "simulation", "visualization")
POU_TYPE = {"PROGRAM": "program", "FUNCTION_BLOCK": "functionBlock", "FUNCTION": "function"}


def main():
    ns = "http://www.plcopen.org/xml/tc6_0201"
    project = ET.Element("project", {"xmlns": ns})
    ET.SubElement(project, "fileHeader", {
        "companyName": "Eigenes technisches Simulationsprojekt",
        "productName": "Simulierte Foerderanlage",
        "productVersion": "1.0",
        "creationDateTime": datetime.date.today().isoformat(),
    })
    content = ET.SubElement(project, "content")
    types = ET.SubElement(content, "types")
    ET.SubElement(types, "dataTypes")
    pous_el = ET.SubElement(content, "pous")
    add = ET.SubElement(project, "addData")

    for sub in SUBDIRS:
        d = os.path.join(PLC, sub)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".st"):
                continue
            path = os.path.join(d, fn)
            with open(path, encoding="utf-8") as fh:
                src = fh.read()
            globals_, tdefs, pous = parse_source(src, fn)
            rel = f"{sub}/{fn}"
            if pous:
                for name, pou in pous.items():
                    pe = ET.SubElement(pous_el, "pou", {
                        "name": name,
                        "pouType": POU_TYPE.get(pou.kind, "functionBlock"),
                    })
                    ET.SubElement(pe, "interface")
                    body = ET.SubElement(pe, "body")
                    st = ET.SubElement(body, "ST")
                    xhtml = ET.SubElement(st, "xhtml", {"xmlns": "http://www.w3.org/1999/xhtml"})
                    xhtml.text = f"(* Quelle: plc/{rel} *)\n" + src
            if globals_ or tdefs:
                bundle = ET.SubElement(add, "data", {"name": f"globals_and_types:{rel}"})
                bundle.text = src

    xml_bytes = ET.tostring(project, encoding="utf-8")
    pretty = minidom.parseString(xml_bytes).toprettyxml(indent="  ", encoding="UTF-8")
    out = os.path.join(OUT, "foerderanlage_plcopen.xml")
    with open(out, "wb") as fh:
        fh.write(pretty)
    print(f"  {os.path.relpath(out, ROOT)}")


if __name__ == "__main__":
    main()
