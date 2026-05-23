"""
Banco de Registros — 32 registros de 32 bits estilo MIPS.
Procesador Monociclo | Ingeniería de Sistemas — Unidad 4
"""

from typing import Iterator


# Nombres convencionales MIPS de los 32 registros
REGISTER_NAMES: dict[int, str] = {
    0:  "$zero", 1:  "$at",
    2:  "$v0",   3:  "$v1",
    4:  "$a0",   5:  "$a1",   6:  "$a2",   7:  "$a3",
    8:  "$t0",   9:  "$t1",   10: "$t2",   11: "$t3",
    12: "$t4",   13: "$t5",   14: "$t6",   15: "$t7",
    16: "$s0",   17: "$s1",   18: "$s2",   19: "$s3",
    20: "$s4",   21: "$s5",   22: "$s6",   23: "$s7",
    24: "$t8",   25: "$t9",
    26: "$k0",   27: "$k1",
    28: "$gp",   29: "$sp",   30: "$fp",   31: "$ra",
}


class RegisterBankError(Exception):
    """Error base del banco de registros."""


class RegisterBank:
    """
    Banco de 32 registros de 32 bits (MIPS).

    Reglas:
        - $zero (R0) es siempre 0 y no puede modificarse.
        - Lecturas son combinacionales (sin latencia).
        - Escritura se realiza al flanco de reloj (método write).

    Responsabilidades:
        - Proveer lectura dual (rs y rt simultáneamente)
        - Permitir escritura controlada por señal RegWrite
        - Mantener el invariante $zero == 0
    """

    SIZE = 32
    MASK = 0xFFFF_FFFF

    def __init__(self):
        self._registers: list[int] = [0] * self.SIZE

    # ─── Interfaz pública ──────────────────────────────────────────────

    def read(self, reg: int) -> int:
        """Lee un registro. R0 siempre devuelve 0."""
        self._validate_index(reg)
        return self._registers[reg]

    def write(self, reg: int, value: int, *, reg_write: bool = True) -> None:
        """
        Escribe en un registro si reg_write está activo.

        Args:
            reg: Índice del registro destino (1–31).
            value: Valor a escribir (se trunca a 32 bits).
            reg_write: Señal de control RegWrite.
        """
        if not reg_write:
            return
        self._validate_index(reg)
        if reg == 0:
            return  # $zero es de solo lectura (se ignora silenciosamente)
        self._registers[reg] = value & self.MASK

    def read_dual(self, rs: int, rt: int) -> tuple[int, int]:
        """Lee dos registros simultáneamente (salidas del banco en ID)."""
        return self.read(rs), self.read(rt)

    def reset(self) -> None:
        """Limpia todos los registros a cero."""
        self._registers = [0] * self.SIZE

    # ─── Introspección ─────────────────────────────────────────────────

    def dump(self) -> dict[str, int]:
        """Devuelve un snapshot {nombre: valor} para la GUI."""
        return {REGISTER_NAMES[i]: self._registers[i] for i in range(self.SIZE)}

    def __iter__(self) -> Iterator[tuple[str, int]]:
        for i in range(self.SIZE):
            yield REGISTER_NAMES[i], self._registers[i]

    def __repr__(self) -> str:
        lines = [f"  {REGISTER_NAMES[i]:6s} ({i:2d}): {self._registers[i]:#010x}"
                 for i in range(self.SIZE)]
        return "RegisterBank:\n" + "\n".join(lines)

    # ─── Privado ────────────────────────────────────────────────────────

    def _validate_index(self, reg: int) -> None:
        if not (0 <= reg < self.SIZE):
            raise RegisterBankError(f"Índice de registro inválido: {reg}")
