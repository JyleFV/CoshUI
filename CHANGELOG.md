# CoshUI - 0.3.3 Changelog
Posted: `August X, 2026`

### Theme System v2.0:
The new theme rework has made it a lot more accessible and actually worth it to make your own themes, by introducing a `token` system that lets users define values and reuse it and also an "inheritance" system that lets themes simply create a copy of an existing theme and override those values as opposed to making new themes from scratch.

An example of how the new `CoshTheme` system works:
```python
cui.CoshTheme(
    tokens={"button_color": (85, 100, 255)},
    nodes={"Button": {"background_color": "@button_color"}}
)
```
This new system lets users create tokens that can then be passed as values to Node defaults. The `@` is what separates a string from an actual token, if that isn't present, it might just accept that as the real value and possibly generate an error if `str` isn't an expected type.

For "inheritance":
```python
cui.create_theme(
    "my_theme", 
    cui.CoshTheme(
        tokens={"primary_color": (255, 100, 100)}
    ),
    inherit="DEFAULT"
)
```
This creates a new theme with `DEFAULT` as the base theme, it will take all the values inside the `DEFAULT` theme and use your new theme as an override. The example will override the `primary_color` token which will change the value of every Node that uses that token.

### New Features:
- **Newline**: CoshML now supports the `[n]` (newline) tag. Breaks the current line and puts the text after it to the new line. You can also just use `\n` to indicate newline, there is *almost* no difference for the system.
- **Property Type Checker**: CoshUI now raises errors if a Node's property is the wrong type (e.g. `width="Hello"`, `font=21`, or `alpha=True`). This works with `inline` properties (and with `class` and `theme` properties if used).
    - **Note for Contributors**: The type checker has a lot of subtleties that are non-obvious, such as `type(None)`, the use of `TupleLength`, and `super()` calls in class inheritance. Remember that new widgets which add new properties *should always* have a `valid_property_types()` method that copy's the parent's types by calling and unpacking `super().valid_property_types()` inside the new dict and adding the types of the new value. Also remember that overriding a parent's property with a new base value doesn't count as a *new* property and ***should not*** be added as a `valid_property_types()` entry if any of its parent already covers it.
- **Type Error for Classes**: Added type error for Node classes. If an unexpected datatype is passed (i.e. `classes=10` or `classes=False`), it will provide a proper error. This is slightly different from the **type checker** as classes are checked before the type checker runs.

### Breaking Changes:
- **Theme Creation**: The `create_theme()` function has gotten an addition with the new `inherit` parameter (which if passed the name of an existing theme, that theme will be used as a base of the users new theme) along with the `CoshTheme()` API overhaul, introducing the new `tokens` and `nodes` parameters.

### Refactors:
- **Type Validation in Lifecycle**: Node properties now has type validation in their lifecycle, it runs after class styles, theme values, and explicit styles are set on a Node so it *should* always catch those values properly. This slightly increases `build_time` but is an overall good change.
- **Build Time & Finalized Defaults**: The Debugger has added the Node build time and `finalized_defaults` pass in its `Profiler`.
- **Errors**: Reworked Errors to all be under the `CoshUIError` namespace. This makes it easier to handle future error types thanks to centralizing them into one namespace. There are currently 2 types of *"errors"*:
    - `CoshUIError.Main`: Formerly `CoshUIError`, this error is for general errors concerning the main API and callsites.
    - `CoshUIError.CoshML`: Formerly `CoshMLError`, this error is strictly for catching CoshML-related issues.
    - **For Contributors**: `warn` is also part of CoshUIError, so when calling `warn()`, do `CoshUIError.warn()`.

### Bug Fixes:
- **Asterisk Import**: Stupidly forgot `,` after `"TextStyle"` in `__all__`.
- **Empty Text**: RichLabel and Label making an error if `text` is set to None. (This is a little weird)

### Planned for 0.3.4 and above:
- **Previously Planned**: All the plans previously discussed.

### Deprecated Plans:
- **Particle System**: Decided it's not worth making a Particle System as it's not really in-scope with CoshUI.
---

# CoshUI - 0.3.2.1 Hotfix
Posted: `July 7, 2026`

### Bug Fixes:
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

### Bug Fixes:
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
