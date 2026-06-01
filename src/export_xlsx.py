"""Export a clean, analysis-ready xlsx with multiple sheets:
  - Importateurs (cleaned + enriched)
  - Top 50
  - Par canton
  - Par groupe (consolidé)
  - Historique OFDF
  - Métriques de concentration
  - Distribution par taille
"""
from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path("data/processed/wine_imports_analysis.xlsx")


def main():
    df = pd.read_csv("data/processed/importateurs.csv")
    hist = pd.read_csv("data/processed/historique_ofdf.csv")

    importateurs = df.sort_values("litres_total", ascending=False).reset_index(drop=True)
    importateurs.insert(0, "rang", importateurs.index + 1)
    total_l = importateurs["litres_total"].sum()
    importateurs["part_marche_pct"] = importateurs["litres_total"] / total_l * 100
    importateurs["share_rouge_pct"] = (
        importateurs["litres_rouge"] / importateurs["litres_total"].clip(lower=1) * 100
    )

    top50 = importateurs.head(50)[
        ["rang", "importateur", "commune", "canton", "litres_rouge",
         "litres_blanc", "litres_total", "part_marche_pct", "share_rouge_pct",
         "groupe", "noga_code"]
    ]

    by_canton = (df.groupby("canton")
                   .agg(n_importateurs=("importateur", "count"),
                        litres_rouge=("litres_rouge", "sum"),
                        litres_blanc=("litres_blanc", "sum"),
                        litres_total=("litres_total", "sum"))
                   .reset_index()
                   .sort_values("litres_total", ascending=False))
    by_canton["part_marche_pct"] = by_canton["litres_total"] / total_l * 100
    by_canton["share_rouge_pct"] = (
        by_canton["litres_rouge"] / by_canton["litres_total"] * 100
    )

    df["groupe_eff"] = df["groupe"].fillna(df["importateur"])
    by_group = (df.groupby("groupe_eff")
                  .agg(n_entites=("importateur", "count"),
                       litres_rouge=("litres_rouge", "sum"),
                       litres_blanc=("litres_blanc", "sum"),
                       litres_total=("litres_total", "sum"))
                  .reset_index()
                  .sort_values("litres_total", ascending=False))
    by_group["part_marche_pct"] = by_group["litres_total"] / total_l * 100
    by_group = by_group.rename(columns={"groupe_eff": "groupe_ou_importateur"})

    v = df["litres_total"].values
    v = v[v > 0]
    v_sorted = np.sort(v)
    cum = np.cumsum(v_sorted)
    gini_imp = (len(v_sorted) + 1 - 2 * cum.sum() / cum[-1]) / len(v_sorted)
    hhi_imp = float(((v / v.sum() * 100) ** 2).sum())

    vg = by_group["litres_total"].values
    vg = vg[vg > 0]
    vg_sorted = np.sort(vg)
    cum_g = np.cumsum(vg_sorted)
    gini_grp = (len(vg_sorted) + 1 - 2 * cum_g.sum() / cum_g[-1]) / len(vg_sorted)
    hhi_grp = float(((vg / vg.sum() * 100) ** 2).sum())

    sorted_t = df["litres_total"].sort_values(ascending=False).values
    metrics = pd.DataFrame([
        {"métrique": "Nombre d'importateurs", "valeur": len(df), "note": ""},
        {"métrique": "Volume total (L)", "valeur": float(total_l), "note": "rouge + blanc"},
        {"métrique": "Volume rouge (L)", "valeur": float(df['litres_rouge'].sum()), "note": ""},
        {"métrique": "Volume blanc (L)", "valeur": float(df['litres_blanc'].sum()), "note": ""},
        {"métrique": "Part rouge (%)", "valeur": float(df['litres_rouge'].sum()/total_l*100), "note": ""},
        {"métrique": "Top 1 (Coop)", "valeur": float(sorted_t[0]/total_l*100), "note": "% du marché"},
        {"métrique": "Top 2", "valeur": float(sorted_t[:2].sum()/total_l*100), "note": "% du marché"},
        {"métrique": "Top 5", "valeur": float(sorted_t[:5].sum()/total_l*100), "note": "% du marché"},
        {"métrique": "Top 10", "valeur": float(sorted_t[:10].sum()/total_l*100), "note": "% du marché"},
        {"métrique": "Top 20", "valeur": float(sorted_t[:20].sum()/total_l*100), "note": "% du marché"},
        {"métrique": "Médiane (L)", "valeur": float(np.median(v)), "note": "importateur médian"},
        {"métrique": "Moyenne (L)", "valeur": float(np.mean(v)), "note": ""},
        {"métrique": "Gini (par importateur)", "valeur": float(gini_imp), "note": "0=égalité, 1=monopole"},
        {"métrique": "Gini (après consolidation)", "valeur": float(gini_grp), "note": ""},
        {"métrique": "HHI (par importateur)", "valeur": hhi_imp, "note": "<1500 = normal, >2500 = élevé"},
        {"métrique": "HHI (après consolidation)", "valeur": hhi_grp, "note": ""},
        {"métrique": "Cantons couverts", "valeur": int(df['canton'].nunique()), "note": "incl. FL (Liechtenstein)"},
        {"métrique": "Communes couvertes", "valeur": int(df['commune'].nunique()), "note": ""},
    ])

    buckets = [
        ("< 100 L", 0, 100),
        ("100 – 1 000 L", 100, 1_000),
        ("1 k – 10 k L", 1_000, 10_000),
        ("10 k – 100 k L", 10_000, 100_000),
        ("100 k – 1 M L", 100_000, 1_000_000),
        ("1 – 10 M L", 1_000_000, 10_000_000),
        ("> 10 M L", 10_000_000, float("inf")),
    ]
    dist_rows = []
    for label, lo, hi in buckets:
        mask = (df["litres_total"] >= lo) & (df["litres_total"] < hi)
        n_b = int(mask.sum())
        vol_b = float(df.loc[mask, "litres_total"].sum())
        dist_rows.append({
            "tranche": label,
            "n_importateurs": n_b,
            "pct_importateurs": n_b / len(df) * 100,
            "volume_total_L": vol_b,
            "pct_volume": vol_b / total_l * 100 if total_l else 0,
        })
    distribution = pd.DataFrame(dist_rows)

    with pd.ExcelWriter(OUT, engine="openpyxl") as writer:
        importateurs.to_excel(writer, sheet_name="Importateurs", index=False)
        top50.to_excel(writer, sheet_name="Top 50", index=False)
        by_canton.to_excel(writer, sheet_name="Par canton", index=False)
        by_group.head(50).to_excel(writer, sheet_name="Par groupe", index=False)
        distribution.to_excel(writer, sheet_name="Distribution tailles", index=False)
        metrics.to_excel(writer, sheet_name="Métriques", index=False)
        hist.to_excel(writer, sheet_name="Historique OFDF", index=False)

        for sheet_name in writer.sheets:
            ws = writer.sheets[sheet_name]
            for col in ws.columns:
                max_length = 0
                col_letter = col[0].column_letter
                for cell in col:
                    try:
                        val = str(cell.value) if cell.value is not None else ""
                        if len(val) > max_length:
                            max_length = len(val)
                    except Exception:
                        pass
                ws.column_dimensions[col_letter].width = min(max_length + 2, 40)

    print(f"✓ {OUT} ({OUT.stat().st_size/1024:.0f} KB, 7 feuilles)")


if __name__ == "__main__":
    main()
