"""A Tkinter PictureBox widget for displaying an OpenCV image.

This module provides the following class definitions:

* PictureBox  - A Tkinter widget class for displaying an OpenCV image
* BorderStyle - A data class of the available border style options
* ImageMode   - A data class of the available image display mode options
"""

__version__ = '1.2.0'

import platform
import warnings
from typing import Any, Tuple, Union
from dataclasses import dataclass
import tkinter as tk
import numpy as np
from PIL import Image, ImageTk, ImageColor
import cv2


@dataclass(frozen=True)
class BorderStyle:
    """The available border style options for the PictureBox.

    Attributes
    ----------
    Raised
        The PictureBox appears raised above the background.
    Sunken
        The PictureBox appears recessed into the background.
    Groove
        The PictureBox has a carved groove border.
    Ridge
        The PictureBox has a raised ridge border.
    Solid
        The PictureBox has a simple solid border.
    Flat
        The PictureBox appears flat, no border.
    """

    Raised = tk.RAISED
    Sunken = tk.SUNKEN
    Groove = tk.GROOVE
    Ridge = tk.RIDGE
    Solid = tk.SOLID
    Flat = tk.FLAT


@dataclass(frozen=True)
class ImageMode:
    """The available image display mode options for the PictureBox.

    Attributes
    ----------
    Normal
        The image is placed in the upper-left corner of the PictureBox.
        The image is clipped if it is larger than the PictureBox.
    CenterImage
        If the PictureBox is larger than the image, the image is displayed
        in the center of the PictureBox.
        If the image is larger than the PictureBox, the image is centered
        in the PictureBox, and the outside edges of the image are clipped.
    StretchImage
        The image is stretched or shrunk to fit the size of the PictureBox.
    AutoSize
        The size of PictureBox is changed to match the size of the image.
    Zoom
        The size of the image is increased or decreased to fit the size
        of the PictureBox, while keeping the image's original size ratio.
    """

    Normal = 0
    CenterImage = 1
    StretchImage = 2
    AutoSize = 3
    Zoom = 4


