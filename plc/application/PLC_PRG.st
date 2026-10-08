(* ============================================================================
   PLC_PRG.st
   Hauptprogramm der SoftPLC (ein Aufruf je Zyklus).

   Ablauf je Zyklus (Reihenfolge ist bewusst festgelegt):
     1. Initialisierung / Prozessabbild lesen
     2. Betriebsart
     3. Prozess (Automatik)
     4. Motorsteuerung (Steuerlogik)
     5. Simulation Leistungsteil (Schuetz, Motor)
     6. Simulation Foerderband (Werkstuecke, Sensoren)
     7. Diagnose (Stau, Zaehler, Sensorplausibilitaet, Meldespeicher)
     8. Zustandsmodell und Ausgaenge
     9. Prozessabbild aktualisieren (Anlage -> SPS-Eingaenge)

   Die Trennung Steuerlogik (Schritte 2-4, 7-8) und elektrisches/mechanisches
   Modell (Schritte 5-6, 9) bildet das reale Zusammenspiel SPS <-> Anlage ab.
   ============================================================================ *)

PROGRAM PLC_PRG
VAR
    fbMode      : FB_ModeManager;
    fbProcess   : FB_ConveyorProcess;
    fbMotor     : FB_MotorControl;
    fbContactor : FB_ContactorMotor;
    fbBelt      : FB_BeltSimulation;
    fbJam       : FB_JamDetection;
    fbCounter   : FB_Counter;
    fbAlarm     : FB_Alarm;

    tonDebounce  : TON;
    xInitDone    : BOOL;
    xWasRunning  : BOOL;
    xModePrev    : BOOL;
    xModeChange  : BOOL;
    xPermissive  : BOOL;
    xStartEffective : BOOL;
    xStopCombined   : BOOL;
    xSensorInconsistency : BOOL;
    eState       : E_SystemState;
    i            : INT;
