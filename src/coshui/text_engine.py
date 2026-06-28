from dataclasses import dataclass
from typing import Literal

from .state import CoshUI
from .cui_error import CoshUIError

# region Validators
def validate_color(value: str) -> tuple:
    try:
        parsed = tuple(int(x.strip()) for x in value.strip("()").split(","))
    except ValueError:
        raise CoshUIError(f"[CoshML] Invalid color value `{value}`. Expected a tuple of 3 integers e.g. `(255, 0, 0)`.")
    
    if len(parsed) != 3 or not all(0 <= c <= 255 for c in parsed):
        raise CoshUIError(f"[CoshML] Invalid color value `{value}`. Each channel must be between 0 and 255.")
    
    return parsed

def validate_font(font : str):
    validated_font = CoshUI._font_library.get(font, None)
    if validated_font is None:
        raise CoshUIError(f"[CoshML] `{font}` is not a valid font.")
    
    return validated_font

def validate_font_size(size : str):
    try:
        final_size = int(size)
    except ValueError:
        raise CoshUIError(f"[CoshML] Invalid size value `{size}` for font_size. Input a proper integer.")
    
    return final_size 
# endregion

TAGS = {
    "color" : {
        "attribute" : "color",
        "validator" : validate_color
    },
    "font" : {
        "attribute" : "font",
        "validator" : validate_font
    },
    "font_size" : {
        "attribute" : "font_size",
        "validator" : validate_font_size
    }
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

@dataclass
class TextRun(TextStyle):
    text : str | None = None

    def _style_dict(self):
        return {
            "color" : self.color,
            "size" : self.font_size,
            "font" : self.font,
            "bold" : self.bold,
            "italic" : self.italic,
            "underline" : self.underline,
            "strikethrough" : self.strikethrough,
        }

class TextContext:
    def __init__(self, letter_spacing=None, word_spacing=None, line_spacing=None):
        self.runs: list[TextRun] = []
        self.letter_spacing = letter_spacing
        self.line_spacing = line_spacing
        self.word_spacing = word_spacing
    
    def is_uniform(self) -> bool:
        if not self.runs:
            return True

        first = self.runs[0]._style_dict()
        return all(run._style_dict() == first for run in self.runs)

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

    # TODO: Add _text_style_class to make user-generated tags using add_class()

    for char in tag:
        if char == "(":
            depth += 1
            current += char
        elif char == ")":
            depth -= 1
            current += char
        elif char == " " and depth == 0:
            if current:
                parts.append(current)
            current = ""
        else:
            current += char
    
    if current:
        parts.append(current)

    for part in parts:
        if "=" in part:
            key, value = part.split("=", 1)
            style[key] = value
        elif part in KEYWORD_MAP:
            attr, val = KEYWORD_MAP[part]
            style[attr] = val
    
    return style

def parse_coshml(text: str, text_color: tuple, font: str, font_size: int, letter_spacing : float, word_spacing : float, line_spacing : float) -> TextContext:
    tokens = tokenize(text)
    context = TextContext(letter_spacing=letter_spacing, word_spacing=word_spacing, line_spacing=line_spacing)

    base_style = TextStyle(color=text_color, font=font, font_size=font_size)
    style_stack = [base_style]

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
            case "tag":
                current = style_stack[-1]
                overrides = parse_tag(token.value)
                override_color = overrides.get("color", current.color)
                override_font = overrides.get("font", current.font)
                override_font_size = overrides.get("font_size", current.font_size)
                new_style = TextStyle(
                    color=TAGS["color"]["validator"](override_color) if isinstance(override_color, str) else override_color,
                    font=TAGS["font"]["validator"](override_font) if isinstance(override_font, str) else override_font,
                    font_size=TAGS["font_size"]["validator"](override_font_size) if isinstance(override_font_size, str) else override_font_size,
                    bold=overrides.get("bold", current.bold),
                    italic=overrides.get("italic", current.italic),
                    underline=overrides.get("underline", current.underline),
                    strikethrough=overrides.get("strikethrough", current.strikethrough),
                )
                style_stack.append(new_style)
            case "close":
                if len(style_stack) > 1:
                    style_stack.pop()

    return context