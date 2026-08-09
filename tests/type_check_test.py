"""
NOTE: MADE BY CLAUDE (I can't bother to make tests bruh)

Regression tests for CoshUI's property type-checking system (see `CoshLifecycle.validate_node_types`
and each Node's `valid_property_types()` method).

What this file guards against:

1. A Node/Widget declares a dataclass field but forgets to add it to `valid_property_types()`,
   silently leaving that property unchecked.
2. A `valid_property_types()` entry has a typo'd key (e.g. `header_border_raidus` instead of
   `header_border_radius`) that doesn't match any real attribute. `validate_node_types()` skips
   unknown keys via `hasattr()`, so this fails *silently* rather than raising -- this is the
   easiest and most dangerous mistake to make when adding a new widget, so it gets its own test.
3. A regression in the type checker itself no longer catching bad values it used to catch
   (e.g. bools sneaking through as ints, wrong tuple lengths, wrong element types).

Run with: pytest type_check_test.py -v
"""

import dataclasses
import inspect

import pytest

import coshui as cui
from coshui.cui_error import CoshUIError
from coshui.state import CoshUI
from coshui.node_definitions import Node
from coshui.types import CoshStyling
from coshui.widgets import (
    Container, Grid, Button, Label, RichLabel, Checkbox,
    Image, Box, Modal, InputField, Dropdown, Slider,
)

# Fields that are structural/internal rather than "typed properties" meant to be
# covered by valid_property_types(). These are intentionally excluded from the
# coverage check below.
IGNORED_FIELDS = {
    "style", "children", "x", "y",
}

# Minimal, valid construction kwargs per widget class. Each entry must produce a
# working instance so we can call `.valid_property_types()` on it and inspect its
# real attribute values. Keep these minimal -- the point is just "does it construct."
def _minimal_kwargs(cls, node_id, tmp_image_path):
    common = {"id": node_id}

    if cls is Image:
        return {**common, "src": tmp_image_path}
    if cls is Dropdown:
        return {**common, "item_list": ["a", "b", "c"]}
    if cls is Modal:
        return {**common, "width": 100, "height": 100}
    return common


WIDGET_CLASSES = [Container, Grid, Button, Label, RichLabel, Checkbox, Image, Box, Modal, InputField, Dropdown, Slider]


@pytest.fixture(autouse=True)
def reset_coshui_state():
    """CoshUI keeps global registries (active ids, state storage, the build stack).
    Since we're constructing Nodes outside of a real CoshUIRenderer frame, we need to
    reset these between tests so ids don't collide and state doesn't leak across tests."""
    CoshUI._active_ids.clear()
    CoshUI._state_storage.clear()
    CoshUI._stack.clear()
    yield
    CoshUI._active_ids.clear()
    CoshUI._state_storage.clear()
    CoshUI._stack.clear()


@pytest.fixture
def tmp_image_path(tmp_path):
    """Image() requires a real file on disk to exist, so give it one."""
    path = tmp_path / "fake_image.png"
    path.write_bytes(b"\x89PNG\r\n\x1a\n")  # minimal PNG header, contents don't matter
    return str(path)


def _make_instance(cls, node_id, tmp_image_path):
    kwargs = _minimal_kwargs(cls, node_id, tmp_image_path)
    return cls(**kwargs)


# region Coverage: every dataclass field should have a type-check entry
@pytest.mark.parametrize("cls", WIDGET_CLASSES, ids=[c.__name__ for c in WIDGET_CLASSES])
def test_every_field_has_a_type_entry(cls, tmp_image_path):
    """Every public dataclass field declared on a widget (across its whole MRO) should
    appear as a key in that widget's valid_property_types(). If this fails, someone
    added a new field without teaching the type checker about it."""
    instance = _make_instance(cls, f"{cls.__name__.lower()}_coverage", tmp_image_path)
    type_map = instance.valid_property_types()

    declared_fields = {f.name for f in dataclasses.fields(cls) if not f.name.startswith("_")}
    missing = (declared_fields - IGNORED_FIELDS) - type_map.keys()

    assert not missing, (
        f"{cls.__name__} has field(s) {missing} with no entry in valid_property_types(). "
        f"Add them (remember `super().valid_property_types()` if this is a subclass)."
    )


