"""CoshUI module for the global and main processes of the UI Engine.

Set the main loop of the UI tree with CoshUIRenderer where every process
runs within its __enter__ and __exit__ dunder operators.

The CoshUI global namespace is private and should only be accessed 
by internal code, never outside."""

import time

from .cui_error import CoshUIError
from .backend import CoshBackend
from .lifecycle import CoshLifecycle
from .state import CoshUI
from .types import CoshMode
from .debug import CoshDebug
from .expanders import register_exapanders
from .widgets import Container
from .pipeline import measure, layout, render, process_events, update, finalize_defaults

class CoshUIRenderer:
    def __init__(self, backend : CoshBackend, debug : CoshMode = CoshMode.NORMAL):
        self.backend = backend
        
        if debug is CoshMode.DEBUG and CoshUI._debugger is None:
            CoshUI._debugger = CoshDebug() 

        screen_w, screen_h = self.backend.get_size()
        self.root = Container(width=screen_w, height=screen_h)
        CoshUI._measure_text = self.backend.measure_text

        register_exapanders()

    def __enter__(self):
        if CoshUI._active_renderer:
            raise CoshUIError("Cannot nest renderer objects.")
        
        now = time.perf_counter()

        if CoshUI._last_time == 0.0:
            delta = 1/60
        else:
            delta = now - CoshUI._last_time
        
        CoshUI._last_time = now

        if delta > 0.1:
            delta = 1/60

        t0 = time.perf_counter()
        update(delta)
        self.update_time = time.perf_counter() - t0

        self.backend.poll_input()

        CoshUI._active_renderer = True
        CoshUI._active_ids.clear()
        CoshUI._widget_counter = 0
        CoshUI._stack.clear()  
        self.root.children.clear()
        CoshUI._stack.append(self.root)
        return self

    def __exit__(self, *args):
        CoshUI._stack.pop()
        CoshUI._active_renderer = False

        CoshLifecycle.expand(self.root)
        finalize_defaults(self.root)

        timings = _run_pipeline(self.root, self.backend, self.update_time)

        if isinstance(CoshUI._debugger, CoshDebug):
            CoshUI._debugger.render(self.root, CoshUI._render_stack, CoshUI._signals, timings)

        CoshUI._render_stack.clear()

        # Clean up stale nodes
        stale = set(CoshUI._state_storage.keys()) - CoshUI._active_ids
        for key in stale:
            del CoshUI._state_storage[key]

def _run_pipeline(root, backend, update_time=0.0) -> dict:
    t0 = time.perf_counter()
    measure(root)
    t1 = time.perf_counter()
    layout(root, root._x, root._y)
    t2 = time.perf_counter()
    render(root)
    t3 = time.perf_counter()
    CoshUI._render_stack.sort(key=lambda d: d.z_index)
    CoshUI._signals.clear()
    process_events()
    t4 = time.perf_counter()
    backend.flush(CoshUI._render_stack)
    t5 = time.perf_counter()

    return {
        "update": update_time,
        "measure": t1 - t0,
        "layout": t2 - t1,
        "render": t3 - t2,
        "process_events": t4 - t3,
        "backend_render": t5 - t4
    }
