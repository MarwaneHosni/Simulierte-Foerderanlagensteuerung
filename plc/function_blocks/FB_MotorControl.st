(* ============================================================================
   FB_MotorControl.st
   Kern der Motorsteuerung (Steuerlogik).

   Konzept:
     - Start ist flankengesteuert (Taster bzw. Automatik-Startimpuls).
     - Selbsthaltung (Latch) des Laufwunsches.
     - Kickout-Bedingungen (Stop, Not-Halt, Ueberlast, fehlende Freigabe,
       Automatik-Stopimpuls) setzen die Selbsthaltung zurueck.
     - Stop hat Vorrang vor Start.
     - Der Schuetzbefehl ist zusaetzlich hart verriegelt.
     - Ueberwachung: "laeuft nicht an" und "stoppt nicht" ueber TON.
   ============================================================================ *)

FUNCTION_BLOCK FB_MotorControl
VAR_INPUT
    xStartManual     : BOOL;   (* S1 Start-Taster (Hand) *)
    xAutoStartPulse  : BOOL;   (* Startimpuls aus dem Automatikprozess *)
    xAutoStopPulse   : BOOL;   (* Stopimpuls (Nachlauf beendet) *)
    xStop            : BOOL;   (* TRUE = Stop betaetigt bzw. Betriebsartwechsel *)
    xEmergencyActive : BOOL;   (* Not-Halt aktiv *)
    xOverloadActive  : BOOL;   (* Ueberlast aktiv *)
    xPermissive      : BOOL;   (* Sammelfreigabe (keine Stoerung) *)
    xMotorFeedback   : BOOL;   (* tatsaechlicher Motorlauf *)
END_VAR
VAR_OUTPUT
    xContactorCmd      : BOOL; (* Befehl an Schuetz K1 *)
    xRunRequest        : BOOL; (* interne Selbsthaltung *)
    xRunning           : BOOL; (* Motor laeuft (Rueckmeldung) *)
    xFaultStartTimeout : BOOL; (* "laeuft nicht an" *)
    xFaultStopTimeout  : BOOL; (* "stoppt nicht" *)
END_VAR
VAR
    rtrigStart  : R_TRIG;
    tonStart    : TON;
    tonStop     : TON;
    xStartAction : BOOL;
    xKickout     : BOOL;
END_VAR

    (* --- Startflanke aus dem Handbetrieb --- *)
    rtrigStart(CLK := xStartManual);

    (* --- Start-/Kickout-Bedingungen --- *)
    xStartAction := (rtrigStart.Q OR xAutoStartPulse)
                    AND xPermissive
                    AND NOT xStop
                    AND NOT xEmergencyActive
                    AND NOT xOverloadActive;

    xKickout := xStop
                OR xAutoStopPulse
                OR xEmergencyActive
                OR xOverloadActive
                OR NOT xPermissive;

    (* --- Selbsthaltung des Laufwunsches; Kickout hat Vorrang --- *)
    IF xKickout THEN
        xRunRequest := FALSE;
    ELSIF xStartAction THEN
        xRunRequest := TRUE;
    END_IF;

    (* --- Schuetzbefehl, zusaetzlich hart verriegelt --- *)
    xContactorCmd := xRunRequest
                     AND NOT xStop
                     AND NOT xEmergencyActive
                     AND NOT xOverloadActive
                     AND xPermissive;

    (* --- Rueckmeldung des tatsaechlichen Motorlaufs --- *)
    xRunning := xMotorFeedback;

    (* --- Startueberwachung: Befehl EIN, keine Rueckmeldung --- *)
    tonStart(IN := xContactorCmd AND NOT xMotorFeedback,
             PT := T_MOTOR_START_TIMEOUT);
    xFaultStartTimeout := tonStart.Q;

    (* --- Stopueberwachung: Befehl AUS, Rueckmeldung bleibt EIN --- *)
    tonStop(IN := (NOT xContactorCmd) AND xMotorFeedback,
            PT := T_MOTOR_STOP_TIMEOUT);
    xFaultStopTimeout := tonStop.Q;
END_FUNCTION_BLOCK