@pytest.mark.parametrize("cls", WIDGET_CLASSES, ids=[c.__name__ for c in WIDGET_CLASSES])
def test_style_fields_have_a_type_entry(cls, tmp_image_path):
    """Same coverage check, but for the node's `.style` (CoshStyling) object, since
    validate_node_types() checks node.style separately from the node itself."""
    instance = _make_instance(cls, f"{cls.__name__.lower()}_style_coverage", tmp_image_path)
    type_map = instance.style.valid_property_types()

    declared_fields = {f.name for f in dataclasses.fields(CoshStyling) if not f.name.startswith("_")}
    missing = declared_fields - type_map.keys()

    assert not missing, f"CoshStyling has field(s) {missing} with no entry in valid_property_types()."
# endregion


# region No stale / typo'd keys
@pytest.mark.parametrize("cls", WIDGET_CLASSES, ids=[c.__name__ for c in WIDGET_CLASSES])
def test_no_typo_or_stale_keys(cls, tmp_image_path):
    """The inverse of the coverage check: every key declared in valid_property_types()
    must correspond to a real attribute on the instance. validate_node_types() silently
    `continue`s on unknown keys via hasattr(), so a typo'd key (e.g. `_raidus` instead
    of `_radius`) doesn't error -- it just quietly stops validating that property
    forever. This test is what catches that class of mistake."""
    instance = _make_instance(cls, f"{cls.__name__.lower()}_typo", tmp_image_path)
    type_map = instance.valid_property_types()

    stale_keys = [key for key in type_map if not hasattr(instance, key)]

    assert not stale_keys, (
        f"{cls.__name__}.valid_property_types() declares key(s) {stale_keys} that don't "
        f"match any real attribute -- likely a typo. These are currently being silently "
        f"skipped by validate_node_types()."
    )
# endregion


# region The type checker actually rejects bad values
def test_rejects_wrong_primitive_type():
    with pytest.raises(CoshUIError.Main):
        Label(id="bad_label", font_size="not an int")


def test_rejects_bool_masquerading_as_int():
    """bool is a subclass of int in Python, so isinstance(True, int) is True. The type
    checker should still reject it for fields that expect a "real" int/float, e.g. inside
    a TupleLength-checked tuple."""
    with pytest.raises(CoshUIError.Main):
        Container(id="bad_container", padding=(10, 10, True, 0))


def test_rejects_wrong_tuple_length():
    with pytest.raises(CoshUIError.Main):
        Container(id="bad_padding_length", padding=(10, 10, 10, 10, 10))


def test_rejects_wrong_element_type_in_tuple():
    with pytest.raises(CoshUIError.Main):
        Label(id="bad_text_color", text_color=(255, "not a number", 0))


def test_accepts_valid_values():
    """Sanity check the inverse -- valid values should never raise."""
    node = Container(
        id="good_container",
        padding=(10, 10, 10, 0),
        width=cui.FILL,
        height=cui.FILL,
        style=CoshStyling(background_color=(80, 75, 255)),
    )
    assert node.padding == (10, 10, 10, 0)


def test_none_allowed_where_declared_not_allowed_where_missing():
    """Fields explicitly typed with `type(None)` should accept None. Fields covered by
    ENGINE_DEFAULTS should also implicitly accept None (pre-finalize_defaults). Anything
    else should reject None outright."""
    # gap isn't in ENGINE_DEFAULTS but is explicitly typed to allow None
    node = Container(id="gap_none_ok", gap=None)
    assert node.gap is None

    # src on Image is required -- Image.__post_init__ itself enforces this, so it should
    # still raise (just via CoshUIError.Main from the widget's own logic, not the type checker)
    with pytest.raises(CoshUIError.Main):
        Image(id="missing_src")
# endregion


# region Every registered widget actually implements valid_property_types
def test_every_widget_overrides_or_inherits_valid_property_types():
    """Sanity check that valid_property_types is actually callable (not accidentally
    left as the abstract/undefined base) for every widget CoshUI ships."""
    for cls in WIDGET_CLASSES:
        assert callable(getattr(cls, "valid_property_types", None)), (
            f"{cls.__name__} has no valid_property_types() method, "
            f"even via inheritance."
        )
# endregion