# ============================================================
#  Programa de prueba — Procesador Monociclo MIPS
#  Calcula la suma de los primeros N números naturales
#  y guarda el resultado en $s0
#
#  Registros usados:
#    $t0 = contador (i)
#    $t1 = N (límite)
#    $s0 = acumulador (suma)
# ============================================================

        addi $t0, $zero, 1      # i = 1
        addi $t1, $zero, 5      # N = 5
        addi $s0, $zero, 0      # suma = 0

loop:   add  $s0, $s0, $t0      # suma += i
        addi $t0, $t0, 1        # i++
        bne  $t0, $t1, loop     # si i != N, repetir

        sw   $s0, 0($zero)      # guardar resultado en MEM[0]
        nop                     # FIN
