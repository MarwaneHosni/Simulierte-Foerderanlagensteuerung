(* ============================================================================
   FB_ContactorMotor.st
   Simulationsmodell des elektrischen Leistungsteils:

       Schütz K1  ->  Drehstrommotor M1
       Motorschutzrelais F2 (Überlast)
       Rückmeldung (Hilfskontakt)

   WICHTIG (Konzept Leistungskreis vs. Steuerkreis):
   Das Schütz zieht nur an, wenn die SPS-Ansteuerung EIN ist UND keine harte
   Schutzbedingung (Überlast, Not-Halt) ansteht. Damit wirkt der Schutz
   unabhängig von der Software - genau wie in einer realen Schützung.
   ============================================================================ *)

FUNCTION_BLOCK FB_ContactorMotor
VAR_INPUT
    xCoilCmd             : BOOL;   (* Ansteuerung von der SPS (K1-Spule) *)
    xEmergencyActive     : BOOL;   (* Not-Halt-Kette offen -> harte Abschaltung *)
    xInjectOverload      : BOOL;   (* Fehlerinjektion Überlast *)
    xInjectFeedbackOpen  : BOOL;   (* Fehlerinjektion: Rückmeldung faellt aus *)
    xInjectFeedbackStuck : BOOL;   (* Fehlerinjektion: Rückmeldung haengt *)
END_VAR
VAR_OUTPUT
    xContactorClosed : BOOL;   (* Schütz angezogen (Hauptkontakt) *)
    xMotorRunning    : BOOL;   (* Motor laeuft (mechanisch) *)
    xMotorFeedback   : BOOL;   (* Rueckmeldung an die SPS *)
    xOverloadTrip    : BOOL;   (* Motorschutz F2 ausgeloest *)
END_VAR
VAR
    tonPull     : TON;
    tonOverload : TON;
    xEnergize   : BOOL;
END_VAR

    (* --- Motorschutzrelais F2: Auslösung bei anhaltender Überlast --- *)
    tonOverload(IN := xInjectOverload AND xMotorRunning, PT := T_OVERLOAD_TRIP);
    IF tonOverload.Q THEN
        xOverloadTrip := TRUE;
    END_IF;
    (* Manuelle Rückstellung des Schutzrelais (Injektion entfernt) *)
    IF NOT xInjectOverload THEN
        xOverloadTrip := FALSE;
        tonOverload(IN := FALSE, PT := T_OVERLOAD_TRIP);
    END_IF;

    (* --- Schützspule: harte Verriegelung durch Motorschutz und Not-Halt --- *)
    xEnergize := xCoilCmd AND NOT xOverloadTrip AND NOT xEmergencyActive;
    tonPull(IN := xEnergize, PT := T_CONTACTOR_PULL);
    xContactorClosed := tonPull.Q;

    (* --- Motor und Rückmeldung --- *)
    xMotorRunning := xContactorClosed;
    xMotorFeedback := xContactorClosed;

    (* --- Fehlerinjektion Rückmeldung --- *)
    IF xInjectFeedbackOpen THEN
        xMotorFeedback := FALSE;
    END_IF;
    IF xInjectFeedbackStuck THEN
        xMotorFeedback := TRUE;
    END_IF;
END_FUNCTION_BLOCK
