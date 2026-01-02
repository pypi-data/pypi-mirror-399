
"""
Some helper functions to display Color related objects using Matplotlib.
"""

# Imports ----------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from littlecolors import Color, Colormap


# Show functions ---------------------------------------------------------------
def show(color_object: Color | Colormap | list[Color] | tuple[Color], title: str | None = None) -> None:
    """Pop a matplotlib window representing the Color, Colormap or list of Colors."""
    if isinstance(color_object, Color):
        show_color(color_object, title=title)
    elif isinstance(color_object, Colormap):
        show_colormap(color_object, title=title)
    elif isinstance(color_object, (list, tuple)) and all([isinstance(c, Color) for c in color_object]):
        show_colors_list(color_object, title=title)
    else:
        raise TypeError("Incorrect input type of color_object to show()")

def show_color(color: Color, title: str | None = None) -> None:
    """Pop a matplotlib window representing the Color."""
    plt.close()
    show_title = f"RGB={color.rgb256} '{color.hex()}'"
    if title is not None:
        show_title = f"{title}\n{show_title}"
    plt.title(show_title)
    plt.bar(0.0, 1.0, color=color)
    plt.ylim(0.0, 1.0)
    plt.xlim(-0.1, 0.1)
    plt.xticks([], [])
    plt.yticks([], [])
    plt.tight_layout()
    plt.show()

def show_colormap(colormap: Colormap, n_steps: int=100, title: str | None = None) -> None:
    """Pop a matplotlib window representing the Colormap (ColorGradient or ColorSegments)"""
    plt.close()
    vmin, vmid, vmax = colormap.vmin, colormap.vmid, colormap.vmax
    gradient = np.linspace(vmin, vmax, n_steps+1).reshape(1, -1)
    colors_list = [colormap.get_color(x).rgb for x in gradient[0]]
    cmap = ListedColormap(colors_list)
    int_range = np.array([list(range(len(colors_list)))])
    fig, ax = plt.subplots(figsize=(5, 1.50))
    ax.imshow(int_range, aspect="auto", cmap=cmap)
    ax.set_yticks([])
    int_range_min = int_range[0][0]
    int_range_max = int_range[0][-1]
    int_range_mid = (int_range_min + int_range_max) / 2.0
    ax.set_xlim([int_range_min, int_range_max])
    ax.set_xticks([int_range_min, int_range_mid, int_range_max], [f"{vmin:.2f}", f"{vmid:.2f}" ,f"{vmax:.2f}"])
    show_title = str(colormap)
    if title is not None:
        show_title = f"{title}\n{show_title}"
    ax.set_title(show_title, fontsize=7)
    plt.tight_layout()
    plt.show()

def show_colors_list(colors_list: list[Color], title: str | None = None) -> None:
    """Pop a matplotlib window representing the list of Colors"""
    MAX_L_TEXT = 50
    plt.close()
    if title is not None:
        plt.title(title)
    for i, color in enumerate(colors_list):
        plt.bar(i, 1.0, color=color, width=1.0)
        if len(colors_list) <= MAX_L_TEXT:
            text_col = Color(0.1) if color.greyscale() > 0.5 else Color(0.9)
            plt.text(
                i, 0.5, color.rgb256_str,
                ha="center",
                va="center",
                rotation=90,
                color=text_col.rgb,
                fontsize=8,
            )
    plt.xlim(-0.5, len(colors_list)-0.5)
    plt.ylim(0.0, 1.0)
    if len(colors_list) <= MAX_L_TEXT:
        plt.xticks(list(range(len(colors_list))), fontsize=8, rotation=90)
    else:
        plt.xticks([], [])
    plt.yticks([], [])
    plt.tight_layout()
    plt.show()
