(* ============================================================================
   FB_BeltSimulation.st
   Mechanisches Modell des Foerderbands.

   - Das Band hat eine normierte Laenge von 0..100 %.
   - Werkstuecke werden in 5 Plaetzen gefuehrt (aPos; -1 = frei).
   - Bei laufendem Motor bewegen sich die Werkstuecke mit BELT_SPEED_PER_S.
   - Beim Durchlaufen der Zonen werden die Sensoren B1 (Einlauf) und B2 (Auslauf)
     gesetzt.
   - xInjectJam blockiert den Transport (Stau).
   - xInjectSensorInconsistency erzwingt ein dauerhaftes Auslaufsignal.
   ============================================================================ *)

FUNCTION_BLOCK FB_BeltSimulation
VAR_INPUT
    xMotorRunning              : BOOL;
    xGenerate                  : BOOL;   (* Werkstuecke automatisch erzeugen *)
    xInjectJam                 : BOOL;
    xInjectSensorInconsistency : BOOL;
END_VAR
VAR_OUTPUT
    xEntrySensor : BOOL;                 (* B1 *)
    xExitSensor  : BOOL;                 (* B2 *)
    aPos         : ARRAY[0..4] OF REAL;  (* Werkstueckpositionen in % *)
END_VAR
VAR
    i          : INT;
    xInitDone  : BOOL;
    xPlaced    : BOOL;
    rStep      : REAL;
    tonGen     : TON;
END_VAR

    (* --- Einmalige Initialisierung --- *)
    IF NOT xInitDone THEN
        FOR i := 0 TO 4 DO
            aPos[i] := -1.0;
        END_FOR;
        xInitDone := TRUE;
    END_IF;

    (* --- Werkstuecke periodisch erzeugen (nur wenn gewuenscht) --- *)
    tonGen(IN := NOT tonGen.Q, PT := WORKPIECE_INTERVAL);
    IF xGenerate AND tonGen.Q THEN
        xPlaced := FALSE;
        FOR i := 0 TO 4 DO
            IF (NOT xPlaced) AND (aPos[i] < 0.0) THEN
                aPos[i] := 0.0;
                xPlaced := TRUE;
            END_IF;
        END_FOR;
    END_IF;

    (* --- Transport --- *)
    rStep := BELT_SPEED_PER_S * CYCLE_TIME_S;
    FOR i := 0 TO 4 DO
        IF aPos[i] >= 0.0 THEN
            IF xMotorRunning THEN
                IF NOT xInjectJam THEN
                    aPos[i] := aPos[i] + rStep;
                ELSE
                    (* Blockade in Bandmitte: Werkstueck laeuft bis 50 % und bleibt stehen *)
                    IF aPos[i] < 50.0 THEN
                        aPos[i] := aPos[i] + rStep;
                        IF aPos[i] > 50.0 THEN
                            aPos[i] := 50.0;
                        END_IF;
                    END_IF;
                END_IF;
            END_IF;
            IF aPos[i] > 100.0 THEN
                aPos[i] := -1.0;   (* Werkstueck hat das Band verlassen *)
            END_IF;
        END_IF;
    END_FOR;

    (* --- Sensorauswertung (Zonen) ---------------------------------------
       Einlaufzone 0..6 %: ein von der Zufuehrung aufgesetztes Werkstueck
       loest B1 unmittelbar aus.
       Auslaufzone 94..100 %: B2 wird bis zum Bandende gehalten.        *)
    xEntrySensor := FALSE;
    xExitSensor := FALSE;
    FOR i := 0 TO 4 DO
        IF (aPos[i] >= 0.0) AND (aPos[i] <= 6.0) THEN
            xEntrySensor := TRUE;
        END_IF;
        IF (aPos[i] >= 94.0) AND (aPos[i] <= 100.0) THEN
            xExitSensor := TRUE;
        END_IF;
    END_FOR;

    (* --- Fehlerinjektion: dauerhaftes Auslaufsignal --- *)
    IF xInjectSensorInconsistency THEN
        xExitSensor := TRUE;
    END_IF;
END_FUNCTION_BLOCK
