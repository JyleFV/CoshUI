import tkinter as tk
from tkinter import ttk

from .types import CoshSignals
from .cui_error import warn

# I understand the code is kinda horrendus, but I don't know how to use tkinter
# Plus it doesn't need to be perfect so I don't really care
class CoshDebug:
    def __init__(self):
        warn("Debug Mode is active, be careful of leaving this turned on in production.")
        
        self.window = tk.Tk()
        self.window.title("CoshUI - Debug View")
        self.window.geometry("500x700")

        def on_close():
            print("CoshUIMessage: Close the main program to get rid of Debugger")

        self.window.protocol("WM_DELETE_WINDOW", on_close)

        self.selected_node = None
        self.selected_class = None

        self.tree = ttk.Treeview(self.window)
        self.tree.heading("#0", text="UI Tree Preview", anchor="w")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        prop_label = tk.Label(self.window, text="Selected Node Properties:", anchor="w")
        prop_label.pack(fill="x", padx=5, pady=2)
        
        self.prop_text = tk.Text(self.window, height=30, bg="#f8f9fa", state="disabled", wrap="none")
        self.prop_text.pack(fill="x", padx=5, pady=5)

        def on_select(event):
            selection = self.tree.selection()
            if selection:
                vals = self.tree.item(selection[0], "values")
                if vals and len(vals) >= 2:
                    self.selected_node = vals[0]
                    self.selected_class = vals[1]

        self.tree.bind("<<TreeviewSelect>>", on_select)
        self.window.update()

    def render(self, ui_root, render_stack, signals):
        # Tree logic
        selected = self.tree.selection()
        selected_text = self.tree.item(selected[0], "text") if selected else None
        current_tree_scroll = self.tree.yview()
        
        open_node_ids = set()
        def collect_open_nodes(parent=""):
            for item in self.tree.get_children(parent):
                if self.tree.item(item, "open"):
                    vals = self.tree.item(item, "values")
                    if vals: open_node_ids.add(vals[0])
                    collect_open_nodes(item)
        collect_open_nodes()

        self.tree.delete(*self.tree.get_children())

        def build_tree_nodes(parent_id, current_node):
            class_name = current_node.__class__.__name__
            node_id_attr = getattr(current_node, "id", "No ID")
            tree_row_id = self.tree.insert(
                parent_id, "end", text=f"{class_name} # {node_id_attr}", 
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
                    if reselect(item): return True
                return False
            reselect()
        self.tree.yview_moveto(current_tree_scroll[0])

        # Property logic
        target_node = next((n for n in render_stack if getattr(n, "id", None) == self.selected_node), None)
        
        if not target_node:
            self.prop_text.config(state="normal")
            self.prop_text.delete("1.0", tk.END)
            self.prop_text.config(state="disabled")
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

            raw_color_val = target_node.background_color
            color_val = fmt(raw_color_val)
            
            props_display = "---------- Node ----------\n\n"
            props_display += f"Component: {self.selected_class}\nID: {target_node.id}\n\n"
            props_display += "---------- Layout ----------\n\n"
            props_display += f"Position: ({fmt(target_node.x)}, {fmt(target_node.y)})\n"
            props_display += f"Dimensions: {fmt(target_node.width)} x {fmt(target_node.height)}\n"
            props_display += f"Padding: {fmt(getattr(target_node, 'padding', '0'))}\n"
            props_display += f"Margin: {fmt(getattr(target_node, 'margin', '0'))}\n"
            props_display += f"Z-Index: {target_node.z_index}\n\n"
            props_display += "---------- Styling ----------\n\n"
            props_display += f"Transform Pos: ({fmt(target_node.transform_x)}, {fmt(target_node.transform_y)})\n"
            
            # Placeholder for the color chip injection
            props_display += f"Background Color: " 
            color_preview_index = f"1.0 + {len(props_display)} chars"
            props_display += f" {color_val}\n"
            
            props_display += f"Border Radius: {fmt(target_node.border_radius)}\n"
            props_display += f"Transform Scale: {fmt(target_node.transform_scale)}\n"
            props_display += f"Transform Rotation: {fmt(target_node.transform_rotation)}\n"
            props_display += f"Border: {fmt(target_node.border)}\n"
            props_display += f"Alpha: {fmt(target_node.alpha)}\n\n"
            props_display += "---------- Events ----------\n\n"
            props_display += f"Mouse Filter: {target_node.mouse_filter}\n\n"
            props_display += "---------- Text ----------\n\n"
            props_display += f"Text: {repr(target_node.text)}\n"
            props_display += f"Text Color: {fmt(target_node.text_color)}\n"
            props_display += f"Font Path: {target_node.font}\n"
            props_display += f"Font Size: {fmt(target_node.font_size)}\n"
            props_display += f"Text Justify: {target_node.text_justify}\n"
            props_display += f"Text Align: {target_node.text_align}\n"
            props_display += f"Text Overflow: {target_node.text_overflow}\n\n"
            props_display += "---------- Image ----------\n\n"
            props_display += f"Image Source: {target_node.image_src}\n\n"
            props_display += "---------- Signals This Frame ----------\n\n"
            props_display += f"CLICKED: {CoshSignals.CLICKED in signals.get(self.selected_node, set())}\n"
            props_display += f"RELEASED: {CoshSignals.RELEASED in signals.get(self.selected_node, set())}\n"
            props_display += f"PRESSED: {CoshSignals.PRESSED in signals.get(self.selected_node, set())}\n"
            props_display += f"HOVERED: {CoshSignals.HOVERED in signals.get(self.selected_node, set())}\n"
            props_display += f"HOVER_ENTER: {CoshSignals.HOVER_ENTER in signals.get(self.selected_node, set())}\n"
            props_display += f"HOVER_EXIT: {CoshSignals.HOVER_EXIT in signals.get(self.selected_node, set())}\n"

            current_scroll = self.prop_text.yview()
            self.prop_text.config(state="normal")
            self.prop_text.delete("1.0", tk.END)
            self.prop_text.insert("1.0", props_display)

            # Color Chip logic
            tk_color = "white"
            if isinstance(raw_color_val, tuple) and len(raw_color_val) >= 3:
                try:
                    r, g, b = raw_color_val[0], raw_color_val[1], raw_color_val[2]
                    r_int = int((r if r > 1.0 else r * 255))
                    g_int = int((g if g > 1.0 else g * 255))
                    b_int = int((b if b > 1.0 else b * 255))
                    tk_color = f"#{max(0, min(255, r_int)):02x}{max(0, min(255, g_int)):02x}{max(0, min(255, b_int)):02x}"
                except (ValueError, TypeError): tk_color = "white"
            elif isinstance(raw_color_val, str): tk_color = raw_color_val

            color_chip = tk.Frame(self.prop_text, bg=tk_color, width=15, height=15, relief="solid", bd=1)
            self.prop_text.window_create(color_preview_index, window=color_chip)

            self.prop_text.yview_moveto(current_scroll[0])
            self.prop_text.config(state="disabled")

        self.window.update_idletasks()
        self.window.update()