"""Chart 06 — Rouge vs blanc scatter (log-log) — reveals specialists."""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from theme import apply, WINE_RED, WINE_WHITE, ACCENT, MUTED, INK, GRID, credit


def main():
    apply()
    df = pd.read_csv("data/processed/importateurs.csv")
    # Keep only rows where both volumes are >0 (log scale)
    d = df.query("litres_rouge > 0 and litres_blanc > 0").copy()

    fig, ax = plt.subplots(figsize=(11, 9))
    fig.subplots_adjust(top=0.88)

    # color by ratio
    ratio = d["litres_rouge"] / (d["litres_rouge"] + d["litres_blanc"])
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("wine", [WINE_WHITE, "#B47C36", WINE_RED])

    ax.scatter(d["litres_rouge"], d["litres_blanc"],
               s=np.sqrt(d["litres_total"]) * 0.3,
               c=ratio, cmap=cmap, alpha=0.55,
               edgecolor=INK, linewidth=0.3)

    # diagonal: equal red & white
    lo, hi = 10, d["litres_total"].max() * 1.2
    ax.plot([lo, hi], [lo, hi], color=MUTED, linestyle="--", linewidth=1,
            label="Rouge = Blanc")

    # Annotate the giants
    big = d.nlargest(8, "litres_total")
    for _, row in big.iterrows():
        ax.annotate(row["importateur"],
                    (row["litres_rouge"], row["litres_blanc"]),
                    xytext=(8, 8), textcoords="offset points",
                    fontsize=9, color=INK, fontweight="bold")

    # Annotate notable specialists (high ratio one way or the other)
    rouge_only = d.nlargest(40, "litres_total").nlargest(3, "litres_rouge") \
                  .loc[lambda x: (x["litres_blanc"] < x["litres_rouge"] * 0.05)]
    blanc_only = d.nlargest(40, "litres_total").loc[
        lambda x: x["litres_rouge"] < x["litres_blanc"] * 0.5
    ].nlargest(3, "litres_blanc")
    for _, row in pd.concat([rouge_only, blanc_only]).iterrows():
        if row["importateur"] in big["importateur"].values:
            continue
        ax.annotate(row["importateur"],
                    (row["litres_rouge"], row["litres_blanc"]),
                    xytext=(8, -10), textcoords="offset points",
                    fontsize=8, color=MUTED, style="italic")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Litres de vin rouge importés (log)")
    ax.set_ylabel("Litres de vin blanc importés (log)")
    ax.set_xlim(10, hi)
    ax.set_ylim(10, hi)
    ax.legend(loc="upper left")

    fig.text(0.04, 0.96,
             "Spécialistes du rouge, du blanc — ou les deux",
             ha="left", va="top", fontsize=20, fontweight="bold", color=INK)
    fig.text(0.04, 0.92,
             "Chaque point = un importateur. Sur la diagonale = portefeuille équilibré ; "
             "écarts vers les axes = spécialisation.",
             ha="left", va="top", fontsize=11, color=MUTED, style="italic")

    credit(ax)
    out = Path("assets/charts/06_rouge_vs_blanc.png")
    plt.savefig(out, dpi=200)
    plt.savefig(out.with_suffix(".svg"))
    print(f"✓ {out}")


if __name__ == "__main__":
    main()
