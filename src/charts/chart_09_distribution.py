"""Chart 09 — Distribution log-scale: the long tail of tiny importers."""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from theme import apply, WINE_RED, ACCENT, MUTED, INK, PAPER, credit


def main():
    apply()
    df = pd.read_csv("data/processed/importateurs.csv")
    v = df["litres_total"].values
    v = v[v > 0]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
    fig.subplots_adjust(top=0.84, wspace=0.25)

    # Left: histogram in log scale
    bins = np.logspace(0, 8, 40)
    ax1.hist(v, bins=bins, color=WINE_RED, edgecolor=INK, linewidth=0.5, alpha=0.8)
    ax1.set_xscale("log")
    ax1.set_xlabel("Volume importé (litres, échelle log)")
    ax1.set_ylabel("Nombre d'importateurs")
    ax1.set_title("Distribution des tailles", loc="left", pad=12, fontsize=14)

    # Reference lines for size categories
    categories = [
        (1_000, "1 000 L"),
        (100_000, "100 k L"),
        (10_000_000, "10 M L"),
    ]
    for x, label in categories:
        ax1.axvline(x, color=MUTED, linestyle=":", linewidth=1)
        ax1.text(x, ax1.get_ylim()[1] * 0.95, label,
                 rotation=90, va="top", ha="right", fontsize=8,
                 color=MUTED, style="italic")

    # Right: size buckets bar chart
    buckets = [
        ("< 100 L",         0,       100),
        ("100 – 1 000 L",   100,     1_000),
        ("1 k – 10 k L",    1_000,   10_000),
        ("10 k – 100 k L",  10_000,  100_000),
        ("100 k – 1 M L",   100_000, 1_000_000),
        ("1 – 10 M L",      1_000_000, 10_000_000),
        ("> 10 M L",        10_000_000, float("inf")),
    ]
    counts = [((v >= lo) & (v < hi)).sum() for _, lo, hi in buckets]
    labels = [b[0] for b in buckets]
    total = len(v)
    pct = [c / total * 100 for c in counts]

    y = range(len(buckets))
    ax2.barh(y, counts, color=WINE_RED, edgecolor=INK, linewidth=0.4)
    ax2.set_yticks(list(y))
    ax2.set_yticklabels(labels)
    ax2.set_xlabel("Nombre d'importateurs")
    ax2.set_title("Par catégorie de taille", loc="left", pad=12, fontsize=14)
    ax2.grid(axis="y", visible=False)

    for i, (c, p) in enumerate(zip(counts, pct)):
        ax2.text(c + total * 0.005, i, f"{c} ({p:.0f}%)",
                 va="center", fontsize=9, color=INK)
    ax2.set_xlim(0, max(counts) * 1.18)

    fig.text(0.04, 0.96, "La très longue traîne du marché",
             ha="left", va="top", fontsize=20, fontweight="bold", color=INK)
    fig.text(0.04, 0.92,
             f"Sur {total} importateurs, la majorité importe moins de 10 000 L — "
             "à peine un demi-conteneur de bouteilles.",
             ha="left", va="top", fontsize=11, color=MUTED, style="italic")

    credit(ax2)
    out = Path("assets/charts/09_distribution.png")
    plt.savefig(out, dpi=200)
    plt.savefig(out.with_suffix(".svg"))

    # Print summary stats
    print(f"✓ {out}")
    print(f"   Médiane : {np.median(v):,.0f} L")
    print(f"   Moyenne : {np.mean(v):,.0f} L")
    print(f"   Importateurs < 1 000 L : {(v < 1000).sum()} "
          f"({(v < 1000).sum()/total*100:.0f}%)")


if __name__ == "__main__":
    main()
