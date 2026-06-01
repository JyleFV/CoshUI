import threading
import tkinter as tk
from tkinter import ttk
from .cui_error import warn

# I understand the code is kinda horrendus, but I don't know how to use tkinter
# Plus it doesn't need to be perfect so I don't really care
class CoshDebug(threading.Thread):
    def __init__(self):
        super().__init__()
        warn("Debug Mode is active, be careful of leaving this turned on in production.")
        
        self.selected_node = None
        self.selected_class = None
        self.ui_root = None
        self.render_stack = None
        self.daemon = True
        
        self.window = None
        self.started = False
        self.prop_text = None

    def run(self):
        self.window = tk.Tk()
        self.window.title("CoshUI - Debug View")
        self.window.geometry("500x700")
        
        def on_close():
            print("CoshUIMessage: Close the main program to get rid of Debugger")

        self.window.protocol("WM_DELETE_WINDOW", on_close)

        tree = ttk.Treeview(self.window)
        tree.heading("#0", text="UI Tree Preview", anchor="w")
        tree.pack(fill="both", expand=True, padx=5, pady=5)

        # -------------------- Bottom Property Box --------------------
        prop_label = tk.Label(self.window, text="Selected Node Properties:", anchor="w")
        prop_label.pack(fill="x", padx=5, pady=2)
        
        self.prop_text = tk.Text(self.window, height=30, bg="#f8f9fa", state="disabled")
        self.prop_text.pack(fill="x", padx=5, pady=5)

        def on_select(event):
            selection = tree.selection()
            if selection:
                vals = tree.item(selection[0], "values")
                if vals and len(vals) >= 2:
                    self.selected_node = vals[0]
                    self.selected_class = vals[1]

        tree.bind("<<TreeviewSelect>>", on_select)

        while True:
            try:
                if self.ui_root is not None:
                    selected = tree.selection()
                    selected_text = tree.item(selected[0], "text") if selected else None

                    current_tree_scroll = tree.yview()
                    open_node_ids = set()
                    has_history = False
                    
                    def collect_open_nodes(parent=""):
                        nonlocal has_history
                        for item in tree.get_children(parent):
                            has_history = True
                            if tree.item(item, "open"):
                                vals = tree.item(item, "values")
                                if vals:
                                    open_node_ids.add(vals[0])
                            collect_open_nodes(item)
                    collect_open_nodes()

                    tree.delete(*tree.get_children())

                    def build_tree_nodes(parent_id, current_node):
                        class_name = current_node.__class__.__name__
                        node_id_attr = getattr(current_node, "id", "No ID")
                        display_text = f"{class_name} # {node_id_attr}"

                        if not has_history:
                            is_open = True
                        else:
                            is_open = node_id_attr in open_node_ids
                        
                        tree_row_id = tree.insert(
                            parent_id, 
                            "end", 
                            text=display_text, 
                            values=(node_id_attr, class_name), 
                            open=is_open
                        )

                        children_list = getattr(current_node, "children", [])
                        for child in children_list:
                            build_tree_nodes(tree_row_id, child)
                    try:
                        root_children = getattr(self.ui_root, "children", [])
                        for child in root_children:
                            build_tree_nodes("", child)
                    except RuntimeError:
                        pass

                    if selected_text:
                        def reselect(parent=""):
                            for item in tree.get_children(parent):
                                if tree.item(item, "text") == selected_text:
                                    tree.selection_set(item)
                                    return True
                                if reselect(item):
                                    return True
                            return False
                        reselect()

                    tree.yview_moveto(current_tree_scroll[0])

                if self.selected_node and self.render_stack:
                    target_node = None 
                    for data in self.render_stack:
                        if getattr(data, "id", None) == self.selected_node:
                            target_node = data
                            break
                    
                    if not target_node:
                        self.prop_text.config(state="normal")
                        self.prop_text.delete("1.0", tk.END)
                        self.prop_text.config(state="disabled")
                    else:
                        color_val = target_node.background_color
                        
                        props_display = ""
                        props_display += "---------- Node  ----------\n"
                        props_display += "\n"
                        props_display += f"Component: {getattr(self, 'selected_class', 'Unknown')}\n"
                        props_display += f"ID: {target_node.id}\n"
                        props_display += "\n"
                        props_display += "---------- Layout ----------\n"
                        props_display += "\n"
                        props_display += f"Position: ({target_node.x}, {target_node.y})\n"
                        props_display += f"Dimensions: {target_node.width} x {target_node.height}\n"
                        props_display += f"Padding: {getattr(target_node, 'padding', '0')}\n"
                        props_display += f"Margin: {getattr(target_node, 'margin', '0')}\n"
                        props_display += f"Z-Index: {target_node.z_index}\n"
                        props_display += "\n"
                        props_display += "---------- Styling ----------\n"
                        props_display += "\n"
                        props_display += f"Transform Pos: ({target_node.transform_x}, {target_node.transform_y})\n"

                        props_display += f"Background Color: " 
                        color_preview_index = f"1.0 + {len(props_display)} chars"
                        props_display += f" {color_val}\n" 
                        
                        props_display += f"Border Radius: {target_node.border_radius}\n"
                        props_display += f"Transform Scale: {target_node.transform_scale}\n"
                        props_display += f"Transform Rotation: {target_node.transform_rotation}\n"
                        props_display += f"Border: {target_node.border}\n"
                        props_display += f"Alpha: {target_node.alpha}\n"
                        props_display += "\n"
                        props_display += "---------- Events ----------\n"
                        props_display += "\n"
                        props_display += f"Mouse Filter: {target_node.mouse_filter}\n"
                        props_display += "\n"
                        props_display += "---------- Text ----------\n"
                        props_display += "\n"
                        props_display += f"Text: {repr(target_node.text)}\n"
                        props_display += f"Text Color: {target_node.text_color}\n"
                        props_display += f"Font Path: {target_node.font}\n"
                        props_display += f"Font Size: {target_node.font_size}\n"
                        props_display += f"Text Justify: {target_node.text_justify}\n"
                        props_display += f"Text Align: {target_node.text_align}\n"
                        props_display += f"Text Overflow: {target_node.text_overflow}\n"
                        props_display += "\n"
                        props_display += "---------- Image ----------\n"
                        props_display += "\n"
                        props_display += f"Image Source: {target_node.image_src}\n"

                        current_text = self.prop_text.get("1.0", "end-1c")
                        
                        if current_text != props_display:
                            current_scroll = self.prop_text.yview()

                            self.prop_text.config(state="normal")
                            self.prop_text.delete("1.0", tk.END)
                            self.prop_text.insert("1.0", props_display)

                            tk_color = "white"
                            if isinstance(color_val, tuple) and len(color_val) >= 3:
                                try:
                                    r, g, b = color_val[0], color_val[1], color_val[2]
                                    if isinstance(r, float) and r <= 1.0 and g <= 1.0 and b <= 1.0:
                                        r_int, g_int, b_int = int(r * 255), int(g * 255), int(b * 255)
                                    else:
                                        r_int, g_int, b_int = int(r), int(g), int(b)
                                    r_int = max(0, min(255, r_int))
                                    g_int = max(0, min(255, g_int))
                                    b_int = max(0, min(255, b_int))
                                    tk_color = f"#{r_int:02x}{g_int:02x}{b_int:02x}"
                                except (ValueError, TypeError):
                                    tk_color = "white"
                            elif isinstance(color_val, str):
                                tk_color = color_val

                            color_chip = tk.Frame(self.prop_text, bg=tk_color, width=15, height=15, relief="solid", bd=1)
                            self.prop_text.window_create(color_preview_index, window=color_chip)

                            self.prop_text.yview_moveto(current_scroll[0])
                            self.prop_text.config(state="disabled")

                self.window.update_idletasks()
                self.window.update()
            except (tk.TclError, AttributeError):
                self.is_alive = False
                break

    def render(self):
        """Called every frame in the main game loop."""
        if not self.started:
            self.start() 
            self.started = True