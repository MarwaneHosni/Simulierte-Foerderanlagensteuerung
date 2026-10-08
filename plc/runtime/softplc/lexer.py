"""Tokenizer fuer die in diesem Projekt verwendete IEC-61131-3-ST-Teilmenge.

Unterstuetzte Token:
  - Bezeichner / Schluesselwoerter (case-insensitiv)
  - Ganzzahl- und REAL-Literale
  - Zeitliterale T#..., TIME#...
  - Hardwareadressen %IX0.0, %QX0.0 (werden nur erkannt, nicht ausgewertet)
  - Kommentare (* ... *) (auch verschachtelt) und // ...
  - Operatoren := = <> < > <= >= + - * / ( ) [ ] ; , : . ..
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .errors import LexerError

_TWO_CHAR_OPS = (":=", "<>", "<=", ">=", "..")
_ONE_CHAR_OPS = set("=<>+-*/()[];,:.")

_WS = " \t\r\n\f"


@dataclass
class Token:
    kind: str          # id | int | real | time | addr | op | eof
    value: object
    line: int
    col: int

    def __repr__(self) -> str:  # pragma: no cover - Diagnose
        return f"Token({self.kind!r}, {self.value!r}, {self.line}:{self.col})"


class Lexer:
    def __init__(self, src: str, filename: str = "<st>"):
        self.src = src
        self.filename = filename
        self.pos = 0
        self.line = 1
        self.col = 1

    # ------------------------------------------------------------------ #
    def _advance(self, n: int = 1) -> None:
        for _ in range(n):
            if self.pos < len(self.src):
                if self.src[self.pos] == "\n":
                    self.line += 1
                    self.col = 1
                else:
                    self.col += 1
                self.pos += 1

    def _peek(self, off: int = 0) -> str:
        i = self.pos + off
        return self.src[i] if i < len(self.src) else ""

    def _error(self, msg: str) -> LexerError:
        return LexerError(f"{self.filename}:{self.line}:{self.col}: {msg}")

    # ------------------------------------------------------------------ #
    def _skip_ws_and_comments(self) -> None:
        while self.pos < len(self.src):
            c = self.src[self.pos]
            if c in _WS:
                self._advance()
            elif c == "(" and self._peek(1) == "*":
                self._skip_block_comment()
            elif c == "/" and self._peek(1) == "/":
                while self.pos < len(self.src) and self.src[self.pos] != "\n":
                    self._advance()
            else:
                break

    def _skip_block_comment(self) -> None:
        depth = 0
        while self.pos < len(self.src):
            if self.src[self.pos] == "(" and self._peek(1) == "*":
                depth += 1
                self._advance(2)
            elif self.src[self.pos] == "*" and self._peek(1) == ")":
                depth -= 1
                self._advance(2)
                if depth == 0:
                    return
            else:
                self._advance()
        raise self._error("Nicht abgeschlossener Kommentar")

    # ------------------------------------------------------------------ #
    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        while True:
            self._skip_ws_and_comments()
            if self.pos >= len(self.src):
                tokens.append(Token("eof", None, self.line, self.col))
                return tokens

            line, col = self.line, self.col
            c = self.src[self.pos]

            if c.isalpha() or c == "_":
                tokens.append(self._read_word(line, col))
            elif c.isdigit():
                tokens.append(self._read_number(line, col))
            elif c == "%":
                tokens.append(self._read_address(line, col))
            elif c == "'" or c == '"':
                raise self._error("Zeichenketten werden nicht unterstuetzt")
            else:
                tokens.append(self._read_operator(line, col))

    # ------------------------------------------------------------------ #
    def _read_word(self, line: int, col: int) -> Token:
        start = self.pos
        while self.pos < len(self.src) and (self.src[self.pos].isalnum() or self.src[self.pos] == "_"):
            self._advance()
        word = self.src[start:self.pos]
        if word.upper() in ("T", "TIME") and self._peek() == "#":
            return self._read_time(line, col)
        return Token("id", word, line, col)

    def _read_time(self, line: int, col: int) -> Token:
        self._advance()  # '#'
        start = self.pos
        while self.pos < len(self.src) and self.src[self.pos].isdigit():
            self._advance()
        num = int(self.src[start:self.pos]) if self.pos > start else 0
        ustart = self.pos
        while self.pos < len(self.src) and self.src[self.pos].isalpha():
            self._advance()
        unit = self.src[ustart:self.pos].lower()
        factors = {
            "us": 0.001, "ns": 0.000001,
            "ms": 1.0, "s": 1000.0,
            "m": 60000.0, "h": 3600000.0,
            "d": 86400000.0,
        }
        if unit not in factors:
            raise self._error(f"Unbekannte Zeiteinheit '{unit}'")
        ms = int(round(num * factors[unit]))
        return Token("time", ms, line, col)

    def _read_number(self, line: int, col: int) -> Token:
        start = self.pos
        while self.pos < len(self.src) and self.src[self.pos].isdigit():
            self._advance()
        is_real = False
        if self._peek() == "." and self._peek(1).isdigit():
            is_real = True
            self._advance()
            while self.pos < len(self.src) and self.src[self.pos].isdigit():
                self._advance()
        text = self.src[start:self.pos]
        if is_real:
            return Token("real", float(text), line, col)
        return Token("int", int(text), line, col)

    def _read_address(self, line: int, col: int) -> Token:
        start = self.pos
        self._advance()  # '%'
        while self.pos < len(self.src) and (self.src[self.pos].isalnum() or self.src[self.pos] in "._"):
            self._advance()
        return Token("addr", self.src[start:self.pos], line, col)

    def _read_operator(self, line: int, col: int) -> Token:
        two = self.src[self.pos:self.pos + 2]
        if two in _TWO_CHAR_OPS:
            self._advance(2)
            return Token("op", two, line, col)
        one = self.src[self.pos]
        if one in _ONE_CHAR_OPS:
            self._advance()
            return Token("op", one, line, col)
        raise self._error(f"Unerwartetes Zeichen {one!r}")
