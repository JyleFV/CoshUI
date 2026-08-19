import tkinter as tk
from tkinter import ttk
from collections import deque

from .types import CoshSignals
from .cui_error import CoshUIError

# Kinda horrendous but it's a debug tool so I don't really care
# Most this file was vibecoded, so I'm not sure what's going on here most of the time
class CoshDebug:
    GRAPH_COLORS = {
        "build_time": "#ff1cf0", 
        "update": "#e9ff42",
        "final_default": "#20ffe5",
        "measure": "#4fc3f7",
        "layout": "#81c784",
        "render": "#ffb74d",
        "process_events": "#f06292",
        "backend_render": "#ff1616"
    }

    # Inspector color scheme
    BG = "#1e1e2e"
    BG_LIGHT = "#2a2a3e"
    FG = "#cdd6f4"
    FG_DIM = "#6c7086"
    ACCENT = "#89b4fa"
    GREEN = "#a6e3a1"
    YELLOW = "#f9e2af"
    RED = "#f38ba8"
    MAUVE = "#cba6f7"

    def __init__(self):
        CoshUIError.warn("Debug Mode is active, expect performance issues on the main process. Be careful of leaving this turned on in production.")

        self.window = tk.Tk()
        self.window.title("CoshUI - Debug View")
        self.window.geometry("520x750")
        self.window.configure(bg=self.BG)

        def on_close():
            print("CoshUIMessage: Close the main program to get rid of Debugger")
        self.window.protocol("WM_DELETE_WINDOW", on_close)

        self._last_selected_node = None

        # Style ttk elements
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=self.BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=self.BG_LIGHT, foreground=self.FG_DIM, padding=(12, 4), font=("Courier", 9))
        style.map("TNotebook.Tab", background=[("selected", self.BG)], foreground=[("selected", self.ACCENT)])
        style.configure("TFrame", background=self.BG)
        style.configure("Treeview", background=self.BG_LIGHT, foreground=self.FG, fieldbackground=self.BG_LIGHT, font=("Courier", 9), rowheight=22, borderwidth=0)
        style.configure("Treeview.Heading", background=self.BG, foreground=self.ACCENT, font=("Courier", 9, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", "#313244")], foreground=[("selected", self.ACCENT)])

        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill="both", expand=True, padx=0, pady=0)

        inspector_frame = ttk.Frame(self.notebook)
        self.profiler_frame = ttk.Frame(self.notebook)

        self.notebook.add(inspector_frame, text="   Inspector  ")
        self.notebook.add(self.profiler_frame, text="   Profiler  ")

        self.selected_node = None
        self.selected_class = None

        # ---- Inspector Tab ----

        # Tree section
        tree_header = tk.Label(inspector_frame, text="UI TREE", bg=self.BG, fg=self.FG_DIM, font=("Courier", 8), anchor="w", padx=8, pady=4)
        tree_header.pack(fill="x")

        tree_container = tk.Frame(inspector_frame, bg=self.BG_LIGHT, bd=0)
        tree_container.pack(fill="both", expand=True, padx=8, pady=(0, 6))

        self.tree = ttk.Treeview(tree_container, show="tree")
        tree_scroll = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")

        # Property section
        prop_header = tk.Label(inspector_frame, text="PROPERTIES", bg=self.BG, fg=self.FG_DIM, font=("Courier", 8), anchor="w", padx=8, pady=4)
        prop_header.pack(fill="x")

        prop_container = tk.Frame(inspector_frame, bg=self.BG_LIGHT)
        prop_container.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.prop_text = tk.Text(
            prop_container,
            bg=self.BG_LIGHT,
            fg=self.FG,
            font=("Courier", 9),
            state="disabled",
            wrap="none",
            relief="flat",
            bd=0,
            padx=8,
            pady=6,
            cursor="arrow",
            selectbackground="#313244",
            insertbackground=self.FG,
        )

        prop_scroll = ttk.Scrollbar(prop_container, orient="vertical", command=self.prop_text.yview)
        self.prop_text.configure(yscrollcommand=prop_scroll.set)
        self.prop_text.pack(side="left", fill="both", expand=True)
        prop_scroll.pack(side="right", fill="y")

        # Text tags for syntax highlighting
        self.prop_text.tag_configure("section", foreground=self.ACCENT, font=("Courier", 9, "bold"))
        self.prop_text.tag_configure("key", foreground=self.FG_DIM, font=("Courier", 9))
        self.prop_text.tag_configure("value", foreground=self.FG, font=("Courier", 9))
        self.prop_text.tag_configure("true", foreground=self.GREEN, font=("Courier", 9))
        self.prop_text.tag_configure("false", foreground=self.RED, font=("Courier", 9))
        self.prop_text.tag_configure("number", foreground=self.YELLOW, font=("Courier", 9))
        self.prop_text.tag_configure("none", foreground=self.FG_DIM, font=("Courier", 9, "italic"))
        self.prop_text.tag_configure("component", foreground=self.MAUVE, font=("Courier", 9, "bold"))

        def on_select(event):
            selection = self.tree.selection()
            if selection:
                vals = self.tree.item(selection[0], "values")
                if vals and len(vals) >= 2:
                    self.selected_node = vals[0]
                    self.selected_class = vals[1]

        self.tree.bind("<<TreeviewSelect>>", on_select)

        # ---- Profiler Tab ----
        self._timing_buffers = {key: deque(maxlen=100) for key in self.GRAPH_COLORS}

        stats_frame = tk.Frame(self.profiler_frame, bg=self.BG)
        stats_frame.pack(fill="x", padx=8, pady=8)

        self._avg_labels = {}
        for key, color in self.GRAPH_COLORS.items():
            row = tk.Frame(stats_frame, bg=self.BG)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"{key}:", fg=color, bg=self.BG, font=("Courier", 10), width=16, anchor="w").pack(side="left")
            lbl = tk.Label(row, text="0.0000ms", fg=self.FG, bg=self.BG, font=("Courier", 10), anchor="w")
            lbl.pack(side="left")
            self._avg_labels[key] = lbl

        separator = tk.Frame(self.profiler_frame, bg=self.BG_LIGHT, height=1)
        separator.pack(fill="x", padx=8, pady=4)

        self._total_label = tk.Label(self.profiler_frame, text="total: 0.0000ms", fg=self.FG, bg=self.BG, font=("Courier", 10, "bold"), anchor="w")
        self._total_label.pack(fill="x", padx=8, pady=4)

        separator2 = tk.Frame(self.profiler_frame, bg=self.BG_LIGHT, height=1)
        separator2.pack(fill="x", padx=8, pady=4)

        self._node_count_label = tk.Label(self.profiler_frame, text="Node Count: 0", fg=self.FG_DIM, bg=self.BG, font=("Courier", 10), anchor="w")
        self._node_count_label.pack(fill="x", padx=8, pady=4)

        self._graph_canvas = tk.Canvas(self.profiler_frame, bg=self.BG, height=200, highlightthickness=0)
        self._graph_canvas.pack(fill="both", expand=True, padx=8, pady=8)

        legend_frame = tk.Frame(self.profiler_frame, bg=self.BG)
        legend_frame.pack(fill="x", padx=8, pady=4)
        for key, color in self.GRAPH_COLORS.items():
            tk.Label(legend_frame, text=f"■ {key}", fg=color, bg=self.BG, font=("Courier", 9)).pack(side="left", padx=6)

        self.window.update()

    def _insert_prop(self, key, value):
        """Insert a key: value line with appropriate tag for the value."""
        self.prop_text.insert(tk.END, f"  {key}: ", "key")

        if value is None or value == "None":
            self.prop_text.insert(tk.END, "None\n", "none")
        elif isinstance(value, bool) or value is True or value is False:
            tag = "true" if value else "false"
            self.prop_text.insert(tk.END, f"{value}\n", tag)
        elif isinstance(value, (int, float)):
            self.prop_text.insert(tk.END, f"{value}\n", "number")
        else:
            self.prop_text.insert(tk.END, f"{value}\n", "value")

    def _insert_section(self, title):
        self.prop_text.insert(tk.END, f"\n{title}\n", "section")

    def render(self, ui_root, render_stack, signals, timings=None):
        # ---- Tree logic ----
        selected = self.tree.selection()
        selected_text = self.tree.item(selected[0], "text") if selected else None
        current_tree_scroll = self.tree.yview()

        open_node_ids = set()
        def collect_open_nodes(parent=""):
            for item in self.tree.get_children(parent):
                if self.tree.item(item, "open"):
                    vals = self.tree.item(item, "values")
                    if vals:
                        open_node_ids.add(vals[0])
                    collect_open_nodes(item)
        collect_open_nodes()

        self.tree.delete(*self.tree.get_children())

        def build_tree_nodes(parent_id, current_node):
            class_name = current_node.__class__.__name__
            node_id_attr = getattr(current_node, "id", "No ID")
            label = f"{class_name}  #{node_id_attr}" if node_id_attr != "No ID" else class_name
            tree_row_id = self.tree.insert(
                parent_id, "end", text=label,
                values=(node_id_attr, class_name), open=(node_id_attr in open_node_ids)
            )
            for child in getattr(current_node, "children", []):
                build_tree_nodes(tree_row_id, child)

        for child in getattr(ui_root, "children", []):
            build_tree_nodes("", child)

        if selected_text:
            def reselect(parent=""):
                for item in self.tree.get_children(parent):
                    if self.tree.item(item, "text") == selected_text:
                        self.tree.selection_set(item)
                        return True
                    if reselect(item):
                        return True
                return False
            reselect()
        self.tree.yview_moveto(current_tree_scroll[0])

        # ---- Property logic ----
        target_node = next((n for n in render_stack if getattr(n, "id", None) == self.selected_node), None)

        same_node = self._last_selected_node == self.selected_node
        self._last_selected_node = self.selected_node

        # Capture the exact vertical scroll fraction before modifying text
        current_prop_index = self.prop_text.index("@0,0")

        self.prop_text.config(state="normal")
        self.prop_text.delete("1.0", tk.END)

        if not target_node:
            self.prop_text.insert(tk.END, "\n  Select a node to inspect.", "none")
        else:
            def fmt(val):
                if isinstance(val, float):
                    s = f"{val:.3f}"
                    return s.rstrip('0').rstrip('.') if '.' in s else s
                if isinstance(val, tuple):
                    try:
                        return tuple(float(fmt(v)) for v in val)
                    except (ValueError, TypeError):
                        return tuple(fmt(v) for v in val)
                return val

            # Component header
            self.prop_text.insert(tk.END, f"  {self.selected_class}", "component")
            self.prop_text.insert(tk.END, f"  #{target_node.id}\n", "none")

            self._insert_section("  ── Layout ─────────────────────")
            self._insert_prop("position", f"({fmt(target_node.x)}, {fmt(target_node.y)})")
            self._insert_prop("dimensions", f"{fmt(target_node.width)} × {fmt(target_node.height)}")
            self._insert_prop("padding", fmt(getattr(target_node, "padding", 0)))
            self._insert_prop("margin", fmt(getattr(target_node, "margin", 0)))
            self._insert_prop("z_index", target_node.z_index)

            self._insert_section("  ── Styling ─────────────────────")
            self._insert_prop("transform_pos", f"({fmt(target_node.transform_x)}, {fmt(target_node.transform_y)})")

            # Color chip inline
            raw_color_val = target_node.background_color
            color_val = fmt(raw_color_val)
            self.prop_text.insert(tk.END, "  background_color: ", "key")
            color_preview_index = self.prop_text.index(tk.END + "-1c")
            self.prop_text.insert(tk.END, f" {color_val}\n", "value")

            self._insert_prop("border_radius", fmt(target_node.border_radius))
            self._insert_prop("transform_scale", fmt(target_node.transform_scale))
            self._insert_prop("transform_rotation", fmt(target_node.transform_rotation))
            self._insert_prop("border", fmt(target_node.border))
            self._insert_prop("alpha", fmt(target_node.alpha))

            self._insert_section("  ── Events ──────────────────────")
            self._insert_prop("mouse_filter", target_node.mouse_filter)

            self._insert_section("  ── Text ────────────────────────")
            text_data = target_node.text_data
            first_run = text_data.runs[0] if text_data and text_data.runs else None
            self._insert_prop("text", repr(text_data.text if text_data else None))
            self._insert_prop("text_color", fmt(first_run.color if first_run else None))
            self._insert_prop("font", first_run.font if first_run else None)
            self._insert_prop("font_size", fmt(first_run.font_size if first_run else None))
            self._insert_prop("text_justify", text_data.text_justify if text_data else None)
            self._insert_prop("text_align", text_data.text_align if text_data else None)
            self._insert_prop("text_overflow", text_data.text_overflow if text_data else None)

            self._insert_section("  ── Image ───────────────────────")
            self._insert_prop("image_src", target_node.image_src)

            self._insert_section("  ── Signals This Frame ──────────")
            node_signals = signals.get(self.selected_node, set())
            for sig in (CoshSignals.CLICKED, CoshSignals.RELEASED, CoshSignals.PRESSED,
                        CoshSignals.HOVERED, CoshSignals.HOVER_ENTER, CoshSignals.HOVER_EXIT):
                active = sig in node_signals
                self.prop_text.insert(tk.END, f"  {sig.name}: ", "key")
                self.prop_text.insert(tk.END, f"{'True' if active else 'False'}\n", "true" if active else "false")

            # Color chip
            tk_color = "white"
            if isinstance(raw_color_val, tuple) and len(raw_color_val) >= 3:
                try:
                    r, g, b = raw_color_val[0], raw_color_val[1], raw_color_val[2]
                    r_int = int(r if r > 1.0 else r * 255)
                    g_int = int(g if g > 1.0 else g * 255)
                    b_int = int(b if b > 1.0 else b * 255)
                    tk_color = f"#{max(0,min(255,r_int)):02x}{max(0,min(255,g_int)):02x}{max(0,min(255,b_int)):02x}"
                except (ValueError, TypeError):
                    tk_color = "white"
            elif isinstance(raw_color_val, str):
                tk_color = raw_color_val

            color_chip = tk.Frame(self.prop_text, bg=tk_color, width=14, height=14, relief="flat", bd=1)
            self.prop_text.window_create(color_preview_index, window=color_chip)

        self.prop_text.config(state="disabled")

        # Restore the previous viewport.
        if not same_node:
            self.prop_text.yview_moveto(0)
        else:
            try:
                self.prop_text.yview(current_prop_index)
            except tk.TclError:
                # If the document became shorter, just clamp to the end.
                self.prop_text.yview_moveto(1.0)

        if timings is not None and self.notebook.index(self.notebook.select()) == 1:
            self._update_profiler(timings, len(render_stack))

        self.window.update_idletasks()
        self.window.update()

    def _update_profiler(self, timings: dict, node_count: int):
        for key, value in timings.items():
            self._timing_buffers[key].append(value * 1000)

        for key, buf in self._timing_buffers.items():
            if buf:
                avg = sum(buf) / len(buf)
                self._avg_labels[key].config(text=f"{avg:.4f}ms")

        total = sum(sum(buf) / len(buf) for buf in self._timing_buffers.values() if buf)
        self._total_label.config(text=f"total: {total:.4f}ms")
        self._node_count_label.config(text=f"Node Count: {node_count}")

        canvas = self._graph_canvas
        canvas.delete("all")
        w = canvas.winfo_width()
        h = canvas.winfo_height()

        if w <= 1:
            return

        left_margin = 52

        all_values = [v for buf in self._timing_buffers.values() for v in buf]
        max_val = max(all_values) if all_values else 1.0
        if max_val == 0:
            max_val = 1.0

        # Grid lines and Y axis labels
        for i in range(5):
            gy = int(h * i / 4)
            canvas.create_line(left_margin, gy, w, gy, fill=self.BG_LIGHT, width=1)
            val_at_line = max_val * (1 - i / 4)
            label = f"{val_at_line:.1f}ms"
            canvas.create_text(4, gy + 2, text=label, fill=self.FG_DIM, font=("Courier", 7), anchor="nw")

        # Graph lines
        for key, color in self.GRAPH_COLORS.items():
            buf = list(self._timing_buffers[key])
            if len(buf) < 2:
                continue

            step = (w - left_margin) / (len(buf) - 1)
            points = []
            for i, val in enumerate(buf):
                px = left_margin + i * step
                py = h - (val / max_val) * h * 0.9
                points.extend([px, py])

            if len(points) >= 4:
                canvas.create_line(points, fill=color, width=2, smooth=True)