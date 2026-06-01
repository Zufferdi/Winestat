"""Chart 11 — Price evolution rouge vs blanc 2012-2025."""
from pathlib import Path
import sys
import pandas as pd
import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from theme import apply, WINE_RED, WINE_WHITE, MUTED, INK, PAPER, credit


def main():
    apply()
    df = pd.read_csv("data/processed/historique_ofdf.csv")
    df = df.query("annee <= 2025")  # exclude incomplete 2026

    rouge = df.query("section_courte == 'Vin rouge (≤2L)'").sort_values("annee")
    blanc = df.query("section_courte == 'Vin blanc (≤2L)'").sort_values("annee")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
    fig.subplots_adjust(top=0.84, wspace=0.22, bottom=0.10)

    # Left: prices
    ax1.plot(rouge["annee"], rouge["prix_par_kg"],
             color=WINE_RED, linewidth=2.6, marker="o", markersize=5, label="Rouge")
    ax1.plot(blanc["annee"], blanc["prix_par_kg"],
             color="#B47C36", linewidth=2.6, marker="o", markersize=5, label="Blanc")

    # endpoint labels
    for series, color, label in [(rouge, WINE_RED, "Rouge"),
                                  (blanc, "#B47C36", "Blanc")]:
        x_end = series["annee"].iloc[-1]
        y_end = series["prix_par_kg"].iloc[-1]
        ax1.annotate(f"{label}\n{y_end:.2f} CHF/kg",
                     xy=(x_end, y_end), xytext=(8, 0),
                     textcoords="offset points",
                     fontsize=10, va="center", color=color, fontweight="bold")

    ax1.set_ylabel("Prix moyen à l'importation (CHF/kg)")
    ax1.set_xlabel("Année")
    ax1.set_title("Prix moyen", loc="left", pad=12, fontsize=14)
    ax1.set_xlim(2011.5, 2026.5)
    ax1.legend(loc="upper left")

    # Right: volume (kilos) — show the diverging trajectories
    ax2.plot(rouge["annee"], rouge["kilos"] / 1e6,
             color=WINE_RED, linewidth=2.6, marker="o", markersize=5, label="Rouge")
    ax2.plot(blanc["annee"], blanc["kilos"] / 1e6,
             color="#B47C36", linewidth=2.6, marker="o", markersize=5, label="Blanc")

    for series, color, label in [(rouge, WINE_RED, "Rouge"),
                                  (blanc, "#B47C36", "Blanc")]:
        x_end = series["annee"].iloc[-1]
        y_end = series["kilos"].iloc[-1] / 1e6
        ax2.annotate(f"{y_end:.0f} Mkg",
                     xy=(x_end, y_end), xytext=(8, 0),
                     textcoords="offset points",
                     fontsize=10, va="center", color=color, fontweight="bold")

    ax2.set_ylabel("Volume importé (millions de kg)")
    ax2.set_xlabel("Année")
    ax2.set_title("Volume", loc="left", pad=12, fontsize=14)
    ax2.set_xlim(2011.5, 2026.5)
    ax2.legend(loc="upper left")

    # Headline + subhead
    r0, r1 = rouge["prix_par_kg"].iloc[0], rouge["prix_par_kg"].iloc[-1]
    b0, b1 = blanc["prix_par_kg"].iloc[0], blanc["prix_par_kg"].iloc[-1]
    delta_r = (r1 - r0) / r0 * 100
    delta_b = (b1 - b0) / b0 * 100

    fig.text(0.04, 0.96, "Rouge vs blanc : deux trajectoires différentes",
             ha="left", va="top", fontsize=20, fontweight="bold", color=INK)
    fig.text(0.04, 0.92,
             f"Depuis 2012, le rouge s'est renchéri de {delta_r:+.0f}% et le blanc de {delta_b:+.0f}%. "
             "Le rouge importé reste près de 70% plus cher au kilo que le blanc.",
             ha="left", va="top", fontsize=11, color=MUTED, style="italic")

    credit(ax2, "Source : OFDF · HS 2204.2121 (blanc) + 2204.2141 (rouge), récipients ≤ 2L")
    out = Path("assets/charts/11_segments.png")
    plt.savefig(out, dpi=200)
    plt.savefig(out.with_suffix(".svg"))
    print(f"✓ {out}")


if __name__ == "__main__":
    main()
