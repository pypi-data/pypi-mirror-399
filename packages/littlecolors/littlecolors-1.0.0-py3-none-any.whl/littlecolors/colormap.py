
# Imports ----------------------------------------------------------------------
from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Iterator
from numbers import Number
import numpy as np
from littlecolors import Color


# Abstract Colormap ------------------------------------------------------------
class Colormap(ABC):
    """Abstract base class for mapping [scalar -> color]
    Instances:
    - ColorGradient
        continuous, n colors = n range_values, so colors are assigned to inflection points
    - ColorSegments
        discrete, n colors = n+1 range_values, so colors are assigned to intervals
    """

    # Constants ----------------------------------------------------------------
    _DEFAULT_COLOR = Color(0.60)
    _DEFAULT_VALUES_RANGE: list[float] = [0.0, 1.0]

    # Constructor --------------------------------------------------------------
    def __init__(
            self,
            colors_array: list[Color],
            values_range: list[float] | None=None,
            name: str | None=None,
            extrapolate_gradient: bool=True,
            default_color: Color | None=None,
        ):
        """
        Parameters
        ----------
        colors_array : list[Color]
            Colors defining the gradient inflection points.
            Must contain at least two colors.

        values_range : list[float] | None, optional
            Scalar values (inflection points) associated with each color.
            for ColorGradient: 2 (min and max) or len(colors_array) values.
            for ColorSegments: 2 (min and max) or len(colors_array)+1 values.
        
        name : str | None, optional
            name of the Colormap

        extrapolate_gradient : bool, optional
            Whether values outside the defined range should be extrapolated as bounds color.

        default_color : Color | None, optional
            Color returned when extrapolation is disabled and the value
            lies outside the range.
        """

        # Init colors array
        if not isinstance(colors_array, (tuple, list)):
            raise TypeError("Input colors_array should be a list or a tuple")
        if len(colors_array) < 2:
            raise ValueError("Input colors_array should contain at least two colors")
        for color in colors_array:
            if not isinstance(color, Color):
                raise TypeError("Each element of input colors_array shoud be a color")
        self.colors_array: list[Color] = colors_array

        # Set base values
        self.name = "" if name is None else name
        self.extrapolate_gradient: bool = extrapolate_gradient
        self.default_color: Color = self._DEFAULT_COLOR.copy() if default_color is None else default_color.copy()

        # Set values range
        self.set_values_range(values_range)

    def set_values_range(self, values_range: list[float] | None=None) -> "Colormap":
        """Set values_range of the Colormap."""

        # Preprocess
        if values_range is None:
            values_range = list(self._DEFAULT_VALUES_RANGE)

        # Guardians
        if not isinstance(values_range, (tuple, list)):
            raise TypeError("Input values_range should be a list or a tuple or None")
        for value in values_range:
            if not isinstance(value, Number):
                raise TypeError("Each element of input values_range shoud be a number")
        for i in range(len(values_range) - 1):
            val1, val2 = values_range[i], values_range[i+1]
            if not val1 < val2:
                raise ValueError("Input values_range should contain stricktly ascending values")
            
        # Uniformize
        values_range = [float(x) for x in values_range] # convert all values to float for stable behaviour

        # Process values_range
        values_range = self._interpolate_values_range(values_range)
        self._verify_values_range_length(values_range)

        # Set
        self.values_range: list[float] = values_range
        return self
    
    def adapt_range(
            self,
            values: list[float],
            symmetric_interval: bool=False,
            range_factor: float | None=None,
        ) -> "Colormap":
        """Adapt values_range so that the Colormap interval covers all values.
        
        Parameters
        ----------
        values : list[float]
            values to be coverted by the Colormap interval

        symmetric_interval : bool, optional
            if True symmetrize the interval [-3, 1.5] -> [-3, 3]

        range_factor: float | None, optional
            if set, adapt the interval like [-1, 2] -> [-1 * range_factor, 2 * range_factor]
        """
        min_val, max_val = np.min(values), np.max(values)
        if symmetric_interval:
            max_abs_val = np.max([np.abs([min_val, max_val])])
            min_val, max_val = -max_abs_val, max_abs_val
        if range_factor is not None:
            if range_factor <=0:
                raise ValueError("Input range_factor should be stricktly positive")
            delta = max_val - min_val
            center = (min_val + max_val) / 2.0
            min_val = center - delta*0.5*range_factor
            max_val = center + delta*0.5*range_factor
        print([min_val, max_val])
        self.set_values_range([min_val, max_val])
        
    @abstractmethod
    def _interpolate_values_range(self, values_range: list[float]) -> list[float]:
        raise NotImplementedError

    @abstractmethod
    def _verify_values_range_length(self, values_range: list[float]) -> None:
        raise NotImplementedError

    # Base Values --------------------------------------------------------------
    def __len__(self) -> int:
        """Number of Colors in the Colormap"""
        return len(self.colors_array)
    
    @property
    def vmin(self) -> float:
        """Minimal input value (outputs first color)"""
        return self.values_range[0]
    
    @property
    def vmax(self) -> float:
        """Maximal input value (outputs last color)"""
        return self.values_range[-1]
    
    @property
    def vmid(self) -> float:
        """Middle input value (outputs median color)"""
        return (self.vmin + self.vmax) / 2.0
    
    @property
    def bounds(self) -> tuple[float, float]:
        """Input values bounds (that scales from first to last color)"""
        return (self.vmin, self.vmax)
    
    @property
    def delta(self) -> float:
        """Range size of input values (vmax - vmin)"""
        return self.vmax - self.vmin
    
    def __str__(self) -> str:
        if len(self) <= 2:
            colors_str = "[" + ", ".join(['C'+str(col.rgb256) for col in self.colors_array]) + "]"
        else:
            colors_str = f"[C{str(self.colors_array[0].rgb256)}, ..., C{str(self.colors_array[-1].rgb256)}] (L={len(self.colors_array)})"
        bounds_str = f"[{self.vmin:.2f}, {self.vmax:.2f}]"
        return f"{self.__class__.__name__}('{self.name}', {colors_str}, bounds={bounds_str})"
    
    def __repr__(self):
        return str(self)
    
    def __getitem__(self, index: int) -> Color:
        return self.colors_array[index]
    
    def __item__(self) -> Iterator[float]:
        return iter(self.colors_array)

    # Methods ------------------------------------------------------------------
    @abstractmethod
    def get_color(self, value: float) -> Color:
        """Map a scalar value to a Color."""
        raise NotImplementedError
    
    def __call__(self, value: float | Iterable[float]) -> Color | Iterable[Color]:
        """Map a scalar or a n-dimentional array value to a Color or Color n-dimentional array of same shape."""
        if np.isscalar(value):
            return self.get_color(value)
        elif isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
            return [self(element) for element in value]
        raise TypeError(f"Incorrect Colormap call type: {type(value)}")
    
    def _get_out_of_range_color(self, value: float) -> Color | None:
        """Return out of range color (left or right) is value if out of range, otherwise return None"""
        
        # Case: NaN
        if not isinstance(value, Number) or np.isnan(value):
            return self.default_color.copy()
        
        # Case: left out of range
        if value <= self.vmin:
            if self.extrapolate_gradient or value == self.vmin:
                return self.colors_array[0]
            return self.default_color.copy()
        
        # Case: right out of range
        if value >= self.vmax:
            if self.extrapolate_gradient or value == self.vmax:
                return self.colors_array[-1]
            return self.default_color.copy()
        
        # Case: color is in range
        return None
    
    def get_colors_list(self, n: int) -> list[Color]:
        """Return an array of n colors range from the Colormap."""
        
        # Extreme cases
        if n < 1:
            raise ValueError("Input n should be a positive integer")
        elif n == 1:
            return [self.get_color(self.vmid)]
        elif n == 2:
            return [self.colors_array[0], self.colors_array[-1]]
        
        # Base case
        step = self.delta / (n-1)
        x_range = [self.vmin + i*step for i in range(n)]
        return [self.get_color(x) for x in x_range]
    
    def copy(self) -> "Colormap":
        """Copy Colormap."""
        return self.__class__(
            colors_array=list(self.colors_array),
            values_range=list(self.values_range),
            extrapolate_gradient=self.extrapolate_gradient,
            default_color=self.default_color.copy(),
        )
    
    def reversed(self) -> "Colormap":
        """Return inversed-scale Colormap."""
        cmap_rev = self.copy()
        cmap_rev.colors_array = cmap_rev.colors_array[::-1]
        return cmap_rev


