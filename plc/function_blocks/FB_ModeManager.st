(* ============================================================================
   FB_ModeManager.st
   Verwaltung der Betriebsart (Hand / Automatik).

   Der Wahlschalter ist ein reines Bedienelement; er hat keine Sicherheitsfunktion.
   ============================================================================ *)

FUNCTION_BLOCK FB_ModeManager
VAR_INPUT
    xAuto : BOOL;   (* S5: 1 = Automatik, 0 = Hand *)
END_VAR
VAR_OUTPUT
    eMode       : E_Betriebsart;
    xAutoActive : BOOL;
    xHandActive : BOOL;
END_VAR

    IF xAuto THEN
        eMode := E_Betriebsart.BETRIEB_AUTO;
    ELSE
        eMode := E_Betriebsart.BETRIEB_HAND;
    END_IF;

    xAutoActive := (eMode = E_Betriebsart.BETRIEB_AUTO);
    xHandActive := NOT xAutoActive;
END_FUNCTION_BLOCK
