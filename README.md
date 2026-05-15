<div align="center">
    <h1>CoshUI</h1>
    <h3>The Python-first, Declarative-Mode, Backend Agnostic, UI Library.</h3>
    <img src="assets/coshui_logo.jfif" alt="CoshUI Logo" width=500> 
</div>

## What is CoshUI?
CoshUI is a Python-first, declarative-mode UI library inspired by the HTML & CSS box model. Unlike most Python UI libraries, CoshUI is fully backend-agnostic. Write your UI once and render it with Pygame, OpenGL, or any backend you build. With an intuitive, web-like structure and a clean API, CoshUI is designed to be simple to pick up without sacrificing flexibility.

## How to Install

## How to Use
CoshUI features a very simple API, using Python's context managers with `with` blocks, it follows modernized Python. An example of the UI in action:

```python
# Within the main loop
with CoshUIRenderer(PygameBackend(screen)): # This uses the Pygame backend thus needing to pass in pygame.Surface
    with Container(id="main_container", direction=ROW, gap=5.0):
        Label(text="Press The Button to Start", width=200, height=50)
        Button(text="Start", id="start_btn", width=100, height=50)
    
# Uses CoshUI's built-in event system and animation system to track click events end animate Nodes.
if get_signal("start_btn", "clicked"):
    print("Hello World!")
    # Gradually turns main_container's background color to dirty white.
    animate("background_color", "main_container", (200, 200, 200), 1.5, "ease_in_out") 
```