"""Chart 07 — Pareto chart of top 30 importers + cumulative line."""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from theme import apply, WINE_RED, ACCENT, MUTED, INK, GRID, credit


def main():
    apply()
    df = pd.read_csv("data/processed/importateurs.csv")
    df = df.sort_values("litres_total", ascending=False).reset_index(drop=True)
    n = 30
    top = df.head(n).copy()
    total = df["litres_total"].sum()
    top["share"] = top["litres_total"] / total * 100
    top["cum"] = top["share"].cumsum()

    fig, ax = plt.subplots(figsize=(13, 8))
    fig.subplots_adjust(top=0.86, bottom=0.22)

    x = np.arange(n)
    ax.bar(x, top["share"], color=WINE_RED, edgecolor=INK, linewidth=0.4,
           width=0.75)
    ax.set_ylabel("Part du marché (%)", color=WINE_RED)
    ax.tick_params(axis="y", colors=WINE_RED)

    ax2 = ax.twinx()
    ax2.plot(x, top["cum"], color=ACCENT, marker="o", markersize=5,
             linewidth=2.2)
    ax2.set_ylabel("Part cumulée (%)", color=ACCENT)
    ax2.tick_params(axis="y", colors=ACCENT)
    ax2.set_ylim(0, 100)
    ax2.grid(False)
    ax2.spines["top"].set_visible(False)

    # 80% reference line
    ax2.axhline(80, color=MUTED, linestyle=":", linewidth=1)
    cross_idx = (top["cum"] >= 80).idxmax() if (top["cum"] >= 80).any() else None
    if cross_idx is not None:
        ax2.annotate(
            f"80 % atteint dès le {cross_idx + 1}ᵉ importateur",
            xy=(cross_idx, 80), xytext=(cross_idx + 1, 55),
            fontsize=10, color=INK,
            arrowprops=dict(arrowstyle="->", color=MUTED, lw=0.8),
        )

    ax.set_xticks(x)
    ax.set_xticklabels(
        [name[:24] + ("…" if len(name) > 24 else "")
         for name in top["importateur"]],
        rotation=45, ha="right", fontsize=9,
    )
    ax.grid(axis="x", visible=False)

    fig.text(0.04, 0.96, "Pareto des 30 plus gros importateurs",
             ha="left", va="top", fontsize=20, fontweight="bold", color=INK)
    fig.text(0.04, 0.92,
             "Barres = part individuelle du marché · ligne = part cumulée.",
             ha="left", va="top", fontsize=11, color=MUTED, style="italic")

    credit(ax)
    out = Path("assets/charts/07_pareto.png")
    plt.savefig(out, dpi=200)
    plt.savefig(out.with_suffix(".svg"))
    print(f"✓ {out}")


if __name__ == "__main__":
    main()
