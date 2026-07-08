# CoshUI - 0.3.2.1 Hotfix
Posted: `July 7, 2026`

### Bug Fix
- **Nested Font Bug**: A small bug in CoshML where if users were to do `"[font=Courier]Hello [bold]World[/][/]"`, the `"World"` word wouldn't be set to designated font. The fix for this was adding a `_font_family` private member variable inside the `TextStyle` object that saves the font name to be used in the `validate_style()` function.

---

# CoshUI - 0.3.2 Changelog
Posted: `July 5, 2026`

### CoshML v1.0:
CoshML is a markup language for CoshUI's `RichLabel` widget. It gives users flexibility when styling their CoshUI text by letting them write CoshML markup directly in the `text` field.

With CoshML comes new fields and possiblities for text, like being able to set `bold` and/or `italic`, setting `underline` and/or `strikethrough`, a **class** system where users can pass in a `TextStyle` object which can then be used as a *tag* on CoshML text, and much more.

Here is a basic example use-case for CoshML:
```python
cui.RichLabel(
    id="example_rich_label",
    text="[color=(255, 100, 100) font_size=38]Hello CoshUI![/] My name is [bold italic]JyleFV[/], this is a [font=Ubuntu bold]test[/] on the CoshML system.",
    width=cui.FILL, height=500,
    text_align=cui.TEXT_ALIGN_TOP, text_justify=cui.TEXT_JUSTIFY_CENTER
)
```

CoshML already features a comprehensive set of tags for its initial release, here's a quick rundown of them all:
> [!TIP]
> "Tag": Requires a value to be set after it separated by "=".
> "Keyword": Works standalone and does not need a value set after it.

| CoshML Tag  | Description |
| :--- | :--- |
| `color` | A **tag** that lets users set the color for that part of the text. This requires a 3-tuple value in the range of 0-255 to be set after it. |
| `font` | A **tag** that lets users set the font for that part of the text. This requires the name of a font that has been declared using `add_font()` or exists in the `_font_library` to be set after it. |
| `font_size` | A **tag** that lets users set the font size for that part of the text. This requires an `int` size value to be set after it. |
| `bold` | A **keyword** that lets users make **bold** for whatever text is encompassed with it. |
| `italic` | A **keyword** that lets users make **italic** for whatever text is encompassed with it. |
| `strikethrough` | A **keyword** that renders a line in the middle whatever text is encompassed with the CoshML tag. |
| `underline` | A **keyword** that renders a line below whatever text is encompassed with the CoshML tag. |
| `red` | A **keyword** that simplifies `color=(255, 0, 0)`. |
| `blue` | A **keyword** that simplifies `color=(0, 0, 255)`. |
| `green` | A **keyword** that simplifies `color=(0, 255, 0)`. |
| `white` | A **keyword** that simplifies `color=(255, 255, 255)`. |

On top of that, users can use the existing `add_class()` function — which used to only take in `CoshStyling` objects — and pass in `TextStyle` objects and use the class as a tag.

**Example:**
```python
cui.add_class("header", cui.TextStyle(color=(0, 0, 0), font_size=48, font="Courier", italic=True, bold=True))

# in CoshUIRenderer:
cui.RichLabel(
    id="example_rich_label",
    text="[header]CoshUI[/]",
    ...
)
```

CoshML is inspired by BBCode visually, but with small differences like how CoshML supports multiple CoshML tags at once as opposed to nested tags or having a universal `[/]` closing tag instead of closing with explicit tag names (like `[/color]` or `</b>`) as seen in BBCode or HTML. It is also heavily tailored towards CoshUI's engine, thus the choice of making it as its own standalone markup language instead of integrating BBCode.

If you want to learn more about CoshML's internals as a contributor, `text_engine.py` is the best entry point.

### New Features:
- **RichLabel**: Added new `RichLabel` widget which CoshML — and by extension this update — centers around.
- **Profiler**: Added a profiler for CoshUI's internal subsystems which tracks and visualizes execution times for all major engine subsystems.

> [!WARNING]
> The profiler only measures the time for the internal pipelines like the animation updates, layout system, event system, and backend rendering. It currently does not take into account Node rebuild time. That will be added in a future version of the profiler.

### Refactors:
- **Padding & Margin**: Added the ability to pass in a 4-value tuple (top, right, bottom, left) to be more precise with what side needs the values.
- **User-Side Functions**: Reworked the internals and functionality of `add_class`, `add_font`, and `set_default_font`.
    - In `add_class()`, you can now pass in `TextStyle` objects that get added to the `_text_style_classes` registry which can be used in CoshML markup text.
    - The `add_font()` function now accepts `bold`, `italic`, and `bold_italic` paths that let users set the `bold` or `italic` fields to True for that font in `Label` or `RichLabel`.
    - For `set_default_font()`, this change is mainly internal, it has no difference from before except that it sets the name of the font in `_default_font` instead of the path.
- **Text System**: Reworked how the CoshUI engine treats text, bundling up text values into a singular `TextData` dataclass.
- **Layout System**: Layout has been split to make it easier to read and now deals with text positioning where before, each backend had to deal with it.
- **Ref On Change**: Added `.on_change(callback)` call for the `Ref` class. It takes in a callback for an argument which if the method is called, will run the callback each time the value changes.
- **Animation Loops**: Added a `.loop()` method to `animate()` which lets you loop your animations. 
    - It has parameters that lets you customize the loop such as `count` which sets how many times it'll loop (with `None` being the default and treated as infinite iterations).
    - There's `delay` which sets a timed pause that loops take in between each iteration.
    - And `ping_pong` which makes it so end and start values smoothly go back in forth instead of resetting the start value every iteration.

