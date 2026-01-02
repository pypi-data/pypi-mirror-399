import math

from .constants import M_RGB_XYZ, M_XYZ_LMS, M_LMS_OKLAB


class OkColor:
    """
    A precision converter for sRGB to Oklab/Oklch.
    """

    @staticmethod
    def _linearize_srgb(v):
        """
        Applies the EOTF to convert non-linear sRGB to linear light intensity.
        Formula constants defined in IEC 61966-2-1.
        """
        if v <= 0.04045:
            return v / 12.92
        else:
            return ((v + 0.055) / 1.055) ** 2.4

    @staticmethod
    def _multiply_matrix_vector(matrix, vector):
        """Helper for matrix multiplication (3x3 * 3x1)."""
        return [
            sum(matrix[i][j] * vector[j] for j in range(3))
            for i in range(3)
        ]

    @staticmethod
    def _cbrt(x):
        """
        Signed cube root function. 
        Necessary for handling negative values in wide-gamut scenarios.
        """
        return math.copysign(abs(x) ** (1 / 3), x)

    @staticmethod
    def _parse_hex(hex_str):
        hex_str = hex_str.lstrip('#')
        if len(hex_str) != 6:
            raise ValueError("Hex string must be 6 characters (e.g., #FF0000)")
        return tuple(int(hex_str[i:i + 2], 16) / 255.0 for i in (0, 2, 4))

    @staticmethod
    def convert(color_input):
        """
        Main entry point. Accepts:
        - Hex String: "#ffffff" or "ffffff"
        - RGB Tuple (0-255): (255, 0, 0)

        Returns a dictionary with 'oklab' and 'oklch' coordinates.
        """
        # 1. Parse Input & Normalize to 0-1
        if isinstance(color_input, str):
            r, g, b = OkColor._parse_hex(color_input)
        elif isinstance(color_input, (tuple, list)):
            r, g, b = [c / 255.0 for c in color_input]
        else:
            raise ValueError("Invalid input format. Use Hex string or RGB tuple.")

        # 2. Linearize sRGB (EOTF)
        r_lin = OkColor._linearize_srgb(r)
        g_lin = OkColor._linearize_srgb(g)
        b_lin = OkColor._linearize_srgb(b)
        rgb_lin_vector = [r_lin, g_lin, b_lin]

        # 3. Linear RGB -> XYZ
        xyz = OkColor._multiply_matrix_vector(M_RGB_XYZ, rgb_lin_vector)

        # 4. XYZ -> LMS (Cone Response)
        lms = OkColor._multiply_matrix_vector(M_XYZ_LMS, xyz)

        # 5. Non-Linear Compression (Cube Root)
        lms_prime = [OkColor._cbrt(c) for c in lms]

        # 6. LMS -> Oklab (Decorrelation)
        l_ok, a_ok, b_ok = OkColor._multiply_matrix_vector(M_LMS_OKLAB, lms_prime)

        # 7. Oklab -> Oklch (Polar conversion)
        chroma = math.sqrt(a_ok ** 2 + b_ok ** 2)
        hue = math.atan2(b_ok, a_ok) * (180 / math.pi)

        # Normalize hue to 0-360 range
        if hue < 0:
            hue += 360

        return {
            "oklab": {"L": l_ok, "a": a_ok, "b": b_ok},
            "oklch": {"L": l_ok, "C": chroma, "h": hue}
        }

