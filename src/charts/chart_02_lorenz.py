"""Chart 02 — Lorenz curve / market concentration with Gini coefficient."""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from theme import apply, WINE_RED, ACCENT, MUTED, INK, PAPER, credit


def gini(values: np.ndarray) -> float:
    v = np.sort(values)
    n = len(v)
    cum = np.cumsum(v)
    return (n + 1 - 2 * cum.sum() / cum[-1]) / n


def main():
    apply()
    df = pd.read_csv("data/processed/importateurs.csv")
    v = df["litres_total"].values
    v = v[v > 0]
    v_sorted = np.sort(v)

    n = len(v_sorted)
    x = np.arange(1, n + 1) / n
    y = np.cumsum(v_sorted) / v_sorted.sum()

    g = gini(v_sorted)

    # Headline shares
    top_pct_shares = {}
    for k in [1, 5, 10, 25]:
        idx = int(n * (1 - k / 100))
        top_pct_shares[k] = 1 - y[idx]

    fig, ax = plt.subplots(figsize=(10, 8.5))
    fig.subplots_adjust(top=0.88, bottom=0.12)

    ax.plot([0, 1], [0, 1], color=MUTED, linestyle="--", linewidth=1.2,
            label="Égalité parfaite")
    ax.plot(x, y, color=WINE_RED, linewidth=2.4, label="Distribution réelle")
    ax.fill_between(x, y, x, color=WINE_RED, alpha=0.12)

    # Mark the top-X% share point — place all labels in the upper-left empty area
    label_y = [0.86, 0.78, 0.70, 0.62]
    for (k, share), ly in zip(top_pct_shares.items(), label_y):
        px, py = 1 - k/100, 1 - share
        ax.annotate(
            f"Top {k}% = {share*100:.0f}% du marché",
            xy=(px, py), xytext=(0.32, ly),
            fontsize=10.5, color=INK, ha="left", va="center",
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.7,
                            connectionstyle="arc3,rad=-0.15"),
        )
        ax.scatter([px], [py], color=ACCENT, s=40, zorder=5,
                   edgecolor=PAPER, linewidth=1.2)

    ax.set_xlabel("Part cumulée des importateurs (triés par volume)")
    ax.set_ylabel("Part cumulée du volume importé")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.legend(loc="lower right", bbox_to_anchor=(1, 0.08))

    # Title and subtitle as figure text — gives full control over spacing
    fig.text(0.04, 0.96,
             "Un marché extrêmement concentré",
             ha="left", va="top", fontsize=18, fontweight="bold", color=INK)
    fig.text(0.04, 0.915,
             f"2 153 importateurs · coefficient de Gini = {g:.2f} · "
             "les deux premiers à eux seuls représentent plus de 40 % du volume.",
             ha="left", va="top", fontsize=11, color=MUTED, style="italic")

    credit(ax)
    out = Path("assets/charts/02_lorenz.png")
    plt.savefig(out, dpi=200)
    plt.savefig(out.with_suffix(".svg"))
    print(f"✓ {out}  (Gini = {g:.3f})")
    for k, share in top_pct_shares.items():
        print(f"   Top {k:>2}%  →  {share*100:5.1f}% du volume")


if __name__ == "__main__":
    main()
