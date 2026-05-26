# ⬡ Procesador Monociclo MIPS

> Simulador completo de un procesador monociclo estilo MIPS de 32 bits,
> desarrollado en Python con interfaz gráfica interactiva, ensamblador integrado
> y visualización animada del datapath.

---

## 👥 Integrantes

| Nombre | Rol |
|--------|-----|
| **Andres Felipe Mogollon España** | Arquitectura del procesador, Unidad de Control, ALU |
| **Juan Esteban Bedoya** | Banco de Registros, Memorias, Program Counter |
| **Michael Hurtado** | Ensamblador, GUI, Integración y Tests |

**Profesor:** David Andres Romero Arenas
**Materia:** Arquitectura de Computadores
**Unidad:** 4 — Procesador Monociclo
**Semestre:** 2026-1

---

## 📋 Descripción

Este proyecto simula el funcionamiento interno de un **procesador monociclo** de 32 bits
con arquitectura MIPS, implementando todas las etapas del ciclo de instrucción:

```
IF → ID → EX → MEM → WB
```

El simulador incluye un **ensamblador de dos pasadas**, soporte para instrucciones tipo R, I y J,
y una interfaz gráfica que permite observar en tiempo real el estado de los registros,
la memoria de datos, las señales de control y el flujo del datapath.

---

## 🎯 Objetivos

- Implementar la arquitectura de un procesador monociclo MIPS de 32 bits
- Simular el ciclo completo de ejecución instrucción por instrucción
- Visualizar el flujo del datapath y las señales de control activas
- Desarrollar un ensamblador MIPS simplificado de dos pasadas
- Aplicar principios SOLID y buenas prácticas de ingeniería de software

---

## 🏗️ Arquitectura del Proyecto

```
procesador_monociclo/
│
├── src/
│   ├── core/
│   │   ├── processor.py          # Orquestador del ciclo IF→ID→EX→MEM→WB
│   │   └── program_counter.py    # Registro PC con modos secuencial/branch/jump
│   │
│   ├── components/
│   │   ├── alu.py                # ALU 32 bits: ADD, SUB, AND, OR, SLT, NOR, XOR
│   │   ├── register_bank.py      # Banco de 32 registros × 32 bits
│   │   ├── instruction_decoder.py# Decodificador de campos R/I/J + extensión de signo
│   │   ├── assembler.py          # Ensamblador MIPS de dos pasadas
│   │   └── mux.py                # Multiplexores del datapath
│   │
│   ├── memory/
│   │   └── memory.py             # InstructionMemory (ROM) + DataMemory (RAM)
│   │
│   ├── control/
│   │   └── control_unit.py       # Unidad de control: opcode → señales de control
│   │
│   └── ui/
│       └── app.py                # GUI completa con Tkinter
│
├── tests/
│   └── test_all.py               # 25+ tests unitarios e integración
│
├── programs/
│   └── example.asm               # Programa de ejemplo (suma de naturales)
│
├── main.py                       # Punto de entrada
├── requirements.txt
├── README.md
└── .gitignore
```

---

## ⚙️ Tecnologías

| Tecnología | Uso |
|------------|-----|
| **Python 3.10+** | Lenguaje principal (match/case, type hints) |
| **Tkinter** | Interfaz gráfica nativa (incluida en Python) |
| **pytest** | Framework de testing |
| **POO + SOLID** | Arquitectura y diseño del código |
| **Git / GitHub** | Control de versiones |

---

## 🚀 Instalación y Ejecución

### Prerrequisitos
- Python 3.10 o superior
- pip

### Instalación

```bash
# Clonar el repositorio
git clone https://github.com/usuario/procesador_monociclo.git
cd procesador_monociclo

# (Opcional) Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### Ejecución

```bash
# Interfaz gráfica (modo principal)
python main.py

# Demo en consola
python main.py --demo

# CLI interactiva
python main.py --cli

