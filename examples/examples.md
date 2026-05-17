# Examples

Since CoshUI is *backend-agnostic*, you can use it with many different frameworks such as:

### Pygame
```
PygameBackend(screen)
```
> [!TIP]   
> `screen` is a `pygame.Surface` object.

### Raylib
```
RaylibBackend()
```

### PyOpenGL
**Coming Soon...**

### ModernGL
**Coming Soon...**

---

Passing these backends to `CoshUIRendrer` as a parameter will let you use your UI Code within any of the listed frameworks.

If you'd like to see implementaions, check out the examples within this folder.