"""
Pre-saved color values
======================

Content:
    - Colors (my favorite and standard CSS colors)
    - Colormaps
    - Colors lists

Examples
--------
>>> from littlecolors.preset import COLORS, COLORS_CSS, CMAPS, CLISTS, CLISTS_SEABORN
>>> col1 = COLORS.BLUE()
>>> col2 = COLORS_CSS.ALICEBLUE()
>>> cmap = CMAPS.PLDDT()
>>> clist1 = CLISTS.THREE()
>>> clist2 = CLISTS_SEABORN.BrBG()
"""

from littlecolors.preset.colors import COLORS, COLORS_CSS
from littlecolors.preset.colormaps import CMAPS
from littlecolors.preset.colorlists import CLISTS, CLISTS_SEABORN
