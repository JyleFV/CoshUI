from dataclasses import dataclass, field
from typing import Literal
import difflib

from .state import CoshUI
from .cui_error import CoshUIError
from .types import TextData
from .utility import resolve_font_variant

# region Validators
def validate_color(value: str) -> tuple:
    try:
        parsed = tuple(int(x.strip()) for x in value.strip("()").split(","))
    except ValueError:
        raise CoshUIError.CoshML(f"Invalid color value `{value}`. Expected a tuple of 3 integers e.g. `(255, 0, 0)`.")
    
    if len(parsed) != 3 or not all(0 <= c <= 255 for c in parsed):
        raise CoshUIError.CoshML(f"Invalid color value `{value}`. Each channel must be between 0 and 255.")
    
    return parsed

def validate_font(font: str, bold: bool, italic: bool):
    validated_font = resolve_font_variant(CoshUI._font_library.get(font), bold, italic, font)
    if validated_font is None:
        raise CoshUIError.CoshML(f"`{font}` is not a valid font.")
    
    return validated_font

def validate_font_size(size: str):
    try:
        final_size = int(size)
    except ValueError:
        raise CoshUIError.CoshML(f"Invalid size value `{size}` for font_size. Input a proper integer.")
    
    return final_size 
# endregion

TAGS = {
    "color": validate_color,
    "font": validate_font,
    "font_size": validate_font_size
}

KEYWORD_MAP = {
    "bold": ("bold", True),
    "italic": ("italic", True),
    "underline": ("underline", True),
    "strikethrough": ("strikethrough", True),
    "blue": ("color", (0, 0, 255)),
    "red": ("color", (255, 0, 0)),
    "green": ("color", (0, 255, 0)),
    "white": ("color", (255, 255, 255)),
}

@dataclass
class TextStyle:
    color: tuple | None = None
    font_size: int | None = None
    font: str | None = None
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strikethrough: bool = False
    _font_family: str | None = field(default=None, repr=False)

    def _style_dict(self):
        return {
            "color": self.color,
            "font_size": self.font_size,
            "font": self.font,
            "bold": self.bold,
            "italic": self.italic,
            "underline": self.underline,
            "strikethrough": self.strikethrough,
        }

@dataclass
class TextRun(TextStyle):
    text: str | None = None

@dataclass
class Token:
    type: Literal["text", "tag", "close"]
    value: str

def tokenize(text: str) -> list[Token]:
    tokens = []
    i = 0
    while i < len(text):
        if text[i] == "[":
            end = text.find("]", i)
            if end == -1:
                raise CoshUIError.CoshML("Missing `]` closing tag. Did you forget to close a tag?")
            tag_content = text[i + 1:end]
            if tag_content == "/":
                tokens.append(Token("close", ""))
            else:
                tokens.append(Token("tag", tag_content))
            i = end + 1
        else:
            end = text.find("[", i)
            end = end if end != -1 else len(text)
            tokens.append(Token("text", text[i:end]))
            i = end
    return tokens

def parse_tag(tag: str) -> dict:
    style = {}
    parts = []
    current = ""
    depth = 0

    for i, char in enumerate(tag):
        if char == "(":
            depth += 1
            current += char

        elif char == ")":
            depth -= 1
            if depth < 0:
                raise CoshUIError.CoshML(f"Unexpected ')' at position {i + 1} of CoshML tag `{tag}`.")
            current += char

        elif char == " " and depth == 0:
            if current:
                parts.append(current)
            current = ""

        else:
            current += char

    if depth > 0:
        raise CoshUIError.CoshML(f"Unclosed parenthesis in CoshML tag `{tag}`.")
    
    if current:
        parts.append(current)

    for part in parts:
        if part in TAGS: # This means the part is a TAG that has no value
            raise CoshUIError.CoshML(f"The tag `{part}` needs a value.")
        elif "=" in part:
            key, value = part.split("=", 1)
            known_keys = set(TAGS.keys())
            if key not in known_keys:
                close_match = difflib.get_close_matches(key, known_keys, n=1)
                raise CoshUIError.CoshML(
                    f"Unknown CoshML attribute `{key}`. Did you mean `{close_match[0] if close_match else 'Unknown'}`?"
                )
            style[key] = value
        elif part in KEYWORD_MAP:
            attr, val = KEYWORD_MAP[part]
            style[attr] = val
        elif part in CoshUI._text_style_class:
            text_style = CoshUI._text_style_class[part]
            style.update(text_style._style_dict())
        else:
            all_known = list(KEYWORD_MAP.keys()) + list(CoshUI._text_style_class.keys())
            close_match = difflib.get_close_matches(part, all_known, n=1)
            raise CoshUIError.CoshML(
                f"Unknown CoshML tag `{part}`. Did you mean `{close_match[0] if close_match else 'Unknown'}`?"
            )

    return style

def parse_coshml(text: str, text_color: tuple, font_name: str, font: str, font_size: int, letter_spacing: float, word_spacing: float, line_spacing: float, text_justify, text_align, text_overflow, strikethrough, underline, bold, italic) -> TextData:
    tokens = tokenize(text)
    context = TextData(
        letter_spacing=letter_spacing, word_spacing=word_spacing, 
        line_spacing=line_spacing, text_align=text_align, 
        text_justify=text_justify, text_overflow=text_overflow,
        raw_text=text, default_color=text_color, default_font=font, default_font_size=font_size
    )

    base_style = TextStyle(color=text_color, _font_family=font_name, font=font, font_size=font_size, strikethrough=strikethrough, underline=underline, bold=bold, italic=italic)
    style_stack = [base_style]
    full_text = ""

    for token in tokens:
        match token.type:
            case "text":
                current = style_stack[-1]
                context.runs.append(TextRun(
                    text=token.value,
                    color=current.color,
                    font=current.font,
                    font_size=current.font_size,
                    bold=current.bold,
                    italic=current.italic,
                    underline=current.underline,
                    strikethrough=current.strikethrough,
                ))
                full_text += token.value
            case "tag":
                current = style_stack[-1]
                overrides = parse_tag(token.value)
                style_stack.append(validate_style(current, overrides))
            case "close":
                if len(style_stack) == 1:
                    raise CoshUIError.CoshML("Closing tag found without any tags, please follow the appropriate use of CoshML.")
                if len(style_stack) > 1:
                    style_stack.pop()

    if len(style_stack) != 1:
        raise CoshUIError.CoshML(f"{len(style_stack) - 1} unclosed tag(s). Did you forget a closing tag `[/]`?")

    context.text = full_text

    return context

# region HELPERS
def validate_style(current: TextStyle, overrides: dict) -> TextStyle:
    # Color
    override_color = overrides.get("color", None)
    if override_color is not None:
        color = TAGS["color"](override_color) if isinstance(override_color, str) else override_color
    else:
        color = current.color

    # Font
    override_font_family = overrides.get("font", current._font_family)
    override_bold = overrides.get("bold", current.bold)
    override_italic = overrides.get("italic", current.italic)

    resolved_font = TAGS["font"](override_font_family, override_bold, override_italic)

    # Font size
    override_font_size = overrides.get("font_size", None)
    if override_font_size is not None:
        font_size = TAGS["font_size"](override_font_size) if isinstance(override_font_size, str) else override_font_size
    else:
        font_size = current.font_size

    return TextStyle(
        color=color,
        font=resolved_font,
        font_size=font_size,
        bold=overrides.get("bold", current.bold),
        italic=overrides.get("italic", current.italic),
        underline=overrides.get("underline", current.underline),
        strikethrough=overrides.get("strikethrough", current.strikethrough),
        _font_family=override_font_family
    )
# endregion