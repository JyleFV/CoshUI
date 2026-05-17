import pytest
import coshui as cui
from coshui.state import CoshUI
from coshui.pipeline import measure, layout, finalize_defaults

def test_container_layout():
    ctr = cui.Container(width=100, height=100)
    finalize_defaults(ctr)
    measure(ctr)
    layout(ctr, 0.0, 0.0)

    assert ctr._x == 0.0
    assert ctr._y == 0.0
    assert ctr.width == 100
    assert ctr.height == 100

def test_container_fill_and_auto_sizing():
    with cui.Container(width=200, padding=10) as parent:
        child = cui.Button(id="btn", text="Hello", width=cui.FILL, height=30)
    
    finalize_defaults(parent)
    measure(parent)
    layout(parent, 0.0, 0.0)

    assert parent.width == 200
    assert parent.height == 30 + (10 * 2)
    assert child.width == 200 - (10 * 2) # 10 is padding
    assert child._x == 10.0
    assert child._y == 10.0

@pytest.fixture(autouse=True)
def clear_coshui_state():
    CoshUI._stack.clear()
    CoshUI._active_ids.clear()
    CoshUI._state_storage.clear()
    yield
    CoshUI._stack.clear()
    CoshUI._active_ids.clear()
    CoshUI._state_storage.clear()