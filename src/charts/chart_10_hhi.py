"""Chart 10 — HHI (Herfindahl-Hirschman Index) and antitrust thresholds."""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from theme import apply, WINE_RED, ACCENT, MUTED, INK, PAPER, GRID, credit


def main():
    apply()
    df = pd.read_csv("data/processed/importateurs.csv")

    # Compute HHI both at importer level and consolidated by group
    def hhi(values: np.ndarray) -> float:
        shares = values / values.sum() * 100  # percentage shares
        return (shares ** 2).sum()

    hhi_imp = hhi(df["litres_total"].values)

    df["groupe_eff"] = df["groupe"].fillna(df["importateur"])
    by_group = df.groupby("groupe_eff")["litres_total"].sum().values
    hhi_grp = hhi(by_group)

    # Reference HHI values for context
    refs = [
        ("Marché parfaitement concurrentiel", 100, "#7FB069"),
        ("Concentration modérée\n(seuil FTC)", 1500, "#E6B85C"),
        ("Concentration élevée\n(seuil FTC)", 2500, "#D88B3B"),
        ("Vin importé en Suisse\n(par importateur)", hhi_imp, WINE_RED),
        ("Vin importé en Suisse\n(consolidé par groupe)", hhi_grp, "#4A0F18"),
        ("Monopole (1 seul acteur)", 10000, INK),
    ]

    fig, ax = plt.subplots(figsize=(13, 8))
    fig.subplots_adjust(top=0.86, left=0.05, right=0.97, bottom=0.10)

    # Background zones for FTC thresholds
    ax.axhspan(0, 1500, color="#7FB069", alpha=0.08, zorder=0)
    ax.axhspan(1500, 2500, color="#E6B85C", alpha=0.10, zorder=0)
    ax.axhspan(2500, 10000, color=WINE_RED, alpha=0.08, zorder=0)

    refs_sorted = sorted(refs, key=lambda x: x[1])
    x = np.arange(len(refs_sorted))
    values = [r[1] for r in refs_sorted]
    colors = [r[2] for r in refs_sorted]
    labels = [r[0] for r in refs_sorted]

    bars = ax.bar(x, values, color=colors, edgecolor=INK, linewidth=0.4, width=0.65)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel("Indice de Herfindahl-Hirschman (HHI)")
    ax.set_ylim(0, 10500)

    # Value labels above bars
    for xi, v in zip(x, values):
        ax.text(xi, v + 150, f"{v:,.0f}".replace(",", " "),
                ha="center", fontsize=10, fontweight="bold", color=INK)

    # Zone annotations on the right
    ax.text(len(x) - 0.4, 750, "ZONE NORMALE", ha="right", fontsize=9,
            color="#5A8A45", fontweight="bold", alpha=0.7)
    ax.text(len(x) - 0.4, 2000, "CONCENTRATION MODÉRÉE", ha="right", fontsize=9,
            color="#A07F30", fontweight="bold", alpha=0.7)
    ax.text(len(x) - 0.4, 4500, "CONCENTRATION ÉLEVÉE", ha="right", fontsize=9,
            color=WINE_RED, fontweight="bold", alpha=0.7)

    fig.text(0.04, 0.96, "Concentration : ce que disent les standards antitrust",
             ha="left", va="top", fontsize=20, fontweight="bold", color=INK)
    fig.text(0.04, 0.92,
             f"L'indice HHI suisse ({hhi_imp:,.0f} par importateur, {hhi_grp:,.0f} après "
             "consolidation des groupes) place le marché en zone de concentration "
             "« modérée » au sens antitrust — moins extrême que ne le suggère le Gini.".replace(",", " "),
             ha="left", va="top", fontsize=11, color=MUTED, style="italic")

    credit(ax)
    out = Path("assets/charts/10_hhi.png")
    plt.savefig(out, dpi=200)
    plt.savefig(out.with_suffix(".svg"))
    print(f"✓ {out}  (HHI importateur = {hhi_imp:.0f}, groupe = {hhi_grp:.0f})")


if __name__ == "__main__":
    main()