END_VAR

    (* ------------------------------------------------------------------ *)
    (* 1. Initialisierung                                                 *)
    (* ------------------------------------------------------------------ *)
    IF NOT xInitDone THEN
        xStopNC         := TRUE;    (* Stop-Taster nicht betaetigt (NC geschlossen) *)
        xNotHaltNC      := TRUE;    (* Sicherheitskette geschlossen *)
        xOverloadNC     := TRUE;    (* Motorschutz in Ordnung *)
        xMotorFeedback  := FALSE;
        xEntrySensor    := FALSE;
        xExitSensor     := FALSE;
        xInitDone       := TRUE;
    END_IF;

    (* Prozessabbild -> logische Bedingungen *)
    xStopOperated    := NOT xStopNC;
    xEmergencyActive := NOT xNotHaltNC;
    xOverloadActive  := NOT xOverloadNC;

    (* ------------------------------------------------------------------ *)
    (* 2. Betriebsart                                                     *)
    (* ------------------------------------------------------------------ *)
    fbMode(xAuto := xModeAuto);
    xModeChange := (xModeAuto <> xModePrev);
    xModePrev := xModeAuto;

    (* ------------------------------------------------------------------ *)
    (* 3. Sammelfreigabe (vorheriger Meldespeicherstand)                  *)
    (* ------------------------------------------------------------------ *)
    xPermissive := NOT fbAlarm.xAnyFault
                   AND NOT xEmergencyActive
                   AND NOT xOverloadActive;

    (* ------------------------------------------------------------------ *)
    (* 4. Prozess (Automatik)                                             *)
    (* ------------------------------------------------------------------ *)
    fbProcess(
        xEnable      := fbMode.xAutoActive AND xPermissive,
        xEntrySensor := xEntrySensor,
        xExitSensor  := xExitSensor);

    (* ------------------------------------------------------------------ *)
    (* 5. Motorsteuerung (Steuerlogik)                                    *)
    (* ------------------------------------------------------------------ *)
    xStartEffective := xStart AND fbMode.xHandActive;
    xStopCombined   := xStopOperated OR xModeChange;

    fbMotor(
        xStartManual     := xStartEffective,
        xAutoStartPulse  := fbProcess.xStartPulse,
        xAutoStopPulse   := fbProcess.xStopPulse,
        xStop            := xStopCombined,
        xEmergencyActive := xEmergencyActive,
        xOverloadActive  := xOverloadActive,
        xPermissive      := xPermissive,
        xMotorFeedback   := xMotorFeedback);

    (* ------------------------------------------------------------------ *)
    (* 6. Simulation Leistungsteil (Schuetz / Motor)                      *)
    (* ------------------------------------------------------------------ *)
    fbContactor(
        xCoilCmd             := fbMotor.xContactorCmd,
        xEmergencyActive     := xEmergencyActive,
        xInjectOverload      := xSimInjectOverload,
        xInjectFeedbackOpen  := xSimInjectFeedbackOpen,
        xInjectFeedbackStuck := xSimInjectFeedbackStuck);

    (* ------------------------------------------------------------------ *)
    (* 7. Simulation Foerderband                                          *)
    (* ------------------------------------------------------------------ *)
    fbBelt(
        xMotorRunning              := fbContactor.xMotorRunning,
        xGenerate                  := xSimGenerateWorkpieces,
        xInjectJam                 := xSimInjectJam,
        xInjectSensorInconsistency := xSimInjectSensorInconsistency);

    (* ------------------------------------------------------------------ *)
    (* 8. Diagnose                                                        *)
    (* ------------------------------------------------------------------ *)
    (* Stau: Antrieb angesteuert (Befehl) oder laeuft *)
    fbJam(
        xEntrySensor := xEntrySensor,
        xExitSensor  := xExitSensor,
        xConveyorRun := fbMotor.xContactorCmd OR fbContactor.xMotorRunning,
        xReset       := xReset);

    (* Zaehler *)
    fbCounter(
        xExitSensor := xExitSensor,
        xResetCount := xSimResetCount);

    (* Sensorplausibilitaet: Auslauf aktiv, obwohl kein Transport laeuft *)
    tonDebounce(IN := xExitSensor AND NOT fbMotor.xRunning AND NOT fbJam.xTransportPending,
                PT := T_DEBOUNCE);
    xSensorInconsistency := tonDebounce.Q;

    (* Störmeldespeicher *)
    fbAlarm(
        xOverload            := xOverloadActive,
        xEmergency           := xEmergencyActive,
        xStartTimeout        := fbMotor.xFaultStartTimeout,
        xStopTimeout         := fbMotor.xFaultStopTimeout,
        xJam                 := fbJam.xJam,
        xSensorInconsistency := xSensorInconsistency,
        xReset               := xReset);

    (* ------------------------------------------------------------------ *)
    (* 9. Zustandsmodell                                                  *)
    (* ------------------------------------------------------------------ *)
    IF xEmergencyActive THEN
        eState := E_SystemState.ST_EMERGENCY;
    ELSIF fbAlarm.xAnyFault THEN
        eState := E_SystemState.ST_FAULT;
    ELSIF fbMotor.xRunning THEN
        eState := E_SystemState.ST_RUNNING;
        xWasRunning := TRUE;
    ELSIF xWasRunning THEN
        eState := E_SystemState.ST_STOPPED;
    ELSE
        eState := E_SystemState.ST_READY;
    END_IF;

    (* ------------------------------------------------------------------ *)
    (* 10. Ausgaenge                                                      *)
    (* ------------------------------------------------------------------ *)
    xMotorContactor := fbMotor.xContactorCmd;
    xLampGreen      := (eState = E_SystemState.ST_READY)
                       OR (eState = E_SystemState.ST_RUNNING);
    xLampRed        := fbAlarm.xLampRed;
    xBuzzer         := fbAlarm.xBuzzer;
    xLampYellow     := fbAlarm.xLampYellow;

    (* ------------------------------------------------------------------ *)
    (* 11. Prozessabbild aktualisieren (Anlage -> SPS)                    *)
    (* ------------------------------------------------------------------ *)
    xOverloadNC     := NOT fbContactor.xOverloadTrip;
    xMotorFeedback  := fbContactor.xMotorFeedback;
    xEntrySensor    := fbBelt.xEntrySensor;
    xExitSensor     := fbBelt.xExitSensor;

    (* Simulations-Anzeigewerte *)
    xSimOverloadTrip := fbContactor.xOverloadTrip;
    xSimContactor    := fbContactor.xContactorClosed;
    xSimMotorRunning := fbContactor.xMotorRunning;

    (* ------------------------------------------------------------------ *)
    (* 12. HMI-Variablen aktualisieren                                    *)
    (* ------------------------------------------------------------------ *)
    eHmiState       := eState;
    eHmiMode        := fbMode.eMode;
    eHmiProcess     := fbProcess.eState;
    eHmiActiveFault := fbAlarm.eActive;
    eHmiFirstFault  := fbAlarm.eFirst;
    xHmiMotorCmd    := fbMotor.xContactorCmd;
    xHmiMotorRun    := fbMotor.xRunning;
    xHmiMotorFb     := xMotorFeedback;
    xHmiOverload    := xOverloadActive;
    xHmiEmergency   := xEmergencyActive;
    xHmiEntry       := xEntrySensor;
    xHmiExit        := xExitSensor;
    xHmiJam         := fbJam.xJam;
    xHmiLampRed     := fbAlarm.xLampRed;
    xHmiBuzzer      := fbAlarm.xBuzzer;
    diHmiCount      := fbCounter.diCount;
    FOR i := 0 TO 4 DO
        aHmiBeltPos[i] := fbBelt.aPos[i];
    END_FOR;
END_PROGRAM
