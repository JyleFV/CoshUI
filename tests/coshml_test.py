import pytest

from coshui.text_engine import parse_coshml, TextRun
from coshui.cui_error import CoshUIError
from coshui.types import *

BASE_ARGS = dict(
    text_color=(255, 255, 255),
    font="Courier",
    font_size=24,
    letter_spacing=None,
    word_spacing=None,
    line_spacing=None,
    text_justify=None,
    text_align=None,
    text_overflow=None,
    bold=False,
    italic=False,
    underline=False,
    strikethrough=False,
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


def test_text_data_same():
    run_1 = TextRun(text="Hello", color=(255, 255, 100), font="Inter", font_size=24)
    run_2 = TextRun(text="World", color=(255, 255, 100), font="Inter", font_size=24)

    data_1 = TextData(runs=[run_1, run_2])
    data_2 = TextData(runs=[run_1, run_2])

    assert data_1 == data_2


def test_text_data_different():
    run_1 = TextRun(text="Hello", color=(255, 255, 100), font="Inter", font_size=24)
    run_2 = TextRun(text="World", color=(255, 255, 100), font="Inter", font_size=24)
    run_3 = TextRun(text="World", color=(255, 255, 100), font="Inter", font_size=24)

    data_1 = TextData(runs=[run_1, run_2])
    data_2 = TextData(runs=[run_2, run_3])

    assert data_1 != data_2


def test_text_data_cache_state():
    data = parse_coshml(
        text="Hello",
        text_color=(255, 255, 255),
        font="Arial.ttf",
        font_size=16,
        letter_spacing=1.0,
        word_spacing=2.0,
        line_spacing=3.0,
        text_justify=CoshTextJustify.CENTER,
        text_align=CoshTextAlign.CENTER,
        text_overflow=CoshTextOverflow.VISIBLE,
        bold=False,
        italic=False,
        underline=False,
        strikethrough=False,
    )

    expected = {
        "raw_text": "Hello",
        "letter_spacing": 1.0,
        "word_spacing": 2.0,
        "line_spacing": 3.0,
        "text_align": CoshTextAlign.CENTER,
        "text_justify": CoshTextJustify.CENTER,
        "text_overflow": CoshTextOverflow.VISIBLE,
        "font": "Arial.ttf",
        "font_size": 16,
        "color": (255, 255, 255),
    }

    assert data.cached_state() == expected


def test_text_data_cache_state_uses_raw_text():
    red = parse_coshml(
        text="[red]Hello[/]",
        text_color=(255, 255, 255),
        font="Arial.ttf",
        font_size=16,
        letter_spacing=None,
        word_spacing=None,
        line_spacing=None,
        text_justify=CoshTextJustify.CENTER,
        text_align=CoshTextAlign.CENTER,
        text_overflow=CoshTextOverflow.VISIBLE,
        bold=False,
        italic=False,
        underline=False,
        strikethrough=False,
    )

    blue = parse_coshml(
        text="[blue]Hello[/]",
        text_color=(255, 255, 255),
        font="Arial.ttf",
        font_size=16,
        letter_spacing=None,
        word_spacing=None,
        line_spacing=None,
        text_justify=CoshTextJustify.CENTER,
        text_align=CoshTextAlign.CENTER,
        text_overflow=CoshTextOverflow.VISIBLE,
        bold=False,
        italic=False,
        underline=False,
        strikethrough=False,
    )

    assert red.text == blue.text
    assert red.raw_text != blue.raw_text
    assert red.cached_state() != blue.cached_state()


def test_text_data_bold_italic():
    data = parse_coshml(
        text="[bold italic]Hello[/]",
        text_color=(255, 255, 255),
        font="Inter",
        font_size=16,
        letter_spacing=None,
        word_spacing=None,
        line_spacing=None,
        text_justify=CoshTextJustify.CENTER,
        text_align=CoshTextAlign.CENTER,
        text_overflow=CoshTextOverflow.VISIBLE,
        bold=False,
        italic=False,
        underline=False,
        strikethrough=False,
    )

    assert len(data.runs) == 1
    assert data.runs[0].bold is True
    assert data.runs[0].italic is True