# Colormap instance: ColorGradient ---------------------------------------------
class ColorGradient(Colormap):
    """
    Class for mapping [scalar -> color]  
    Continuous scale: n colors = n range_values, so colors are assigned to inflection points:

        c1     c2     c3
        |------|------|
    """

    # Constructor --------------------------------------------------------------
    def _interpolate_values_range(self, values_range: list[float]) -> list[float]:
        if len(self.colors_array) > 2 and len(values_range) == 2:
            n = len(self.colors_array) - 1
            delta = values_range[1] - values_range[0]
            step = delta / n
            values_range = [values_range[0] + i*step for i in range(n+1)]
        return values_range

    def _verify_values_range_length(self, values_range: list[float]) -> None:
        if len(self.colors_array) != len(values_range):
            raise ValueError(
                f"Input values_range for ColorGradient (l={len(values_range)}) "
                "should contain l=2 values (min and max bounds) "
                f"or the same number of values as colors_array (l={len(self.colors_array)})"
            )

    # Methods ------------------------------------------------------------------    
    def get_color(self, value: float) -> Color:
        """Map a scalar value to a Color."""

        # Case out of range
        out_of_range_color = self._get_out_of_range_color(value)
        if out_of_range_color is not None:
            return out_of_range_color

        # Find value interval
        interval_i = 0
        for i in range(len(self)-1):
            if value < self.values_range[i+1]:
                interval_i = i
                break

        # Interpolate between two colors
        interval_min, interval_max = self.values_range[interval_i], self.values_range[interval_i+1]
        color_min, color_max = self.colors_array[interval_i], self.colors_array[interval_i+1]
        dist_min = float(value - interval_min)
        dist_max = float(interval_max - value)
        step = interval_max - interval_min
        return (step - dist_min) * color_min + (step - dist_max) * color_max
    

