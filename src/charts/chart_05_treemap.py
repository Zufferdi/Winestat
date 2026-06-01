"""Chart 05 — Treemap of top importers (inline squarify implementation)."""
from pathlib import Path
import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from theme import apply, WINE_RED, WINE_WHITE, INK, MUTED, PAPER, credit


# --- Minimal squarified treemap (Bruls, Huijbregts & van Wijk, 2000) ---
def _layout_row(sizes, x, y, dx, dy):
    """Lay out one row, returning list of (x, y, dx, dy) and remaining rect."""
    total = sum(sizes)
    if dx >= dy:
        rw = total / dy
        rects = []
        cy = y
        for s in sizes:
            h = s / rw
            rects.append((x, cy, rw, h))
            cy += h
        return rects, (x + rw, y, dx - rw, dy)
    else:
        rh = total / dx
        rects = []
        cx = x
        for s in sizes:
            w = s / rh
            rects.append((cx, y, w, rh))
            cx += w
        return rects, (x, y + rh, dx, dy - rh)


def _worst(sizes, side):
    s = sum(sizes)
    smax = max(sizes)
    smin = min(sizes)
    return max((side * side * smax) / (s * s), (s * s) / (side * side * smin))


def squarified(sizes, x=0, y=0, dx=100, dy=60):
    sizes = sorted(sizes, reverse=True)
    total_area = dx * dy
    sizes = [s * total_area / sum(sizes) for s in sizes]

    rects = []
    remaining = sizes[:]
    cx, cy, cdx, cdy = x, y, dx, dy
    row = []
    while remaining:
        side = min(cdx, cdy)
        if not row:
            row = [remaining.pop(0)]
            continue
        with_new = row + [remaining[0]]
        if _worst(with_new, side) <= _worst(row, side):
            row.append(remaining.pop(0))
        else:
            placed, (cx, cy, cdx, cdy) = _layout_row(row, cx, cy, cdx, cdy)
            rects.extend(placed)
            row = []
    if row:
        placed, _ = _layout_row(row, cx, cy, cdx, cdy)
        rects.extend(placed)
    return rects


def main():
    apply()
    df = pd.read_csv("data/processed/importateurs.csv")

    n_top = 40
    top = df.nlargest(n_top, "litres_total").copy()
    others_total = df["litres_total"].sum() - top["litres_total"].sum()
    others_rouge = df["litres_rouge"].sum() - top["litres_rouge"].sum()
    others_blanc = df["litres_blanc"].sum() - top["litres_blanc"].sum()
    n_others = len(df) - n_top

    others = pd.DataFrame([{
        "importateur": f"+ {n_others} autres importateurs",
        "litres_total": others_total,
        "litres_rouge": others_rouge,
        "litres_blanc": others_blanc,
    }])
    plot_df = pd.concat([top, others], ignore_index=True)
    plot_df["share_rouge"] = plot_df["litres_rouge"] / plot_df["litres_total"].clip(lower=1)
    plot_df = plot_df.sort_values("litres_total", ascending=False).reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(15, 9))
    fig.subplots_adjust(top=0.88, left=0.04, right=0.96, bottom=0.06)

    rects = squarified(plot_df["litres_total"].tolist(), 0, 0, 100, 60)

    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("wine", [WINE_WHITE, "#B47C36", WINE_RED])

    for (x, y, dx, dy), (_, row) in zip(rects, plot_df.iterrows()):
        is_other = row["importateur"].startswith("+ ")
        color = "#D9CFC4" if is_other else cmap(row["share_rouge"])
        rect = patches.Rectangle((x, y), dx, dy, facecolor=color,
                                 edgecolor=PAPER, linewidth=2)
        ax.add_patch(rect)

        area = dx * dy
        if area > 30:
            name = row["importateur"]
            display_name = (name[:28] + "…") if len(name) > 30 else name
            litres = f"{row['litres_total']/1e6:.1f}M L"
            cx, cy = x + dx / 2, y + dy / 2
            font_main = 10 if area > 80 else 8
            font_sub = 8 if area > 80 else 7
            txt_col = "white" if (row["share_rouge"] > 0.6 and not is_other) else INK
            ax.text(cx, cy + dy * 0.07, display_name, ha="center", va="center",
                    fontsize=font_main, fontweight="bold", color=txt_col)
            ax.text(cx, cy - dy * 0.12, litres, ha="center", va="center",
                    fontsize=font_sub, color=txt_col)

    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.set_aspect("equal")
    ax.axis("off")

    fig.text(0.04, 0.96, "Anatomie du marché : 40 importateurs vs 2 113 autres",
             ha="left", va="top", fontsize=20, fontweight="bold", color=INK)
    fig.text(0.04, 0.92,
             "Taille = volume total importé · couleur = type de vin dominant "
             "(bordeaux = surtout rouge, doré = surtout blanc).",
             ha="left", va="top", fontsize=11, color=MUTED, style="italic")

    credit(ax)
    out = Path("assets/charts/05_treemap.png")
    plt.savefig(out, dpi=200)
    plt.savefig(out.with_suffix(".svg"))
    print(f"✓ {out}")


if __name__ == "__main__":
    main()
