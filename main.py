#!/usr/bin/env python3
"""
Procesador Monociclo MIPS — Punto de entrada principal.

Uso:
    python main.py              # Lanza la GUI
    python main.py --cli        # Modo consola (sin GUI)
    python main.py --test       # Ejecuta los tests
    python main.py --demo       # Demo automática en consola

Autores: Andres Felipe Mogollon España, Juan Esteban Bedoya, Michael Hurtado
Profesor: David Andres Romero Arenas
Materia: Arquitectura de Computadores — Unidad 4
"""

import sys
import os

# Asegurar que src/ esté en el path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)


def run_gui():
    """Lanza la interfaz gráfica."""
    from src.ui.app import main
    main()


def run_demo():
    """Ejecuta un programa de demostración en consola."""
    from src.core.processor import MonocycleProcessor
    from src.components.assembler import Assembler

    asm  = Assembler()
    proc = MonocycleProcessor()

    source = """\
# Suma de los primeros 4 números: 1+2+3+4 = 10
        addi $t0, $zero, 1
        addi $t1, $zero, 5
        addi $s0, $zero, 0
loop:   add  $s0, $s0, $t0
        addi $t0, $t0, 1
        bne  $t0, $t1, loop
        sw   $s0, 0($zero)
        nop
"""
    print("─" * 60)
    print("  PROCESADOR MONOCICLO MIPS — Demo de consola")
    print("─" * 60)

    instructions = asm.assemble(source)
    print(f"\n  Programa ensamblado: {len(instructions)} instrucciones\n")

    proc.load_program(instructions)

    while not proc.is_halted:
        snap = proc.step()
        print(snap)
        print()

    print("─" * 60)
    print(f"  Ciclos ejecutados : {proc.cycle}")
    print(f"  $s0 (resultado)   : {proc.registers.read(16)}")
    print(f"  MEM[0x00000000]   : {proc.data_mem.read(0, mem_read=True)}")
    print("─" * 60)


def run_tests():
    """Ejecuta la suite de tests con pytest."""
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_all.py", "-v", "--tb=short"],
        cwd=BASE_DIR
    )
    sys.exit(result.returncode)


def run_cli():
    """Modo CLI interactivo."""
    from src.core.processor import MonocycleProcessor
    from src.components.assembler import Assembler, AssemblerError

    print("\n  Procesador Monociclo MIPS — CLI Interactiva")
    print("  Comandos: load <archivo.asm>, step, run, reset, regs, mem, quit\n")

    asm  = Assembler()
    proc = MonocycleProcessor()

    while True:
        try:
            cmd = input("mips> ").strip().split()
            if not cmd:
                continue

            match cmd[0]:
                case "load":
                    path = cmd[1] if len(cmd) > 1 else input("Archivo: ").strip()
                    with open(path) as f:
                        src = f.read()
                    instructions = asm.assemble(src)
                    proc.load_program(instructions)
                    print(f"  ✔ {len(instructions)} instrucciones cargadas.")

                case "step":
                    if proc.is_halted:
                        print("  ⏹ Procesador detenido. Usa 'reset'.")
                    else:
                        snap = proc.step()
                        print(snap)

                case "run":
                    proc.run()
                    print(f"  ⏹ Fin. {proc.cycle} ciclos ejecutados.")

                case "reset":
                    proc.reset()
                    print("  ↺ Reset completo.")

                case "regs":
                    for name, val in proc.registers:
                        if val != 0:
                            print(f"  {name:6s}: {val:#010x}  ({val})")

                case "mem":
                    entries = proc.data_mem.dump()
                    if entries:
                        for addr, val in entries:
                            print(f"  {addr:#010x}: {val:#010x}  ({val})")
                    else:
                        print("  (memoria vacía)")

                case "quit" | "exit":
                    break

                case _:
                    print(f"  Comando desconocido: '{cmd[0]}'")

        except AssemblerError as e:
            print(f"  Error de ensamblado: {e}")
        except FileNotFoundError as e:
            print(f"  Archivo no encontrado: {e}")
        except KeyboardInterrupt:
            break

    print("\n  Hasta luego.")


# ─── Entrada principal ────────────────────────────────────────────────────────

if __name__ == "__main__":
    args = sys.argv[1:]

    if "--test" in args:
        run_tests()
    elif "--demo" in args:
        run_demo()
    elif "--cli" in args:
        run_cli()
    else:
        run_gui()