class PictureBox(tk.Label):
    """The Tkinter PictureBox widget for displaying an OpenCV image."""

    @dataclass
    class _Properties:
        """The PictureBox widget properties."""

        size: Tuple[int, int]
        color: tuple
        mode: int
        image: Any
        backgnd_image: Any

    def __init__(self, parent: Any, width: int, height: int):
        """Create and initialize the PictureBox widget.

        Parameters
        ----------
        parent : Any
            The parent widget of the PictureBox
        width : int
            The initial width of the PictureBox (in pixels)
        height: int
            The initial height of the PictureBox (in pixels)

        Notes
        -----
        By default, the border style is set to BorderStyle.Flat,
        and the image display mode is set to ImageMode.Normal
        """
        super().__init__(parent)
        linux = platform.platform().startswith('Linux')
        color = ImageColor.getrgb('#d9d9d9' if linux else '#f0f0f0')[0:3]
        size = (max(1, int(width)), max(1, int(height)))
        mode = ImageMode.Normal
        image = Image.new('RGB', size, color)
        self._image = np.array(image)
        self._widget = self._Properties(size, color, mode, image, image)
        self._disp_image = ImageTk.PhotoImage(image)
        self['image'] = self._disp_image
        self.border_style = BorderStyle.Flat

    @property
    def border_style(self) -> str:
        """Get/Set the border style of the PictureBox.

        This must be one of the available BorderStyle options.
        """
        return self['relief']

    @border_style.setter
    def border_style(self, style: str) -> None:
        """Get/Set the border style of the PictureBox.

        This must be one of the available BorderStyle options.
        """
        width = -1
        if style in (tk.RAISED, tk.SUNKEN, tk.RIDGE):
            width = 3
        elif style in (tk.GROOVE, tk.SOLID):
            width = 2
        elif style == tk.FLAT:
            width = 0

        if width >= 0:
            self['bd'] = width
            self['relief'] = style
        else:
            warnings.warn('Invalid border style designator', stacklevel=2)

    @property
    def image_mode(self) -> int:
        """Get/Set the image display mode of the PictureBox.

        This must be one of the available ImageMode options.
        """
        return self._widget.mode

    @image_mode.setter
    def image_mode(self, mode: int) -> None:
        """Get/Set the image display mode of the PictureBox.

        This must be one of the available ImageMode options.
        """
        if self._valid_display(mode):
            self._widget.mode = mode
            self._create_displayed_image()
        else:
            warnings.warn('Invalid image mode designator', stacklevel=2)

    @property
    def height(self) -> int:
        """Get/Set the current height of the PictureBox (in pixels)."""
        return self._widget.size[1]

    @height.setter
    def height(self, value: int) -> None:
        """Get/Set the current height of the PictureBox (in pixels)."""
        self._widget.size = (self.width, max(1, int(value)))
        self._redraw_widget()

    @property
    def width(self) -> int:
        """Get/Set the current width of the PictureBox (in pixels)."""
        return self._widget.size[0]

    @width.setter
    def width(self, value: int) -> None:
        """Get/Set the current width of the PictureBox (in pixels)."""
        self._widget.size = (max(1, int(value)), self.height)
        self._redraw_widget()

    def clear(self) -> None:
        """Clear the currently displayed image."""
        self._widget.backgnd_image = self._widget.image = self._backgnd_image()
        self._image = np.array(self._widget.image)
        self._redraw_image()

    def display(self, image: Union[np.ndarray, cv2.Mat, None]) -> bool:
        """Display the specified image in the PictureBox.

        Parameters
        ----------
        image : ndarray | Mat | None
            Images with a color space representation of Grayscale,
            BGR, or BGRA will be displayed correctly in the PictureBox.
            The cv2.cvtColor(src, code) function should to used to convert
            images, with other color spaces, into the BGR color space.

        Returns
        -------
        bool
            True if the specified image is valid, False otherwise
        """
        if isinstance(image, cv2.Mat):
            image = np.array(image)

        if isinstance(image, np.ndarray) and self._valid_format(image):
            if image.ndim == 2:
                mode = cv2.COLOR_GRAY2RGB
            else:
                depth = image.shape[2]
                mode = cv2.COLOR_BGR2RGB if depth == 3 else cv2.COLOR_BGRA2RGB
            self._image = cv2.cvtColor(image, mode)
            self._create_displayed_image()
            success = True
        else:
            warnings.warn('Missing or invalid image', stacklevel=2)
            success = False
        return success

    def load(self, filename: str) -> bool:
        """Load and display an image from the specified file.

        Parameters
        ----------
        filename : str
            The full pathname of the image file

        Returns
        -------
        bool
            True if the image was successfully loaded, False otherwise
        """
        return self.display(cv2.imread(filename, cv2.IMREAD_COLOR_BGR))

    def save(self, filename: str) -> bool:
        """Save the currently displayed image to the specified file.

        Parameters
        ----------
        filename : str
            The full pathname of the image file

        Returns
        -------
        bool
            True if the image was successfully saved, False otherwise
        """
        image = cv2.cvtColor(np.array(self._widget.image), cv2.COLOR_RGB2BGR)
        try:
            success = cv2.imwrite(filename, image)
        except cv2.error:
            warnings.warn('Invalid image filename', stacklevel=2)
            success = False
        return success

    def set_background(
        self,
        color: Union[str, Tuple[int, int, int], Tuple[float, float, float]],
    ) -> None:
        """Set the background color of the PictureBox.

        Parameters
        ----------
        color : str | tuple[int, int, int] | tuple[float, float, float]
            This value can be specified as a named color, e.g. 'white',
            specified as a 6-digit hexadecimal notation string: '#rrggbb',
            or specified as a tuple value (red, green, blue) which contains
            either three integer color values ranging from 0 to 255,
            or three floating point color values ranging from 0.0 to 1.0
        """
        try:
            if isinstance(color, str):
                self._widget.color = ImageColor.getrgb(color)[0:3]
            else:
                self._widget.color = self._rgb(color)
            self._redraw_widget()
        except ValueError:
            warnings.warn('Unrecognized background color name', stacklevel=2)

    def _backgnd_image(self) -> Any:
        """Generate a new background color image."""
        return Image.new('RGB', self._widget.size, self._widget.color)

    def _create_displayed_image(self) -> None:
        """Create the displayed image as dictated by the size mode."""
        image_height, image_width = self._image.shape[0:2]

        if self._widget.mode == ImageMode.AutoSize:
            if self._widget.size != (image_width, image_height):
                self._widget.size = (image_width, image_height)
                self._widget.backgnd_image = self._backgnd_image()
            displayed_image = self._image

        elif self._widget.mode == ImageMode.StretchImage:
            displayed_image = cv2.resize(self._image, self._widget.size)

        elif self._widget.mode == ImageMode.CenterImage:
            displayed_image = self._centered_image(image_width, image_height)

        elif self._widget.mode == ImageMode.Zoom:
            displayed_image = self._zoomed_image(image_width, image_height)

        else:  # ImageMode.Normal
            width = min(image_width, self.width)
            height = min(image_height, self.height)
            displayed_image = np.array(self._widget.backgnd_image)
            displayed_image[0:height, 0:width] = self._image[0:height, 0:width]

        self._widget.image = Image.fromarray(displayed_image)
        self._redraw_image()

    def _centered_image(self, image_width, image_height) -> np.ndarray:
        """Center the image in the PictureBox."""
        width = min(image_width, self.width)
        start = (max(image_width, self.width) - width) // 2
        x_0, x_2 = (0, start) if image_width > width else (start, 0)
        x_1, x_3 = x_0 + width, x_2 + width

        height = min(image_height, self.height)
        start = (max(image_height, self.height) - height) // 2
        y_0, y_2 = (0, start) if image_height > height else (start, 0)
        y_1, y_3 = y_0 + height, y_2 + height

        centered_image = np.array(self._widget.backgnd_image)
        centered_image[y_0:y_1, x_0:x_1] = self._image[y_2:y_3, x_2:x_3]
        return centered_image

    def _zoomed_image(self, image_width, image_height) -> np.ndarray:
        """Fit the image in the PictureBox keeping its original size ratio."""
        size_ratio = image_width / image_height

        if size_ratio > self.width / self.height:
            width, height = self.width, int(self.width / size_ratio)
            x_0, y_0 = 0, (self.height - height) // 2
        else:
            width, height = int(self.height * size_ratio), self.height
            x_0, y_0 = (self.width - width) // 2, 0

        size = (width, height)
        x_1, y_1 = x_0 + width, y_0 + height

        zoomed_image = np.array(self._widget.backgnd_image)
        zoomed_image[y_0:y_1, x_0:x_1] = cv2.resize(self._image, size)
        return zoomed_image

    def _redraw_image(self) -> None:
        """Redraw the PictureBox image."""
        self._disp_image = ImageTk.PhotoImage(self._widget.image)
        self['image'] = self._disp_image

    def _redraw_widget(self) -> None:
        """Redraw the entire PictureBox widget."""
        if self._widget.backgnd_image == self._widget.image:
            self.clear()
        else:
            self._widget.backgnd_image = self._backgnd_image()
            self._create_displayed_image()

    def _rgb(self, color: tuple) -> tuple:
        """Generate a valid rgb color value."""
        if len(color) == 3 and all(self._is_number(value) for value in color):
            if any(isinstance(value, float) for value in color):
                color = tuple(round(256 * value) for value in color)
            color_value = tuple(max(0, min(value, 255)) for value in color)
        else:
            color_value = self._widget.color
            warnings.warn('Invalid background color value', stacklevel=3)
        return color_value

    @staticmethod
    def _is_number(value: Any) -> bool:
        """Test for a numerical value."""
        return isinstance(value, (int, float)) and not isinstance(value, bool)

    @staticmethod
    def _valid_format(image: np.ndarray) -> bool:
        """Test for a valid 2d-image format."""
        valid = (image.dtype == np.uint8) and image.ndim in (2, 3)
        if valid and image.ndim == 3:
            valid = image.shape[2] in (3, 4)
        return valid

    @staticmethod
    def _valid_display(mode: Any) -> bool:
        """Test for a valid image display mode value."""
        return (
            isinstance(mode, int)
            and ImageMode.Normal <= mode <= ImageMode.Zoom
        )
