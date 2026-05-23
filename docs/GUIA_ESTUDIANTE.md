# 📘 Guía de Usuario — Simulador de Procesador Monociclo MIPS

**Para:** Estudiantes de Arquitectura de Computadores  
**Nivel:** Introducción al Procesador Monociclo  
**Materia:** Unidad 4 — Procesador Monociclo  
**Autores:** Andres Mogollon · Juan Bedoya · Michael Hurtado  
**Profesor:** David Andres Romero Arenas

---

## ¿Qué es este simulador?

Este programa te permite **ver en acción** cómo funciona un procesador por dentro.
Cuando escribes código en lenguaje ensamblador, el simulador te muestra exactamente:

- Qué instrucción se está ejecutando y en qué etapa
- Qué pasa dentro de la ALU (operaciones matemáticas/lógicas)
- Cómo cambian los registros y la memoria
- Qué señales de control se activan en cada ciclo

> 💡 **Analogía:** Imagina que el procesador es una fábrica de instrucciones.
> Este simulador es el "vidrio" que te permite ver la línea de ensamblaje por dentro,
> paso a paso, sin que vaya demasiado rápido.

---

## Instalación rápida

```bash
# 1. Necesitas Python 3.10 o superior instalado
python --version        # debe decir 3.10.x o mayor

# 2. Entra a la carpeta del proyecto
cd procesador_monociclo

# 3. Ejecuta el programa
python main.py
```

---

## La interfaz — ¿Qué hay en cada parte?

```
┌─────────────────────────────────────────────────────────────────────┐
│  HEADER: nombre, estado actual, PC y contador de ciclos             │
├──────────────┬──────────────────────────┬───────────────────────────┤
│              │                          │                           │
│   EDITOR     │     DATAPATH             │   REGISTROS               │
│   (escribe   │     (visualización       │   MEMORIA                 │
│   tu código) │      del procesador)     │   SEÑALES                 │
│              │                          │   (3 pestañas)            │
│   CONTROLES  ├──────────────────────────┤                           │
│   (botones)  │     LOG DE CICLOS        │                           │
│              │     (historial)          │                           │
└──────────────┴──────────────────────────┴───────────────────────────┘
│  BARRA DE ESTADO: información del ciclo actual                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Paso a paso: tu primera simulación

### Paso 1 — Escribe o carga el programa

En el **Editor Ensamblador** (columna izquierda), ya hay un programa de ejemplo cargado:

```asm
# Suma los números 1 + 2 + 3 + 4 = 10
addi $t0, $zero, 1      # i = 1
addi $t1, $zero, 5      # límite = 5
addi $s0, $zero, 0      # suma = 0

loop:
    add  $s0, $s0, $t0  # suma = suma + i
    addi $t0, $t0, 1    # i = i + 1
    bne  $t0, $t1, loop # si i ≠ 5, repetir

sw   $s0, 0($zero)      # guardar resultado en memoria
nop                     # fin del programa
```

> 💡 Las líneas que empiezan con `#` son **comentarios** — el procesador las ignora,
> son solo notas para que los humanos entendamos el código.

---

### Paso 2 — Ensamblar

Haz clic en el botón **▶ Ensamblar**.

Esto convierte tu código de texto (ensamblador) a números binarios de 32 bits
que el procesador puede leer. Si hay algún error de escritura en el código,
te aparecerá un mensaje explicando en qué línea está el problema.

Si todo sale bien, verás el mensaje **"✔ N instrucciones ensambladas correctamente"**.

---

### Paso 3 — Ejecutar paso a paso (recomendado para aprender)

Haz clic en **⏭ Paso** una vez.

Observa qué pasa en cada parte de la pantalla:

**En el Datapath:**
- Se ilumina el bloque que está activo en ese momento (IF, ID, EX, MEM o WB)
- El texto en la parte inferior dice exactamente qué etapa se ejecutó

**En el Log de Ejecución:**
- Aparece una nueva línea con el número de ciclo, el PC, la instrucción
  ejecutada, el resultado de la ALU y el registro que fue modificado

