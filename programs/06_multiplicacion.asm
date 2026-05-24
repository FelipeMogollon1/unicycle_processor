# ═══════════════════════════════════════════════════════════════
#  NIVEL 6 — Multiplicación por Sumas Sucesivas
#  Tema: Algoritmo iterativo, bucle con acumulador
#
#  Qué hace:
#    MIPS básico no tiene instrucción MUL en este procesador.
#    Implementa A × B = A + A + A + ... (B veces)
#
#    Equivale en C a:
#      int resultado = 0;
#      for (int i = 0; i < B; i++) resultado += A;
#
#  Parámetros: A = 7, B = 6
#
#  Resultado esperado:
#    $s0 (resultado) = 42  (7 × 6)
#    $t0 (contador)  = 0   (se agota al terminar)
#    MEM[0]          = 42
# ═══════════════════════════════════════════════════════════════

        addi $t0, $zero, 7      # A = 7  (multiplicando)
        addi $t1, $zero, 6      # B = 6  (multiplicador / contador)
        addi $s0, $zero, 0      # resultado = 0

mul_loop:
        beq  $t1, $zero, mul_fin  # si contador == 0 → terminar
        add  $s0, $s0, $t0        # resultado += A
        addi $t1, $t1, -1         # contador--
        j    mul_loop

mul_fin:
        sw   $s0, 0($zero)      # MEM[0] = 42
        nop                     # FIN — $s0 = 42
