(* ============================================================================
   FB_Counter.st
   Werkstueckzaehlung.

   Gezaehlt wird am Auslauf ueber die steigende Flanke des Sensors B2.
   Begruendung: Der Auslauf repraesentiert ein fertig transportiertes Werkstueck.
   Die Flankenauswertung (R_TRIG) verhindert Mehrfachzaehlung, solange der
   Sensor aktiv bleibt.
   ============================================================================ *)

FUNCTION_BLOCK FB_Counter
VAR_INPUT
    xExitSensor : BOOL;    (* B2 *)
    xResetCount : BOOL;
END_VAR
VAR_OUTPUT
    diCount      : DINT;
    xJustCounted : BOOL;   (* Impuls fuer HMI/Statistik *)
END_VAR
VAR
    rtrigExit : R_TRIG;
END_VAR

    rtrigExit(CLK := xExitSensor);
    xJustCounted := FALSE;

    IF rtrigExit.Q THEN
        diCount := diCount + 1;
        xJustCounted := TRUE;
    END_IF;

    IF xResetCount THEN
        diCount := 0;
    END_IF;
END_FUNCTION_BLOCK
