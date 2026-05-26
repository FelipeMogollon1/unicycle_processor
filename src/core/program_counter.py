"""
Program Counter (PC) — Registro de dirección de la próxima instrucción.
Procesador Monociclo MIPS
"""


class ProgramCounter:
    """
    Contador de programa de 32 bits.

    En cada ciclo, el PC se actualiza con una de tres fuentes:
        1. PC + 4        (siguiente instrucción secuencial)
        2. PC + 4 + (imm << 2)  (salto BEQ/BNE tomado)
        3. {PC+4[31:28], addr26, 00}  (salto J/JAL)

    Responsabilidades:
        - Mantener la dirección actual
        - Calcular la dirección del próximo ciclo
        - Soportar los tres modos de actualización
    """

    WORD_SIZE = 4
    MASK_32   = 0xFFFF_FFFF

    def __init__(self, start_address: int = 0x0000_0000):
        self._pc: int = start_address & self.MASK_32
        self._history: list[int] = [self._pc]

    @property
    def value(self) -> int:
        """Valor actual del PC."""
        return self._pc

    def next_sequential(self) -> int:
        """Calcula PC + 4 sin modificar el PC."""
        return (self._pc + self.WORD_SIZE) & self.MASK_32

    def update_sequential(self) -> None:
        """Avanza al PC + 4."""
        self._advance((self._pc + self.WORD_SIZE) & self.MASK_32)

    def update_branch(self, imm_signed: int, pc_plus_4: int) -> None:
        """
        Actualiza PC para un salto condicional tomado.
        Destino = PC+4 + (imm << 2)
        """
        target = (pc_plus_4 + (imm_signed << 2)) & self.MASK_32
        self._advance(target)

    def update_jump(self, jump_addr: int, pc_plus_4: int) -> None:
        """
        Actualiza PC para una instrucción J/JAL.
        Destino = {PC+4[31:28], addr26, 00}
        """
        target = ((pc_plus_4 & 0xF000_0000) |
                  ((jump_addr & 0x03FF_FFFF) << 2)) & self.MASK_32
        self._advance(target)

    def reset(self, address: int = 0x0000_0000) -> None:
        """Reinicia el PC a la dirección dada."""
        self._pc = address & self.MASK_32
        self._history = [self._pc]

    @property
    def history(self) -> list[int]:
        """Historial de direcciones visitadas."""
        return list(self._history)

    def _advance(self, new_pc: int) -> None:
        self._pc = new_pc
        self._history.append(new_pc)

    def __repr__(self) -> str:
        return f"PC = {self._pc:#010x}"
