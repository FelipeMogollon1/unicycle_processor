# ═══════════════════════════════════════════════════════════════
#  NIVEL 8 — Máximo en un Arreglo
#  Tema: Recorrido de arreglo en memoria, comparación iterativa
#
#  Qué hace:
#    Carga un arreglo de 6 enteros en memoria, luego recorre
#    el arreglo buscando el valor máximo.
#
#    Equivale en C a:
#      int arr[] = {14, 37, 8, 52, 21, 3};
#      int max = arr[0];
#      for (int i=1; i<6; i++)
#          if (arr[i] > max) max = arr[i];
#
#  Arreglo: [14, 37, 8, 52, 21, 3]
#
#  Resultado esperado:
#    $s0 (máximo)  = 52
#    MEM[0..20]    = arreglo original
#    MEM[24]       = 52  (resultado guardado)
# ═══════════════════════════════════════════════════════════════

        # ── Cargar arreglo en memoria ───────────────────────
        addi $t0, $zero, 14
        sw   $t0, 0($zero)      # arr[0] = 14

        addi $t0, $zero, 37
        sw   $t0, 4($zero)      # arr[1] = 37

        addi $t0, $zero, 8
        sw   $t0, 8($zero)      # arr[2] = 8

        addi $t0, $zero, 52
        sw   $t0, 12($zero)     # arr[3] = 52

        addi $t0, $zero, 21
        sw   $t0, 16($zero)     # arr[4] = 21

        addi $t0, $zero, 3
        sw   $t0, 20($zero)     # arr[5] = 3

        # ── Inicializar búsqueda ────────────────────────────
        lw   $s0, 0($zero)      # max = arr[0] = 14
        addi $t1, $zero, 4      # dirección actual = 4  (empieza en arr[1])
        addi $t2, $zero, 24     # dirección límite = 6*4 = 24

max_loop:
        beq  $t1, $t2, max_fin  # si dir == 24 → fin

        lw   $t3, 0($t1)        # $t3 = arr[i]
        slt  $t4, $s0, $t3      # $t4 = 1 si max < arr[i]
        beq  $t4, $zero, no_update  # si max >= arr[i] → no actualizar

        move $s0, $t3           # max = arr[i]  (nuevo máximo)

no_update:
        addi $t1, $t1, 4        # avanzar al siguiente elemento
        j    max_loop

max_fin:
        sw   $s0, 24($zero)     # guardar máximo en MEM[24]
        nop                     # FIN — $s0 = 52
