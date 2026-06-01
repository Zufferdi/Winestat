"""Chart 04 — Bubble map of cantons (approx. centroids, no GIS dep)."""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from theme import apply, WINE_RED, WINE_WHITE, MUTED, INK, PAPER, credit

# Approx. canton centroids (lat, lon) — public-domain knowledge.
CENTROIDS = {
    "ZH": (47.42, 8.65), "BE": (46.95, 7.55), "LU": (47.07, 8.18),
    "UR": (46.75, 8.65), "SZ": (47.05, 8.75), "OW": (46.85, 8.25),
    "NW": (46.95, 8.40), "GL": (46.95, 9.00), "ZG": (47.16, 8.50),
    "FR": (46.75, 7.10), "SO": (47.30, 7.65), "BS": (47.56, 7.60),
    "BL": (47.43, 7.74), "SH": (47.72, 8.62), "AR": (47.40, 9.32),
    "AI": (47.32, 9.42), "SG": (47.30, 9.30), "GR": (46.70, 9.55),
    "AG": (47.40, 8.20), "TG": (47.55, 9.05), "TI": (46.30, 8.85),
    "VD": (46.60, 6.50), "VS": (46.20, 7.55), "NE": (46.95, 6.80),
    "GE": (46.20, 6.15), "JU": (47.30, 7.10), "FL": (47.16, 9.55),
}


def main():
    apply()
    df = pd.read_csv("data/processed/importateurs.csv")
    by_canton = (df.groupby("canton")
                   .agg(rouge=("litres_rouge", "sum"),
                        blanc=("litres_blanc", "sum"),
                        total=("litres_total", "sum"),
                        n=("importateur", "count"))
                   .reset_index())
    by_canton["share_rouge"] = by_canton["rouge"] / by_canton["total"]

    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    fig.subplots_adjust(top=0.85, wspace=0.05)

    fig.text(0.04, 0.95, "La Suisse du vin importé, canton par canton",
             ha="left", va="top", fontsize=20, fontweight="bold", color=INK)
    fig.text(0.04, 0.905,
             "Volume et nombre d'acteurs par canton de siège social. "
             "Note : les bulles reflètent le siège de l'importateur, pas la destination finale du vin.",
             ha="left", va="top", fontsize=11, color=MUTED, style="italic")

    # Build a colormap interpolating between white-wine gold and red-wine bordeaux
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("wine", [WINE_WHITE, "#B47C36", WINE_RED])

    for ax, mode in zip(axes, ["volume", "count"]):
        # Outline placeholder — draw a soft envelope around the points
        lons = [c[1] for c in CENTROIDS.values()]
        lats = [c[0] for c in CENTROIDS.values()]
        ax.scatter(lons, lats, s=1, color="white")  # establish axes range

        for _, row in by_canton.iterrows():
            if row["canton"] not in CENTROIDS:
                continue
            lat, lon = CENTROIDS[row["canton"]]
            if mode == "volume":
                size = (row["total"] / df["litres_total"].sum()) * 28000 + 60
                color = cmap(row["share_rouge"])
                ax.scatter(lon, lat, s=size, color=color,
                           edgecolor=INK, linewidth=0.5, alpha=0.78, zorder=3)
            else:
                size = row["n"] * 6 + 50
                ax.scatter(lon, lat, s=size, color=WINE_RED,
                           edgecolor=INK, linewidth=0.5, alpha=0.55, zorder=3)

            # Label only the meaningful cantons
            thresh = 1_000_000 if mode == "volume" else 30
            metric = row["total"] if mode == "volume" else row["n"]
            if metric > thresh:
                ax.annotate(row["canton"], (lon, lat),
                            ha="center", va="center", fontsize=9,
                            fontweight="bold", color=INK, zorder=4)

        ax.set_xlim(5.8, 10.1)
        ax.set_ylim(45.8, 47.95)
        ax.set_aspect(1.4)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)
        for s in ax.spines.values():
            s.set_visible(False)

        title = ("Volume importé" if mode == "volume"
                 else "Nombre d'importateurs basés dans le canton")
        ax.set_title(title, fontsize=13, color=INK, loc="left", pad=10)

    # Legend for color
    from matplotlib.lines import Line2D
    legend_handles = [
        Line2D([], [], marker='o', linestyle='', markersize=14,
               markerfacecolor=WINE_RED, markeredgecolor=INK,
               label="Surtout rouge"),
        Line2D([], [], marker='o', linestyle='', markersize=14,
               markerfacecolor="#B47C36", markeredgecolor=INK,
               label="Équilibré"),
        Line2D([], [], marker='o', linestyle='', markersize=14,
               markerfacecolor=WINE_WHITE, markeredgecolor=INK,
               label="Surtout blanc"),
    ]
    axes[0].legend(handles=legend_handles, loc="lower left",
                   fontsize=9, ncol=3, columnspacing=1.0,
                   bbox_to_anchor=(0, -0.05))

    credit(axes[1])
    out = Path("assets/charts/04_carte_cantons.png")
    plt.savefig(out, dpi=200)
    plt.savefig(out.with_suffix(".svg"))
    print(f"✓ {out}")


if __name__ == "__main__":
    main()
