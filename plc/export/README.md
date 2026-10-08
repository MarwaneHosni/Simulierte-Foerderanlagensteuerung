# PLC-/SPS-Export

## Maßgebliche Quelle

Die **maßgebliche Quelle** der SPS-Logik sind die `.st`-Dateien unter:

```text
plc/application/       PLC_PRG, Config
plc/function_blocks/   Steuer- und Diagnosebausteine
plc/simulation/        Anlagensimulation (Leistungsteil, Förderband)
plc/visualization/     HMI-Globalvariablen
plc/standard/          Datentypen (Types), I/O-Prozessabbild (GVL_IO)
plc/runtime/           Selbstständige Python-SoftPLC (Referenz-Runtime)
```

## PLCopen-/TC6-Export

`foerderanlage_plcopen.xml` wird von `tools/gen_plcopen.py` erzeugt. Es bildet
die POU-Struktur (Programme/Funktionsbausteine) ab und bettet die ST-Quelltexte
ein. Damit lässt sich der Code in eine IEC-61131-3-Umgebung übernehmen.

> Hinweis: CODESYS war in der Erstellungsumgebung nicht verfügbar. Der Export
> ist **portabel aufgebaut**, aber nicht in CODESYS verifiziert. Die einfachste
> Übernahme ist, die `.st`-Dateien direkt als ST-POUs in das Zielprojekt zu
> importieren bzw. einzufügen.

## Ausführen ohne CODESYS

Die SoftPLC ist direkt lauffähig (siehe Repository-README):

```text
python plc/runtime/run.py --cycles 500 --auto --generate --interactive
```
