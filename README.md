<div align="center">

# CoshUI
### The Python-first, Declarative-Mode, Backend Agnostic, UI Library.

![CoshUI Logo](https://raw.githubusercontent.com/JyleFV/CoshUI/main/assets/coshui_logo.png)

[![PyPI version](https://img.shields.io/pypi/v/coshui?color=blue&style=flat-square)](https://pypi.org/project/coshui/)
[![Python](https://img.shields.io/pypi/pyversions/coshui?style=flat-square)](https://pypi.org/project/coshui/)
[![License](https://img.shields.io/pypi/l/coshui?style=flat-square)](https://gitlab.com/jylefv/CoshUI/-/blob/main/LICENSE)
[![GitLab](https://img.shields.io/badge/gitlab-primary%20repo-orange?style=flat-square&logo=gitlab)](https://gitlab.com/jylefv/CoshUI)
[![Docs](https://img.shields.io/badge/docs-website-green?style=flat-square)](https://terrarizer03.github.io/coshui-docs/)

</div>

## Table of Contents
- [What is CoshUI?](#what-is-coshui)
- [How to Install](#how-to-install)
- [How to Use and Example](#how-to-use-and-what-it-renders-in-pygame)
- [Documentation](#documentation)
- [How to Contribute](#contributing)
- [Author](#author)
- [Socials and Contact](#contact)

## What is CoshUI?
CoshUI is a Python-first, declarative UI library inspired by CSS, Godot, React, and Dear ImGui. Unlike most Python UI libraries, CoshUI is fully backend-agnostic — write your UI once and render it with Pygame, Raylib, ModernGL, or any backends you build or are supported.

CoshUI features:
- Full layout engine with flexbox-inspired sizing
- Retained-state reconciliation system
- Tween animation with configurable easing
- Signal-based event model
- Theme system with class support
- CoshML — a markup language for rich inline text styling
- Built-in debugger with live node inspector and profiler
- And more...

All within in a declarative API that's simple to pick up without sacrificing flexibility.

## How to Install

```bash
pip install coshui
```

CoshUI is backend-agnostic — install with your renderer of choice:
```bash
# Pygame
pip install coshui[pygame]

# Raylib
pip install coshui[raylib]

# ModernGL
pip install coshui[moderngl] # or [moderngl-mglw]

# PyOpenGL
pip install coshui[pyopengl]

# All
pip install coshui[all]
```

## How to Use and What it Renders (in Pygame)
CoshUI uses Python's context managers to define UI hierarchy through indentation — familiar if you've worked with HTML or CSS:

```python
import coshui as cui

# Within your loop
with cui.CoshUIRenderer(...):
    with cui.Container(id="main_container", width=cui.FILL, height=cui.FILL, direction=cui.COLUMN, align=cui.ALIGN_CENTER, justify=cui.JUSTIFY_CENTER, gap=20):
        cui.Label(id="menu_label", text="CoshUI", width=200, height=50, font_size=64)
        cui.Button(id="print_btn", text="Print Hello World!", width=210)
        cui.Button(id="color_btn", text="Change Color!", width=210)

# Listen for signals
if cui.get_signal("print_btn", cui.CLICKED):
    print("Hello World!")

# Animate with one line
if cui.get_signal("color_btn", cui.CLICKED):
    cui.animate("background_color", "main_container", (200, 200, 200), 1.5, "ease_in_out")
```

![gif of the top example rendering](https://raw.githubusercontent.com/JyleFV/CoshUI/main/assets/README_example.gif)

To learn more, check out the [examples](https://gitlab.com/jylefv/CoshUI/-/blob/main/examples/examples.md) in the repo or visit the [documentation](https://terrarizer03.github.io/coshui-docs/).

## Documentation
CoshUI's documentation features the basic API coverage and all you need to know about how to use it. It can be viewed [here.](https://terrarizer03.github.io/coshui-docs)

## Contributing
CoshUI is primarily developed on [GitLab](https://gitlab.com/jylefv/CoshUI). Please open issues and pull requests there.

To learn more about how to contribute, check the [contributing](https://gitlab.com/jylefv/CoshUI/-/blob/main/CONTRIBUTING.md) markdown.

## Author
**Main Developer and Maintainer:** Jyle Frazier (Terra) Villareal

## Contact
- GitLab: [JyleFV](https://gitlab.com/jylefraziervillareal)
- GitHub: [JyleFV](https://github.com/JyleFV)
- X/Twitter: [@JyleFV](https://x.com/JyleFV)
- Discord: [CoshUI](https://discord.gg/wZUqKv9ux)
- Email: jylefraziervillareal@gmail.com