**En la pestaña Registros:**
- El registro que cambió se resalta brevemente en verde

**En el Header:**
- El contador de ciclos sube en 1
- El PC muestra la siguiente dirección

Repite el proceso haciendo clic en **⏭ Paso** para cada instrucción.

---

### Paso 4 — Modo automático

Cuando ya entiendes el flujo, usa **⏩ Auto** para que el procesador ejecute
solo todas las instrucciones, una por una, con una pausa entre cada ciclo.

Puedes ajustar la velocidad con el **deslizador** (0.05 = muy rápido, 2.0 = lento).

Para pausar en cualquier momento, haz clic en **⏸ Pausar**.

---

### Paso 5 — Reiniciar

Haz clic en **↺ Reset** para volver al estado inicial (PC = 0, todos los
registros en 0, memoria limpia) sin perder el programa cargado.

---

## Las 5 etapas del procesador — qué significa cada una

Cada instrucción pasa por estas etapas en orden. Con el simulador puedes ver
cuándo ocurre cada una.

### 🟦 IF — Instruction Fetch (Búsqueda)
El procesador lee la instrucción que está en la dirección apuntada por el **PC**.
Es como buscar una tarea en tu lista de pendientes.

**Qué ves en el simulador:** El bloque "Inst. Memory" se ilumina.
El header muestra el valor del PC actual.

---

### 🟨 ID — Instruction Decode (Decodificación)
El procesador descifra qué operación debe hacer y qué registros usar.
También activa la **Unidad de Control** que genera las señales.
Es como leer la instrucción y entender qué hay que hacer.

**Qué ves en el simulador:** El bloque "Register Bank" y "Unidad de Control"
se iluminan. En la pestaña **Señales** puedes ver cuáles se activaron.

---

### 🟩 EX — Execute (Ejecución)
La **ALU** realiza la operación matemática o lógica.
Por ejemplo: suma, resta, AND, comparación, etc.

**Qué ves en el simulador:** El bloque "ALU" se ilumina.
En el Log aparece `ALU=0x...` con el resultado.

---

### 🟧 MEM — Memory Access (Acceso a memoria)
Solo se usa para instrucciones `LW` (cargar dato) y `SW` (guardar dato).
Para las demás instrucciones, esta etapa no hace nada relevante.

**Qué ves en el simulador:** El bloque "Data Memory" se ilumina.
Si hubo escritura, aparece el nuevo valor en la pestaña **Memoria**.

---

### 🟥 WB — Write Back (Escritura de resultado)
El resultado final se guarda en el registro destino del banco de registros.

**Qué ves en el simulador:** El bloque "Write Back" se ilumina.
En la pestaña **Registros**, el registro modificado parpadea en verde.

---

## Los registros — ¿qué son y para qué sirven?

Un registro es una **memoria ultrarrápida** dentro del procesador.
El procesador MIPS tiene 32 registros, cada uno de 32 bits.

| Registro | Nombre convencional | Para qué se usa normalmente |
|----------|--------------------|-----------------------------|
| `$0` | `$zero` | Siempre vale 0 (no se puede cambiar) |
| `$8–$15` | `$t0–$t7` | Variables temporales (para cálculos) |
| `$16–$23` | `$s0–$s7` | Variables a guardar (resultados importantes) |
| `$29` | `$sp` | Puntero de pila (stack pointer) |
| `$31` | `$ra` | Dirección de retorno (para funciones) |

> 💡 **Importante:** `$zero` siempre es 0 sin importar qué intentes escribir en él.
> Se usa mucho para inicializar valores o para comparaciones.

---

## Las señales de control — ¿qué significan?

Estas señales son como "interruptores" que el procesador enciende o apaga
dependiendo de qué instrucción se está ejecutando.

