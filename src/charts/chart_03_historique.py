"""Chart 03 — Historical evolution of wine imports 2012-2025 (OFDF series)."""
from pathlib import Path
import sys
import pandas as pd
import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from theme import apply, WINE_RED, WINE_WHITE, ACCENT, MUTED, INK, GRID, credit


def main():
    apply()
    df = pd.read_csv("data/processed/historique_ofdf.csv")

    # Use only the all-wine total, exclude incomplete 2026
    total = (df[df["section_courte"] == "Tous vins"]
             .query("annee <= 2025")
             .sort_values("annee"))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 9), sharex=True,
                                    gridspec_kw={"height_ratios": [1.2, 1]})
    fig.subplots_adjust(top=0.88, hspace=0.18)

    # --- volume area chart ---
    kg = total["kilos"] / 1e6
    ax1.fill_between(total["annee"], kg, color=WINE_RED, alpha=0.18)
    ax1.plot(total["annee"], kg, color=WINE_RED, linewidth=2.6, marker="o",
             markersize=5)

    # endpoint labels
    for x, y in [(total["annee"].iloc[0], kg.iloc[0]),
                 (total["annee"].iloc[-1], kg.iloc[-1])]:
        ax1.annotate(f"{y:.0f} Mkg", xy=(x, y),
                     xytext=(0, 12), textcoords="offset points",
                     fontsize=10, color=INK, ha="center", fontweight="bold")

    # Covid annotation
    covid_y = total[total["annee"] == 2020]["kilos"].iloc[0] / 1e6
    ax1.annotate("Covid-19\n(consommation à domicile ↑)",
                 xy=(2020, covid_y),
                 xytext=(2017.6, covid_y + 18),
                 fontsize=9, color=MUTED, ha="center", style="italic",
                 arrowprops=dict(arrowstyle="->", color=MUTED, lw=0.7))

    ax1.set_ylabel("Volume importé (millions de kg)")
    ax1.set_ylim(0, kg.max() * 1.18)
    ax1.set_yticks(range(0, 220, 50))

    # --- price line ---
    price = total["prix_par_kg"]
    ax2.plot(total["annee"], price, color=ACCENT, linewidth=2.6, marker="o",
             markersize=5)

    for x, y in [(total["annee"].iloc[0], price.iloc[0]),
                 (total["annee"].iloc[-1], price.iloc[-1])]:
        ax2.annotate(f"{y:.2f} CHF/kg", xy=(x, y),
                     xytext=(0, 10), textcoords="offset points",
                     fontsize=10, color=INK, ha="center", fontweight="bold")

    ax2.set_ylabel("Prix moyen à l'importation (CHF/kg)")
    ax2.set_xlabel("Année")
    ax2.set_ylim(4.5, 8)

    # title block
    fig.text(0.04, 0.96,
             "Moins de vin, mais plus cher",
             ha="left", va="top", fontsize=20, fontweight="bold", color=INK)
    fig.text(0.04, 0.92,
             "Évolution des importations totales de vin en Suisse (2012-2025) — "
             "le volume recule, la valeur unitaire grimpe.",
             ha="left", va="top", fontsize=11, color=MUTED, style="italic")

    for ax in (ax1, ax2):
        ax.set_xticks(range(2012, 2026, 2))
        ax.grid(axis="x", visible=False)

    credit(ax2, "Source : OFDF (Administration fédérale des douanes) · HS 2204")
    out = Path("assets/charts/03_historique.png")
    plt.savefig(out, dpi=200)
    plt.savefig(out.with_suffix(".svg"))
    print(f"✓ {out}")


if __name__ == "__main__":
    main()
