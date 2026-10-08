(* ============================================================================
   FB_ConveyorProcess.st
   Prozessablauf Automatikbetrieb.

   Zwei Varianten, gesteuert durch die Konstante AUTO_CONTINUOUS:
     - Bedarfsbetrieb (FALSE): Start bei Werkstueck am Einlauf, Nachlauf nach
       dem Auslauf, dann Rueckkehr nach IDLE.
     - Dauerlauf (TRUE): Start beim Aktivieren der Automatik, kein Stopp.

   Ausgaenge sind Impulse (ein Zyklus) fuer die Motorsteuerung.
   ============================================================================ *)

FUNCTION_BLOCK FB_ConveyorProcess
VAR_INPUT
    xEnable      : BOOL;   (* Automatik aktiv, READY, keine Stoerung *)
    xEntrySensor : BOOL;   (* B1 *)
    xExitSensor  : BOOL;   (* B2 *)
END_VAR
VAR_OUTPUT
    xStartPulse : BOOL;    (* Startimpuls an Motorsteuerung *)
    xStopPulse  : BOOL;    (* Stopimpuls an Motorsteuerung *)
    eState      : E_ProcessState;
END_VAR
VAR
    xEnablePrev : BOOL;
    tonRunOn    : TON;
    xRunOnCond  : BOOL;
END_VAR

    xStartPulse := FALSE;
    xStopPulse  := FALSE;

    (* Nachlauf-Timer jede Scan aufrufen; ausserhalb P_RUN_ON zuruecksetzen *)
    xRunOnCond := (eState = E_ProcessState.P_RUN_ON) AND NOT xExitSensor;
    tonRunOn(IN := xRunOnCond, PT := T_RUN_ON);

    IF NOT xEnable THEN
        IF xEnablePrev THEN
            xStopPulse := TRUE;   (* Automatik verlassen -> Band stoppen *)
        END_IF;
        eState := E_ProcessState.P_IDLE;
        xEnablePrev := FALSE;
    ELSE
        CASE eState OF
            E_ProcessState.P_IDLE :
                IF AUTO_CONTINUOUS THEN
                    IF NOT xEnablePrev THEN
                        xStartPulse := TRUE;
                    END_IF;
                    eState := E_ProcessState.P_TRANSPORT;
                ELSE
                    IF xEntrySensor THEN
                        xStartPulse := TRUE;
                        eState := E_ProcessState.P_TRANSPORT;
                    END_IF;
                END_IF;

            E_ProcessState.P_TRANSPORT :
                IF (NOT AUTO_CONTINUOUS) AND xExitSensor THEN
                    eState := E_ProcessState.P_RUN_ON;
                END_IF;

            E_ProcessState.P_RUN_ON :
                IF tonRunOn.Q THEN
                    xStopPulse := TRUE;
                    eState := E_ProcessState.P_IDLE;
                END_IF;

            ELSE
                eState := E_ProcessState.P_IDLE;
        END_CASE;
        xEnablePrev := TRUE;
    END_IF;
END_FUNCTION_BLOCK
