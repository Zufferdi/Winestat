"""Chart 01 — Top 20 importers, stacked red + white."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from theme import apply, WINE_RED, WINE_WHITE, INK, credit


def main():
    apply()
    df = pd.read_csv("data/processed/importateurs.csv")

    top = df.nlargest(20, "litres_total").iloc[::-1]  # reverse for barh

    fig, ax = plt.subplots(figsize=(11, 9))
    y = range(len(top))

    ax.barh(y, top["litres_rouge"] / 1e6, color=WINE_RED, label="Vin rouge",
            edgecolor=INK, linewidth=0.4)
    ax.barh(y, top["litres_blanc"] / 1e6, left=top["litres_rouge"] / 1e6,
            color=WINE_WHITE, label="Vin blanc",
            edgecolor=INK, linewidth=0.4)

    ax.set_yticks(list(y))
    ax.set_yticklabels(top["importateur"], fontsize=10)
    ax.set_xlabel("Litres importés (millions)")
    ax.set_title("Top 20 des importateurs de vin en Suisse — 2025",
                 loc="left", pad=18)

    # Value labels at the end of each bar
    for i, (_, row) in enumerate(top.iterrows()):
        total_m = row["litres_total"] / 1e6
        ax.text(total_m + 0.3, i, f"{total_m:,.1f}M",
                va="center", fontsize=9, color=INK)

    ax.legend(loc="lower right")
    ax.set_xlim(0, top["litres_total"].max() / 1e6 * 1.1)
    ax.grid(axis="y", visible=False)

    credit(ax)
    out = Path("assets/charts/01_top20.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, dpi=200)
    plt.savefig(out.with_suffix(".svg"))
    print(f"✓ {out}")


if __name__ == "__main__":
    main()
