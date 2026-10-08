(* ============================================================================
   FB_Alarm.st
   Störmeldespeicher, Priorisierung und First-out-Erkennung.

   - Ueberlast und Not-Halt sind "lebende" Bedingungen (fallen mit dem Signal).
   - Timeout-/Stau-/Sensorstoerungen werden gespeichert und nur quittiert,
     wenn die Ursache nicht mehr ansteht.
   - eFirst haelt die zuerst aufgetretene Stoerung fest.
   ============================================================================ *)

FUNCTION_BLOCK FB_Alarm
VAR_INPUT
    xOverload            : BOOL;
    xEmergency           : BOOL;
    xStartTimeout        : BOOL;
    xStopTimeout         : BOOL;
    xJam                 : BOOL;
    xSensorInconsistency : BOOL;
    xReset               : BOOL;
END_VAR
VAR_OUTPUT
    eActive    : E_FaultCode;
    eFirst     : E_FaultCode;
    xAnyFault  : BOOL;
    xLampRed   : BOOL;
    xLampYellow: BOOL;
    xBuzzer    : BOOL;
    xOverloadLatched  : BOOL;
    xEmergencyLatched : BOOL;
    xStartLatched     : BOOL;
    xStopLatched      : BOOL;
    xJamLatched       : BOOL;
    xSensorLatched    : BOOL;
END_VAR

    (* --- Ereignisstoerungen speichern --- *)
    IF xOverload THEN
        xOverloadLatched := TRUE;
    END_IF;
    IF xEmergency THEN
        xEmergencyLatched := TRUE;
    END_IF;
    IF xStartTimeout THEN
        xStartLatched := TRUE;
    END_IF;
    IF xStopTimeout THEN
        xStopLatched := TRUE;
    END_IF;
    IF xJam THEN
        xJamLatched := TRUE;
    END_IF;
    IF xSensorInconsistency THEN
        xSensorLatched := TRUE;
    END_IF;

    (* --- Sammelstoerung --- *)
    xAnyFault := xOverloadLatched
                 OR xEmergencyLatched
                 OR xStartLatched
                 OR xStopLatched
                 OR xJamLatched
                 OR xSensorLatched;

    (* --- Quittung nur, wenn keine Ursache mehr ansteht --- *)
    IF xReset
       AND NOT xOverload
       AND NOT xEmergency
       AND NOT xStartTimeout
       AND NOT xStopTimeout
       AND NOT xJam
       AND NOT xSensorInconsistency THEN
        xOverloadLatched := FALSE;
        xEmergencyLatched := FALSE;
        xStartLatched := FALSE;
        xStopLatched := FALSE;
        xJamLatched := FALSE;
        xSensorLatched := FALSE;
    END_IF;

    (* --- Priorisierte Anzeige der aktiven Stoerung --- *)
    IF xEmergencyLatched THEN
        eActive := E_FaultCode.FAULT_EMERGENCY;
    ELSIF xOverloadLatched THEN
        eActive := E_FaultCode.FAULT_OVERLOAD;
    ELSIF xStartLatched THEN
        eActive := E_FaultCode.FAULT_START_TIMEOUT;
    ELSIF xStopLatched THEN
        eActive := E_FaultCode.FAULT_STOP_TIMEOUT;
    ELSIF xJamLatched THEN
        eActive := E_FaultCode.FAULT_JAM;
    ELSIF xSensorLatched THEN
        eActive := E_FaultCode.FAULT_SENSOR_INCONSISTENCY;
    ELSE
        eActive := E_FaultCode.FAULT_NONE;
    END_IF;

    (* --- First-out --- *)
    IF (eFirst = E_FaultCode.FAULT_NONE) AND xAnyFault THEN
        eFirst := eActive;
    END_IF;
    IF xReset AND NOT xAnyFault THEN
        eFirst := E_FaultCode.FAULT_NONE;
    END_IF;

    (* --- Meldeorgane --- *)
    xLampRed := xAnyFault;
    xBuzzer := xAnyFault;
    xLampYellow := (eActive = E_FaultCode.FAULT_JAM)
                   OR (eActive = E_FaultCode.FAULT_SENSOR_INCONSISTENCY);
END_FUNCTION_BLOCK
