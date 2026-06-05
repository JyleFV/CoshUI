# Examples

Since CoshUI is *backend-agnostic*, you can use it with many different frameworks such as:

### Pygame
```bash
PygameBackend(screen)
```
> [!TIP]   
> `screen` is a `pygame.Surface` object.

### Raylib
```bash
RaylibBackend()
```

### ModernGL
```bash
ModernGLBackend(context, cui.GLFW)
# or
ModernGLBackend(context, cui.MGLW)
```
> [!TIP]   
> `context` is a a `moderngl.Context` object. The second parameter is the supported windower. As of now, only GLFW and MGLW is supported.

### PyOpenGL
**Coming Soon...**

---

Passing these backends to `CoshUIRendrer` as a parameter will let you use your UI Code within any of the listed frameworks and graphics pipelines.

If you'd like to see implementaions, check out the examples within this folder.