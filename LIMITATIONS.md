# CoshUI Limitations
This markdown file outlines limitations that the CoshUI framework might have as a whole and for each backend.

### Definition of Terms

| Limitation Type | Description |
| :--- | :--- |
| ![Overall Limitation](https://img.shields.io/badge/limitation-all-red?style=flat-square) | A limitation that affects all of the CoshUI framework. | 
| ![Backend Limitation](https://img.shields.io/badge/limitation-backend-orange?style=flat-square) | A limitation that affects only a specific backend. The backend will be emphasized in the `backend` part of the badge. |

---

### External Node Tree 
![Overall Limitation](https://img.shields.io/badge/limitation-all-red?style=flat-square)

CoshUI uses an Immediate-Mode structure that makes it hard to integrate the UI elements with the user's actual game elements.

### Axis Alignment 
![Overall Limitation](https://img.shields.io/badge/limitation-all-red?style=flat-square)

The rendering in CoshUI's backends are axis-aligned, thus when the `overflow` property is set to `HIDDEN` with a Node that has a `transform_rotation` property set to anything but `0.0`, the overflow clipping breaks as they don't mesh well with each other.

### AUTO-Sized Scroll Parents
![Overall Limitation](https://img.shields.io/badge/limitation-all-red?style=flat-square)

Setting `width` or `height` to `CoshSizing.AUTO` on a scrollable ParentNode causes it to size itself exactly to its content's size, making `max_scroll` always compute to `0.0`. Scrollable ParentNodes will require an explicit numeric or percentage size.

### Scroll Events
![Pygame Limitation](https://img.shields.io/badge/limitation-pygame-orange?style=flat-square)

When building a project within the pygame framework, CoshUI's scroll positioning won't work unless `pygame.event.get()` is called somewhere within the main loop. This is sort of an unnecessary worry as most if not all pygame projects will call the `pygame.event.get()` function, but it's still a problem and it should be explained to the users.

### Window Close
![ModernGL-MGLW Limitation](https://img.shields.io/badge/limitation-moderngl%20window-orange?style=flat-square)

When `CoshUIRenderer` has the `DEBUG` state set within the ModernGL backend's `MGLW` window driver, it makes it hard or even impossible to close the window through the `x` button and will need to be task ended through the task manager.

> [!NOTE]
> This might be fixable, but I have no clue how.

### Rounded Edges
![Raylib Limitation](https://img.shields.io/badge/limitation-raylib-orange?style=flat-square)

Due to Raylib not fully supporting rounded edges, it may look decently weird compared to other backends. CoshUI has tried to make it a possibility, especially with corner-specific rounding, but note that it will look weird no matter what due to Raylib's philosophy and scope.