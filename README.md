<div align="center">

# CoshUI
### The Python-first, Declarative-Mode, Backend Agnostic, UI Library.

![CoshUI Logo](/assets/coshui_logo.png)

</div>

## What is CoshUI?
CoshUI is a Python-first, declarative-mode UI library inspired by HTML, CSS, and Godot. Unlike most Python UI libraries, CoshUI is fully backend-agnostic. Write your UI once and render it with Pygame, Raylib, PyOpenGL, or any backend you build. With an intuitive, web-like structure and a clean API, CoshUI is designed to be simple to pick up without sacrificing flexibility.

## How to Install

### Get started on CoshUI:
```
pip install coshui
```

---

Due to CoshUI being *backend-agnostic* you can use CoshUI with different dependencies which lets you use their specific backends.

**For the Pygame Dependency:**
```
pip install coshui[pygame]
```
**For the Raylib Dependency:**
```
pip install coshui[raylib]
```

## How to Use
CoshUI features a very simple API, using Python's *context managers*, it follows modernized Python. An example of the UI in action:

```python
# Import CoshUI
import coshui as cui

...

# Within your loop

# 1. Write your UI Structure 
with cui.CoshUIRenderer(...):
    with cui.Container(id="main_container", width=cui.FILL, height=cui.FILL, direction=cui.ROW, align=cui.ALIGN_CENTER, justify=cui.JUSTIFY_CENTER, gap=5.0):
        cui.Label(id="menu_label", text="CoshUI", width=200, height=50, font_size=64)
        cui.Button(id="print_btn", text="Print Hello World!")
        cui.Button(id="color_btn", text="Change Container Color!")

# 2. Listen for the `CLICKED` signal that gets emitted by the Button Node.
if cui.get_signal("print_btn", cui.CLICKED):
    print("Hello World!")

# 3. Animate the container's background color using the built in animation system.
if cui.get_signal("color_btn", cui.CLICKED):
    cui.animate("background_color", "main_container", (200, 200, 200), 1.5, "ease_in_out") 
```

To learn more, check out our [examples](/examples/examples.md) or visit the [website](https://terrarizer03.github.io/coshui-docs/)

## Author
**Main Developer and Maintainer:** Jyle Frazier (Terra) Villareal

## Contact
- Socials: [GitHub](https://github.com/JyleFV) • [X/Twitter](https://x.com/JyleFV)
- Email: jylefraziervillareal@gmail.com