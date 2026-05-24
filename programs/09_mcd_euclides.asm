# ═══════════════════════════════════════════════════════════════
#  NIVEL 9 — Máximo Común Divisor (Algoritmo de Euclides)
#  Tema: Bucle con módulo por restas, flujo no lineal
#
#  Qué hace:
#    Calcula el MCD de dos números usando el algoritmo de
#    Euclides por restas sucesivas:
#      mientras a != b:
#          si a > b: a = a - b
#          sino:     b = b - a
#      MCD = a
#
#  Parámetros: A = 48, B = 18
#
#  Proceso:
#    48,18 → 30,18 → 12,18 → 12,6 → 6,6 → MCD=6
#
#  Resultado esperado:
#    $s0 (MCD)  = 6
#    MEM[0]     = 6
# ═══════════════════════════════════════════════════════════════

        addi $t0, $zero, 48     # A = 48
        addi $t1, $zero, 18     # B = 18

gcd_loop:
        beq  $t0, $t1, gcd_fin  # si A == B → terminó

        slt  $t2, $t0, $t1      # $t2 = 1 si A < B
        bne  $t2, $zero, b_mayor_gcd  # si A < B → restar A de B

        # Rama: A >= B  →  A = A - B
        sub  $t0, $t0, $t1      # A = A - B
        j    gcd_loop

b_mayor_gcd:
        # Rama: B > A  →  B = B - A
        sub  $t1, $t1, $t0      # B = B - A
        j    gcd_loop

gcd_fin:
        move $s0, $t0           # MCD = A (en este punto A == B)
        sw   $s0, 0($zero)      # guardar resultado
        nop                     # FIN — $s0 = 6
