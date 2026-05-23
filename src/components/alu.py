"""
ALU - Unidad Aritmético Lógica
Procesador Monociclo MIPS
Autores: Andres Felipe Mogollon España, Juan Esteban Bedoya, Michael Hurtado
Profesor: David Andres Romero Arenas
"""

from dataclasses import dataclass
from enum import IntEnum


class ALUOp(IntEnum):
    """Códigos de operación de la ALU (señal ALUControl de 3 bits)."""
    AND  = 0b000
    OR   = 0b001
    ADD  = 0b010
    SUB  = 0b110
    SLT  = 0b111
    NOR  = 0b100
    XOR  = 0b101


@dataclass
class ALUResult:
    """Resultado de una operación ALU."""
    value: int          # Resultado de 32 bits
    zero: bool          # Señal Zero (usado para BEQ)
    overflow: bool      # Señal de desbordamiento
    negative: bool      # Señal negativa


class ALU:
    """
    Unidad Aritmético-Lógica de 32 bits.

    Recibe dos operandos (A, B) y una señal de control (ALUControl)
    y produce un resultado de 32 bits junto con señales de estado.

    Responsabilidades:
        - Ejecutar operaciones aritméticas y lógicas
        - Generar señal Zero para instrucciones de salto
        - Detectar overflow en operaciones con signo
    """

    MASK_32 = 0xFFFF_FFFF  # Máscara 32 bits

    def __init__(self):
        self._last_result: ALUResult | None = None

    @property
    def last_result(self) -> ALUResult | None:
        """Último resultado calculado (para depuración)."""
        return self._last_result

    def execute(self, operand_a: int, operand_b: int, alu_control: int) -> ALUResult:
        """
        Ejecuta la operación indicada por alu_control.

        Args:
            operand_a: Primer operando (32 bits, con signo)
            operand_b: Segundo operando (32 bits, con signo)
            alu_control: Código de operación (3 bits)

        Returns:
            ALUResult con value, zero, overflow, negative
        """
        a = self._to_signed32(operand_a)
        b = self._to_signed32(operand_b)
        overflow = False

        match alu_control:
            case ALUOp.AND:
                raw = a & b
            case ALUOp.OR:
                raw = a | b
            case ALUOp.ADD:
                raw = a + b
                overflow = self._check_overflow(a, b, raw)
            case ALUOp.SUB:
                raw = a - b
                overflow = self._check_overflow(a, -b, raw)
            case ALUOp.SLT:
                raw = 1 if a < b else 0
            case ALUOp.NOR:
                raw = ~(a | b)
            case ALUOp.XOR:
                raw = a ^ b
            case _:
                raise ValueError(f"ALUControl desconocido: {alu_control:#05b}")

        value = raw & self.MASK_32
        result = ALUResult(
            value=value,
            zero=(value == 0),
            overflow=overflow,
            negative=bool(value >> 31),
        )
        self._last_result = result
        return result

    # ─── Utilidades privadas ────────────────────────────────────────────

    def _to_signed32(self, val: int) -> int:
        """Convierte un entero a representación con signo de 32 bits."""
        val &= self.MASK_32
        return val - 0x1_0000_0000 if val >= 0x8000_0000 else val

    @staticmethod
    def _check_overflow(a: int, b: int, result: int) -> bool:
        """Detecta overflow en suma con signo."""
        return (a > 0 and b > 0 and result < 0) or \
               (a < 0 and b < 0 and result > 0)
