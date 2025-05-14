"""
Tests for color schemes used in PDF generation.
"""

import pytest
from reportlab.lib import colors

from src.pdf.color_schemes import COLOR_SCHEMES


def test_color_schemes_exist():
    """Test that all expected color schemes exist."""
    expected_schemes = ["blue", "green", "purple", "orange", "red", "dark"]
    assert set(COLOR_SCHEMES.keys()) == set(expected_schemes)


def test_color_scheme_structure():
    """Test that each color scheme has the required color definitions."""
    required_colors = ["primary", "secondary", "accent", "background", "text", "muted"]

    for scheme_name, scheme in COLOR_SCHEMES.items():
        for color_name in required_colors:
            assert (
                color_name in scheme
            ), f"Color '{color_name}' missing from scheme '{scheme_name}'"
            assert isinstance(
                scheme[color_name], colors.Color
            ), f"'{color_name}' in '{scheme_name}' is not a Color instance"


def test_blue_scheme():
    """Test the blue color scheme specifically."""
    scheme = COLOR_SCHEMES["blue"]
    assert scheme["primary"].hexval().lower() == "0x1a73e8"
    assert scheme["secondary"].hexval().lower() == "0x4285f4"
    assert scheme["accent"].hexval().lower() == "0x34a853"
    assert scheme["background"].hexval().lower() == "0xffffff"
    assert scheme["text"].hexval().lower() == "0x202124"
    assert scheme["muted"].hexval().lower() == "0x5f6368"


def test_dark_scheme():
    """Test the dark color scheme specifically."""
    scheme = COLOR_SCHEMES["dark"]
    assert scheme["primary"].hexval().lower() == "0xbb86fc"
    assert scheme["secondary"].hexval().lower() == "0x03dac6"
    assert scheme["accent"].hexval().lower() == "0xcf6679"
    assert scheme["background"].hexval().lower() == "0x080808"
    assert scheme["text"].hexval().lower() == "0xffffff"
    assert scheme["muted"].hexval().lower() == "0xb3b3b3"


def test_color_contrast():
    """Test that text colors have sufficient contrast with backgrounds."""
    for scheme_name, scheme in COLOR_SCHEMES.items():
        background = scheme["background"]
        text = scheme["text"]

        # Calculate relative luminance (simplified version of WCAG formula)
        # This helps ensure text remains readable on backgrounds
        bg_luminance = _calculate_luminance(background)
        text_luminance = _calculate_luminance(text)

        # Calculate contrast ratio (higher is better)
        contrast_ratio = _calculate_contrast_ratio(bg_luminance, text_luminance)

        # WCAG AA requires at least 4.5:1 for normal text
        assert (
            contrast_ratio >= 4.5
        ), f"Contrast ratio for {scheme_name} scheme is only {contrast_ratio:.2f}:1"


def _calculate_luminance(color):
    """Calculate relative luminance of a color (simplified WCAG formula)."""
    r, g, b = color.rgb()
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _calculate_contrast_ratio(luminance1, luminance2):
    """Calculate contrast ratio between two luminance values."""
    # Ensure lighter color is first
    lighter = max(luminance1, luminance2)
    darker = min(luminance1, luminance2)

    # WCAG contrast formula
    return (lighter + 0.05) / (darker + 0.05)
