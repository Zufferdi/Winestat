"""Run the full pipeline: clean data, generate every chart, build interactive."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STEPS = [
    ("Nettoyage des données",                ["python3", "src/clean_data.py"]),
    ("Chart 01 — Top 20",                    ["python3", "src/charts/chart_01_top20.py"]),
    ("Chart 02 — Lorenz / Gini",             ["python3", "src/charts/chart_02_lorenz.py"]),
    ("Chart 03 — Historique 2012-2025",      ["python3", "src/charts/chart_03_historique.py"]),
    ("Chart 04 — Carte cantons",             ["python3", "src/charts/chart_04_carte_cantons.py"]),
    ("Chart 05 — Treemap",                   ["python3", "src/charts/chart_05_treemap.py"]),
    ("Chart 06 — Rouge vs blanc",            ["python3", "src/charts/chart_06_rouge_vs_blanc.py"]),
    ("Chart 07 — Pareto",                    ["python3", "src/charts/chart_07_pareto.py"]),
    ("Chart 08 — Consolidation groupes",     ["python3", "src/charts/chart_08_consolidation.py"]),
    ("Chart 09 — Distribution (long tail)",  ["python3", "src/charts/chart_09_distribution.py"]),
    ("Chart 10 — HHI & concentration",       ["python3", "src/charts/chart_10_hhi.py"]),
    ("Chart 11 — Prix par segment",          ["python3", "src/charts/chart_11_segments.py"]),
    ("Données pour l'explorateur",           ["python3", "src/build_interactive.py"]),
    ("Données pour le dashboard D3",         ["python3", "src/build_dashboard.py"]),
    ("Export xlsx analytique",               ["python3", "src/export_xlsx.py"]),
]


def main():
    for label, cmd in STEPS:
        print(f"\n▶ {label}")
        result = subprocess.run(cmd, cwd=ROOT)
        if result.returncode != 0:
            print(f"  ✗ Échec : {' '.join(cmd)}")
            sys.exit(result.returncode)
    print("\n✓ Pipeline complète.")
    print("  Voir assets/charts/, assets/interactive/, assets/dashboard/")


if __name__ == "__main__":
    main()
