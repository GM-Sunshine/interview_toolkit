"""
Color schemes for PDF generation
"""

from reportlab.lib import colors

COLOR_SCHEMES = {
    "blue": {
        "primary": colors.HexColor("#1a73e8"),
        "secondary": colors.HexColor("#4285f4"),
        "accent": colors.HexColor("#34a853"),
        "background": colors.HexColor("#ffffff"),
        "text": colors.HexColor("#202124"),
        "muted": colors.HexColor("#5f6368"),
    },
    "green": {
        "primary": colors.HexColor("#0f9d58"),
        "secondary": colors.HexColor("#34a853"),
        "accent": colors.HexColor("#4285f4"),
        "background": colors.HexColor("#ffffff"),
        "text": colors.HexColor("#202124"),
        "muted": colors.HexColor("#5f6368"),
    },
    "purple": {
        "primary": colors.HexColor("#673ab7"),
        "secondary": colors.HexColor("#7b1fa2"),
        "accent": colors.HexColor("#e91e63"),
        "background": colors.HexColor("#ffffff"),
        "text": colors.HexColor("#202124"),
        "muted": colors.HexColor("#5f6368"),
    },
    "orange": {
        "primary": colors.HexColor("#f57c00"),
        "secondary": colors.HexColor("#ff9800"),
        "accent": colors.HexColor("#ff5722"),
        "background": colors.HexColor("#ffffff"),
        "text": colors.HexColor("#202124"),
        "muted": colors.HexColor("#5f6368"),
    },
    "red": {
        "primary": colors.HexColor("#d32f2f"),
        "secondary": colors.HexColor("#f44336"),
        "accent": colors.HexColor("#ff9800"),
        "background": colors.HexColor("#ffffff"),
        "text": colors.HexColor("#202124"),
        "muted": colors.HexColor("#5f6368"),
    },
    "dark": {
        "primary": colors.HexColor("#bb86fc"),
        "secondary": colors.HexColor("#03dac6"),
        "accent": colors.HexColor("#cf6679"),
        "background": colors.HexColor("#080808"),
        "text": colors.HexColor("#ffffff"),
        "muted": colors.HexColor("#b3b3b3"),
    },
}
