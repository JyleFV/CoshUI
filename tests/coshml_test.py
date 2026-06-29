import pytest

from coshui.text_engine import parse_coshml
from coshui.cui_error import CoshUIError


BASE_ARGS = dict(
    text_color=(255, 255, 255),
    font="Courier",
    font_size=24,
    letter_spacing=None,
    word_spacing=None,
    line_spacing=None,
)


def test_coshml_basic():
    context = parse_coshml(
        text="[color=(255, 0, 0) font=Courier bold font_size=36]Hello[/] World",
        **BASE_ARGS,
    )

    assert len(context.runs) == 2

    assert context.runs[0].text == "Hello"
    assert context.runs[0].color == (255, 0, 0)
    assert context.runs[0].font_size == 36
    assert context.runs[0].bold is True

    assert context.runs[1].text == " World"
    assert context.runs[1].color == (255, 255, 255)
    assert context.runs[1].font_size == 24
    assert context.runs[1].bold is False


def test_coshml_full_text():
    context = parse_coshml(
        text="[color=(255, 0, 0) font=Courier bold font_size=36]Hello[/] World",
        **BASE_ARGS,
    )

    assert len(context.runs) == 2
    assert context.text == "Hello World"


def test_coshml_nested_tags():
    context = parse_coshml(
        text="[red]Hello [bold]World[/]![/]",
        **BASE_ARGS,
    )

    assert len(context.runs) == 3

    assert context.runs[0].text == "Hello "
    assert context.runs[0].color == (255, 0, 0)
    assert context.runs[0].bold is False

    assert context.runs[1].text == "World"
    assert context.runs[1].color == (255, 0, 0)
    assert context.runs[1].bold is True

    assert context.runs[2].text == "!"
    assert context.runs[2].color == (255, 0, 0)
    assert context.runs[2].bold is False


def test_coshml_keyword_colors():
    context = parse_coshml(
        text="[blue]Hello[/]",
        **BASE_ARGS,
    )

    assert len(context.runs) == 1
    assert context.runs[0].color == (0, 0, 255)


def test_coshml_plain_text():
    context = parse_coshml(
        text="Hello World",
        **BASE_ARGS,
    )

    assert len(context.runs) == 1
    assert context.runs[0].text == "Hello World"
    assert context.runs[0].color == (255, 255, 255)
    assert context.runs[0].font_size == 24


def test_coshml_style_restoration():
    context = parse_coshml(
        text="[red]A[/]B",
        **BASE_ARGS,
    )

    assert len(context.runs) == 2

    assert context.runs[0].color == (255, 0, 0)
    assert context.runs[1].color == (255, 255, 255)


def test_coshml_multiple_keywords():
    context = parse_coshml(
        text="[green italic underline]Hello[/]",
        **BASE_ARGS,
    )

    run = context.runs[0]

    assert run.color == (0, 255, 0)
    assert run.italic is True
    assert run.underline is True


def test_coshml_empty_tag():
    context = parse_coshml(
        text="[]Hello[/]",
        **BASE_ARGS,
    )

    assert len(context.runs) == 1
    assert context.runs[0].text == "Hello"
    assert context.runs[0].color == (255, 255, 255)


def test_coshml_uniform_detection():
    context = parse_coshml(
        text="Hello World",
        **BASE_ARGS,
    )

    assert context.is_uniform() is True


def test_coshml_non_uniform_detection():
    context = parse_coshml(
        text="[red]Hello[/] World",
        **BASE_ARGS,
    )

    assert context.is_uniform() is False