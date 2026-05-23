"""
GUI del Procesador Monociclo — CustomTkinter + Canvas interactivo.

Características:
  ✓ Visualización animada del datapath
  ✓ Panel de registros en tiempo real
  ✓ Panel de memoria de datos
  ✓ Panel de señales de control con indicadores de color
  ✓ Editor de código ensamblador integrado
  ✓ Ejecución paso a paso y modo automático
  ✓ Log de ciclos con mnemónicos
  ✓ Estadísticas de ejecución

Procesador Monociclo MIPS
Autores: Andres Felipe Mogollon España, Juan Esteban Bedoya, Michael Hurtado
Profesor: David Andres Romero Arenas
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.core.processor import MonocycleProcessor, CycleSnapshot
from src.components.assembler import Assembler, AssemblerError


# ── Paleta de colores ─────────────────────────────────────────────────────────
BG_DARK   = "#0D1117"
BG_PANEL  = "#161B22"
BG_CARD   = "#21262D"
BG_HOVER  = "#2D333B"
ACCENT    = "#58A6FF"
ACCENT2   = "#3FB950"
ACCENT3   = "#F78166"
ACCENT4   = "#D2A8FF"
ACCENT5   = "#FFA657"
TEXT_PRI  = "#E6EDF3"
TEXT_SEC  = "#8B949E"
TEXT_MUT  = "#484F58"
BORDER    = "#30363D"
RED       = "#F85149"
GREEN     = "#3FB950"
YELLOW    = "#D29922"
PURPLE    = "#BC8CFF"
CYAN      = "#79C0FF"


EXAMPLE_PROGRAM = """\
# ── Programa de ejemplo: suma 1+2+3+4 = 10 ──────────────
# Registros: $t0=contador, $t1=límite, $s0=acumulador

        addi $t0, $zero, 1      # i = 1
        addi $t1, $zero, 5      # N = 5  (suma hasta 4)
        addi $s0, $zero, 0      # suma = 0

loop:   add  $s0, $s0, $t0      # suma += i
        addi $t0, $t0, 1        # i++
        bne  $t0, $t1, loop     # si i != 5, repetir

        sw   $s0, 0($zero)      # guardar resultado
        nop                     # FIN → $s0 = 10
