"""Strands Fun Tools - Individual tool modules."""

__version__ = "0.1.0"

# Core tools (only require base deps: pyautogui, pyperclip, pillow)
from .cursor import cursor
from .clipboard import clipboard
from .human_typer import human_typer
from .dynamic_package import dynamic_package

__all__ = [
    "cursor",
    "clipboard",
    "human_typer",
    "dynamic_package",
]

# Optional tools (require extra dependencies)
try:
    from .template import template

    __all__.append("template")
except ImportError:
    pass

try:
    from .utility import utility

    __all__.append("utility")
except ImportError:
    pass

try:
    from .chess import chess

    __all__.append("chess")
except ImportError:
    pass

try:
    from .bluetooth import bluetooth

    __all__.append("bluetooth")
except ImportError:
    pass

try:
    from .screen_reader import screen_reader

    __all__.append("screen_reader")
except ImportError:
    pass

try:
    from .yolo_vision import yolo_vision

    __all__.append("yolo_vision")
except ImportError:
    pass

try:
    from .face_recognition import face_recognition

    __all__.append("face_recognition")
except ImportError:
    pass

try:
    from .take_photo import take_photo

    __all__.append("take_photo")
except ImportError:
    pass

try:
    from .listen import listen

    __all__.append("listen")
except ImportError:
    pass

try:
    from .spinner_generator import spinner_generator

    __all__.append("spinner_generator")
except ImportError:
    pass

try:
    from .npm import npm

    __all__.append("npm")
except ImportError:
    pass

try:
    from .dialog import dialog

    __all__.append("dialog")
except ImportError:
    pass

try:
    from .asciimatics_ui import asciimatics_ui

    __all__.append("asciimatics_ui")
except ImportError:
    pass
