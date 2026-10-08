(* ============================================================================
   GVL_Simulation.st
   Globale Variablen der Anlagensimulation (elektrisches/mechanisches Modell).

   ACHTUNG: Diese Variablen existieren NUR in der Simulation. Sie bilden das
   Verhalten von Schuetz, Motor, Motorschutz und Foerderband nach und erlauben
   eine gezielte Fehlerinjektion fuer Tests und Diagnose.
   ============================================================================ *)

VAR_GLOBAL
    (* --- Fehlerinjektion (nur Simulation) --- *)
    xSimInjectOverload            : BOOL;  (* Motorschutz nach T_OVERLOAD_TRIP ausloesen *)
    xSimInjectFeedbackOpen        : BOOL;  (* Rueckmeldung faellt aus (laeuft nicht an) *)
    xSimInjectFeedbackStuck       : BOOL;  (* Rueckmeldung haengt (stoppt nicht) *)
    xSimInjectJam                 : BOOL;  (* Band blockiert (Stau) *)
    xSimInjectSensorInconsistency : BOOL;  (* Auslaufsensor liefert Dauersignal *)
    xSimGenerateWorkpieces        : BOOL;  (* Werkstuecke automatisch erzeugen *)
    xSimResetCount                : BOOL;  (* Werkstueckzaehler ruecksetzen *)

    (* --- Simulations-Anzeigewerte --- *)
    xSimOverloadTrip  : BOOL;  (* Motorschutz F2 ausgeloest *)
    xSimContactor     : BOOL;  (* Schuetz K1 angezogen *)
    xSimMotorRunning  : BOOL;  (* Motor laeuft (mechanisch) *)
END_VAR
