"""
Ensamblador MIPS Simplificado — Convierte texto ensamblador a instrucciones binarias.

Soporta: ADD, SUB, AND, OR, NOR, XOR, SLT, ADDI, ORI, ANDI, SLTI, LUI,
         LW, SW, BEQ, BNE, J, JAL, NOP, MOVE (pseudo)

Procesador Monociclo MIPS
Autores: Andres Felipe Mogollon España, Juan Esteban Bedoya, Michael Hurtado
Profesor: David Andres Romero Arenas
"""

from __future__ import annotations
import re
from dataclasses import dataclass


@dataclass
class AssemblerError(Exception):
    line: int
    text: str
    message: str

    def __str__(self) -> str:
        return f"[Línea {self.line}] Error en '{self.text}': {self.message}"


# ── Tablas de registros ──────────────────────────────────────────────────────

_REG_MAP: dict[str, int] = {
    "$zero":0, "$0":0,
    "$at":1,   "$1":1,
    "$v0":2,   "$v1":3,
    "$a0":4,   "$a1":5,   "$a2":6,   "$a3":7,
    "$t0":8,   "$t1":9,   "$t2":10,  "$t3":11,
    "$t4":12,  "$t5":13,  "$t6":14,  "$t7":15,
    "$s0":16,  "$s1":17,  "$s2":18,  "$s3":19,
    "$s4":20,  "$s5":21,  "$s6":22,  "$s7":23,
    "$t8":24,  "$t9":25,
    "$k0":26,  "$k1":27,
    "$gp":28,  "$sp":29,  "$fp":30,  "$ra":31,
}
# Soporte numérico: $0..$31
for _i in range(32):
    _REG_MAP[f"${_i}"] = _i


def _reg(name: str) -> int:
    """Convierte nombre de registro a número."""
    n = name.strip().lower()
    if n not in _REG_MAP:
        raise ValueError(f"Registro desconocido: '{name}'")
    return _REG_MAP[n]


def _imm(val: str, bits: int, signed: bool = True) -> int:
    """Convierte una cadena inmediata y valida su rango."""
    v = int(val.strip(), 0)
    lo = -(1 << (bits - 1)) if signed else 0
    hi = (1 << (bits - 1)) - 1 if signed else (1 << bits) - 1
    if not (lo <= v <= hi):
        raise ValueError(f"Inmediato {v} fuera de rango [{lo}, {hi}] ({bits} bits)")
    return v & ((1 << bits) - 1)


# ── Encoders por formato ──────────────────────────────────────────────────────

def _r(op: int, rs: int, rt: int, rd: int, sh: int, fn: int) -> int:
    return ((op & 0x3F) << 26 | (rs & 0x1F) << 21 | (rt & 0x1F) << 16 |
            (rd & 0x1F) << 11 | (sh & 0x1F) << 6  | (fn & 0x3F))


def _i(op: int, rs: int, rt: int, imm: int) -> int:
    return ((op & 0x3F) << 26 | (rs & 0x1F) << 21 |
            (rt & 0x1F) << 16 | (imm & 0xFFFF))


def _j(op: int, addr: int) -> int:
    return ((op & 0x3F) << 26 | (addr & 0x03FF_FFFF))


# ── Tabla de instrucciones ────────────────────────────────────────────────────
# Formato: "MNEMÓNICO": (tipo, opcode, funct_o_extra)
# tipo: "R", "I_rt_rs_imm", "I_rt_rs_off", "I_rs_rt_off", "J", "PSEUDO"

_INSTR: dict[str, tuple] = {
    # R-type                   op     funct
    "add":  ("R",   0x00, 0x20),
    "addu": ("R",   0x00, 0x21),
    "sub":  ("R",   0x00, 0x22),
    "and":  ("R",   0x00, 0x24),
    "or":   ("R",   0x00, 0x25),
    "xor":  ("R",   0x00, 0x26),
    "nor":  ("R",   0x00, 0x27),
    "slt":  ("R",   0x00, 0x2A),
    # I-type (rt, rs, imm)
    "addi": ("Irt", 0x08, None),
    "andi": ("Irt", 0x0C, None),
    "ori":  ("Irt", 0x0D, None),
    "slti": ("Irt", 0x0A, None),
    "lui":  ("Lui", 0x0F, None),   # lui rt, imm  (rs=0)
    # I-type memory (rt, imm(rs))
    "lw":   ("Imem",0x23, None),
    "sw":   ("Imem",0x2B, None),
    # I-type branch (rs, rt, label/offset)
    "beq":  ("Ibr", 0x04, None),
    "bne":  ("Ibr", 0x05, None),
    # J-type
    "j":    ("J",   0x02, None),
    "jal":  ("J",   0x03, None),
    # Pseudo
    "nop":  ("NOP", None, None),
    "move": ("MOVE",None, None),  # move rd, rs  →  add rd, $zero, rs
    "li":   ("LI",  None, None),  # li  rt, imm  →  addi rt, $zero, imm
    "la":   ("LA",  None, None),  # la  rt, label  (simplified: addi rt, $zero, addr)
}