"""


class ProcessorGUI:
    """Interfaz gráfica principal del Procesador Monociclo."""

    def __init__(self):
        self.proc = MonocycleProcessor()
        self.asm  = Assembler()
        self._auto_running = False
        self._auto_delay   = 0.6   # segundos entre ciclos en modo auto
        self._current_snapshot: CycleSnapshot | None = None
        self._cycle_log: list[CycleSnapshot] = []

        self._build_window()
        self._build_layout()
        self._set_example_code()

    # ═══════════════════════════════════════════════════════
    #  Ventana principal
    # ═══════════════════════════════════════════════════════

    def _build_window(self):
        self.root = tk.Tk()
        self.root.title("Procesador Monociclo MIPS — Simulador")
        self.root.configure(bg=BG_DARK)
        self.root.geometry("1400x900")
        self.root.minsize(1100, 700)

        # Estilos ttk
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook",         background=BG_DARK,    borderwidth=0)
        style.configure("TNotebook.Tab",     background=BG_CARD,    foreground=TEXT_SEC,
                        padding=[12, 6],     font=("Consolas", 10))
        style.map("TNotebook.Tab",
                  background=[("selected", BG_PANEL)],
                  foreground=[("selected", TEXT_PRI)])
        style.configure("TSeparator",        background=BORDER)
        style.configure("Vertical.TScrollbar",
                        background=BG_CARD,  troughcolor=BG_DARK,
                        arrowcolor=TEXT_SEC, borderwidth=0)
        style.configure("Horizontal.TScrollbar",
                        background=BG_CARD,  troughcolor=BG_DARK,
                        arrowcolor=TEXT_SEC, borderwidth=0)

    # ═══════════════════════════════════════════════════════
    #  Layout general
    # ═══════════════════════════════════════════════════════

    def _build_layout(self):
        # Header
        self._build_header()

        # Cuerpo principal (3 columnas)
        body = tk.Frame(self.root, bg=BG_DARK)
        body.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        body.columnconfigure(0, weight=2, minsize=280)
        body.columnconfigure(1, weight=5, minsize=450)
        body.columnconfigure(2, weight=3, minsize=300)
        body.rowconfigure(0, weight=1)

        # Columna izquierda — editor + controles
        left = tk.Frame(body, bg=BG_DARK)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        self._build_editor(left)
        self._build_controls(left)

        # Columna central — datapath + log
        center = tk.Frame(body, bg=BG_DARK)
        center.grid(row=0, column=1, sticky="nsew", padx=4)
        center.rowconfigure(0, weight=3)
        center.rowconfigure(1, weight=2)
        center.columnconfigure(0, weight=1)
        self._build_datapath(center)
        self._build_cycle_log(center)

        # Columna derecha — registros + memoria + señales
        right = tk.Frame(body, bg=BG_DARK)
        right.grid(row=0, column=2, sticky="nsew", padx=(4, 0))
        self._build_right_panel(right)

        # Status bar
        self._build_statusbar()

    # ─── Header ──────────────────────────────────────────────────────────

    def _build_header(self):
        hdr = tk.Frame(self.root, bg=BG_PANEL, height=52)
        hdr.pack(fill="x", padx=0, pady=0)
        hdr.pack_propagate(False)

        tk.Label(hdr, text="⬡", font=("Consolas", 22), fg=ACCENT,
                 bg=BG_PANEL).pack(side="left", padx=(16, 4))
        tk.Label(hdr, text="Procesador Monociclo MIPS",
                 font=("Consolas", 14, "bold"), fg=TEXT_PRI,
                 bg=BG_PANEL).pack(side="left")

        tk.Label(hdr, text="Unidad 4 — Arquitectura de Computadores",
                 font=("Consolas", 9), fg=TEXT_SEC, bg=BG_PANEL).pack(
                     side="left", padx=16)

        # Contadores en el header
        self._lbl_cycle = tk.Label(hdr, text="Ciclo: 0",
                                    font=("Consolas", 10, "bold"),
                                    fg=ACCENT, bg=BG_PANEL)
        self._lbl_cycle.pack(side="right", padx=16)

        self._lbl_pc = tk.Label(hdr, text="PC: 0x00000000",
                                  font=("Consolas", 10),
                                  fg=ACCENT4, bg=BG_PANEL)
        self._lbl_pc.pack(side="right", padx=8)

        self._lbl_status = tk.Label(hdr, text="● LISTO",
                                      font=("Consolas", 10, "bold"),
                                      fg=GREEN, bg=BG_PANEL)
        self._lbl_status.pack(side="right", padx=8)

        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x")

    # ─── Editor de código ─────────────────────────────────────────────────

    def _build_editor(self, parent):
        frame = self._card(parent, "📝  Editor Ensamblador")
        frame.pack(fill="both", expand=True, pady=(0, 4))

        txt_frame = tk.Frame(frame, bg=BG_CARD)
        txt_frame.pack(fill="both", expand=True, padx=6, pady=6)

        # Números de línea
        self._line_nums = tk.Text(
            txt_frame, width=3, state="disabled",
            bg=BG_HOVER, fg=TEXT_MUT, font=("Consolas", 10),
            bd=0, padx=4, pady=4, selectbackground=BG_HOVER,
            insertbackground=BG_HOVER, relief="flat",
        )
        self._line_nums.pack(side="left", fill="y")

        # Editor principal
        self._editor = tk.Text(
            txt_frame, wrap="none",
            bg=BG_CARD, fg=TEXT_PRI,
            font=("Consolas", 10),
            insertbackground=ACCENT,
            selectbackground=BG_HOVER,
            bd=0, padx=8, pady=4,
            undo=True, relief="flat",
        )
        self._editor.pack(side="left", fill="both", expand=True)

        scrolly = ttk.Scrollbar(txt_frame, orient="vertical",
                                 command=self._editor.yview)
        scrolly.pack(side="right", fill="y")
        self._editor.configure(yscrollcommand=scrolly.set)
        self._editor.bind("<KeyRelease>", self._update_line_numbers)

        # Sintaxis básica con tags
        self._editor.tag_configure("comment", foreground=TEXT_MUT)
        self._editor.tag_configure("keyword", foreground=ACCENT)
        self._editor.tag_configure("register", foreground=ACCENT2)
        self._editor.tag_configure("label", foreground=ACCENT5)
        self._editor.tag_configure("number", foreground=PURPLE)

        self._editor.bind("<KeyRelease>", self._on_editor_change)

    def _update_line_numbers(self, *_):
        self._line_nums.configure(state="normal")
        self._line_nums.delete("1.0", "end")
        lines = self._editor.get("1.0", "end").count("\n")
        nums = "\n".join(str(i) for i in range(1, lines + 1))
        self._line_nums.insert("1.0", nums)
        self._line_nums.configure(state="disabled")

    def _on_editor_change(self, *_):
        self._update_line_numbers()
        self._highlight_syntax()

    def _highlight_syntax(self):
        """Resaltado de sintaxis básico."""
        import re
        content = self._editor.get("1.0", "end")
        for tag in ("comment", "keyword", "register", "label", "number"):
            self._editor.tag_remove(tag, "1.0", "end")

        patterns = [
            ("comment",  r"#.*$"),
            ("label",    r"^\s*\w+:"),
            ("keyword",  r"\b(add|addi|sub|and|andi|or|ori|nor|xor|slt|slti|lw|sw|beq|bne|j|jal|lui|nop|move|li|la)\b"),
            ("register", r"\$\w+"),
            ("number",   r"\b(0x[0-9a-fA-F]+|\d+|-\d+)\b"),
        ]
        for tag, pattern in patterns:
            for m in re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE):
                start = f"1.0 + {m.start()} chars"
                end   = f"1.0 + {m.end()} chars"
                self._editor.tag_add(tag, start, end)

    # ─── Controles ────────────────────────────────────────────────────────

    def _build_controls(self, parent):
        frame = self._card(parent, "⚙  Controles")
        frame.pack(fill="x", pady=(0, 4))

        # Fila 1 — botones principales
        row1 = tk.Frame(frame, bg=BG_CARD)
        row1.pack(fill="x", padx=6, pady=(6, 2))

        self._btn_load  = self._btn(row1, "▶  Ensamblar", ACCENT,   self._on_assemble)
        self._btn_step  = self._btn(row1, "⏭  Paso",     ACCENT2,  self._on_step,  state="disabled")
        self._btn_auto  = self._btn(row1, "⏩  Auto",     ACCENT5,  self._on_auto,  state="disabled")
        self._btn_reset = self._btn(row1, "↺  Reset",    ACCENT3,  self._on_reset, state="disabled")

        for b in (self._btn_load, self._btn_step, self._btn_auto, self._btn_reset):
            b.pack(side="left", fill="x", expand=True, padx=2, ipady=5)

        # Fila 2 — velocidad y cargar archivo
        row2 = tk.Frame(frame, bg=BG_CARD)
        row2.pack(fill="x", padx=6, pady=(2, 8))

        tk.Label(row2, text="Velocidad:", font=("Consolas", 9),
                 fg=TEXT_SEC, bg=BG_CARD).pack(side="left")

        self._speed_var = tk.DoubleVar(value=0.6)
        sp = tk.Scale(row2, from_=0.05, to=2.0, orient="horizontal",
                      variable=self._speed_var, resolution=0.05,
                      bg=BG_CARD, fg=TEXT_PRI, troughcolor=BG_HOVER,
                      highlightthickness=0, bd=0,
                      command=lambda v: setattr(self, "_auto_delay", float(v)))
        sp.pack(side="left", fill="x", expand=True, padx=(4, 8))

        self._btn(row2, "📂 Abrir", TEXT_SEC, self._on_open_file).pack(
            side="right", ipady=3, padx=2)

    # ─── Datapath visual ──────────────────────────────────────────────────

    def _build_datapath(self, parent):
        frame = self._card(parent, "🔀  Datapath — Camino de Datos")
        frame.grid(row=0, column=0, sticky="nsew", pady=(0, 4))

        self._dp_canvas = tk.Canvas(
            frame, bg=BG_CARD, bd=0, highlightthickness=0,
        )
        self._dp_canvas.pack(fill="both", expand=True, padx=4, pady=4)
        self._dp_canvas.bind("<Configure>", lambda e: self._draw_datapath())
        self._draw_datapath()

    def _draw_datapath(self, active_stage: str = ""):
        c = self._dp_canvas
        c.delete("all")
        W = c.winfo_width()  or 500
        H = c.winfo_height() or 260

        # Colores por etapa activa
        def stage_color(stage: str) -> str:
            if active_stage == stage:
                return ACCENT
            return BG_HOVER

        def stage_text_color(stage: str) -> str:
            return BG_DARK if active_stage == stage else TEXT_SEC

        # ── Bloques del datapath ──────────────────────────────────────

        blocks = [
            ("IF",   "Inst.\nMemory",  0.05, 0.2, 0.14, 0.8),
            ("ID",   "Register\nBank", 0.22, 0.2, 0.36, 0.8),
            ("EX",   "ALU",            0.44, 0.3, 0.55, 0.7),
            ("MEM",  "Data\nMemory",   0.62, 0.2, 0.75, 0.8),
            ("WB",   "Write\nBack",    0.82, 0.3, 0.95, 0.7),
        ]

        block_coords: dict[str, tuple] = {}

        for stage, label, x1r, y1r, x2r, y2r in blocks:
            x1, y1 = W * x1r, H * y1r
            x2, y2 = W * x2r, H * y2r
            fill = stage_color(stage)
            c.create_rectangle(x1, y1, x2, y2,
                                fill=fill, outline=ACCENT if active_stage == stage else BORDER,
                                width=2 if active_stage == stage else 1)
            c.create_text((x1 + x2) / 2, (y1 + y2) / 2,
                           text=label, fill=stage_text_color(stage),
                           font=("Consolas", 8, "bold"), justify="center")
            c.create_text((x1 + x2) / 2, y1 - 8,
                           text=stage, fill=ACCENT if active_stage == stage else TEXT_MUT,
                           font=("Consolas", 7))
            block_coords[stage] = (x1, y1, x2, y2)

        # ── PC ─────────────────────────────────────────────────────────
        px, py = W * 0.01, H * 0.45
        c.create_rectangle(px, py - 14, px + W * 0.04, py + 14,
                            fill=ACCENT4 if active_stage == "IF" else BG_HOVER,
                            outline=ACCENT4, width=1)
        c.create_text(px + W * 0.02, py,
                       text="PC", fill=BG_DARK if active_stage == "IF" else ACCENT4,
                       font=("Consolas", 8, "bold"))

        # ── Flechas de conexión (se iluminan hasta la etapa activa) ───────
        stage_order = ["IF", "ID", "EX", "MEM", "WB"]
        active_idx  = stage_order.index(active_stage) if active_stage in stage_order else -1

        # Cada flecha corresponde al tramo ANTES del bloque indicado
        # connections: (x1r, y1r, x2r, y2r, iluminar_si_etapa_activa_>=_idx)
        connections = [
            (0.04, 0.5,  0.05, 0.5,  0),   # PC → IF       (activa desde IF=0)
            (0.14, 0.5,  0.22, 0.5,  1),   # IF → ID       (activa desde ID=1)
            (0.36, 0.5,  0.44, 0.5,  2),   # ID → EX       (activa desde EX=2)
            (0.55, 0.5,  0.62, 0.5,  3),   # EX → MEM      (activa desde MEM=3)
            (0.75, 0.5,  0.82, 0.5,  4),   # MEM → WB      (activa desde WB=4)
        ]
        for x1r, y1r, x2r, y2r, min_idx in connections:
            lit   = active_idx >= min_idx
            color = ACCENT if lit else BORDER
            width = 2 if lit else 1
            c.create_line(W * x1r, H * y1r, W * x2r, H * y2r,
                          fill=color, width=width, arrow="last",
                          arrowshape=(8, 10, 3))

        # ── Unidad de control (arriba) ──────────────────────────────────
        cu_x1, cu_y1 = W * 0.22, H * 0.02
        cu_x2, cu_y2 = W * 0.55, H * 0.18
        c.create_rectangle(cu_x1, cu_y1, cu_x2, cu_y2,
                            fill=YELLOW if active_stage == "ID" else BG_HOVER,
                            outline=YELLOW, width=1)
        c.create_text((cu_x1 + cu_x2) / 2, (cu_y1 + cu_y2) / 2,
                       text="Unidad de Control",
                       fill=BG_DARK if active_stage == "ID" else YELLOW,
                       font=("Consolas", 8, "bold"))

        # Flechas de señales de control
        ctrl_y_src = cu_y2
        ctrl_y_dst = H * 0.2
        for xr in [0.29, 0.38, 0.50]:
            c.create_line(W * xr, ctrl_y_src, W * xr, ctrl_y_dst,
                          fill=YELLOW, width=1, dash=(3, 3))

        # ── Indicador de etapa activa ──────────────────────────────────
        if active_stage:
            label_map = {
                "IF": "FETCH — Leyendo instrucción",
                "ID": "DECODE — Decodificando",
                "EX": "EXECUTE — Operando en ALU",
                "MEM": "MEMORY — Accediendo a datos",
                "WB": "WRITEBACK — Escribiendo resultado",
                "HALT": "HALT — Programa terminado",
                "ERROR": "ERROR — Excepción",
            }
            c.create_rectangle(0, H - 22, W, H,
                                fill=BG_HOVER, outline="")
            c.create_text(W / 2, H - 11,
                           text=label_map.get(active_stage, active_stage),
                           fill=ACCENT, font=("Consolas", 9, "bold"))

        # ── Info del ciclo actual ──────────────────────────────────────
        if self._current_snapshot and self._current_snapshot.decoded:
            d = self._current_snapshot.decoded
            c.create_text(8, H - 38, anchor="w",
                           text=f"Instrucción: {d.mnemonic}",
                           fill=TEXT_PRI, font=("Consolas", 9))

    # ─── Log de ciclos ────────────────────────────────────────────────────

    def _build_cycle_log(self, parent):
        frame = self._card(parent, "📋  Log de Ejecución")
        frame.grid(row=1, column=0, sticky="nsew")

        self._log_text = tk.Text(
            frame, bg=BG_CARD, fg=TEXT_PRI,
            font=("Consolas", 9), state="disabled",
            bd=0, padx=8, pady=4, relief="flat",
            wrap="none",
        )
        self._log_text.pack(side="left", fill="both", expand=True, padx=4, pady=4)

        scrolly = ttk.Scrollbar(frame, orient="vertical",
                                 command=self._log_text.yview)
        scrolly.pack(side="right", fill="y")
        self._log_text.configure(yscrollcommand=scrolly.set)

        # Tags de color para el log
        self._log_text.tag_configure("cycle",   foreground=ACCENT,  font=("Consolas", 9, "bold"))
        self._log_text.tag_configure("pc",      foreground=ACCENT4)
        self._log_text.tag_configure("mnem",    foreground=TEXT_PRI)
        self._log_text.tag_configure("alu",     foreground=ACCENT2)
        self._log_text.tag_configure("signals", foreground=YELLOW)
        self._log_text.tag_configure("halt",    foreground=RED, font=("Consolas", 9, "bold"))
        self._log_text.tag_configure("sep",     foreground=TEXT_MUT)

    def _log_append(self, snapshot: CycleSnapshot):
        t = self._log_text
        t.configure(state="normal")

        if snapshot.stage == "HALT":
            t.insert("end", f"\n{'─'*50}\n", "sep")
            t.insert("end", "  ⏹  PROGRAMA TERMINADO\n", "halt")
            stats = f"  Total ciclos: {snapshot.cycle_number} | PC final: {self.proc.pc.value:#010x}\n"
            t.insert("end", stats, "signals")
        else:
            t.insert("end", f"#{snapshot.cycle_number:03d} ", "cycle")
            t.insert("end", f"PC={snapshot.pc:#010x} ", "pc")
            if snapshot.decoded:
                t.insert("end", f"{snapshot.decoded.mnemonic:<28}", "mnem")
            if snapshot.alu_result:
                t.insert("end", f"ALU={snapshot.alu_result.value:#010x} Z={int(snapshot.alu_result.zero)}", "alu")
            if snapshot.write_reg and snapshot.signals and snapshot.signals.reg_write:
                t.insert("end", f" → R{snapshot.write_reg}={snapshot.write_back:#010x}", "signals")
            t.insert("end", "\n")

        t.configure(state="disabled")
        t.see("end")

    # ─── Panel derecho ────────────────────────────────────────────────────

    def _build_right_panel(self, parent):
        nb = ttk.Notebook(parent)
        nb.pack(fill="both", expand=True)

        # Tab 1: Registros
        reg_tab = tk.Frame(nb, bg=BG_PANEL)
        nb.add(reg_tab, text="  Registros  ")
        self._build_registers_tab(reg_tab)

        # Tab 2: Memoria
        mem_tab = tk.Frame(nb, bg=BG_PANEL)
        nb.add(mem_tab, text="  Memoria  ")
        self._build_memory_tab(mem_tab)

        # Tab 3: Señales
        sig_tab = tk.Frame(nb, bg=BG_PANEL)
        nb.add(sig_tab, text="  Señales  ")
        self._build_signals_tab(sig_tab)

    def _build_registers_tab(self, parent):
        hdr = tk.Frame(parent, bg=BG_PANEL)
        hdr.pack(fill="x", padx=8, pady=(8, 4))
        tk.Label(hdr, text="Banco de Registros (32 × 32 bits)",
                 font=("Consolas", 9), fg=TEXT_SEC, bg=BG_PANEL).pack(side="left")

        container = tk.Frame(parent, bg=BG_PANEL)
        container.pack(fill="both", expand=True, padx=4)

        canvas = tk.Canvas(container, bg=BG_PANEL, bd=0, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        self._reg_frame = tk.Frame(canvas, bg=BG_PANEL)
        canvas_window = canvas.create_window((0, 0), window=self._reg_frame, anchor="nw")

        def on_frame_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        def on_canvas_configure(e):
            canvas.itemconfig(canvas_window, width=e.width)

        self._reg_frame.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)

        # Construir filas de registros
        self._reg_labels: dict[str, tk.Label] = {}
        from src.components.register_bank import REGISTER_NAMES
        for i in range(32):
            name = REGISTER_NAMES[i]
            row = tk.Frame(self._reg_frame, bg=BG_PANEL)
            row.pack(fill="x", padx=4, pady=1)

            tk.Label(row, text=f"{name:6s}", width=6,
                     font=("Consolas", 9), fg=ACCENT4,
                     bg=BG_PANEL, anchor="w").pack(side="left")
            tk.Label(row, text=f"({i:2d})", width=4,
                     font=("Consolas", 9), fg=TEXT_MUT,
                     bg=BG_PANEL).pack(side="left")

            lbl = tk.Label(row, text="0x00000000", width=12,
                           font=("Consolas", 9), fg=TEXT_PRI,
                           bg=BG_CARD, anchor="e", padx=4)
            lbl.pack(side="right", fill="x", expand=True)
            self._reg_labels[name] = lbl

    def _update_registers(self, snapshot: CycleSnapshot):
        """Actualiza la UI de registros, destacando el registro modificado."""
        regs = snapshot.registers
        for name, lbl in self._reg_labels.items():
            val = regs.get(name, 0)
            lbl.configure(text=f"{val:#010x}")

        # Destacar registro escrito
        if snapshot.signals and snapshot.signals.reg_write and snapshot.write_reg:
            from src.components.register_bank import REGISTER_NAMES
            written_name = REGISTER_NAMES.get(snapshot.write_reg)
            if written_name and written_name in self._reg_labels:
                lbl = self._reg_labels[written_name]
                lbl.configure(fg=ACCENT2, bg=BG_HOVER)
                self.root.after(800, lambda l=lbl: l.configure(fg=TEXT_PRI, bg=BG_CARD))

    def _build_memory_tab(self, parent):
        tk.Label(parent, text="Memoria de Datos (palabras no-cero)",
                 font=("Consolas", 9), fg=TEXT_SEC, bg=BG_PANEL).pack(
                     anchor="w", padx=8, pady=(8, 4))

        container = tk.Frame(parent, bg=BG_PANEL)
        container.pack(fill="both", expand=True, padx=4, pady=4)

        self._mem_text = tk.Text(
            container, bg=BG_CARD, fg=TEXT_PRI,
            font=("Consolas", 9), state="disabled",
            bd=0, padx=8, pady=4, relief="flat",
        )
        self._mem_text.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(container, orient="vertical",
                                   command=self._mem_text.yview)
        scrollbar.pack(side="right", fill="y")
        self._mem_text.configure(yscrollcommand=scrollbar.set)

        self._mem_text.tag_configure("addr",  foreground=ACCENT4)
        self._mem_text.tag_configure("val",   foreground=TEXT_PRI)
        self._mem_text.tag_configure("new",   foreground=ACCENT2,
                                      font=("Consolas", 9, "bold"))
        self._mem_text.tag_configure("empty", foreground=TEXT_MUT)

    def _update_memory(self, snapshot: CycleSnapshot):
        t = self._mem_text
        t.configure(state="normal")
        t.delete("1.0", "end")

        entries = self.proc.data_mem.dump()
        if not entries:
            t.insert("end", "  (vacía)\n", "empty")
        else:
            t.insert("end", f"  {'Dirección':<14} {'Valor (hex)':<12} {'Decimal'}\n", "addr")
            t.insert("end", f"  {'─'*40}\n", "empty")
            new_addrs = {addr for addr, _ in snapshot.memory_changes}
            for addr, val in entries:
                tag = "new" if addr in new_addrs else "val"
                t.insert("end", f"  {addr:#010x}     {val:#010x}     {val}\n", tag)

        t.configure(state="disabled")

    def _build_signals_tab(self, parent):
        tk.Label(parent, text="Señales de Control activas",
                 font=("Consolas", 9), fg=TEXT_SEC, bg=BG_PANEL).pack(
                     anchor="w", padx=8, pady=(8, 4))

        self._sig_frame = tk.Frame(parent, bg=BG_PANEL)
        self._sig_frame.pack(fill="both", expand=True, padx=8, pady=4)

        signal_defs = [
            ("RegDst",    "Registro destino: 1=rd, 0=rt"),
            ("ALUSrc",    "Fuente B ALU: 1=Inmediato, 0=Reg"),
            ("MemToReg",  "WB fuente: 1=Memoria, 0=ALU"),
            ("RegWrite",  "Habilitar escritura en registros"),
            ("MemRead",   "Habilitar lectura de memoria"),
            ("MemWrite",  "Habilitar escritura en memoria"),
            ("Branch",    "Instrucción de salto condicional"),
            ("Jump",      "Salto incondicional J/JAL"),
            ("ALUOp",     "Código de operación ALU (2 bits)"),
            ("ALUControl","Control fino de ALU (3 bits)"),
        ]

        self._signal_indicators: dict[str, tk.Label] = {}

        for sig, desc in signal_defs:
            row = tk.Frame(self._sig_frame, bg=BG_PANEL)
            row.pack(fill="x", pady=2)

            ind = tk.Label(row, text="●", font=("Consolas", 12),
                           fg=TEXT_MUT, bg=BG_PANEL, width=2)
            ind.pack(side="left")

            tk.Label(row, text=f"{sig:<12}", font=("Consolas", 9, "bold"),
                     fg=TEXT_PRI, bg=BG_PANEL, width=12,
                     anchor="w").pack(side="left")

            tk.Label(row, text=desc, font=("Consolas", 8),
                     fg=TEXT_SEC, bg=BG_PANEL).pack(side="left", padx=4)

            self._signal_indicators[sig] = ind

    def _update_signals(self, snapshot: CycleSnapshot):
        if not snapshot.signals:
            for ind in self._signal_indicators.values():
                ind.configure(fg=TEXT_MUT)
            return

        sigs = snapshot.signals.to_dict()
        for sig, ind in self._signal_indicators.items():
            val = sigs.get(sig, 0)
            if isinstance(val, bool) or sig not in ("ALUOp", "ALUControl"):
                color = ACCENT2 if val else TEXT_MUT
            else:
                color = ACCENT if val > 0 else TEXT_MUT
            ind.configure(fg=color,
                          text=f"{'●' if val else '○'}")

    # ─── Status bar ──────────────────────────────────────────────────────

    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg=BG_PANEL, height=24)
        bar.pack(fill="x", side="bottom")
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x", side="bottom")

        self._lbl_statusbar = tk.Label(
            bar, text="Ingresa código ensamblador y presiona ▶ Ensamblar",
            font=("Consolas", 8), fg=TEXT_SEC, bg=BG_PANEL
        )
        self._lbl_statusbar.pack(side="left", padx=8)

        tk.Label(bar, text="Andres Mogollon · Juan Bedoya · Michael Hurtado  |  Prof. David Romero",
                 font=("Consolas", 8), fg=TEXT_MUT, bg=BG_PANEL).pack(side="right", padx=8)

    # ═══════════════════════════════════════════════════════
    #  Event Handlers
    # ═══════════════════════════════════════════════════════

    def _on_assemble(self):
        source = self._editor.get("1.0", "end")
        try:
            instructions = self.asm.assemble(source)
            if not instructions:
                messagebox.showwarning("Advertencia", "El programa está vacío.")
                return
            self.proc.load_program(instructions)
            self._cycle_log.clear()
            self._log_text.configure(state="normal")
            self._log_text.delete("1.0", "end")
            self._log_text.configure(state="disabled")
            self._current_snapshot = None
            self._draw_datapath()

            count = len(instructions)
            self._set_status(f"✔  {count} instrucciones ensambladas correctamente", GREEN)
            self._statusbar(f"Programa cargado — {count} instrucciones | PC = 0x00000000")
            self._lbl_pc.configure(text="PC: 0x00000000")
            self._lbl_cycle.configure(text="Ciclo: 0")
            self._lbl_status.configure(text="● LISTO", fg=GREEN)
            self._btn_step.configure(state="normal")
            self._btn_auto.configure(state="normal")
            self._btn_reset.configure(state="normal")
            self._update_registers(CycleSnapshot(0, 0, 0,
                                                   registers=self.proc.registers.dump()))
            self._update_memory(CycleSnapshot(0, 0, 0))
        except AssemblerError as e:
            messagebox.showerror("Error de Ensamblado", str(e))
            self._set_status(f"✘  Error: {e.message}", RED)

    def _on_step(self):
        if self.proc.is_halted:
            messagebox.showinfo("Halt", "El procesador está detenido. Presiona Reset.")
            return
        try:
            snap = self.proc.step()
            self._current_snapshot = snap
            self._cycle_log.append(snap)
            self._animate_stages(snap)
        except Exception as e:
            messagebox.showerror("Error de Ejecución", str(e))

    # ── Animación de etapas del datapath ────────────────────────────────

    def _animate_stages(self, snap: CycleSnapshot):
        """
        Recorre visualmente IF→ID→EX→MEM→WB iluminando cada bloque
        en secuencia antes de actualizar los paneles con el resultado final.
        """
        if snap.stage in ("HALT", "ERROR"):
            self._update_ui(snap)
            return

        # Delay por etapa: proporcional a la velocidad configurada
        stage_delay_ms = max(55, int(self._auto_delay * 170))
        stages = ["IF", "ID", "EX", "MEM", "WB"]

        def show_stage(idx: int):
            if idx < len(stages):
                self._draw_datapath(stages[idx])
                self._lbl_status.configure(text=f"● {stages[idx]}", fg=ACCENT)
                self.root.after(stage_delay_ms, lambda: show_stage(idx + 1))
            else:
                # Animación completa → pintar paneles con datos reales
                self._update_ui(snap)

        show_stage(0)

    def _on_auto(self):
        if self._auto_running:
            self._auto_running = False
            self._btn_auto.configure(text="⏩  Auto")
            return
        self._auto_running = True
        self._btn_auto.configure(text="⏸  Pausar")
        threading.Thread(target=self._auto_run, daemon=True).start()

    def _auto_run(self):
        while self._auto_running and not self.proc.is_halted:
            self.root.after(0, self._on_step)
            # Esperar animación (5 etapas) + pausa entre ciclos
            anim_ms = max(55, int(self._auto_delay * 170)) * 5
            total_wait = self._auto_delay + anim_ms / 1000.0
            time.sleep(total_wait)
        self._auto_running = False
        self.root.after(0, lambda: self._btn_auto.configure(text="⏩  Auto"))

    def _on_reset(self):
        self._auto_running = False
        self.proc.reset()
        self._current_snapshot = None
        self._cycle_log.clear()
        self._log_text.configure(state="normal")
        self._log_text.delete("1.0", "end")
        self._log_text.configure(state="disabled")
        self._draw_datapath()
        self._lbl_pc.configure(text="PC: 0x00000000")
        self._lbl_cycle.configure(text="Ciclo: 0")
        self._lbl_status.configure(text="● LISTO", fg=GREEN)
        self._update_registers(CycleSnapshot(0, 0, 0,
                                              registers=self.proc.registers.dump()))
        self._update_memory(CycleSnapshot(0, 0, 0))
        for ind in self._signal_indicators.values():
            ind.configure(fg=TEXT_MUT, text="○")
        self._statusbar("Reset completo — PC = 0x00000000")

    def _on_open_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Assembly", "*.asm *.s *.txt"), ("Todos", "*.*")]
        )
        if path:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self._editor.delete("1.0", "end")
            self._editor.insert("1.0", content)
            self._on_editor_change()
            self._statusbar(f"Archivo cargado: {path}")

    # ═══════════════════════════════════════════════════════
    #  Actualización de UI
    # ═══════════════════════════════════════════════════════

    def _update_ui(self, snap: CycleSnapshot):
        """Actualiza header, datapath final y todos los paneles."""
        # Header
        self._lbl_cycle.configure(text=f"Ciclo: {snap.cycle_number}")
        self._lbl_pc.configure(text=f"PC: {snap.pc:#010x}")

        if snap.stage == "HALT":
            self._lbl_status.configure(text="⏹ HALT", fg=RED)
            self._btn_step.configure(state="disabled")
            self._btn_auto.configure(state="disabled")
            self._draw_datapath("HALT")
        elif snap.stage == "ERROR":
            self._lbl_status.configure(text="⚠ ERROR", fg=RED)
            self._draw_datapath("")
        else:
            # Mostrar WB como estado final del ciclo completado
            self._lbl_status.configure(text="● WB", fg=ACCENT)
            self._draw_datapath("WB")

        # Paneles laterales
        self._update_registers(snap)
        self._update_memory(snap)
        self._update_signals(snap)

        # Log de ciclos
        self._log_append(snap)

        # Status bar
        if snap.decoded:
            alu_str = f"{snap.alu_result.value:#010x}" if snap.alu_result else "0x00000000"
            self._statusbar(
                f"Ciclo {snap.cycle_number}: {snap.decoded.mnemonic}  |  "
                f"ALU={alu_str}  |  PC={snap.pc:#010x}"
            )

    # ═══════════════════════════════════════════════════════
    #  Helpers UI
    # ═══════════════════════════════════════════════════════

    def _card(self, parent, title: str) -> tk.Frame:
        outer = tk.Frame(parent, bg=BG_PANEL, bd=0)
        header = tk.Frame(outer, bg=BG_PANEL)
        header.pack(fill="x", padx=8, pady=(6, 0))
        tk.Label(header, text=title, font=("Consolas", 9, "bold"),
                 fg=TEXT_SEC, bg=BG_PANEL).pack(side="left")
        tk.Frame(outer, bg=BORDER, height=1).pack(fill="x", padx=0, pady=(4, 0))
        inner = tk.Frame(outer, bg=BG_CARD)
        inner.pack(fill="both", expand=True, padx=6, pady=6)
        return outer

    @staticmethod
    def _btn(parent, text, color, command, state="normal") -> tk.Button:
        return tk.Button(
            parent, text=text, command=command, state=state,
            bg=BG_HOVER, fg=color, activebackground=BG_CARD,
            activeforeground=color, font=("Consolas", 9, "bold"),
            bd=0, cursor="hand2", relief="flat",
        )

    def _set_status(self, text: str, color: str):
        self._lbl_status.configure(text=text, fg=color)

    def _statusbar(self, text: str):
        self._lbl_statusbar.configure(text=text)

    def _set_example_code(self):
        self._editor.insert("1.0", EXAMPLE_PROGRAM)
        self._on_editor_change()

    # ═══════════════════════════════════════════════════════
    #  Run
    # ═══════════════════════════════════════════════════════

    def run(self):
        self.root.mainloop()


def main():
    app = ProcessorGUI()
    app.run()


if __name__ == "__main__":
    main()
