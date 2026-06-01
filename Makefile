# Makefile — convenience commands for Winestat.

.PHONY: all clean charts interactive dashboard xlsx install help serve

help:
	@echo "Cibles disponibles :"
	@echo "  make install      Installer les dépendances Python"
	@echo "  make all          Tout reconstruire (données + 11 charts + interactifs + xlsx)"
	@echo "  make charts       Régénérer les 11 graphiques statiques"
	@echo "  make interactive  Régénérer l'explorateur tabulaire"
	@echo "  make dashboard    Régénérer le dashboard D3"
	@echo "  make xlsx         Régénérer le fichier xlsx analytique"
	@echo "  make clean        Supprimer les fichiers générés"
	@echo "  make serve        Servir le repo sur http://localhost:8000"

install:
	pip install -r requirements.txt

all:
	python3 src/run_all.py

charts:
	python3 src/clean_data.py
	for f in src/charts/chart_*.py; do echo "▶ $$f"; python3 "$$f" || exit 1; done

interactive:
	python3 src/clean_data.py
	python3 src/build_interactive.py

dashboard:
	python3 src/clean_data.py
	python3 src/build_dashboard.py

xlsx:
	python3 src/clean_data.py
	python3 src/export_xlsx.py

clean:
	rm -rf data/processed/*.csv data/processed/*.xlsx
	rm -rf assets/charts/*.png assets/charts/*.svg
	rm -rf assets/interactive/*.json assets/interactive/*.html
	rm -rf assets/dashboard/*.json assets/dashboard/*.html
	find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true

serve:
	@echo "Explorateur  : http://localhost:8000/assets/interactive/explorer.html"
	@echo "Dashboard D3 : http://localhost:8000/assets/dashboard/dashboard.html"
	python3 -m http.server 8000