class Assembler:
    """
    Ensamblador MIPS de dos pasadas.

    Primera pasada: recolecta etiquetas y sus direcciones.
    Segunda pasada: genera código binario resolviendo referencias.
    """

    def assemble(self, source: str) -> list[int]:
        """
        Ensambla el texto fuente y devuelve lista de instrucciones binarias.

        Args:
            source: Código ensamblador como texto multilínea.

        Returns:
            Lista de enteros de 32 bits.

        Raises:
            AssemblerError en caso de error de sintaxis.
        """
        lines = self._clean(source)
        labels, code_lines = self._first_pass(lines)
        return self._second_pass(code_lines, labels)

    # ─── Primera pasada ──────────────────────────────────────────────────

    def _first_pass(
        self, lines: list[tuple[int, str]]
    ) -> tuple[dict[str, int], list[tuple[int, str]]]:
        """Identifica etiquetas y devuelve líneas de código puras."""
        labels: dict[str, int] = {}
        code:   list[tuple[int, str]] = []
        pc = 0

        for lineno, text in lines:
            # Separar etiqueta del resto
            if ":" in text:
                parts = text.split(":", 1)
                lbl = parts[0].strip()
                rest = parts[1].strip()
                if lbl:
                    labels[lbl] = pc
                if rest:
                    code.append((lineno, rest))
                    pc += 4
            else:
                code.append((lineno, text))
                pc += 4

        return labels, code

    # ─── Segunda pasada ──────────────────────────────────────────────────

    def _second_pass(
        self,
        lines: list[tuple[int, str]],
        labels: dict[str, int],
    ) -> list[int]:
        instructions: list[int] = []
        pc = 0

        for lineno, text in lines:
            try:
                instr = self._encode_line(text, labels, pc)
                instructions.append(instr)
                pc += 4
            except (ValueError, IndexError) as exc:
                raise AssemblerError(lineno, text, str(exc))

        return instructions

    # ─── Encoder de línea ────────────────────────────────────────────────

    def _encode_line(self, text: str, labels: dict[str, int], pc: int) -> int:
        tokens = re.split(r"[\s,()]+", text.strip())
        tokens = [t for t in tokens if t]
        mnem = tokens[0].lower()

        if mnem not in _INSTR:
            raise ValueError(f"Instrucción desconocida: '{mnem}'")

        kind, opcode, funct = _INSTR[mnem]

        match kind:
            case "R":
                rd, rs, rt = _reg(tokens[1]), _reg(tokens[2]), _reg(tokens[3])
                return _r(opcode, rs, rt, rd, 0, funct)

            case "Irt":   # addi rt, rs, imm
                rt = _reg(tokens[1])
                rs = _reg(tokens[2])
                im = _imm(tokens[3], 16, signed=True)
                return _i(opcode, rs, rt, im)

            case "Lui":   # lui rt, imm
                rt = _reg(tokens[1])
                im = _imm(tokens[2], 16, signed=False)
                return _i(opcode, 0, rt, im)

            case "Imem":  # lw/sw rt, imm(rs)   →  tokens: mnem rt imm rs
                rt = _reg(tokens[1])
                im = _imm(tokens[2], 16, signed=True)
                rs = _reg(tokens[3])
                return _i(opcode, rs, rt, im)

            case "Ibr":   # beq/bne rs, rt, label
                rs = _reg(tokens[1])
                rt = _reg(tokens[2])
                target = self._resolve_label(tokens[3], labels)
                offset = ((target - (pc + 4)) >> 2) & 0xFFFF
                return _i(opcode, rs, rt, offset)

            case "J":
                target = self._resolve_label(tokens[1], labels)
                return _j(opcode, target >> 2)

            case "NOP":
                return 0x0000_0000

            case "MOVE":  # move rd, rs  →  add rd, $zero, rs
                rd = _reg(tokens[1])
                rs = _reg(tokens[2])
                return _r(0x00, rs, 0, rd, 0, 0x20)

            case "LI":    # li rt, imm  →  addi rt, $zero, imm
                rt = _reg(tokens[1])
                im = _imm(tokens[2], 16, signed=True)
                return _i(0x08, 0, rt, im)

            case "LA":    # la rt, label  →  addi rt, $zero, addr (simplificado)
                rt = _reg(tokens[1])
                target = self._resolve_label(tokens[2], labels)
                return _i(0x08, 0, rt, target & 0xFFFF)

            case _:
                raise ValueError(f"Tipo de instrucción no manejado: {kind}")

    # ─── Utilidades ──────────────────────────────────────────────────────

    @staticmethod
    def _clean(source: str) -> list[tuple[int, str]]:
        """Elimina comentarios y líneas vacías. Devuelve (lineno, texto)."""
        result = []
        for i, line in enumerate(source.splitlines(), start=1):
            line = re.sub(r"#.*$", "", line).strip()   # remover comentarios
            line = re.sub(r";.*$", "", line).strip()
            if line:
                result.append((i, line))
        return result

    @staticmethod
    def _resolve_label(token: str, labels: dict[str, int]) -> int:
        """Resuelve etiqueta o literal numérico a entero."""
        token = token.strip()
        if token in labels:
            return labels[token]
        try:
            return int(token, 0)
        except ValueError:
            raise ValueError(f"Etiqueta no definida: '{token}'")
