# ═══════════════════════════════════════════════════════════════
#  NIVEL 5 — Bucle For: Suma de 1 a N
#  Tema: BNE como estructura de repetición (for/while)
#
#  Qué hace:
#    Calcula la suma de los primeros N números naturales:
#    suma = 1 + 2 + 3 + ... + N
#
#    Equivale en C a:
#      int suma = 0;
#      for (int i = 1; i <= N; i++) suma += i;
#
#  Parámetro: N = 10
#
#  Resultado esperado:
#    $s0 (suma)  = 55   (1+2+3+...+10)
#    $t0 (i)     = 11   (contador al salir del bucle)
#    MEM[0]      = 55   (resultado guardado)
# ═══════════════════════════════════════════════════════════════

        addi $t0, $zero, 1      # i = 1
        addi $t1, $zero, 11     # límite = N+1 = 11
        addi $s0, $zero, 0      # suma = 0

for:    # mientras i != 11, sumar
        add  $s0, $s0, $t0      # suma += i
        addi $t0, $t0, 1        # i++
        bne  $t0, $t1, for      # si i != 11 → repetir

        sw   $s0, 0($zero)      # guardar resultado en MEM[0]
        nop                     # FIN — $s0 = 55
