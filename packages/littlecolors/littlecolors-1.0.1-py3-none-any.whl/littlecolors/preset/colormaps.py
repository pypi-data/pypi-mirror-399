"""
Namespaces for preset Colormaps (ColorGradient / ColorSegments)
"""

# Imports ----------------------------------------------------------------------
from dataclasses import dataclass
from enum import Enum
from littlecolors import Color, Colormap, ColorGradient, ColorSegments


# Struct to store a Colormap parameters ----------------------------------------
@dataclass(slots=True, frozen=True)
class ColormapParameters:
    segments: bool
    colors_array: list[tuple[float, float, float] | tuple[int, int, int]]
    values_range: list[float]
    extrapolate_gradient: bool = True
    default_color: tuple[float, float, float] | tuple[int, int, int] | None = None


# Saved Colormaps --------------------------------------------------------------
class CMAPS(Enum):
    """
    Namespace for preset Colormaps (ColorGradient / ColorSegments).

    Examples
    --------
    >>> from littlecolors.preset import CMAPS
    >>> cmap = CMAPS.PLDDT()
    """

    def __call__(self) -> Colormap:
        """Colormap facory from presaved parameters."""
        colors_array = [Color(c) for c in self.value.colors_array]
        values_range = list(self.value.values_range)
        default_color = None
        if self.value.default_color is not None:
            default_color = Color(self.value.default_color)
        if not self.value.segments:
            return ColorGradient(
                colors_array,
                values_range,
                name=self.name,
                extrapolate_gradient=self.value.extrapolate_gradient,
                default_color=default_color,
            )
        else:
            return ColorSegments(
                colors_array,
                values_range,
                name=self.name,
                extrapolate_gradient=self.value.extrapolate_gradient,
                default_color=default_color,
            )
    
    # pLDDT score color map for protein 3D structures
    # https://www.ebi.ac.uk/training/online/courses/alphafold/inputs-and-outputs/evaluating-alphafolds-predicted-structures-using-confidence-scores/plddt-understanding-local-confidence/
    PLDDT = ColormapParameters(
        segments=True,
        colors_array=[
            (1.000, 0.490, 0.271),   # low confidence, orange
            (1.000, 0.859, 0.075),   # medium-low confidence, yellow
            (0.396, 0.796, 0.953),   # medium-high confidence, light blue
            (0.000, 0.325, 0.839),   # high confidence, dark blue
        ],
        values_range=[0.0, 50.0, 70.0, 90.0, 100.0],
    )

    # Relative Solvent Accessibility color mapping for protein 3D structures
    # https://academic.oup.com/bioinformatics/article/41/6/btaf322/8152299
    RSA = ColormapParameters(
        segments=False,
        colors_array=[
            (  0,   0,   0),   # burried (black)
            (  0,  95, 115),   # almost burried (deep blue)
            (255, 255, 255),   # exposed (white)
        ],
        values_range=[0.0, 30.0, 100.0],
    )

    # Ok score in [0, 1] range
    MATCH_RATIO = ColormapParameters(
        segments=False,
        colors_array=[
            (0.883, 0.000, 0.047),   # low confidence, red
            (1.000, 0.490, 0.271),   # low confidence, orange
            (1.000, 0.859, 0.075),   # medium-low confidence, yellow
            (0.396, 0.796, 0.953),   # medium-high confidence, light blue
            (0.000, 0.325, 0.839),   # high confidence, dark blue
        ],
        values_range=[0.0, 1.0],
    )

    # Preset Blue -> Orange sequential scale
    BlueOrange = ColormapParameters(
        segments=False,
        colors_array=[
            (  0,  95, 115), # blue
            (238, 155,   0), # orange
        ],
        values_range=[0.0, 1.0],
    )

    # Preset Blue -> Orange -> Magenta divergeant scale
    BlueOrangeMagenta = ColormapParameters(
        segments=False,
        colors_array=[
            (  0,  95, 115), # blue
            (238, 155,   0), # orange
            (222,  31, 107), # magenta
        ],
        values_range=[-1.0, 1.0],
    )

    # Prese Blue -> Grey -> Orange divergeant scale
    BlueGreyOrange = ColormapParameters(
        segments=False,
        colors_array=[
            (  0,  95, 115), # blue
            (120, 120, 120), # grey
            (238, 155,   0), # orange
        ],
        values_range=[-1.0, 1.0],
    )

    # Red to Blue divergenat scale
    RedBlue = ColormapParameters(
        segments=False,
        colors_array=[
            (225,   0,  12),   # red
            (178, 178, 178),   # grey
            ( 10,  80, 161),   # blue
        ],
        values_range=[-1.0, 0.0, 1.0],
    )

