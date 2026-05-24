# ═══════════════════════════════════════════════════════════════
#  NIVEL 3 — Memoria: Load Word y Store Word
#  Tema: LW, SW con desplazamiento (offset)
#
#  Qué hace:
#    Guarda tres valores en posiciones contiguas de memoria
#    y los vuelve a cargar en registros diferentes.
#    Demuestra el esquema base[offset] de direccionamiento.
#
#  Mapa de memoria usado:
#    MEM[0x00]  = 100   ($s0)
#    MEM[0x04]  = 200   ($s1)
#    MEM[0x08]  = 300   ($s2)
#
#  Resultado esperado:
#    $t0 = 100  (cargado desde MEM[0])
#    $t1 = 200  (cargado desde MEM[4])
#    $t2 = 300  (cargado desde MEM[8])
#    $t3 = 600  (suma de los tres valores leídos)
# ═══════════════════════════════════════════════════════════════

        # ── Guardar valores en memoria ──────────────────────
        addi $s0, $zero, 100    # $s0 = 100
        addi $s1, $zero, 200    # $s1 = 200
        addi $s2, $zero, 300    # $s2 = 300

        sw   $s0, 0($zero)      # MEM[0] = 100
        sw   $s1, 4($zero)      # MEM[4] = 200
        sw   $s2, 8($zero)      # MEM[8] = 300

        # ── Cargar valores desde memoria ────────────────────
        lw   $t0, 0($zero)      # $t0 = MEM[0] = 100
        lw   $t1, 4($zero)      # $t1 = MEM[4] = 200
        lw   $t2, 8($zero)      # $t2 = MEM[8] = 300

        # ── Operar con los datos cargados ───────────────────
        add  $t3, $t0, $t1      # $t3 = 100 + 200 = 300
        add  $t3, $t3, $t2      # $t3 = 300 + 300 = 600

        sw   $t3, 12($zero)     # guardar resultado en MEM[12]

        nop                     # FIN
