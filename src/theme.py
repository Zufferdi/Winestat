"""Shared visual theme — wine-coloured palette and matplotlib defaults."""
import matplotlib as mpl
import matplotlib.pyplot as plt

# Palette
WINE_RED = "#722F37"       # deep bordeaux
WINE_RED_LIGHT = "#A63D47"
WINE_WHITE = "#D4A547"     # straw gold for white wine
WINE_WHITE_LIGHT = "#E6C36A"
PAPER = "#FAF7F2"          # warm off-white background
INK = "#2C1810"            # dark brown for text
GRID = "#E8E0D3"
MUTED = "#7A6F66"
ACCENT = "#C9444E"

SEQUENTIAL_RED = ["#F2DDD9", "#E0B0A6", "#C9837A", "#A85A52", "#7A2E2E", "#4A0F18"]
DIVERGING = ["#722F37", "#A85A52", "#D4A547", "#E6C36A"]


def apply():
    """Apply the project's matplotlib theme."""
    mpl.rcParams.update({
        "figure.facecolor": PAPER,
        "axes.facecolor": PAPER,
        "savefig.facecolor": PAPER,
        "axes.edgecolor": INK,
        "axes.labelcolor": INK,
        "axes.titlecolor": INK,
        "axes.titleweight": "bold",
        "axes.titlesize": 16,
        "axes.titlepad": 18,
        "axes.labelsize": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "axes.axisbelow": True,
        "xtick.color": INK,
        "ytick.color": INK,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "text.color": INK,
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "legend.frameon": False,
        "legend.fontsize": 10,
        "figure.dpi": 110,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
    })


def credit(ax, text="Source : OFAG · Contingents d'importation de vin 2025"):
    """Add a small credit line under a chart."""
    ax.figure.text(
        0.01, 0.005, text, ha="left", va="bottom",
        fontsize=8, color=MUTED, style="italic"
    )
