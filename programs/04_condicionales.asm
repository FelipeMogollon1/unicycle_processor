# ═══════════════════════════════════════════════════════════════
#  NIVEL 4 — Saltos Condicionales: BEQ y BNE
#  Tema: Estructuras if-else con BEQ/BNE + SLT
#
#  Qué hace:
#    Simula el siguiente código en C:
#
#    int a = 15, b = 10;
#    int mayor, menor;
#    if (a > b) {
#        mayor = a;
#        menor = b;
#    } else {
#        mayor = b;
#        menor = a;
#    }
#
#  Resultado esperado:
#    $s0 (mayor) = 15
#    $s1 (menor) = 10
#    $s2 (iguales) = 0  (no son iguales)
# ═══════════════════════════════════════════════════════════════

        addi $t0, $zero, 15     # a = 15
        addi $t1, $zero, 10     # b = 10

        # ── Comparar igualdad ───────────────────────────────
        beq  $t0, $t1, iguales  # si a == b → rama iguales
        addi $s2, $zero, 0      # $s2 = 0 (no son iguales)
        j    comparar

iguales:
        addi $s2, $zero, 1      # $s2 = 1 (son iguales)

        # ── Determinar mayor/menor con SLT ──────────────────
comparar:
        slt  $t2, $t1, $t0      # $t2 = 1 si b < a  (a es mayor)
        beq  $t2, $zero, b_mayor  # si $t2==0 → b >= a → b es mayor

        # Rama: a es mayor
        move $s0, $t0           # mayor = a
        move $s1, $t1           # menor = b
        j    fin

b_mayor:
        # Rama: b es mayor (o iguales)
        move $s0, $t1           # mayor = b
        move $s1, $t0           # menor = a

fin:
        nop                     # FIN
