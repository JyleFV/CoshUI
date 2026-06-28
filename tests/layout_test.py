import pytest
import coshui as cui
from coshui.state import CoshUI
from coshui.pipeline import measure, layout, finalize_defaults
from coshui.text_engine import parse_coshml

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
    assert parent.height == 30 + (parent.padding * 2)
    assert child.width == 200 - (parent.padding * 2)
    assert child._x == 10.0
    assert child._y == 10.0

def test_container_percentage_sizing():
    with cui.Container(width=800, height=800, padding=10) as parent:
        child = cui.Container(width=cui.PERCENTAGE(50), height=cui.PERCENTAGE(75))
    
    finalize_defaults(parent)
    measure(parent)
    layout(parent, 0.0, 0.0)

    assert child.width == ((parent.width) - (parent.padding * 2)) * 0.50
    assert child.height == ((parent.width) - (parent.padding * 2)) * 0.75

@pytest.fixture(autouse=True)
def clear_coshui_state():
    CoshUI._stack.clear()
    CoshUI._active_ids.clear()
    CoshUI._state_storage.clear()
    yield
    CoshUI._stack.clear()
    CoshUI._active_ids.clear()
    CoshUI._state_storage.clear()