# Ejecutar tests
python main.py --test
# o directamente:
pytest tests/ -v
```

---

## 📖 Instrucciones Soportadas

### R-type (opcode = 000000)

| Mnemónico | Funct | Operación |
|-----------|-------|-----------|
| `ADD rd, rs, rt` | 0x20 | rd = rs + rt |
| `SUB rd, rs, rt` | 0x22 | rd = rs - rt |
| `AND rd, rs, rt` | 0x24 | rd = rs & rt |
| `OR  rd, rs, rt` | 0x25 | rd = rs \| rt |
| `XOR rd, rs, rt` | 0x26 | rd = rs ^ rt |
| `NOR rd, rs, rt` | 0x27 | rd = ~(rs \| rt) |
| `SLT rd, rs, rt` | 0x2A | rd = (rs < rt) ? 1 : 0 |

### I-type

| Mnemónico | Opcode | Operación |
|-----------|--------|-----------|
| `ADDI rt, rs, imm` | 0x08 | rt = rs + SignExt(imm) |
| `LW   rt, imm(rs)` | 0x23 | rt = MEM[rs + imm] |
| `SW   rt, imm(rs)` | 0x2B | MEM[rs + imm] = rt |
| `BEQ  rs, rt, off` | 0x04 | if rs==rt: PC+=4+(off<<2) |
| `BNE  rs, rt, off` | 0x05 | if rs!=rt: PC+=4+(off<<2) |
| `ORI  rt, rs, imm` | 0x0D | rt = rs \| ZeroExt(imm) |
| `ANDI rt, rs, imm` | 0x0C | rt = rs & ZeroExt(imm) |
| `SLTI rt, rs, imm` | 0x0A | rt = (rs < imm) ? 1 : 0 |
| `LUI  rt, imm`     | 0x0F | rt = imm << 16 |

### J-type

| Mnemónico | Opcode | Operación |
|-----------|--------|-----------|
| `J   addr` | 0x02 | PC = {PC+4[31:28], addr, 00} |
| `JAL addr` | 0x03 | $ra = PC+4; saltar |

### Pseudoinstrucciones

| Mnemónico | Equivalente |
|-----------|-------------|
| `NOP` | `SLL $zero, $zero, 0` |
| `MOVE rd, rs` | `ADD rd, $zero, rs` |
| `LI rt, imm` | `ADDI rt, $zero, imm` |

---

## 🔀 Datapath — Señales de Control

```
Instrucción | RegDst ALUSrc MemToReg RegWrite MemRead MemWrite Branch Jump
────────────|────────────────────────────────────────────────────────────
R-type      |   1      0      0        1       0        0       0     0
ADDI        |   0      1      0        1       0        0       0     0
LW          |   0      1      1        1       1        0       0     0
SW          |   X      1      X        0       0        1       0     0
BEQ         |   X      0      X        0       0        0       1     0
J           |   X      X      X        0       0        0       0     1
```

---

## 🧪 Tests

```bash
pytest tests/ -v --tb=short
```

Cobertura de tests:
- ✅ ALU: 8 casos (ADD, SUB, AND, OR, SLT, NOR, XOR, overflow)
- ✅ Banco de registros: 7 casos (inmutabilidad $zero, R/W, máscara 32b)
- ✅ Unidad de Control: 6 casos (R-type, LW, SW, BEQ, J, opcode inválido)
- ✅ Decodificador: 4 casos (R, I, J, extensión de signo)
- ✅ Memorias: 5 casos (fetch, alineación, R/W, señales)
- ✅ Program Counter: 4 casos (secuencial, branch, jump)
- ✅ Ensamblador: 5 casos (NOP, ADDI, R-type, labels, pseudos)
- ✅ Integración: 6 casos (pipeline completo, loops, LW/SW, BEQ)

---

## 💡 Características Innovadoras

- **Visualización animada del datapath** — Cada etapa se ilumina durante su ejecución
- **Resaltado de sintaxis** en el editor ensamblador integrado
- **Log de ciclos** con mnemónicos, valores ALU y registros modificados
- **Indicadores de señales de control** con LEDs de color
- **Modo automático con velocidad ajustable** (0.05 – 2.0 segundos/ciclo)
- **CLI interactiva** para entornos sin interfaz gráfica
- **Ensamblador de dos pasadas** con soporte a etiquetas y pseudoinstrucciones

---

## 📄 Flujo Git Recomendado

```bash
# Branches principales
main          # Código estable, releases
develop       # Integración de features

# Branches de desarrollo
feature/alu
feature/control-unit
feature/gui
bugfix/pc-jump

# Conventional Commits
feat(alu): add XOR operation support
fix(decoder): correct sign extension for 16-bit immediate
docs(readme): add instruction set table
test(processor): add BEQ integration test
refactor(memory): extract base class for ROM and RAM
```

---

## 📜 Licencia

Proyecto académico — Universidad, 2026.
Uso libre para fines educativos con atribución.

---

<p align="center">
  Desarrollado con ❤️ para Arquitectura de Computadores<br>
  <strong>Andres Mogollon · Juan Bedoya · Michael Hurtado</strong><br>
  Prof. David Andres Romero Arenas
</p>
