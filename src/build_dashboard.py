"""Build the interactive D3 dashboard with linked views.

Emits to assets/dashboard/:
  - dashboard_data.json — all aggregates needed by the dashboard
  - dashboard.html      — standalone D3 dashboard (linked map + bars + scatter)
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd


OUT = Path("assets/dashboard")
OUT.mkdir(parents=True, exist_ok=True)


def main():
    df = pd.read_csv("data/processed/importateurs.csv")
    hist = pd.read_csv("data/processed/historique_ofdf.csv")

    importers = [{
        "n": r.importateur,
        "c": r.canton,
        "co": r.commune,
        "r": int(r.litres_rouge),
        "b": int(r.litres_blanc),
        "t": int(r.litres_total),
        "g": r.groupe if isinstance(r.groupe, str) else None,
    } for r in df.itertuples()]

    by_canton = (df.groupby("canton")
                   .agg(total=("litres_total", "sum"),
                        rouge=("litres_rouge", "sum"),
                        blanc=("litres_blanc", "sum"),
                        n=("importateur", "count"))
                   .reset_index())
    by_canton["share_rouge"] = by_canton["rouge"] / by_canton["total"]
    cantons = by_canton.to_dict("records")

    df["groupe_eff"] = df["groupe"].fillna(df["importateur"])
    groups = (df.groupby("groupe_eff")
                .agg(total=("litres_total", "sum"),
                     rouge=("litres_rouge", "sum"),
                     blanc=("litres_blanc", "sum"),
                     n=("importateur", "count"))
                .reset_index()
                .sort_values("total", ascending=False)
                .head(25)
                .rename(columns={"groupe_eff": "name"})
                .to_dict("records"))

    history_all = (hist.query("section_courte == 'Tous vins'")
                       .sort_values("annee").to_dict("records"))
    history_rouge = (hist.query("section_courte == 'Vin rouge (≤2L)'")
                         .sort_values("annee").to_dict("records"))
    history_blanc = (hist.query("section_courte == 'Vin blanc (≤2L)'")
                         .sort_values("annee").to_dict("records"))

    total_l = float(df["litres_total"].sum())
    sorted_t = df["litres_total"].sort_values(ascending=False).values
    v = sorted_t[sorted_t > 0]
    cum = np.cumsum(v)
    gini = (len(v) + 1 - 2 * cum.sum() / cum[-1]) / len(v)
    hhi = float(((v / v.sum() * 100) ** 2).sum())

    kpis = {
        "n_importers": len(df),
        "n_cantons": int(df["canton"].nunique()),
        "n_communes": int(df["commune"].nunique()),
        "total_litres": total_l,
        "share_rouge": float(df["litres_rouge"].sum() / total_l),
        "top2_share": float(sorted_t[:2].sum() / total_l),
        "top10_share": float(sorted_t[:10].sum() / total_l),
        "gini": float(gini),
        "hhi": hhi,
        "median": float(np.median(v)),
        "mean": float(np.mean(v)),
    }

    payload = {
        "kpis": kpis,
        "importers": importers,
        "cantons": cantons,
        "groups": groups,
        "history": {"all": history_all, "rouge": history_rouge, "blanc": history_blanc},
    }

    (OUT / "dashboard_data.json").write_text(
        json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    )
    print(f"✓ {OUT}/dashboard_data.json "
          f"({(OUT/'dashboard_data.json').stat().st_size/1024:.0f} KB)")

    html = _build_html(payload)
    (OUT / "dashboard.html").write_text(html)
    print(f"✓ {OUT}/dashboard.html "
          f"({(OUT/'dashboard.html').stat().st_size/1024:.0f} KB)")


def _build_html(payload: dict) -> str:
    """Render the standalone D3 dashboard with embedded data."""
    data_json = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    template = (Path(__file__).resolve().parent / "dashboard_template.html").read_text()
    return template.replace("__PAYLOAD__", data_json)


if __name__ == "__main__":
    main()
