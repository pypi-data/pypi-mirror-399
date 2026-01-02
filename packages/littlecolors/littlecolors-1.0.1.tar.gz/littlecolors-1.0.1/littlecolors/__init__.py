"""
littlecolors
============

A simple python package to manipulate colors.

Example of usage:
>>> from littlecolors import Color, ColorGradient, COLORS
>>> from littlecolors.helpers import show
>>> c1 = Color(0.2)
>>> c2 = Color(120, 189, 56)
>>> c2.update_lightness(+0.1)
>>> c3 = Color('#33cccc')
>>> c4 = COLORS.MAGENTA()
>>> colormap = ColorGradient([c1, c2, c3, c4])
>>> colors_list = colormap([0.1, 0.1, 0.2, 0.25, 0.15, 0.89, 0.14])
>>> show(colormap)
"""

from littlecolors.color import Color
from littlecolors.colormap import Colormap, ColorGradient, ColorSegments
from littlecolors.preset import COLORS, COLORS_CSS, CMAPS, CLISTS, CLISTS_SEABORN
