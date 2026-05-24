# ═══════════════════════════════════════════════════════════════
#  NIVEL 10 — Ordenamiento Burbuja (Bubble Sort)
#  Tema: Bucles anidados, acceso a arreglo, intercambio
#
#  Qué hace:
#    Ordena un arreglo de 5 enteros de menor a mayor usando
#    el algoritmo de burbuja.
#
#    Equivale en C a:
#      for (int i=0; i<N-1; i++)
#        for (int j=0; j<N-1-i; j++)
#          if (arr[j] > arr[j+1]) swap(arr[j], arr[j+1]);
#
#  Arreglo inicial en MEM[0..16]: [64, 25, 12, 22, 11]
#
#  Resultado esperado en MEM[0..16]:
#    MEM[0]  = 11
#    MEM[4]  = 12
#    MEM[8]  = 22
#    MEM[12] = 25
#    MEM[16] = 64
#
#  Registros clave:
#    $t0 = puntero externo (i)
#    $t1 = puntero interno (j, dirección)
#    $t2 = arr[j]
#    $t3 = arr[j+1]
#    $t4 = comparación SLT
#    $t5 = dirección límite externo
#    $s0 = base del arreglo (0)
# ═══════════════════════════════════════════════════════════════

        # ── Cargar arreglo ──────────────────────────────────
        addi $t0, $zero, 64
        sw   $t0, 0($zero)

        addi $t0, $zero, 25
        sw   $t0, 4($zero)

        addi $t0, $zero, 12
        sw   $t0, 8($zero)

        addi $t0, $zero, 22
        sw   $t0, 12($zero)

        addi $t0, $zero, 11
        sw   $t0, 16($zero)

        # ── Bubble Sort ─────────────────────────────────────
        # $t0 = i (pasadas externas: 0..3)
        # $t5 = límite externo = 4 (N-1)
        addi $t0, $zero, 0      # i = 0
        addi $t5, $zero, 4      # límite externo = N-1 = 4

outer:
        beq  $t0, $t5, sort_fin # si i == 4 → terminar

        # $t1 = j*4 (dirección de arr[j], empieza en 0)
        # $t6 = límite interno = (N-1-i)*4
        sub  $t6, $t5, $t0      # $t6 = N-1-i
        addi $t7, $zero, 4
        # Multiplicar $t6 × 4 por sumas (N-1-i es pequeño)
        addi $t8, $zero, 0      # acumulador
        move $t9, $t6           # contador temporal
mul4:
        beq  $t9, $zero, mul4_fin
        add  $t8, $t8, $t7
        addi $t9, $t9, -1
        j    mul4
mul4_fin:
        move $t6, $t8           # $t6 = (N-1-i)*4  (límite interno en bytes)

        addi $t1, $zero, 0      # j = 0  (byte offset)

inner:
        beq  $t1, $t6, inner_fin    # si j == límite → fin del pase

        lw   $t2, 0($t1)            # $t2 = arr[j]
        lw   $t3, 4($t1)            # $t3 = arr[j+1]

        slt  $t4, $t3, $t2          # $t4 = 1 si arr[j+1] < arr[j]
        beq  $t4, $zero, no_swap    # si no → no intercambiar

        # Intercambiar arr[j] y arr[j+1]
        sw   $t3, 0($t1)            # arr[j]   = arr[j+1]
        sw   $t2, 4($t1)            # arr[j+1] = arr[j]

no_swap:
        addi $t1, $t1, 4            # j++
        j    inner

inner_fin:
        addi $t0, $t0, 1            # i++
        j    outer

sort_fin:
        nop                     # FIN — revisar pestaña Memoria