### Performance:
- **[PygameBackend] Surface Caching**: 20%~ reduction in rendering time for some cases, seeing a drop from 1.4-1.5ms to 1.1-1.2ms when rendering 14-19 of mostly different Nodes. Rotation adds an extra 0.7ms~ to those times so a separate `_rotation_cache` might be a future path.

### Bug Fixes:
- **GL Minimize Bug**: When clicking minimize on GL backends, the screen-size suddenly becomes (0, 0) which prompts the `_get_orthographic_matrix()` function of the GL Backends to malfunction due to a *"division by 0"* error.
- **PRESSED Signal Propagation**: The signal `PRESSED` did not consume clicks which naturally propagated it downwards to every Node. So Nodes above, even if their `mouse_filter` field was set to STOP, would still let Nodes below get the `PRESSED` signal.
- **GL Text Offset**: The GL backend's text used to use the `scaled_font_size` for the text's baseline_y value. This caused a small downwards shift from the actual position.
- **Text Rotation Pivot**: Backends rotated text from the text's center, this caused problems with Node rotations that had `text_align` or `text_justify` *not* set to `CENTER`.
- **Layout FILL/Percentage Sizing**: Cross-axis FILL and percentage-sized children did not subtract `child.margin` before computing available space, causing incorrect sizing in certain layouts.

### Planned for v0.3.3 and above:
- **Particle System**: Let users emit particles.
- **Theme System Rework**: Rework of the theme system to make it easier and more viable to use.
- **More CoshML Capabilities**: Things like `[n]` (newline) tags and letter-word-line spacing support for text.
- **The Previously Planned**: The plans previously discussed in `v0.3.0`.
- **And Much More...**

---

# CoshUI - 0.3.1 Patch Notes
Posted: `June 18, 2026`

### Patches:

- **Missing Shaders**: PyOpenGL and ModernGL not working at all due to shaders not being added to the PyPI package.

### DX Additions:

- **PyOpenGL Windower Warning**: If anything other than `cui.GLFW` is passed into `PyOpenGLBackend`, it gives an error
- **Wrong Node ID**: `get_signal` now has a Node ID check, before it did not.
- **Dropdown Default Theme**: Added a basic default theme for Dropdown to reduce resistance of usage.

---

# CoshUI - 0.3.0 Changelog
Posted: `June 7, 2026`

### New Features:

- **CoshPercentage**: New sizing type that lets users set width/height as a percentage of the parent’s dimensions.
- **CoshDebug**: New debugger that opens its own tkinter window and shows a live node inspector showing the full UI tree, computed layout values, style properties, and signals fired each frame.
- **More Easing Curves**: Added new easing curves to `animate()`.
    -   | New Curves |
        | :---: |
        | `"ease_in_bounce"` |
        | `"ease_out_bounce"` |
        | `"ease_in_elastic"` |
        | `"ease_out_elastic"` |

### Behavior Changes:

- **ABSOLUTE FILL**: Gave the ability for `ABSOLUTE` positioning Nodes to use cui.FILL for its `width` and `height` values.

### Breaking Changes:

- **On Complete**: `animate()` function no longer takes in an on_complete callback, but returns a Tween that lets you call a `.finished()` method that accepts the callback. This is partly to make it more pythonic but also to clean up the API and to add new methods in the future like `.loop()`.
    - **Example**: `animate(...).finished(callback)`
- **Property Name Changes**: `animate()` function's property names changed. By doing this, it becomes easier to use the animation system by mapping the new names to the actual properties being animated. 
    -   | Old | New |
        | :--- | :--- |
        | `animate("scale", …)` | `animate("transform_scale", …)` |
        | `animate("position", …)` | `animate("transform_position", …)` |
        | `animate("rotation", …)` | `animate("transform_rotation", …)` |

### Bug Fixes:

- **Pygame’s Missing Alpha**: Alpha value not being set when rotation was 0.0 for rectangles, this is due to being accidentally forgotten when implementing rotation.
- **Raylib Border-radius Rotation**: Raylib losing border radius when rotated is now fixed.

### Backends:

- **PyOpenGLBackend**: New backend for PyOpenGL with GLFW support.
- **ModernGLBackend**: New backend for ModernGL with GLFW and MGLW support.

> [!WARNING]
> ModernGL-Window's support acts fairly weird with the debugger. My main theory is the debugger consumes a bit too much and hangs some parts of it. If this is true, then this may also be a program complexity problem — which if it is, might be a need for a complete rework of the debugger.

### Planned for v0.3.1 and above:

- **Gradients**: Gradient support for all backends.
- **Drop Shadow**: Drop Shadow support for all backends.
- **Glow**: Glow support for all backends.
- **Profiler**: "Profile" tab in Debugger that gives context in frame by frame execution times of each engine pass.
- **More Alignment Options**: Self alignment in `Grid` cells. 
- **And Much More...**

---

# CoshUI - 0.2.4 Initial Release

Posted: `May 23, 2026`

The first public release of CoshUI — a Python-first, declarative, backend-agnostic UI library.

### What's included

- Full layout engine with flexbox-inspired sizing (FILL, AUTO, padding, margin, gap)
- Container and Grid layout nodes
- Widget set: Button, Label, Checkbox, Slider, Modal, Image, InputField, Dropdown
- Pygame and Raylib backends
- Tween animation system with configurable easing
- Signal-based event system
- Theme and CSS-inspired class system
- Text wrapping and transform rotation support
- Full documentation at https://terrarizer03.github.io/coshui-docs/

### Install

```bash
pip install coshui
```

### Notes
This is an early release. Grid has not been thoroughly tested and may have edge cases. Issues and contributions welcome on GitLab.
