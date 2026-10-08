"""Gemeinsame elektrotechnische Stammdaten (Klemmen, Stueckliste, Netze).

Diese Daten sind die einzige Quelle fuer Klemmenplan, Stueckliste, Schaltplan
und Konsistenzpruefung. Aenderungen wirken sich damit konsistent aus.

Alle Angaben sind Konzept-/Simulationsannahmen (siehe docs/10_Grenzen_und_Annahmen.md).
"""

# (Klemme, Signal, Richtung, Beschreibung)
TERMINALS = [
    ("X1.1", "+24V", "PWR", "Steuerspannung +24 V DC"),
    ("X1.2", "0V", "PWR", "Steuerspannung 0 V (Bezug)"),
    ("X1.3", "PE", "PWR", "Schutzleiter Steuerung"),
    ("X2.1", "Start", "DI", "S1 Start-Taster (Schließer)"),
    ("X2.2", "Stop", "DI", "S2 Stop-Taster (Öffner)"),
    ("X2.3", "Not-Halt", "DI", "S3 Not-Halt-Taster (Öffner)"),
    ("X2.4", "Reset", "DI", "S4 Reset-Taster (Schließer)"),
    ("X2.5", "Betriebsart Auto", "DI", "S5 Wahlschalter Hand/Auto"),
    ("X2.6", "+24V Bedienung", "PWR", "gemeinsame Versorgung Bedienfeld"),
    ("X3.1", "Sensor Einlauf B1", "DI", "Lichtschranke Einlauf"),
    ("X3.2", "Sensor Auslauf B2", "DI", "Lichtschranke Auslauf"),
    ("X3.3", "Rückmeldung K1", "DI", "Hilfskontakt Schütz / Motorlauf"),
    ("X3.4", "Motorschutz F2", "DI", "Öffner-Hilfskontakt Motorschutzrelais"),
    ("X3.5", "+24V Sensorik", "PWR", "Versorgung Sensorik"),
    ("X3.6", "0V Sensorik", "PWR", "Bezug Sensorik"),
    ("X4.1", "Schütz K1", "DO", "Ansteuerung Schützspule K1"),
    ("X4.2", "Meldeleuchte H1", "DO", "Betrieb/READY grün"),
    ("X4.3", "Meldeleuchte H2", "DO", "Störung rot"),
    ("X4.4", "Hupe H3", "DO", "Störsignal"),
    ("X4.5", "Meldeleuchte H4", "DO", "Warnung gelb (optional)"),
    ("X4.6", "0V Aktorik", "PWR", "Bezug Aktorik"),
    ("X5.1", "M1 U", "PWR", "Motorwicklung U"),
    ("X5.2", "M1 V", "PWR", "Motorwicklung V"),
    ("X5.3", "M1 W", "PWR", "Motorwicklung W"),
    ("X5.4", "M1 PE", "PWR", "Schutzleiter Motor"),
    ("X6.1", "L1", "PWR", "Einspeisung Außenleiter L1"),
    ("X6.2", "L2", "PWR", "Einspeisung Außenleiter L2"),
    ("X6.3", "L3", "PWR", "Einspeisung Außenleiter L3"),
    ("X6.4", "PE", "PWR", "Einspeisung Schutzleiter"),
    ("X6.5", "N", "PWR", "Einspeisung Neutralleiter"),
]

# (Bezeichner, Komponente, Beschreibung, Menge, Bemerkung)
BOM = [
    ("Q1", "Hauptschalter / Isolator, 3-polig", "Freischaltung der Anlage", 1,
     "Konzept, Bemessung nach realer Anlage"),
    ("F1", "Leitungsschutzsicherung", "Schutz der Einspeisung/Steuerkreis", 1,
     "Bemessung nach realem Stromkreis"),
    ("F2", "Motorschutzrelais, einstellbar", "Überlastschutz Motor M1", 1,
     "Annahme: Einstellbereich passend zu M1"),
    ("K1", "Schütz, 3 Hauptkontakte + Hilfskontakt", "Schalten des Motorstroms", 1,
     "Spule 24 V DC (Annahme)"),
    ("T1", "Netzteil 24 V DC", "Steuerspannung", 1,
     "Leistung nach Verbrauchern"),
    ("M1", "Drehstrommotor (Annahme 0,75 kW / 400 V)", "Antrieb Förderband", 1,
     "Nur didaktische Annahme, kein reales Typenschild"),
    ("S1", "Taster Schließer", "Start", 1, ""),
    ("S2", "Taster Öffner", "Stop", 1, ""),
    ("S3", "Not-Halt-Taster Öffner", "Not-Halt (konzeptionell)", 1, ""),
    ("S4", "Taster Schließer", "Reset", 1, ""),
    ("S5", "Wahlschalter", "Hand/Auto", 1, ""),
    ("B1", "Lichtschranke", "Werkstück Einlauf", 1, ""),
    ("B2", "Lichtschranke", "Werkstück Auslauf", 1, ""),
    ("H1", "Meldeleuchte grün", "Betrieb", 1, ""),
    ("H2", "Meldeleuchte rot", "Störung", 1, ""),
    ("H3", "Hupe/Signalgeber", "Störmeldung", 1, ""),
    ("H4", "Meldeleuchte gelb", "Warnung", 1, "optional"),
    ("X1-X6", "Reihenklemmen", "Klemmen mit Zubehör", 1, "siehe Klemmenplan"),
]
