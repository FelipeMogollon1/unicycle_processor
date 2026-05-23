"""
Unidad de Control — Decodifica el opcode y genera todas las señales de control.
Procesador Monociclo MIPS
"""

from dataclasses import dataclass
from enum import IntEnum


class Opcode(IntEnum):
    """Opcodes MIPS principales."""
    R_TYPE  = 0b000000  # 0x00 — ADD, SUB, AND, OR, SLT
    ADDI    = 0b001000  # 0x08
    LW      = 0b100011  # 0x23
    SW      = 0b101011  # 0x2B
    BEQ     = 0b000100  # 0x04
    BNE     = 0b000101  # 0x05
    J       = 0b000010  # 0x02
    JAL     = 0b000011  # 0x03
    ORI     = 0b001101  # 0x0D
    ANDI    = 0b001100  # 0x0C
    SLTI    = 0b001010  # 0x0A
    LUI     = 0b001111  # 0x0F


class Funct(IntEnum):
    """Códigos de función para instrucciones R-type."""
    ADD  = 0b100000  # 0x20
    ADDU = 0b100001  # 0x21
    SUB  = 0b100010  # 0x22
    AND  = 0b100100  # 0x24
    OR   = 0b100101  # 0x25
    XOR  = 0b100110  # 0x26
    NOR  = 0b100111  # 0x27
    SLT  = 0b101010  # 0x2A
    SLL  = 0b000000  # 0x00
    SRL  = 0b000010  # 0x02
    JR   = 0b001000  # 0x08


@dataclass
class ControlSignals:
    """
    Conjunto completo de señales de control generadas por la Unidad de Control.

    Cada señal es un bit (bool) o un código de 2 bits (int) según la arquitectura.
    """
    reg_dst:    bool  # 0=rt destino, 1=rd destino
    alu_src:    bool  # 0=registro B, 1=inmediato extendido
    mem_to_reg: bool  # 0=ALU result, 1=dato de memoria
    reg_write:  bool  # 1=habilita escritura en banco de registros
    mem_read:   bool  # 1=habilita lectura de memoria de datos
    mem_write:  bool  # 1=habilita escritura en memoria de datos
    branch:     bool  # 1=instrucción de salto condicional
    jump:       bool  # 1=salto incondicional J/JAL
    alu_op:     int   # 2 bits: 00=LW/SW, 01=BEQ, 10=R-type, 11=I-type
    alu_control: int  # 3 bits: operación específica de la ALU

    def to_dict(self) -> dict[str, int | bool]:
        """Serializa las señales a diccionario para la GUI."""
        return {
            "RegDst":    int(self.reg_dst),
            "ALUSrc":    int(self.alu_src),
            "MemToReg":  int(self.mem_to_reg),
            "RegWrite":  int(self.reg_write),
            "MemRead":   int(self.mem_read),
            "MemWrite":  int(self.mem_write),
            "Branch":    int(self.branch),
            "Jump":      int(self.jump),
            "ALUOp":     self.alu_op,
            "ALUControl":self.alu_control,
        }


class ControlUnit:
    """
    Unidad de Control del procesador monociclo.

    Implementa la lógica combinacional que, dado el opcode (y funct para R-type),
    genera el vector de señales de control para el ciclo completo.

    Responsabilidades:
        - Decodificar opcode
        - Determinar ALUControl (tabla de verdad de la ALU)
        - Generar todas las señales del datapath
    """

    # Tabla: opcode → (reg_dst, alu_src, mem_to_reg, reg_write,
    #                   mem_read, mem_write, branch, jump, alu_op)
    _CONTROL_TABLE: dict[int, tuple] = {
        Opcode.R_TYPE: (True,  False, False, True,  False, False, False, False, 0b10),
        Opcode.ADDI:   (False, True,  False, True,  False, False, False, False, 0b11),
        Opcode.LW:     (False, True,  True,  True,  True,  False, False, False, 0b00),
        Opcode.SW:     (False, True,  False, False, False, True,  False, False, 0b00),
        Opcode.BEQ:    (False, False, False, False, False, False, True,  False, 0b01),
        Opcode.BNE:    (False, False, False, False, False, False, True,  False, 0b01),
        Opcode.J:      (False, False, False, False, False, False, False, True,  0b00),
        Opcode.JAL:    (False, False, False, True,  False, False, False, True,  0b00),
        Opcode.ORI:    (False, True,  False, True,  False, False, False, False, 0b11),
        Opcode.ANDI:   (False, True,  False, True,  False, False, False, False, 0b11),
        Opcode.SLTI:   (False, True,  False, True,  False, False, False, False, 0b11),
        Opcode.LUI:    (False, True,  False, True,  False, False, False, False, 0b11),
    }

    # Tabla funct → ALUControl (solo para R-type, alu_op=10)
    _FUNCT_TO_ALU: dict[int, int] = {
        Funct.ADD:  0b010,
        Funct.ADDU: 0b010,
        Funct.SUB:  0b110,
        Funct.AND:  0b000,
        Funct.OR:   0b001,
        Funct.XOR:  0b101,
        Funct.NOR:  0b100,
        Funct.SLT:  0b111,
    }

    # Tabla opcode → ALUControl (para instrucciones I-type, alu_op=11)
    _ITYPE_TO_ALU: dict[int, int] = {
        Opcode.ADDI: 0b010,
        Opcode.LW:   0b010,
        Opcode.SW:   0b010,
        Opcode.BEQ:  0b110,
        Opcode.BNE:  0b110,
        Opcode.ORI:  0b001,
        Opcode.ANDI: 0b000,
        Opcode.SLTI: 0b111,
        Opcode.LUI:  0b010,
    }

    def decode(self, opcode: int, funct: int = 0) -> ControlSignals:
        """
        Genera el vector de señales de control.

        Args:
            opcode: 6 bits superiores de la instrucción.
            funct:  6 bits inferiores (solo relevantes en R-type).

        Returns:
            ControlSignals con todas las señales activas.

        Raises:
            ValueError si el opcode no está soportado.
        """
        if opcode not in self._CONTROL_TABLE:
            raise ValueError(f"Opcode no soportado: {opcode:#08b} ({opcode:#04x})")

        (reg_dst, alu_src, mem_to_reg, reg_write,
         mem_read, mem_write, branch, jump, alu_op) = self._CONTROL_TABLE[opcode]

        alu_control = self._resolve_alu_control(opcode, funct, alu_op)

        return ControlSignals(
            reg_dst=reg_dst, alu_src=alu_src, mem_to_reg=mem_to_reg,
            reg_write=reg_write, mem_read=mem_read, mem_write=mem_write,
            branch=branch, jump=jump, alu_op=alu_op, alu_control=alu_control,
        )

    def _resolve_alu_control(self, opcode: int, funct: int, alu_op: int) -> int:
        """Determina el código final de 3 bits para la ALU."""
        if alu_op == 0b10:   # R-type: usar tabla funct
            return self._FUNCT_TO_ALU.get(funct, 0b010)
        elif alu_op == 0b01: # BEQ/BNE: siempre SUB
            return 0b110
        elif alu_op == 0b00: # LW/SW: siempre ADD
            return 0b010
        else:                # I-type ALU
            return self._ITYPE_TO_ALU.get(opcode, 0b010)
