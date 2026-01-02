import cv2
import numpy as np
import tkinter as tk
from dataclasses import dataclass
from typing import Any

__version__: str

@dataclass(frozen=True)
class BorderStyle:
    Raised: str
    Sunken: str
    Groove: str
    Ridge: str
    Solid: str
    Flat: str

@dataclass(frozen=True)
class ImageMode:
    Normal: int
    CenterImage: int
    StretchImage: int
    AutoSize: int
    Zoom: int

class PictureBox(tk.Label):
    def __init__(self, parent: Any, width: int, height: int): ...
    @property
    def border_style(self) -> str: ...
    @border_style.setter
    def border_style(self, style: str) -> None: ...
    @property
    def image_mode(self) -> int: ...
    @image_mode.setter
    def image_mode(self, mode: int) -> None: ...
    @property
    def height(self) -> int: ...
    @height.setter
    def height(self, value: int) -> None: ...
    @property
    def width(self) -> int: ...
    @width.setter
    def width(self, value: int) -> None: ...
    def clear(self) -> None: ...
    def display(self, image: np.ndarray | cv2.Mat | None) -> bool: ...
    def load(self, filename: str) -> bool: ...
    def save(self, filename: str) -> bool: ...
    def set_background(self, color: str | tuple[int, int, int] | tuple[float, float, float]) -> None: ...
