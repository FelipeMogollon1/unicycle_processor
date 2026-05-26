"""
Decodificador de Instrucciones — Descompone los 32 bits de una instrucción MIPS.
Procesador Monociclo
"""

from dataclasses import dataclass
from enum import Enum


class InstructionType(Enum):
    R = "R-type"
    I = "I-type"
    J = "J-type"
    UNKNOWN = "Unknown"


@dataclass
class DecodedInstruction:
    """
    Campos decodificados de una instrucción MIPS de 32 bits.

    R-type: | opcode(6) | rs(5) | rt(5) | rd(5) | shamt(5) | funct(6) |
    I-type: | opcode(6) | rs(5) | rt(5) | imm(16)                      |
    J-type: | opcode(6) | address(26)                                   |
    """
    raw: int               # Instrucción original (32 bits)
    opcode: int            # bits [31:26]
    rs: int                # bits [25:21]
    rt: int                # bits [20:16]
    rd: int                # bits [15:11]
    shamt: int             # bits [10:6]
    funct: int             # bits [5:0]
    imm: int               # bits [15:0] — sin extensión de signo
    imm_signed: int        # imm extendido con signo (32 bits)
    jump_addr: int         # bits [25:0] — dirección de salto J-type
    instr_type: InstructionType
    mnemonic: str = ""     # Texto legible, ej. "ADD $t0, $t1, $t2"

    def __str__(self) -> str:
        return (
            f"[{self.raw:#010x}] {self.instr_type.value:7s} | "
            f"op={self.opcode:#08b} rs={self.rs:2d} rt={self.rt:2d} "
            f"rd={self.rd:2d} shamt={self.shamt} funct={self.funct:#08b} "
            f"imm={self.imm_signed} | {self.mnemonic}"
        )


class InstructionDecoder:
    """
    Decodificador combinacional de instrucciones MIPS de 32 bits.

    Separa cada campo de la instrucción y determina su tipo.
    También realiza extensión de signo del inmediato.

    Responsabilidades:
        - Extraer campos bit a bit
        - Clasificar la instrucción (R/I/J)
        - Extender signo del inmediato de 16 a 32 bits
        - Generar texto legible (mnemónico)
    """

    # Opcodes J-type
    J_OPCODES = {0b000010, 0b000011}  # J, JAL

    def decode(self, instruction: int) -> DecodedInstruction:
        """
        Descompone una instrucción de 32 bits en sus campos.

        Args:
            instruction: Valor entero sin signo de 32 bits.

        Returns:
            DecodedInstruction con todos los campos.
        """
        instruction &= 0xFFFF_FFFF

        opcode    = (instruction >> 26) & 0x3F
        rs        = (instruction >> 21) & 0x1F
        rt        = (instruction >> 16) & 0x1F
        rd        = (instruction >> 11) & 0x1F
        shamt     = (instruction >>  6) & 0x1F
        funct     =  instruction        & 0x3F
        imm       =  instruction        & 0xFFFF
        jump_addr =  instruction        & 0x03FF_FFFF

        imm_signed = imm if imm < 0x8000 else imm - 0x10000

        # Clasificar tipo
        if opcode == 0:
            instr_type = InstructionType.R
        elif opcode in self.J_OPCODES:
            instr_type = InstructionType.J
        elif opcode != 0:
            instr_type = InstructionType.I
        else:
            instr_type = InstructionType.UNKNOWN

        decoded = DecodedInstruction(
            raw=instruction, opcode=opcode,
            rs=rs, rt=rt, rd=rd,
            shamt=shamt, funct=funct,
            imm=imm, imm_signed=imm_signed,
            jump_addr=jump_addr,
            instr_type=instr_type,
        )
        decoded.mnemonic = self._build_mnemonic(decoded)
        return decoded

    @staticmethod
    def _build_mnemonic(d: DecodedInstruction) -> str:
        """Genera texto legible de la instrucción."""
        from src.control.control_unit import Opcode, Funct
        from src.components.register_bank import REGISTER_NAMES as RN

        r = lambda n: RN.get(n, f"${n}")

        try:
            op = Opcode(d.opcode)
        except ValueError:
            return f"UNKNOWN(op={d.opcode:#04x})"

        match op:
            case Opcode.R_TYPE:
                try:
                    fn = Funct(d.funct)
                    name = fn.name
                except ValueError:
                    name = f"FUNCT{d.funct}"
                return f"{name} {r(d.rd)}, {r(d.rs)}, {r(d.rt)}"
            case Opcode.ADDI:
                return f"ADDI {r(d.rt)}, {r(d.rs)}, {d.imm_signed}"
            case Opcode.LW:
                return f"LW {r(d.rt)}, {d.imm_signed}({r(d.rs)})"
            case Opcode.SW:
                return f"SW {r(d.rt)}, {d.imm_signed}({r(d.rs)})"
            case Opcode.BEQ:
                return f"BEQ {r(d.rs)}, {r(d.rt)}, {d.imm_signed}"
            case Opcode.BNE:
                return f"BNE {r(d.rs)}, {r(d.rt)}, {d.imm_signed}"
            case Opcode.J:
                return f"J {d.jump_addr:#010x}"
            case Opcode.JAL:
                return f"JAL {d.jump_addr:#010x}"
            case Opcode.ORI:
                return f"ORI {r(d.rt)}, {r(d.rs)}, {d.imm:#06x}"
            case Opcode.ANDI:
                return f"ANDI {r(d.rt)}, {r(d.rs)}, {d.imm:#06x}"
            case Opcode.LUI:
                return f"LUI {r(d.rt)}, {d.imm:#06x}"
            case _:
                return f"OP({d.opcode:#04x})"
