"""Chart 08 — Consolidation by holding group: see the hidden concentration."""
from pathlib import Path
import sys
import pandas as pd
import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from theme import apply, WINE_RED, WINE_WHITE, ACCENT, MUTED, INK, credit


def main():
    apply()
    df = pd.read_csv("data/processed/importateurs.csv")

    # Build the consolidated table: where a 'groupe' is defined, sum under it;
    # otherwise the importer is its own group.
    df["groupe_eff"] = df["groupe"].fillna(df["importateur"])
    consolidated = (df.groupby("groupe_eff")
                      .agg(litres=("litres_total", "sum"),
                           n_filiales=("importateur", "count"))
                      .reset_index()
                      .sort_values("litres", ascending=False))

    top_groups = consolidated.head(15).copy()
    top_groups["is_group"] = top_groups["n_filiales"] > 1

    fig, ax = plt.subplots(figsize=(12, 8.5))
    fig.subplots_adjust(top=0.86, left=0.28)

    top_groups = top_groups.iloc[::-1]  # for barh
    colors = [ACCENT if g else WINE_RED for g in top_groups["is_group"]]

    bars = ax.barh(range(len(top_groups)), top_groups["litres"] / 1e6,
                   color=colors, edgecolor=INK, linewidth=0.4)

    labels = []
    for _, row in top_groups.iterrows():
        if row["is_group"]:
            labels.append(f"{row['groupe_eff']}  ({row['n_filiales']} ent.)")
        else:
            labels.append(row["groupe_eff"])
    ax.set_yticks(range(len(top_groups)))
    ax.set_yticklabels(labels, fontsize=10)

    for i, (_, row) in enumerate(top_groups.iterrows()):
        ax.text(row["litres"] / 1e6 + 0.3, i, f"{row['litres']/1e6:.1f}M L",
                va="center", fontsize=9, color=INK)

    ax.set_xlabel("Litres importés (millions, après consolidation)")
    ax.grid(axis="y", visible=False)

    # Legend
    from matplotlib.patches import Patch
    ax.legend(handles=[
        Patch(facecolor=ACCENT, edgecolor=INK, label="Groupe (filiales consolidées)"),
        Patch(facecolor=WINE_RED, edgecolor=INK, label="Acteur indépendant"),
    ], loc="lower right")

    fig.text(0.04, 0.96, "Quand on regroupe les filiales : les vrais poids lourds",
             ha="left", va="top", fontsize=20, fontweight="bold", color=INK)
    fig.text(0.04, 0.92,
             "Coop, Migros, Schenk… plusieurs « petits » importateurs appartiennent en réalité "
             "à un même groupe. Top 15 après consolidation.",
             ha="left", va="top", fontsize=11, color=MUTED, style="italic")

    credit(ax)
    out = Path("assets/charts/08_consolidation.png")
    plt.savefig(out, dpi=200)
    plt.savefig(out.with_suffix(".svg"))
    print(f"✓ {out}")


if __name__ == "__main__":
    main()
