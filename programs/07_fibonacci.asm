# ═══════════════════════════════════════════════════════════════
#  NIVEL 7 — Sucesión de Fibonacci
#  Tema: Dos acumuladores, bucle con estado doble
#
#  Qué hace:
#    Calcula los primeros N términos de Fibonacci y los
#    almacena secuencialmente en memoria desde MEM[0].
#    F(0)=0, F(1)=1, F(n)=F(n-1)+F(n-2)
#
#    Equivale en C a:
#      int a=0, b=1;
#      MEM[i++] = a;
#      for (int k=0; k<N-1; k++) {
#          int tmp = a + b;
#          a = b; b = tmp;
#          MEM[i++] = b;
#      }
#
#  Parámetro: N = 8 términos
#
#  Resultado en memoria (byte address):
#    MEM[0]  = 0   (F0)
#    MEM[4]  = 1   (F1)
#    MEM[8]  = 1   (F2)
#    MEM[12] = 2   (F3)
#    MEM[16] = 3   (F4)
#    MEM[20] = 5   (F5)
#    MEM[24] = 8   (F6)
#    MEM[28] = 13  (F7)
#
#  Registros:
#    $t0 = a (término anterior)
#    $t1 = b (término actual)
#    $t2 = tmp (siguiente)
#    $t3 = dirección de escritura
#    $t4 = contador de iteraciones
# ═══════════════════════════════════════════════════════════════

        addi $t0, $zero, 0      # a = F(0) = 0
        addi $t1, $zero, 1      # b = F(1) = 1
        addi $t3, $zero, 0      # dirección = 0
        addi $t4, $zero, 7      # iteraciones restantes = N-1 = 7

        sw   $t0, 0($t3)        # MEM[0] = 0  (guardar F0)
        addi $t3, $t3, 4        # dirección += 4

fib_loop:
        beq  $t4, $zero, fib_fin    # si contador == 0 → fin

        sw   $t1, 0($t3)            # MEM[dir] = b
        add  $t2, $t0, $t1          # tmp = a + b
        move $t0, $t1               # a = b
        move $t1, $t2               # b = tmp

        addi $t3, $t3, 4            # dirección += 4
        addi $t4, $t4, -1           # contador--
        j    fib_loop

fib_fin:
        # $t1 tiene el último término calculado
        nop                     # FIN — revisar pestaña Memoria