| Señal | Encendida (1) significa... | Apagada (0) significa... |
|-------|---------------------------|--------------------------|
| **RegWrite** | Escribir resultado en un registro | No modificar registros |
| **MemRead** | Leer un dato de la memoria (LW) | No leer memoria |
| **MemWrite** | Guardar un dato en memoria (SW) | No escribir memoria |
| **ALUSrc** | El segundo operando es un número inmediato | El segundo operando es un registro |
| **MemToReg** | El resultado viene de la memoria | El resultado viene de la ALU |
| **RegDst** | El registro destino es `rd` (R-type) | El registro destino es `rt` (I-type) |
| **Branch** | Es una instrucción de salto condicional | No es salto condicional |
| **Jump** | Es un salto incondicional (J/JAL) | No es salto incondicional |

---

## Instrucciones disponibles — referencia rápida

### Operaciones aritméticas y lógicas (tipo R)
```asm
add  $rd, $rs, $rt    # rd = rs + rt
sub  $rd, $rs, $rt    # rd = rs - rt
and  $rd, $rs, $rt    # rd = rs AND rt  (bit a bit)
or   $rd, $rs, $rt    # rd = rs OR rt   (bit a bit)
xor  $rd, $rs, $rt    # rd = rs XOR rt  (bit a bit)
nor  $rd, $rs, $rt    # rd = NOT(rs OR rt)
slt  $rd, $rs, $rt    # rd = 1 si rs < rt, sino 0
```

### Operaciones con número inmediato (tipo I)
```asm
addi $rt, $rs, NUM    # rt = rs + NUM  (suma inmediata)
andi $rt, $rs, NUM    # rt = rs AND NUM
ori  $rt, $rs, NUM    # rt = rs OR NUM
slti $rt, $rs, NUM    # rt = 1 si rs < NUM, sino 0
lui  $rt, NUM         # rt = NUM << 16  (carga en 16 bits altos)
```

### Memoria
```asm
lw   $rt, OFFSET($rs) # rt = Memoria[rs + OFFSET]  → cargar
sw   $rt, OFFSET($rs) # Memoria[rs + OFFSET] = rt  → guardar
```

### Saltos condicionales
```asm
beq  $rs, $rt, etiqueta  # saltar si rs == rt
bne  $rs, $rt, etiqueta  # saltar si rs ≠ rt
```

### Saltos incondicionales
```asm
j    etiqueta   # saltar siempre a etiqueta
jal  etiqueta   # saltar y guardar dirección de retorno en $ra
```

### Pseudoinstrucciones (atajos)
```asm
nop              # no hacer nada (fin de programa)
move $rd, $rs    # rd = rs  (copia un registro)
li   $rt, NUM    # rt = NUM (cargar número directo)
```

---

## Ejercicios prácticos para entender el tema

### Ejercicio 1 — Operación simple ⭐
Carga los valores 10 y 20 en registros temporales y súmalos.
```asm
addi $t0, $zero, 10   # $t0 = 10
addi $t1, $zero, 20   # $t1 = 20
add  $t2, $t0, $t1    # $t2 = $t0 + $t1 = 30
nop
```
**Observa:** Después de ejecutar, la pestaña Registros debe mostrar `$t2 = 0x0000001e` (30 en hexadecimal).

---

### Ejercicio 2 — Guardar y cargar de memoria ⭐⭐
```asm
addi $t0, $zero, 42   # $t0 = 42
sw   $t0, 0($zero)    # guardar 42 en dirección 0
lw   $t1, 0($zero)    # cargar desde dirección 0 a $t1
nop
```
**Observa:** La pestaña Memoria debe mostrar `0x00000000: 0x0000002a` (42 en hex).
Después del LW, `$t1` también debe tener 42.

---

### Ejercicio 3 — Contador con salto ⭐⭐
```asm
addi $t0, $zero, 0    # contador = 0
addi $t1, $zero, 5    # límite = 5
loop:
    addi $t0, $t0, 1  # contador++
    bne  $t0, $t1, loop
nop
```
**Observa:** El procesador ejecuta el loop 5 veces. Al final `$t0 = 5`.
Cuenta cuántos ciclos se ejecutan en total.

---

