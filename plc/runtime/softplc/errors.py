"""Fehlerklassen der SoftPLC (Parser und Laufzeit)."""


class SoftPlcError(Exception):
    """Basisklasse fuer alle SoftPLC-Fehler."""


class LexerError(SoftPlcError):
    pass


class ParseError(SoftPlcError):
    pass


class RuntimeError_(SoftPlcError):
    """Laufzeitfehler (nicht mit dem Python-Builtin verwechseln)."""
