(* ============================================================================
   Config.st
   Zentrale Konfigurations- und Zeitkonstanten der Simulation.

   Alle Zeiten sind Simulationsannahmen (didaktisch), keine realen
   Anlagenparameter. Siehe docs/10_Grenzen_und_Annahmen.md.
   ============================================================================ *)

VAR_GLOBAL CONSTANT
    (* Zykluszeit der SoftPLC-Simulation *)
    T_ZYKLUS               : TIME := T#20ms;
    CYCLE_TIME_S           : REAL := 0.02;       (* Zykluszeit in Sekunden (Rechenwert) *)

    (* Motorueberwachung *)
    T_MOTOR_START_TIMEOUT  : TIME := T#2000ms;   (* Befehl EIN, Rueckmeldung AUS *)
    T_MOTOR_STOP_TIMEOUT   : TIME := T#2000ms;   (* Befehl AUS, Rueckmeldung EIN *)

    (* Transport-/Stauueberwachung Einlauf -> Auslauf *)
    T_MAX_TRANSPORT        : TIME := T#8000ms;
    T_RUN_ON               : TIME := T#1500ms;   (* Nachlauf nach Auslauf *)

    (* Schaltgeraete / Motorschutz (Simulationsmodell) *)
    T_CONTACTOR_PULL       : TIME := T#300ms;    (* Anzugsverzoegerung Schuetz *)
    T_OVERLOAD_TRIP        : TIME := T#3000ms;   (* Ausloesezeit Motorschutz *)

    (* Entprellung / Plausibilitaet *)
    T_DEBOUNCE             : TIME := T#500ms;

    (* Prozess *)
    AUTO_CONTINUOUS        : BOOL := FALSE;      (* FALSE = Bedarfsbetrieb, TRUE = Dauerlauf *)
    BELT_SPEED_PER_S       : REAL := 25.0;       (* Bandweg in % je Sekunde *)
    WORKPIECE_INTERVAL     : TIME := T#4000ms;   (* Werkstueck-Erzeugung (Automatik) *)
END_VAR