# Colormap instance: ColorSegments ---------------------------------------------
class ColorSegments(Colormap):
    """
    Class for mapping [scalar -> color].  
    Discrete scale: n colors = n+1 range_values, so colors are assigned to intervals:

           c1     c2   
        |------|------|
    """

    # Constructor --------------------------------------------------------------
    def _interpolate_values_range(self, values_range: list[float]) -> list[float]:
        if len(values_range) == 2:
            n = len(self.colors_array)
            delta = values_range[1] - values_range[0]
            step = delta / n
            values_range = [values_range[0] + i*step for i in range(n+1)]
        return values_range
        
    def _verify_values_range_length(self, values_range: list[float] | None=None) -> None:
        if len(self.colors_array) + 1 != len(values_range):
            raise ValueError(
                f"Input values_range for ColorSegments (l={len(values_range)}) "
                "should contain l=2 values (min and max bounds) "
                f"or n+1 values as colors_array (l={len(self.colors_array)})"
            )

    # Methods ------------------------------------------------------------------    
    def get_color(self, value: float) -> Color:
        """Map a scalar value to a Color."""

        # Case out of range
        out_of_range_color = self._get_out_of_range_color(value)
        if out_of_range_color is not None:
            return out_of_range_color

        # Find value interval
        for i in range(len(self)):
            if value < self.values_range[i+1]:
                return self.colors_array[i].copy()
        return self.colors_array[-1].copy()
