(* ============================================================================
   GVL_IO.st
   Globaler Ein-/Ausgangs-Prozessabbild der SoftPLC.

   Referenz: ../../electrical/io_list/io_list.md
   Konvention: Signalpegel wie am SPS-Klemmen-Eingang.
     - NO (Schliesser): 0 = nicht betaetigt, 1 = betaetigt
     - NC (Oeffner, fail-safe): 1 = Kette geschlossen / gesund, 0 = betaetigt/Stoerung
   ============================================================================ *)

VAR_GLOBAL
    (* ----- Eingaenge (%I) ----- *)
    xStart          AT %IX0.0 : BOOL;  (* S1 Start-Taster (NO): 1 = Start angefordert *)
    xStopNC         AT %IX0.1 : BOOL;  (* S2 Stop-Taster (NC): 1 = Kette geschlossen *)
    xNotHaltNC      AT %IX0.2 : BOOL;  (* S3 Not-Halt (NC): 1 = Sicherheitskette geschlossen *)
    xOverloadNC     AT %IX0.3 : BOOL;  (* F2 Motorschutz (NC): 1 = Motorschutz OK *)
    xEntrySensor    AT %IX0.4 : BOOL;  (* B1 Lichtschranke Einlauf: 1 = Werkstueck erfasst *)
    xExitSensor     AT %IX0.5 : BOOL;  (* B2 Lichtschranke Auslauf: 1 = Werkstueck erfasst *)
    xMotorFeedback  AT %IX0.6 : BOOL;  (* K1/M1 Rueckmeldung: 1 = Motor laeuft *)
    xModeAuto       AT %IX0.7 : BOOL;  (* S5 Wahlschalter: 1 = Automatik, 0 = Hand *)
    xReset          AT %IX1.0 : BOOL;  (* S4 Reset-Taster (NO) *)
    xBeltSpeedPulse AT %IX1.1 : BOOL;  (* Reserve: Bandgeschwindigkeit/Impuls (optional) *)

    (* ----- Ausgaenge (%Q) ----- *)
    xMotorContactor AT %QX0.0 : BOOL;  (* K1 Schuetzansteuerung *)
    xLampGreen      AT %QX0.1 : BOOL;  (* H1 Betrieb/READY *)
    xLampRed        AT %QX0.2 : BOOL;  (* H2 Stoerung *)
    xBuzzer         AT %QX0.3 : BOOL;  (* H3 Hupe *)
    xLampYellow     AT %QX0.4 : BOOL;  (* H4 Warnung (optional) *)
END_VAR

(* Abgeleitete, logische Bedingungen (aus den Rohsignalen).
   Diese GVL wird durch die Anwendung einmal je Zyklus aktualisiert. *)
VAR_GLOBAL
    xStopOperated    : BOOL;  (* Stop betaetigt  = NOT xStopNC *)
    xEmergencyActive : BOOL;  (* Not-Halt aktiv  = NOT xNotHaltNC *)
    xOverloadActive  : BOOL;  (* Ueberlast aktiv = NOT xOverloadNC *)
END_VAR
