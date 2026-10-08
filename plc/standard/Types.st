(* ============================================================================
   Types.st
   Benutzerdefinierte Datentypen (Enumerationen, Strukturen).

   Hinweis: In der SoftPLC-Runtime und in CODESYS koennen Enum-Werte qualifiziert
   (z. B. E_SystemState.ST_READY) verwendet werden.
   ============================================================================ *)

TYPE
    (* Betriebsart des Bedieners *)
    E_Betriebsart : (
        BETRIEB_HAND := 0,
        BETRIEB_AUTO := 1
    );

    (* Zustandsmodell der Anlage *)
    E_SystemState : (
        ST_INIT := 0,
        ST_READY := 10,
        ST_RUNNING := 20,
        ST_STOPPED := 30,
        ST_FAULT := 40,
        ST_EMERGENCY := 50
    );

    (* Stoerungs-Codes *)
    E_FaultCode : (
        FAULT_NONE := 0,
        FAULT_OVERLOAD := 1,
        FAULT_START_TIMEOUT := 2,
        FAULT_STOP_TIMEOUT := 3,
        FAULT_JAM := 4,
        FAULT_SENSOR_INCONSISTENCY := 5,
        FAULT_EMERGENCY := 6
    );

    (* Prozesszustand Automatik *)
    E_ProcessState : (
        P_IDLE := 0,
        P_TRANSPORT := 1,
        P_RUN_ON := 2
    );
END_TYPE
