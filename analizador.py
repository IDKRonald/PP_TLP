#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analizador.py
Analizador (Lexer + Parser) para el DSL .brik (Snake/Tetris).

Características:
- Comentarios: // (línea) y /* ... */ (bloque)
- Parámetros simples: nombre = valor
- Parámetros compuestos (bloques): nombre { a = v, b = w, ... }
- Listas: a = [x1, x2, ..., xn] (valores: number, string, bool, listas anidadas)
- Mapeos tipo evento: izquierda -> derecha (p.ej., colision -> perder_vida)
- Comas entre entradas dentro de bloques (coma final opcional)
- Tipos: NUMBER (int/float), STRING ("..."), BOOL (true/false)

Salida:
- Imprime en stdout un AST en JSON.

Uso:
    python analizador.py archivo.brik
    python analizador.py archivo.brik --pretty
"""
from __future__ import annotations

import sys
import json
import re
from dataclasses import dataclass
from typing import Any, Optional, List, Dict
from pathlib import Path

# --------------------
# Tokens y errores
# --------------------

@dataclass
class Token:
    type: str
    value: Any
    line: int
    col: int

class LexerError(Exception):
    pass

class ParserError(Exception):
    pass

# --------------------
# Lexer
# --------------------

_re_ident  = re.compile(r'[a-z_][a-z0-9_]*', re.IGNORECASE)
_re_number = re.compile(r'-?[0-9]+(?:\.[0-9]+)?') # eñ -? es para permitir negativos 
_re_string = re.compile(r'"([^"\\]|\\.)*"')  # admite escapes \" \\ \n etc.

WHITESPACE = set(' \t\r\n')

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.i = 0
        self.n = len(text)
        self.line = 1
        self.col = 1

    def _peek(self, k: int=0) -> str:
        j = self.i + k
        return self.text[j] if 0 <= j < self.n else ''

    def _advance(self, count: int=1) -> None:
        for _ in range(count):
            if self.i >= self.n:
                return
            ch = self.text[self.i]
            self.i += 1
            if ch == '\n':
                self.line += 1
                self.col = 1
            else:
                self.col += 1

    def _skip_ws_and_comments(self) -> None:
        while True:
            # espacios
            moved = False
            while self._peek() and self._peek() in WHITESPACE:
                self._advance()
                moved = True
            # // comentario de línea
            if self._peek() == '/' and self._peek(1) == '/':
                while self._peek() and self._peek() != '\n':
                    self._advance()
                moved = True
                continue
            # /* comentario de bloque */
            if self._peek() == '/' and self._peek(1) == '*':
                start_line, start_col = self.line, self.col
                self._advance(2)
                while True:
                    if self.i >= self.n:
                        raise LexerError(f"Comentario de bloque sin cerrar iniciado en línea {start_line}, col {start_col}")
                    if self._peek() == '*' and self._peek(1) == '/':
                        self._advance(2)
                        break
                    self._advance()
                moved = True
                continue
            if not moved:
                break

    def next(self) -> Token:
        self._skip_ws_and_comments()
        if self.i >= self.n:
            return Token('EOF', None, self.line, self.col)

        ch = self._peek()

        # Unarios
        if ch == '{':
            tok = Token('LBRACE', '{', self.line, self.col); self._advance(); return tok
        if ch == '}':
            tok = Token('RBRACE', '}', self.line, self.col); self._advance(); return tok
        if ch == '[':
            tok = Token('LBRACK', '[', self.line, self.col); self._advance(); return tok
        if ch == ']':
            tok = Token('RBRACK', ']', self.line, self.col); self._advance(); return tok
        if ch == ',':
            tok = Token('COMMA', ',', self.line, self.col); self._advance(); return tok
        if ch == '=':
            tok = Token('EQUAL', '=', self.line, self.col); self._advance(); return tok

        # ->
        if ch == '-' and self._peek(1) == '>':
            tok = Token('ARROW', '->', self.line, self.col); self._advance(2); return tok

        # string
        m = _re_string.match(self.text, self.i)
        if m:
            raw = m.group(0)
            # decodifica secuencias de escape estándar
            value = bytes(raw[1:-1], 'utf-8').decode('unicode_escape')
            tok = Token('STRING', value, self.line, self.col)
            self._advance(len(raw))
            return tok

        # bool
        if self.text.startswith('true', self.i) and not self._is_ident_char(self._peek(4)):
            tok = Token('BOOL', True, self.line, self.col); self._advance(4); return tok
        if self.text.startswith('false', self.i) and not self._is_ident_char(self._peek(5)):
            tok = Token('BOOL', False, self.line, self.col); self._advance(5); return tok

        # number
        m = _re_number.match(self.text, self.i)
        if m:
            s = m.group(0)
            value = float(s) if '.' in s else int(s)
            tok = Token('NUMBER', value, self.line, self.col)
            self._advance(len(s))
            return tok

        # identifier
        m = _re_ident.match(self.text, self.i)
        if m:
            ident = m.group(0)
            tok = Token('IDENT', ident, self.line, self.col)
            self._advance(len(ident))
            return tok

        raise LexerError(f"Caracter inesperado '{ch}' en línea {self.line}, col {self.col}")

    def _is_ident_char(self, ch: str) -> bool:
        return bool(ch) and (ch.isalnum() or ch == '_')

# --------------------
# Parser
# --------------------

class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.cur: Token = self.lexer.next()

    def _eat(self, ttype: str) -> Token:
        if self.cur.type != ttype:
            self._error(f"Se esperaba {ttype}, se encontró {self.cur.type}")
        tok = self.cur
        self.cur = self.lexer.next()
        return tok

    def _accept(self, ttype: str) -> Optional[Token]:
        if self.cur.type == ttype:
            tok = self.cur
            self.cur = self.lexer.next()
            return tok
        return None

    def _error(self, msg: str) -> None:
        raise ParserError(f"{msg} (línea {self.cur.line}, col {self.cur.col})")

    def parse(self) -> Dict[str, Any]:
        doc: Dict[str, Any] = {}
        while self.cur.type != 'EOF':
            if self.cur.type != 'IDENT':
                self._error("Se esperaba un identificador al inicio de una declaración")
            name = self._eat('IDENT').value

            if self._accept('EQUAL'):
                value = self._parse_value()
                doc[name] = value
            elif self.cur.type == 'LBRACE':
                block = self._parse_block()
                if name in doc and isinstance(doc[name], dict) and isinstance(block, dict):
                    # merge simple
                    doc[name].update(block)
                elif name in doc:
                    self._error(f"Bloque duplicado '{name}' incompatible")
                else:
                    doc[name] = block
            else:
                self._error("Se esperaba '=' o '{' después del identificador")
        return doc

    # Bloque: { entry (, entry)* (,)? }
    def _parse_block(self) -> Dict[str, Any]:
        self._eat('LBRACE')
        entries: List[Any] = []
        while self.cur.type != 'RBRACE':
            entries.append(self._parse_entry())
            # Separador: coma opcional O inicio de una nueva entrada (IDENT) en la línea siguiente
            if self._accept('COMMA'):
                # permitir coma final
                if self.cur.type == 'RBRACE':
                    break
                continue
            # Si no hay coma, aceptamos que venga otra entrada directamente (IDENT) o cierre de bloque
            if self.cur.type in ('IDENT', 'RBRACE'):
                # continuar el ciclo (nueva entrada o cierre)
                continue
            # en cualquier otro caso, es error
            self._error("Se esperaba ',' o nuevo identificador o '}' en bloque")
        self._eat('RBRACE')

        # Reducir entries a un dict:
        # - asignaciones: {name: value}
        # - subbloques: {name: dict}
        # - mapeos: acumulados en clave especial "_mappings" como lista de pares
        result: Dict[str, Any] = {}
        mappings: List[Dict[str, str]] = []

        for e in entries:
            if e['type'] == 'assign':
                k = e['name']
                v = e['value']
                if k in result and isinstance(result[k], dict) and isinstance(v, dict):
                    result[k].update(v)
                elif k in result and not isinstance(result[k], list):
                    # Si ya existe y no es bloque repetible, sobreescribe
                    result[k] = v
                else:
                    result[k] = v
            elif e['type'] == 'block':
                k = e['name']
                v = e['value']
                if k in result and isinstance(result[k], dict):
                    result[k].update(v)
                elif k in result:
                    self._error(f"Entrada duplicada incompatible '{k}'")
                else:
                    result[k] = v
            elif e['type'] == 'map':
                mappings.append({'from': e['left'], 'to': e['right']})

        if mappings:
            result['_mappings'] = mappings
        return result

    # entry: IDENT '=' value
    #      | IDENT '{' ... '}'
    #      | IDENT '->' IDENT_OR_STRING
    def _parse_entry(self) -> Dict[str, Any]:
        if self.cur.type != 'IDENT':
            self._error("Se esperaba un identificador dentro del bloque")
        name = self._eat('IDENT').value

        # mapping
        if self._accept('ARROW'):
            right = self._parse_ident_or_string()
            return {'type': 'map', 'left': name, 'right': right}

        # assignment
        if self._accept('EQUAL'):
            val = self._parse_value()
            return {'type': 'assign', 'name': name, 'value': val}

        # nested block
        if self.cur.type == 'LBRACE':
            block = self._parse_block()
            return {'type': 'block', 'name': name, 'value': block}

        self._error("Se esperaba '->', '=' o '{' tras el identificador")

    def _parse_ident_or_string(self) -> str:
        if self.cur.type == 'IDENT':
            return self._eat('IDENT').value
        if self.cur.type == 'STRING':
            return self._eat('STRING').value
        self._error("Se esperaba un identificador o cadena")

    # value: STRING | NUMBER | BOOL | list | block
    def _parse_value(self) -> Any:
        t = self.cur.type
        if t == 'STRING':
            return self._eat('STRING').value
        if t == 'NUMBER':
            return self._eat('NUMBER').value
        if t == 'BOOL':
            return self._eat('BOOL').value
        if t == 'LBRACK':
            return self._parse_list()
        if t == 'LBRACE':
            return self._parse_block()
        self._error(f"Valor no válido (encontrado {t})")

    # list: '[' (value (',' value)*)? ']'
    def _parse_list(self) -> List[Any]:
        self._eat('LBRACK')
        items: List[Any] = []
        if self.cur.type != 'RBRACK':
            items.append(self._parse_value())
            while self._accept('COMMA'):
                if self.cur.type == 'RBRACK':  # coma final opcional
                    break
                items.append(self._parse_value())
        self._eat('RBRACK')
        return items

# --------------------
# CLI
# --------------------

def main(argv: List[str]) -> int:
    if len(argv) < 2:
        print("Uso: python analizador.py archivo.brik [--pretty]", file=sys.stderr)
        return 2
    path = argv[1]
    pretty = '--pretty' in argv[2:]

    try:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"No se pudo leer '{path}': {e}", file=sys.stderr)
        return 1

    try:
        lexer = Lexer(text)
        parser = Parser(lexer)
        ast = parser.parse()
    except (LexerError, ParserError) as e:
        print(f"Error de análisis: {e}", file=sys.stderr)
        return 1

    # Guardar siempre el AST en un archivo 'arbol.ast' junto al .brik
    out_path = Path(path).with_name('arbol.ast')
    try:
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(ast, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"No se pudo escribir '{out_path}': {e}", file=sys.stderr)
        return 1

    if pretty:
        print(json.dumps(ast, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(ast, ensure_ascii=False, separators=(',', ':')))
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
