"""
Some helper functions
=====================

These are not contained in the package by default (as they could contain some additional dependencies).

Content:
    - some functions to display Color, Colormap or list of Colors (using Matplotlib)

Examples
--------
>>> from littlecolors import Color, ColorGradient
>>> from littlecolors.helpers import show
>>> show(Color(0.2, 0.3, 0.4))
>>> show(ColorGradient([Color(0.2, 0.3, 0.8), Color(0.9)]))
"""

from littlecolors.helpers.show_functions import show, show_color, show_colormap, show_colors_list
