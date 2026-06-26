from dataclasses import dataclass

from .cui_error import CoshUIError

# region Validators
def validate_color():
    pass

def validate_font():
    pass
# endregion

TAGS = {
    "color" : {
        "attribute" : "color",
        "validator" : validate_color,
        "expects_value" : True
    },
    "font" : {
        "attribute" : "font",
        "validator" : validate_font,
        "expects_value" : True
    }
}

@dataclass
class TextStyle:
    color: tuple = (255, 255, 255)
    font_size: int | None = None
    font: str | None = None
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strikethrough: bool = False
    letter_spacing : float | None = None
    line_spacing : float | None = None
    word_spacing : float | None = None

@dataclass
class TextRun(TextStyle):
    text : str | None = None

    def _style_dict(self):
        return {
            "color" : self.color,
            "size" : self.size,
            "font" : self.font,
            "bold" : self.bold,
            "italic" : self.italic,
            "underline" : self.underline,
            "strikethrough" : self.strikethrough,
            "letter_spacing" : self.letter_spacing,
            "line_spacing" : self.line_spacing,
            "word_spacing" : self.word_spacing
        }

class TextContext:
    def __init__(self):
        self.runs : list[TextRun] = []
    
    def is_uniform(self) -> bool:
        if not self.runs:
            return True

        first = self.runs[0]._style_dict()
        return all(run.style_dict() == first for run in self.runs)

def parse_coshml(text : str, text_color : tuple, font : str, font_size : int) -> TextContext:
    base = TextContext()

    default_style = TextStyle(
        color=text_color,
        font=font,
        font_size=font_size
    )

    if "[" not in text and "]" not in text:
        base.runs.append(TextRun(text=text, font_size=font_size, font=font, color=text_color))
    
        return base

    style_stack = [default_style]
    buffer = ""
    i = 0

    while i < len(text):
        current_character = text[i]

        if current_character == "[":
            end = text.find("]", i)

            if end == -1:
                raise CoshUIError("Missing closing ']' for a tag.")
            
            tag = text[i + 1:end]

            if "[" == tag:
                raise CoshUIError("""
                                [CoshML] \n
                                Unexpected '[' inside tag.
                                Did you forget to close a tag with ']'?
                                """)

            if "=" == tag:
                attribute, value = tag.split("=", 1)

            i = end + 1
            continue
        else:
            pass
        
        i += 1