### Ejercicio 4 — Valor máximo entre dos números ⭐⭐⭐
```asm
addi $t0, $zero, 7    # a = 7
addi $t1, $zero, 12   # b = 12
slt  $t2, $t0, $t1    # $t2 = 1 si a < b
beq  $t2, $zero, fin  # si $t2 == 0, a >= b
move $s0, $t1         # max = b
j    salir
fin:
    move $s0, $t0     # max = a
salir:
    nop
```
**Observa:** `$s0` debe tener el valor mayor (12 en este caso).
Cambia los valores de `$t0` y `$t1` para probar distintos casos.

---

## Preguntas frecuentes

**¿Por qué el programa termina con `nop`?**
El simulador interpreta la instrucción `NOP` (no operation, valor binario = 0x00000000)
como la señal de fin de programa. Sin ella, el procesador seguiría
leyendo posiciones de memoria vacías indefinidamente.

**¿Por qué los valores se muestran en hexadecimal?**
Porque internamente el procesador trabaja con bits. El hexadecimal es más compacto
que el binario para representar los 32 bits de cada valor.
`0x0000000A` = 10 en decimal.

**¿Qué significa PC?**
PC = Program Counter (Contador de Programa). Es un registro especial que guarda
la dirección de la **siguiente instrucción** a ejecutar. Empieza en `0x00000000`
y avanza de 4 en 4 (porque cada instrucción ocupa 4 bytes).

**¿Por qué las direcciones de memoria son múltiplos de 4?**
Porque cada instrucción e cada dato ocupa exactamente 4 bytes (32 bits).
Es lo que se llama arquitectura "word-aligned" (alineada a palabras).

**¿Qué pasa si escribo mal una instrucción?**
El ensamblador te mostrará un error indicando el número de línea y
la instrucción problemática antes de intentar ejecutar algo.

**¿Puedo cargar mi propio archivo .asm?**
Sí. Usa el botón **📂 Abrir** para cargar cualquier archivo de texto
con extensión `.asm`, `.s` o `.txt` que contenga instrucciones MIPS.

---

## Referencia rápida de atajos

| Acción | Cómo hacerlo |
|--------|-------------|
| Ensamblar programa | Botón **▶ Ensamblar** |
| Ejecutar 1 ciclo | Botón **⏭ Paso** |
| Ejecutar automático | Botón **⏩ Auto** |
| Pausar modo auto | Botón **⏸ Pausar** (mismo botón) |
| Reiniciar | Botón **↺ Reset** |
| Cambiar velocidad | Deslizador en la sección Controles |
| Cargar archivo | Botón **📂 Abrir** |
| Ver registros | Pestaña **Registros** (panel derecho) |
| Ver memoria | Pestaña **Memoria** (panel derecho) |
| Ver señales | Pestaña **Señales** (panel derecho) |

---

## Glosario básico

| Término | Definición |
|---------|-----------|
| **ALU** | Unidad Aritmético-Lógica. Circuito que hace las operaciones matemáticas y lógicas |
| **Banco de registros** | Conjunto de 32 memorias ultrarrápidas dentro del procesador |
| **Ciclo de reloj** | Una "pulsación" del procesador. Cada instrucción tarda exactamente 1 ciclo |
| **Datapath** | Camino de datos. El recorrido que hace una instrucción por el procesador |
| **Ensamblador** | Programa que traduce código legible (ADD, SUB...) a binario |
| **Inmediato** | Número constante escrito directamente en la instrucción |
| **Opcode** | Los 6 bits que identifican qué tipo de instrucción es |
| **PC** | Program Counter. Registro que apunta a la próxima instrucción |
| **Registro** | Pequeño espacio de almacenamiento ultrarrápido dentro del procesador |
| **Señal de control** | Bit que activa o desactiva una parte del circuito del procesador |
| **Tipo R** | Instrucciones que operan solo con registros (ADD, SUB, AND...) |
| **Tipo I** | Instrucciones que usan un número inmediato (ADDI, LW, SW, BEQ...) |
| **Tipo J** | Instrucciones de salto incondicional (J, JAL) |

---

*Simulador desarrollado para la asignatura Arquitectura de Computadores, 2025.*  
*Andres Mogollon · Juan Bedoya · Michael Hurtado · Prof. David Andres Romero Arenas*
