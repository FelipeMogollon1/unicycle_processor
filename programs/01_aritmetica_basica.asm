# ═══════════════════════════════════════════════════════════════
#  NIVEL 1 — Operaciones Aritméticas Básicas
#  Tema: ADD, SUB, ADDI con registros
#
#  Qué hace:
#    Realiza suma, resta y almacena resultados en registros.
#    Es el "Hola Mundo" del procesador.
#
#  Resultado esperado:
#    $t0 = 10   (primer operando)
#    $t1 = 3    (segundo operando)
#    $t2 = 13   (suma:  10 + 3)
#    $t3 = 7    (resta: 10 - 3)
#    $t4 = 30   (suma con inmediato: 10 + 20)
# ═══════════════════════════════════════════════════════════════

        addi $t0, $zero, 10     # $t0 = 10
        addi $t1, $zero, 3      # $t1 = 3

        add  $t2, $t0, $t1      # $t2 = $t0 + $t1 = 13
        sub  $t3, $t0, $t1      # $t3 = $t0 - $t1 = 7
        addi $t4, $t0, 20       # $t4 = $t0 + 20  = 30

        nop                     # FIN
