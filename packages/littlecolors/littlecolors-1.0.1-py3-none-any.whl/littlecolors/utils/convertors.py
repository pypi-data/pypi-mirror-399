
# Convertors -------------------------------------------------------------------

def clamp(cval: float) -> float:
    """Clip a float color value to interval [0.0, 1.0]"""
    return max(0.0, min(1.0, cval))

def cval_to_cval256(cval: float) -> int:
    """Convert color values from float (in [0.0, 1.0]) to int (in [0, 255])"""
    return round(cval * 255.0)

def cval256_to_str(cval: int) -> str:
    """Return a string representing cval with spaces ' ' before if the integer is not 3 digits."""
    cval_str = str(cval)
    return "0" * (3 - len(cval_str)) + cval_str

def hex_to_rgb(hex_str: str) -> tuple[float, float, float]:
    hex_str = hex_str.removeprefix("#")
    if len(hex_str) != 6:
        raise ValueError("HEX string color (without '#') must be 6 digits")
    try:
        r = int(hex_str[0:2], 16) / 255.0
        g = int(hex_str[2:4], 16) / 255.0
        b = int(hex_str[4:6], 16) / 255.0
    except Exception as err:
        raise ValueError(
            f"HEX string color is invalid: '{hex_str}'"
            f" -> parging failed: {err}"
        )
    return r, g, b

def rgb_to_hex(r: float, g: float, b: float) -> str:
    r256, g256, b256 = cval_to_cval256(r), cval_to_cval256(g), cval_to_cval256(b)
    return f"#{r256:02x}{g256:02x}{b256:02x}"
