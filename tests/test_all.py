"""
Tests unitarios del Procesador Monociclo.
Ejecutar con: python -m pytest tests/ -v
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from src.components.alu import ALU, ALUOp, ALUResult
from src.components.register_bank import RegisterBank, RegisterBankError
from src.control.control_unit import ControlUnit, Opcode
from src.components.instruction_decoder import InstructionDecoder, InstructionType
from src.core.program_counter import ProgramCounter
from src.memory.memory import InstructionMemory, DataMemory
from src.core.processor import MonocycleProcessor
from src.components.assembler import Assembler


# ══════════════════════════════════════════════════════════════
#  ALU
# ══════════════════════════════════════════════════════════════

class TestALU:
    def setup_method(self):
        self.alu = ALU()

    def test_add(self):
        r = self.alu.execute(10, 20, ALUOp.ADD)
        assert r.value == 30
        assert not r.zero

    def test_sub_zero(self):
        r = self.alu.execute(5, 5, ALUOp.SUB)
        assert r.value == 0
        assert r.zero

    def test_and(self):
        r = self.alu.execute(0b1100, 0b1010, ALUOp.AND)
        assert r.value == 0b1000

    def test_or(self):
        r = self.alu.execute(0b1100, 0b1010, ALUOp.OR)
        assert r.value == 0b1110

    def test_slt_true(self):
        r = self.alu.execute(3, 5, ALUOp.SLT)
        assert r.value == 1

    def test_slt_false(self):
        r = self.alu.execute(10, 5, ALUOp.SLT)
        assert r.value == 0

    def test_negative_operand(self):
        r = self.alu.execute(0, 1, ALUOp.SUB)   # 0 - 1 = -1
        assert r.value == 0xFFFF_FFFF
        assert r.negative

    def test_unknown_op(self):
        with pytest.raises(ValueError):
            self.alu.execute(1, 2, 0b011)  # código no asignado


# ══════════════════════════════════════════════════════════════
#  Banco de Registros
# ══════════════════════════════════════════════════════════════

class TestRegisterBank:
    def setup_method(self):
        self.rb = RegisterBank()

    def test_zero_register_immutable(self):
        self.rb.write(0, 999)
        assert self.rb.read(0) == 0

    def test_write_read(self):
        self.rb.write(8, 42)
        assert self.rb.read(8) == 42

    def test_mask_32_bits(self):
        self.rb.write(1, 0xDEAD_BEEF_1234)
        assert self.rb.read(1) == 0xBEEF_1234  # solo 32 bits

    def test_reg_write_disabled(self):
        self.rb.write(5, 100)
        self.rb.write(5, 200, reg_write=False)
        assert self.rb.read(5) == 100

    def test_dual_read(self):
        self.rb.write(2, 10)
        self.rb.write(3, 20)
        a, b = self.rb.read_dual(2, 3)
        assert a == 10 and b == 20

    def test_invalid_index(self):
        with pytest.raises(RegisterBankError):
            self.rb.read(32)

    def test_reset(self):
        self.rb.write(10, 999)
        self.rb.reset()
        assert self.rb.read(10) == 0


# ══════════════════════════════════════════════════════════════
#  Unidad de Control
# ══════════════════════════════════════════════════════════════

class TestControlUnit:
    def setup_method(self):
        self.cu = ControlUnit()

    def test_r_type_signals(self):
        s = self.cu.decode(Opcode.R_TYPE, funct=0x20)  # ADD
        assert s.reg_dst   == True
        assert s.alu_src   == False
        assert s.reg_write == True
        assert s.mem_read  == False
        assert s.mem_write == False
        assert s.branch    == False
        assert s.jump      == False
        assert s.alu_control == 0b010  # ADD

    def test_lw_signals(self):
        s = self.cu.decode(Opcode.LW)
        assert s.mem_read  == True
        assert s.mem_to_reg== True
        assert s.reg_write == True
        assert s.alu_src   == True

    def test_sw_signals(self):
        s = self.cu.decode(Opcode.SW)
        assert s.mem_write == True
        assert s.reg_write == False

    def test_beq_signals(self):
        s = self.cu.decode(Opcode.BEQ)
        assert s.branch     == True
        assert s.reg_write  == False
        assert s.alu_control == 0b110  # SUB para comparar

    def test_j_signals(self):
        s = self.cu.decode(Opcode.J)
        assert s.jump == True

    def test_unknown_opcode(self):
        with pytest.raises(ValueError):
            self.cu.decode(0x3F)


# ══════════════════════════════════════════════════════════════
#  Decodificador de Instrucciones
# ══════════════════════════════════════════════════════════════

class TestInstructionDecoder:
    def setup_method(self):
        self.dec = InstructionDecoder()

    def test_r_type_add(self):
        # ADD $t0, $t1, $t2  →  0x012A4020
        # op=0 rs=$t1(9) rt=$t2(10) rd=$t0(8) sh=0 fn=0x20
        instr = (0 << 26) | (9 << 21) | (10 << 16) | (8 << 11) | 0x20
        d = self.dec.decode(instr)
        assert d.instr_type == InstructionType.R
        assert d.opcode == 0
        assert d.rs == 9
        assert d.rt == 10
        assert d.rd == 8
        assert d.funct == 0x20

    def test_i_type_addi(self):
        # ADDI $t0, $zero, 5
        instr = (0x08 << 26) | (0 << 21) | (8 << 16) | 5
        d = self.dec.decode(instr)
        assert d.instr_type == InstructionType.I
        assert d.imm_signed == 5

    def test_sign_extension_negative(self):
        # ADDI con inmediato negativo (-10 = 0xFFF6)
        instr = (0x08 << 26) | (0x20 << 16) | 0xFFF6
        d = self.dec.decode(instr)
        assert d.imm_signed == -10

    def test_j_type(self):
        instr = (0x02 << 26) | 0x00001000
        d = self.dec.decode(instr)
        assert d.instr_type == InstructionType.J
        assert d.jump_addr == 0x1000


# ══════════════════════════════════════════════════════════════
#  Memorias
# ══════════════════════════════════════════════════════════════

class TestMemory:
    def test_instruction_load_and_fetch(self):
        mem = InstructionMemory()
        mem.load_program([0xABCD1234, 0x00000000])
        assert mem.fetch(0) == 0xABCD1234
        assert mem.fetch(4) == 0x00000000

    def test_instruction_unaligned(self):
        from src.memory.memory import MemoryError as ME
        mem = InstructionMemory()
        with pytest.raises(ME):
            mem.fetch(3)

    def test_data_write_read(self):
        mem = DataMemory()
        mem.write(0, 0xDEAD_BEEF, mem_write=True)
        assert mem.read(0, mem_read=True) == 0xDEAD_BEEF

    def test_data_read_disabled(self):
        mem = DataMemory()
        mem.write(0, 42, mem_write=True)
        assert mem.read(0, mem_read=False) == 0

    def test_data_write_disabled(self):
        mem = DataMemory()
        mem.write(0, 42, mem_write=False)
        assert mem.read(0, mem_read=True) == 0


# ══════════════════════════════════════════════════════════════
#  Program Counter
# ══════════════════════════════════════════════════════════════

class TestProgramCounter:
    def test_initial_value(self):
        pc = ProgramCounter(0x1000)
        assert pc.value == 0x1000

    def test_sequential(self):
        pc = ProgramCounter(0)
        pc.update_sequential()
        assert pc.value == 4

    def test_branch(self):
        pc = ProgramCounter(0x10)
        pc.update_branch(2, 0x14)   # dest = 0x14 + 8 = 0x1C
        assert pc.value == 0x1C

    def test_jump(self):
        pc = ProgramCounter(0x0000_0000)
        # J 0x00000100  →  target = (0x4 & 0xF0000000) | (0x100 << 2)
        pc.update_jump(0x100, 0x4)
        assert pc.value == 0x400


# ══════════════════════════════════════════════════════════════
#  Ensamblador
# ══════════════════════════════════════════════════════════════

class TestAssembler:
    def setup_method(self):
        self.asm = Assembler()

    def test_nop(self):
        assert self.asm.assemble("nop") == [0]

    def test_addi(self):
        code = self.asm.assemble("addi $t0, $zero, 10")
        assert len(code) == 1
        d = InstructionDecoder().decode(code[0])
        assert d.opcode == 0x08
        assert d.rt == 8        # $t0
        assert d.imm_signed == 10

    def test_add_r_type(self):
        code = self.asm.assemble("add $t0, $t1, $t2")
        assert len(code) == 1
        d = InstructionDecoder().decode(code[0])
        assert d.instr_type == InstructionType.R
        assert d.rd == 8
        assert d.funct == 0x20

    def test_branch_label(self):
        src = """
            addi $t0, $zero, 1
        loop:
            addi $t0, $t0, -1
            bne  $t0, $zero, loop
            nop
        """
        code = self.asm.assemble(src)
        assert len(code) == 4

    def test_pseudo_move(self):
        code = self.asm.assemble("move $t0, $t1")
        d = InstructionDecoder().decode(code[0])
        assert d.instr_type == InstructionType.R
        assert d.rd == 8   # $t0


# ══════════════════════════════════════════════════════════════
#  Integración — Procesador completo
# ══════════════════════════════════════════════════════════════

class TestProcessor:
    def setup_method(self):
        self.proc = MonocycleProcessor()
        self.asm  = Assembler()

    def test_addi_writes_register(self):
        code = self.asm.assemble("addi $t0, $zero, 42\nnop")
        self.proc.load_program(code)
        self.proc.step()
        assert self.proc.registers.read(8) == 42  # $t0 = R8

    def test_add_r_type(self):
        src = "addi $t0, $zero, 7\naddi $t1, $zero, 3\nadd $t2, $t0, $t1\nnop"
        self.proc.load_program(self.asm.assemble(src))
        self.proc.run()
        assert self.proc.registers.read(10) == 10  # $t2 = 10

    def test_lw_sw(self):
        src = "addi $t0, $zero, 99\nsw $t0, 0($zero)\nlw $t1, 0($zero)\nnop"
        self.proc.load_program(self.asm.assemble(src))
        self.proc.run()
        assert self.proc.registers.read(9) == 99   # $t1

    def test_beq_taken(self):
        src = """
            addi $t0, $zero, 5
            addi $t1, $zero, 5
            beq  $t0, $t1, end
            addi $s0, $zero, 1   # NO debe ejecutarse
        end:
            addi $s1, $zero, 2
            nop
        """
        self.proc.load_program(self.asm.assemble(src))
        self.proc.run()
        assert self.proc.registers.read(16) == 0   # $s0 sin modificar
        assert self.proc.registers.read(17) == 2   # $s1 = 2

    def test_sum_loop(self):
        # Suma 1+2+3+4 = 10
        src = """
            addi $t0, $zero, 1
            addi $t1, $zero, 5
            addi $s0, $zero, 0
        loop:
            add  $s0, $s0, $t0
            addi $t0, $t0, 1
            bne  $t0, $t1, loop
            nop
        """
        self.proc.load_program(self.asm.assemble(src))
        self.proc.run()
        assert self.proc.registers.read(16) == 10  # $s0 = 10

    def test_cycle_count(self):
        src = "addi $t0, $zero, 1\naddi $t1, $zero, 2\nnop"
        self.proc.load_program(self.asm.assemble(src))
        self.proc.run()
        assert self.proc.cycle == 2   # 2 instrucciones antes del NOP


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
