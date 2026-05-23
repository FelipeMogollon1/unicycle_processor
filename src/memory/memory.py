"""
Memorias del Procesador Monociclo:
  - InstructionMemory : ROM de instrucciones (solo lectura, word-addressed)
  - DataMemory        : RAM de datos (lectura/escritura, byte-addressed)

Procesador Monociclo MIPS
"""

from __future__ import annotations


class MemoryError(Exception):
    """Error base de acceso a memoria."""


class InstructionMemory:
    """
    Memoria de instrucciones (ROM) — 1024 palabras de 32 bits.

    Solo permite lectura. Las instrucciones se cargan mediante load_program().
    El acceso es word-addressed (cada posición = 4 bytes).

    Responsabilidades:
        - Almacenar el programa en binario
        - Proveer instrucciones dada una dirección PC
        - Validar rangos de acceso
    """

    WORD_SIZE  = 4          # bytes por instrucción
    CAPACITY   = 1024       # instrucciones máximas
    NOP        = 0x0000_0000  # NOP = SLL $zero, $zero, 0

    def __init__(self):
        self._memory: list[int] = [self.NOP] * self.CAPACITY

    def load_program(self, instructions: list[int]) -> None:
        """
        Carga una lista de instrucciones desde la posición 0.

        Args:
            instructions: Lista de enteros de 32 bits.

        Raises:
            MemoryError si excede la capacidad.
        """
        if len(instructions) > self.CAPACITY:
            raise MemoryError(
                f"Programa demasiado grande: {len(instructions)} > {self.CAPACITY}"
            )
        self._memory = [self.NOP] * self.CAPACITY
        for i, instr in enumerate(instructions):
            self._memory[i] = instr & 0xFFFF_FFFF

    def fetch(self, pc: int) -> int:
        """
        Obtiene la instrucción en la dirección PC.

        Args:
            pc: Dirección byte (debe ser múltiplo de 4).

        Returns:
            Instrucción de 32 bits.
        """
        if pc % self.WORD_SIZE != 0:
            raise MemoryError(f"Dirección PC no alineada: {pc:#010x}")
        idx = pc // self.WORD_SIZE
        if not (0 <= idx < self.CAPACITY):
            raise MemoryError(f"PC fuera de rango: {pc:#010x}")
        return self._memory[idx]

    def __len__(self) -> int:
        return self.CAPACITY

    def dump(self, start: int = 0, count: int = 16) -> list[tuple[int, int]]:
        """Devuelve [(dirección, instrucción)] para visualización."""
        return [(i * self.WORD_SIZE, self._memory[i])
                for i in range(start, min(start + count, self.CAPACITY))]


class DataMemory:
    """
    Memoria de datos (RAM) — 2048 palabras de 32 bits.

    Lectura controlada por MemRead, escritura por MemWrite.
    El acceso es word-addressed internamente pero la interfaz es byte-addressed.

    Responsabilidades:
        - Soportar LW (load word) y SW (store word)
        - Validar señales MemRead y MemWrite
        - Proveer snapshot para la GUI
    """

    WORD_SIZE = 4
    CAPACITY  = 2048

    def __init__(self):
        self._memory: list[int] = [0] * self.CAPACITY

    def read(self, address: int, *, mem_read: bool) -> int:
        """
        Lee una palabra de 32 bits.

        Args:
            address: Dirección byte (múltiplo de 4).
            mem_read: Señal MemRead (si False, retorna 0).
        """
        if not mem_read:
            return 0
        idx = self._byte_to_word(address)
        return self._memory[idx]

    def write(self, address: int, value: int, *, mem_write: bool) -> None:
        """
        Escribe una palabra de 32 bits.

        Args:
            address: Dirección byte (múltiplo de 4).
            value: Valor a escribir.
            mem_write: Señal MemWrite (si False, no hace nada).
        """
        if not mem_write:
            return
        idx = self._byte_to_word(address)
        self._memory[idx] = value & 0xFFFF_FFFF

    def reset(self) -> None:
        """Limpia toda la memoria."""
        self._memory = [0] * self.CAPACITY

    def dump(self, start: int = 0, count: int = 32) -> list[tuple[int, int]]:
        """Devuelve [(dirección, valor)] para visualización."""
        return [(i * self.WORD_SIZE, self._memory[i])
                for i in range(start, min(start + count, self.CAPACITY))
                if self._memory[i] != 0]

    def _byte_to_word(self, address: int) -> int:
        if address % self.WORD_SIZE != 0:
            raise MemoryError(f"Dirección no alineada: {address:#010x}")
        idx = address // self.WORD_SIZE
        if not (0 <= idx < self.CAPACITY):
            raise MemoryError(f"Dirección fuera de rango: {address:#010x}")
        return idx
