(* ============================================================================
   FB_JamDetection.st
   Stau-/Blockadeerkennung.

   Verfahren: Ein Werkstueck wird am Einlauf erkannt und der Antrieb laeuft.
   Erreicht es den Auslauf nicht innerhalb T_MAX_TRANSPORT, liegt ein Stau vor.
   Die Stau-Stoerung wird bis zur Quittung gespeichert.
   ============================================================================ *)

FUNCTION_BLOCK FB_JamDetection
VAR_INPUT
    xEntrySensor      : BOOL;   (* B1 *)
    xExitSensor       : BOOL;   (* B2 *)
    xConveyorRun      : BOOL;   (* Antrieb angesteuert bzw. laeuft *)
    xReset            : BOOL;
END_VAR
VAR_OUTPUT
    xJam              : BOOL;
    xTransportPending : BOOL;   (* Werkstueck unterwegs, Auslauf erwartet *)
END_VAR
VAR
    rtrigEntry : R_TRIG;
    tonJam     : TON;
END_VAR

    rtrigEntry(CLK := xEntrySensor);

    (* Transportauftrag setzen, sobald ein Werkstueck einlaeuft und der Antrieb laeuft *)
    IF rtrigEntry.Q AND xConveyorRun THEN
        xTransportPending := TRUE;
    END_IF;

    (* Auslauf erreicht -> Transportauftrag beendet *)
    IF xExitSensor THEN
        xTransportPending := FALSE;
    END_IF;

    (* Ueberwachung der Transportzeit *)
    tonJam(IN := xTransportPending, PT := T_MAX_TRANSPORT);
    IF tonJam.Q THEN
        xJam := TRUE;
    END_IF;

    (* Quittung nur bei freiem Einlauf *)
    IF xReset AND NOT xEntrySensor THEN
        xJam := FALSE;
        xTransportPending := FALSE;
        tonJam(IN := FALSE, PT := T_MAX_TRANSPORT);
    END_IF;
END_FUNCTION_BLOCK
