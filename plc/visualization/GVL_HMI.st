(* ============================================================================
   GVL_HMI.st
   Globale Anzeigevariablen fuer das HMI / die Prozessvisualisierung.

   Diese Variablen werden einmal je Zyklus aus den realen Simulations- und
   Steuervariablen aktualisiert. Das HMI liest ausschliesslich diese Werte,
   damit die Anzeige immer den tatsaechlichen Zustand widerspiegelt.
   ============================================================================ *)

VAR_GLOBAL
    eHmiState        : E_SystemState;
    eHmiMode         : E_Betriebsart;
    eHmiProcess      : E_ProcessState;
    eHmiActiveFault  : E_FaultCode;
    eHmiFirstFault   : E_FaultCode;

    xHmiMotorCmd     : BOOL;
    xHmiMotorRun     : BOOL;
    xHmiMotorFb      : BOOL;
    xHmiOverload     : BOOL;
    xHmiEmergency    : BOOL;
    xHmiEntry        : BOOL;
    xHmiExit         : BOOL;
    xHmiJam          : BOOL;
    xHmiLampRed      : BOOL;
    xHmiBuzzer       : BOOL;

    diHmiCount       : DINT;
    aHmiBeltPos      : ARRAY[0..4] OF REAL;
END_VAR
