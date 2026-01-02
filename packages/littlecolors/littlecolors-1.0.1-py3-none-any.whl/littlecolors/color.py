
# Imports ----------------------------------------------------------------------
import random
from typing import Iterator
from collections.abc import Sequence
from dataclasses import dataclass
import colorsys
from littlecolors.utils import clamp, cval_to_cval256, hex_to_rgb, rgb_to_hex, cval256_to_str


# Color ------------------------------------------------------------------------
@dataclass(init=False, slots=True)
class Color:
    """Object to define and manipulate a Color."""

    # Color properties
    _rgb: tuple[float, float, float]
    _weight: float # only used for color interpolation

    # Constructor --------------------------------------------------------------
    def __init__(
            self,
            arg1: int | float | str | Sequence[float | int],
            arg2: int | float | None = None,
            arg3: int | float | None = None,
        ):
        """
        Parameters
        ----------
        arg1 : int | float | str | Sequence[float | int]
            red (as int in [0, 255] or float in [0., 1.]),  
            or greyscale if next values are omitted,  
            or hexadecimal color string as '#33cccc'

        arg2 : int | float | None, optional
            green (as int in [0, 255] or float in [0., 1.])

        arg3 : int | float | None, optional
            blue (as int in [0, 255] or float in [0., 1.])

        Example
        -------
        >>> from littlecolors import Color
        >>> c1 = Color(0.2)
        >>> c2 = Color(120, 189, 56)
        >>> c3 = Color('#33cccc')
        """

        # Input as HEX string
        if isinstance(arg1, str):

            # Guardians
            if arg2 is not None or arg3 is not None:
                raise TypeError("If arg1 is a string, Color() expects only 1 argument")
            
            # Convert
            arg1, arg2, arg3 = hex_to_rgb(arg1)

        # Unpack from a list / tuple
        elif isinstance(arg1, Sequence):

            # Guardians
            if arg2 is not None or arg3 is not None:
                raise TypeError("If arg1 is a list / tuple, Color() expects only 1 argument")
            if len(arg1) != 3:
                raise ValueError("If Color() arg1 is a list / tuple, it must be of length 3")
            
            # Unpack
            arg1, arg2, arg3 = arg1

        # Ensure either 1 argument (grayscale) or 3 arguments (RGB)
        if (arg2 is None) != (arg3 is None):
            raise TypeError("Color() must be called with 1 or 3 arguments.")

        # Input from greyscale (1 single value)
        if arg2 is None and arg3 is None:
            arg2 = arg3 = arg1
        
        # Convert from integerts
        if isinstance(arg1, int):
            if not isinstance(arg2, int) or not isinstance(arg3, int):
                raise TypeError("All RGB arguments must be of the same type (int or float)")
            if not (0 <= arg1 <= 255 and 0 <= arg2 <= 255 and 0 <= arg3 <= 255):
                raise ValueError("Color integer descriptor should be in [0, ..., 255]")
            arg1 = arg1 / 255.0
            arg2 = arg2 / 255.0
            arg3 = arg3 / 255.0

        # Float values guardians
        elif isinstance(arg1, float):
            if not isinstance(arg2, float) or not isinstance(arg3, float):
                raise TypeError("All RGB arguments must be of the same type (int or float)")
            if not (0.0 <= arg1 <= 1.0 and 0.0 <= arg2 <= 1.0 and 0.0 <= arg3 <= 1.0):
                raise ValueError("Color() float descriptor should be in interval [0.0, 1.0]")
        else:
            raise TypeError(
                "Color() arguments must be: 1 grayscale (int or float), "
                "3 RGB (int or float), or a HEX string"
            )

        # Define color
        self._rgb = (arg1, arg2, arg3)
        self._weight = 1.0

    @classmethod
    def random(cls) -> "Color":
        return Color(random.random(), random.random(), random.random())

    @classmethod
    def from_hls(cls, h: float, l: float, s: float) -> "Color":
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return Color(r, g, b)
    
    @classmethod
    def from_hsv(cls, h: float, s: float, v: float) -> "Color":
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return Color(r, g, b)

    # Utils Properties ---------------------------------------------------------
    def copy(self) -> "Color":
        col = Color(self.r, self.g, self.b)
        col._weight = self._weight
        return col
    
    def __eq__(self, other: "Color") -> bool:
        return self.r256 == other.r256 and self.g256 == other.g256 and self.b256 == other.b256
    
    def __str__(self):
        return f"Color({self.r256}, {self.g256}, {self.b256})"
    
    def __repr__(self):
        return str(self)
    
    def __mul__(self, other: float | int) -> "Color": # for color interpolation
        if not isinstance(other, (int, float)):
            raise TypeError("Color can only be multiplied by a float or int")
        if other < 0.0:
            raise ValueError("Color can only be multipled by a positive number")
        col = self.copy()
        col._weight = col._weight * float(other)
        return col
    __rmul__ = __mul__ # also define right multiplication by commutativity
    
    def __add__(self, other: "Color") -> "Color":
        if not isinstance(other, Color):
            raise TypeError("Addition is only defined between two colors")
        r1, g1, b1 = self.rgb
        r2, g2, b2 = other.rgb
        w1, w2 = self._weight, other._weight
        w = w1 + w2
        if w == 0.0:
            w = 1.0
        r = (w1*r1 + w2*r2) / w
        g = (w1*g1 + w2*g2) / w
        b = (w1*b1 + w2*b2) / w
        return Color(r, g, b)
        
    def __lt__(self, other: "Color") -> bool:
        return self.greyscale256() < other.greyscale256()

    def __le__(self, other: "Color") -> bool:
        return self.greyscale256() <= other.greyscale256()
    
    # Base Values --------------------------------------------------------------
    @property
    def rgb(self) -> tuple[float, float, float]:
        """Return RGB as a tuple of floats in interval [0.0, 1.0]."""
        return self._rgb
        
    @property
    def red(self) -> float:
        return self._rgb[0]
    r = red
    
    @property
    def green(self) -> float:
        return self._rgb[1]
    g = green
    
    @property
    def blue(self) -> float:
        return self._rgb[2]
    b = blue
    
    @property
    def rgb256(self) -> tuple[int, int, int]:
        """Return RGB as a tuple of int in interval [0.0, 255]."""
        return (self.r256, self.g256, self.b256)
    
    @property
    def rgb256_str(self) -> str:
        """Return RGB 256 representation as a standarized string '(  2,  25, 152)'"""
        return f"({cval256_to_str(self.r256)}, {cval256_to_str(self.g256)}, {cval256_to_str(self.b256)})"
    
    @property
    def red256(self) -> int:
        return cval_to_cval256(self.red)
    r256 = red256
    
    @property
    def green256(self) -> int:
        return cval_to_cval256(self.green)
    g256 = green256
    
    @property
    def blue256(self) -> int:
        return cval_to_cval256(self.blue)
    b256 = blue256    

    # Convertions --------------------------------------------------------------
    def greyscale(self) -> float:
        return (self.r + self.g + self.b) / 3.0
    
    def greyscale256(self) -> int:
        return cval_to_cval256(self.greyscale())

    def hls(self) -> tuple[float, float, float]:
        r, g, b = self.rgb
        return colorsys.rgb_to_hls(r, g, b)
    
    def hsv(self) -> tuple[float, float, float]:
        r, g, b = self.rgb
        return colorsys.rgb_to_hsv(r, g, b)
    
    def hue(self) -> float:
        return self.hls()[0]
    h = hue
    
    def lightness(self) -> float:
        return self.hls()[1]
    l = lightness
    
    def saturation(self) -> float:
        return self.hls()[2]
    s = saturation
    
    def value(self) -> float:
        return self.hsv()[2]
    v = value
    
    def hex(self) -> str:
        """Return HEX string color."""
        r, g, b = self._rgb
        return rgb_to_hex(r, g, b)
        
    # Methods ------------------------------------------------------------------
    @classmethod
    def interpolate(cls, color1: "Color", color2: "Color", coeff: float=0.5) -> "Color":
        if not 0.0 <= coeff <= 1.0:
            raise ValueError(f"Argument coeff={coeff} should be in interval [0.0, 1.0]")
        l1, l2 = 1.0 - coeff, coeff
        return l1 * color1 + l2 * color2
    
    # Mutations ----------------------------------------------------------------
    def update_red(self, update_term: float) -> "Color":
        self._rgb = (clamp(self.r + update_term), self.g, self.b)
        return self

    def update_green(self, update_term: float) -> "Color":
        self._rgb = (self.r, clamp(self.g + update_term), self.b)
        return self

    def update_blue(self, update_term: float) -> "Color":
        self._rgb = (self.r, self.g, clamp(self.b + update_term))
        return self

    def update_hue(self, update_term: float) -> "Color":
        h, l, s = self.hls()
        h = clamp(h + update_term)
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        self._rgb = (r, g, b)
        return self
    
    def update_lightness(self, update_term: float) -> "Color":
        h, l, s = self.hls()
        l = clamp(l + update_term)
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        self._rgb = (r, g, b)
        return self
    
    def update_saturation(self, update_term: float) -> "Color":
        h, l, s = self.hls()
        s = clamp(s + update_term)
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        self._rgb = (r, g, b)
        return self
    
    def update_value(self, update_term: float) -> "Color":
        h, s, v = self.hsv()
        v = clamp(v + update_term)
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        self._rgb = (r, g, b)
        return self

    # Compatibility with Color as a tuple --------------------------------------
    def __getitem__(self, index: int) -> float:
        return self._rgb[index]
    
    def __item__(self) -> Iterator[float]:
        return iter(self._rgb)
    
    def __len__(self) -> int:
        return len(self._rgb)
