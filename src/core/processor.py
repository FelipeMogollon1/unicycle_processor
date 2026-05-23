"""
Procesador Monociclo — Orquestador del ciclo completo de ejecución.

Implementa el ciclo: IF → ID → EX → MEM → WB en una sola pasada por ciclo.

Procesador Monociclo MIPS
Autores: Andres Felipe Mogollon España, Juan Esteban Bedoya, Michael Hurtado
Profesor: David Andres Romero Arenas
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable

from src.components.alu import ALU, ALUResult
from src.components.register_bank import RegisterBank
from src.components.instruction_decoder import InstructionDecoder, DecodedInstruction
from src.control.control_unit import ControlUnit, ControlSignals
from src.core.program_counter import ProgramCounter
from src.memory.memory import InstructionMemory, DataMemory


@dataclass
class CycleSnapshot:
    """
    Captura completa del estado del procesador en un ciclo.
    Utilizada por la GUI para visualizar cada etapa.
    """
    cycle_number:    int
    pc:              int
    raw_instruction: int
    decoded:         DecodedInstruction | None = None
    signals:         ControlSignals     | None = None
    alu_result:      ALUResult          | None = None
    mem_data:        int                = 0
    write_back:      int                = 0
    write_reg:       int                = 0
    registers:       dict               = field(default_factory=dict)
    memory_changes:  list               = field(default_factory=list)
    stage:           str                = "IF"  # IF|ID|EX|MEM|WB|HALT

    def __str__(self) -> str:
        lines = [
            f"─── Ciclo #{self.cycle_number} ───────────────────────",
            f"  PC          : {self.pc:#010x}",
            f"  Instrucción : {self.raw_instruction:#010x}",
        ]
        if self.decoded:
            lines.append(f"  Mnemónico   : {self.decoded.mnemonic}")
            lines.append(f"  Tipo        : {self.decoded.instr_type.value}")
        if self.signals:
            lines.append(f"  Señales     : {self.signals.to_dict()}")
        if self.alu_result:
            lines.append(f"  ALU Result  : {self.alu_result.value:#010x}  "
                         f"Zero={self.alu_result.zero}")
        if self.write_reg:
            lines.append(f"  Write Back  : R{self.write_reg} ← {self.write_back:#010x}")
        return "\n".join(lines)


class ProcessorHaltError(Exception):
    """Se lanza cuando el procesador llega a una instrucción NOP o dirección inválida."""


class MonocycleProcessor:
    """
    Procesador Monociclo MIPS de 32 bits.

    Ejecuta instrucciones tipo R, I y J en un único ciclo de reloj cada una.
    Soporta ejecución paso a paso y modo automático.

    Señales implementadas:
        RegDst, ALUSrc, MemToReg, RegWrite, MemRead, MemWrite, Branch, Jump

    Instrucciones soportadas:
        R-type: ADD, SUB, AND, OR, SLT, NOR, XOR
        I-type: ADDI, LW, SW, BEQ, BNE, ORI, ANDI, SLTI, LUI
        J-type: J, JAL
    """

    def __init__(self):
        self.pc          = ProgramCounter()
        self.registers   = RegisterBank()
        self.inst_mem    = InstructionMemory()
        self.data_mem    = DataMemory()
        self.alu         = ALU()
        self.decoder     = InstructionDecoder()
        self.control     = ControlUnit()

        self._cycle:    int  = 0
        self._halted:   bool = False
        self._log:      list[CycleSnapshot] = []

        # Callbacks opcionales para la GUI
        self.on_cycle_complete: Callable[[CycleSnapshot], None] | None = None

    # ─── API pública ────────────────────────────────────────────────────

    def load_program(self, instructions: list[int]) -> None:
        """Carga instrucciones en la memoria y reinicia el procesador."""
        self.inst_mem.load_program(instructions)
        self.reset()

    def step(self) -> CycleSnapshot:
        """
        Ejecuta UN ciclo completo: IF → ID → EX → MEM → WB.

        Returns:
            CycleSnapshot con el estado completo del ciclo.

        Raises:
            ProcessorHaltError si el procesador está detenido.
        """
        if self._halted:
            raise ProcessorHaltError("El procesador está detenido (HALT).")

        snapshot = CycleSnapshot(
            cycle_number=self._cycle,
            pc=self.pc.value,
            raw_instruction=0,
        )

        try:
            # ── IF: Instruction Fetch ────────────────────────────────
            snapshot.stage = "IF"
            raw = self.inst_mem.fetch(self.pc.value)
            snapshot.raw_instruction = raw
            pc_plus_4 = self.pc.next_sequential()

            if raw == 0:  # NOP al final del programa
                snapshot.stage = "HALT"
                self._halted = True
                self._commit_snapshot(snapshot)
                return snapshot

            # ── ID: Instruction Decode ────────────────────────────────
            snapshot.stage = "ID"
            decoded = self.decoder.decode(raw)
            snapshot.decoded = decoded

            signals = self.control.decode(decoded.opcode, decoded.funct)
            snapshot.signals = signals

            read_data1, read_data2 = self.registers.read_dual(decoded.rs, decoded.rt)

            # ── EX: Execute ───────────────────────────────────────────
            snapshot.stage = "EX"
            alu_b = decoded.imm_signed if signals.alu_src else read_data2
            alu_result = self.alu.execute(read_data1, alu_b, signals.alu_control)
            snapshot.alu_result = alu_result

            # ── MEM: Memory Access ────────────────────────────────────
            snapshot.stage = "MEM"
            mem_data = self.data_mem.read(
                alu_result.value, mem_read=signals.mem_read
            )
            self.data_mem.write(
                alu_result.value, read_data2, mem_write=signals.mem_write
            )
            snapshot.mem_data = mem_data

            if signals.mem_write:
                snapshot.memory_changes.append(
                    (alu_result.value, read_data2)
                )

            # ── WB: Write Back ────────────────────────────────────────
            snapshot.stage = "WB"
            write_data = mem_data if signals.mem_to_reg else alu_result.value
            write_reg  = decoded.rd if signals.reg_dst else decoded.rt

            # JAL guarda PC+4 en $ra (R31)
            if decoded.opcode == 0b000011:  # JAL
                self.registers.write(31, pc_plus_4, reg_write=True)

            self.registers.write(write_reg, write_data, reg_write=signals.reg_write)
            snapshot.write_back = write_data
            snapshot.write_reg  = write_reg
            snapshot.registers  = self.registers.dump()

            # ── PC Update ─────────────────────────────────────────────
            self._update_pc(signals, decoded, alu_result, pc_plus_4)

        except Exception as exc:
            snapshot.stage = "ERROR"
            self._halted = True
            raise

        self._cycle += 1
        self._commit_snapshot(snapshot)
        return snapshot

    def run(self, max_cycles: int = 10_000) -> list[CycleSnapshot]:
        """
        Ejecuta el programa completo hasta HALT o max_cycles.

        Returns:
            Lista de snapshots de cada ciclo.
        """
        while not self._halted and self._cycle < max_cycles:
            self.step()
        return self._log.copy()

    def reset(self) -> None:
        """Reinicia el procesador sin borrar la memoria de instrucciones."""
        self.pc.reset()
        self.registers.reset()
        self.data_mem.reset()
        self._cycle   = 0
        self._halted  = False
        self._log.clear()

    @property
    def is_halted(self) -> bool:
        return self._halted

    @property
    def cycle(self) -> int:
        return self._cycle

    @property
    def log(self) -> list[CycleSnapshot]:
        return list(self._log)

    # ─── Privado ────────────────────────────────────────────────────────

    def _update_pc(
        self,
        signals: ControlSignals,
        decoded: DecodedInstruction,
        alu_result: ALUResult,
        pc_plus_4: int,
    ) -> None:
        """Selecciona y aplica la próxima dirección del PC."""
        if signals.jump:
            self.pc.update_jump(decoded.jump_addr, pc_plus_4)
        elif signals.branch:
            is_bne = (decoded.opcode == 0b000101)   # BNE
            take_branch = (not alu_result.zero) if is_bne else alu_result.zero
            if take_branch:
                self.pc.update_branch(decoded.imm_signed, pc_plus_4)
            else:
                self.pc.update_sequential()
        else:
            self.pc.update_sequential()

    def _commit_snapshot(self, snapshot: CycleSnapshot) -> None:
        self._log.append(snapshot)
        if self.on_cycle_complete:
            self.on_cycle_complete(snapshot)
