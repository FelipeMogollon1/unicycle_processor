# ═══════════════════════════════════════════════════════════════
#  NIVEL 2 — Operaciones Lógicas Bit a Bit
#  Tema: AND, OR, XOR, NOR, ANDI, ORI
#
#  Qué hace:
#    Aplica operaciones lógicas entre dos patrones de bits.
#    Útil para máscaras, flags y manipulación de bits.
#
#  Valores de entrada:
#    $t0 = 0b1111_0000  = 0xF0 = 240
#    $t1 = 0b1010_1010  = 0xAA = 170
#
#  Resultado esperado:
#    $t2 = AND  → 0b1010_0000 = 0xA0 = 160
#    $t3 = OR   → 0b1111_1010 = 0xFA = 250
#    $t4 = XOR  → 0b0101_1010 = 0x5A = 90
#    $t5 = NOR  → NOT(OR)     = 0xFFFFFF05
#    $t6 = ANDI → $t0 AND 0x0F = 0x00 (limpia bits altos)
#    $t7 = ORI  → $t0 OR  0x0F = 0xFF (pone bits bajos)
# ═══════════════════════════════════════════════════════════════

        addi $t0, $zero, 240    # $t0 = 0xF0 = 1111_0000
        addi $t1, $zero, 170    # $t1 = 0xAA = 1010_1010

        and  $t2, $t0, $t1      # AND  bit a bit
        or   $t3, $t0, $t1      # OR   bit a bit
        xor  $t4, $t0, $t1      # XOR  bit a bit
        nor  $t5, $t0, $t1      # NOR  bit a bit

        andi $t6, $t0, 15       # AND con inmediato 0x0F → máscara baja
        ori  $t7, $t0, 15       # OR  con inmediato 0x0F → enciende bits bajos

        nop                     # FIN
