"""Build the interactive HTML explorer with embedded data — enhanced version.

New features vs original:
  - Dark mode toggle
  - Sticky controls bar
  - CSV export of filtered selection
  - Click row to expand detail panel
  - Fade-in animations on load
"""
from pathlib import Path
import json
import pandas as pd


HTML_TEMPLATE = r"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Le marché suisse du vin importé · 2025</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Manrope:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {
    --paper: #FAF7F2; --paper-2: #F2EDE4; --ink: #2C1810; --muted: #7A6F66;
    --grid: #E8E0D3; --wine: #722F37; --wine-2: #A63D47; --gold: #D4A547;
    --accent: #C9444E;
    --transition: 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  }
  [data-theme="dark"] {
    --paper: #1A1410; --paper-2: #251D18; --ink: #F2EDE4; --muted: #9C9389;
    --grid: #3A2E26; --wine: #C9444E; --wine-2: #A63D47; --gold: #E6C36A;
    --accent: #E6C36A;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; background: var(--paper); color: var(--ink);
    transition: background var(--transition), color var(--transition); }
  body { font-family: 'Manrope', system-ui, sans-serif; font-feature-settings: "tnum"; line-height: 1.5; }
  .wrap { max-width: 1200px; margin: 0 auto; padding: 64px 32px 96px; }

  @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
  .header, .kpis, .controls-bar, .chips, .table-wrap { animation: fadeIn 0.6s both; }
  .kpis { animation-delay: 0.1s; }
  .controls-bar { animation-delay: 0.2s; }
  .chips { animation-delay: 0.3s; }
  .table-wrap { animation-delay: 0.4s; }

  .header { display: flex; justify-content: space-between; align-items: flex-start; gap: 24px; margin-bottom: 48px; }
  .header-text { flex: 1; }
  .eyebrow { text-transform: uppercase; letter-spacing: 0.18em; font-size: 11px; color: var(--wine); font-weight: 600; margin-bottom: 18px; }
  h1 { font-family: 'Fraunces', serif; font-weight: 600; font-size: clamp(40px, 6vw, 76px); line-height: 1.02; margin: 0 0 24px; letter-spacing: -0.02em; }
  h1 em { font-style: italic; color: var(--wine); font-weight: 400; }
  .lede { font-family: 'Fraunces', serif; font-size: 20px; color: var(--muted); max-width: 720px; line-height: 1.5; margin: 0; }
  .theme-toggle { background: none; border: 1px solid var(--ink); width: 44px; height: 44px; border-radius: 50%; cursor: pointer; font-size: 20px; color: var(--ink); display: flex; align-items: center; justify-content: center; flex-shrink: 0; transition: all var(--transition); }
  .theme-toggle:hover { background: var(--paper-2); transform: rotate(15deg); }

  .kpis { display: grid; grid-template-columns: repeat(4, 1fr); border-top: 1px solid var(--ink); border-bottom: 1px solid var(--ink); margin: 0 0 64px; }
  .kpi { padding: 24px 20px; border-right: 1px solid var(--grid); }
  .kpi:last-child { border-right: none; }
  .kpi-value { font-family: 'Fraunces', serif; font-size: 38px; font-weight: 600; line-height: 1; letter-spacing: -0.01em; }
  .kpi-unit { font-family: 'Fraunces', serif; font-size: 20px; color: var(--muted); margin-left: 4px; }
  .kpi-label { margin-top: 10px; font-size: 12px; text-transform: uppercase; letter-spacing: 0.1em; color: var(--muted); }

  .section-title { font-family: 'Fraunces', serif; font-size: 30px; font-weight: 600; margin: 0 0 24px; letter-spacing: -0.01em; }

  .controls-bar { position: sticky; top: 0; z-index: 20; background: var(--paper); padding: 16px 0; margin: 0 -32px 4px; padding-left: 32px; padding-right: 32px; border-bottom: 1px solid var(--grid); transition: background var(--transition); }
  .controls { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; }
  .search { flex: 1; min-width: 220px; position: relative; }
  .search input { width: 100%; padding: 11px 16px 11px 40px; border: 1px solid var(--ink); background: var(--paper); font-family: inherit; font-size: 14px; color: var(--ink); border-radius: 0; outline: none; transition: border-color var(--transition); }
  .search input:focus { border-color: var(--wine); }
  .search::before { content: ""; position: absolute; left: 14px; top: 50%; transform: translateY(-50%); width: 12px; height: 12px; border: 1.5px solid var(--ink); border-radius: 50%; }
  .search::after { content: ""; position: absolute; left: 23px; top: 50%; transform: translateY(1px) rotate(45deg); width: 6px; height: 1.5px; background: var(--ink); }
  .type-toggle { display: inline-flex; border: 1px solid var(--ink); }
  .type-toggle button { background: var(--paper); border: none; padding: 10px 16px; font-family: inherit; font-size: 13px; font-weight: 500; color: var(--ink); cursor: pointer; border-right: 1px solid var(--ink); transition: all var(--transition); }
  .type-toggle button:last-child { border-right: none; }
  .type-toggle button.active { background: var(--ink); color: var(--paper); }
  .export-btn { background: var(--paper); border: 1px solid var(--grid); padding: 10px 14px; font-family: inherit; font-size: 13px; font-weight: 500; color: var(--muted); cursor: pointer; transition: all var(--transition); }
  .export-btn:hover { color: var(--wine); border-color: var(--wine); }

  .chips { display: flex; flex-wrap: wrap; gap: 6px; margin: 20px 0 24px; }
  .chip { border: 1px solid var(--grid); background: var(--paper); padding: 5px 11px; font-size: 12px; font-family: inherit; color: var(--muted); cursor: pointer; font-weight: 500; letter-spacing: 0.04em; transition: all var(--transition); }
  .chip:hover { border-color: var(--ink); color: var(--ink); }
  .chip.active { background: var(--wine); color: var(--paper); border-color: var(--wine); }
  .meta { font-size: 13px; color: var(--muted); margin-bottom: 12px; font-style: italic; }
  .table-wrap { overflow-x: auto; }
  table { width: 100%; border-collapse: collapse; font-size: 14px; }
  thead th { text-align: left; padding: 14px 12px; border-bottom: 1px solid var(--ink); font-weight: 600; font-size: 11px; text-transform: uppercase; letter-spacing: 0.1em; color: var(--muted); cursor: pointer; user-select: none; background: var(--paper); transition: color var(--transition); }
  thead th.sorted { color: var(--ink); }
  thead th .arrow { display: inline-block; margin-left: 4px; opacity: .4; }
  thead th.sorted .arrow { opacity: 1; color: var(--wine); }
  tbody tr { border-bottom: 1px solid var(--grid); transition: background var(--transition); cursor: pointer; }
  tbody tr:hover { background: var(--paper-2); }
  tbody tr.expanded { background: var(--paper-2); }
  tbody td { padding: 13px 12px; vertical-align: middle; }
  tbody tr.detail-row { cursor: default; background: var(--paper-2); }
  tbody tr.detail-row:hover { background: var(--paper-2); }
  .detail-content { padding: 16px 24px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; font-size: 13px; }
  .detail-content > div { line-height: 1.5; }
  .detail-content .label { color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 4px; }
  .detail-content .value { font-family: 'Fraunces', serif; font-weight: 600; }
  .rank { font-family: 'Fraunces', serif; font-style: italic; color: var(--muted); width: 36px; }
  .name { font-weight: 600; }
  .name .group-tag { display: inline-block; margin-left: 8px; padding: 2px 7px; background: var(--paper-2); color: var(--wine); border-radius: 999px; font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
  .place { color: var(--muted); font-size: 13px; }
  .num { text-align: right; font-variant-numeric: tabular-nums; }
  .bar-cell { width: 140px; }
  .bar { height: 8px; background: var(--paper-2); display: flex; overflow: hidden; }
  .bar-r { background: var(--wine); height: 100%; }
  .bar-b { background: var(--gold); height: 100%; }
  .canton-tag { display: inline-block; padding: 2px 8px; background: var(--paper-2); font-weight: 600; font-size: 11px; letter-spacing: 0.05em; }
  .footer { margin-top: 64px; padding-top: 24px; border-top: 1px solid var(--grid); color: var(--muted); font-size: 12px; display: flex; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
  .footer a { color: var(--wine); text-decoration: none; }
  .footer a:hover { text-decoration: underline; }
  @media (max-width: 760px) {
    .kpis { grid-template-columns: repeat(2, 1fr); }
    .kpi { border-right: none; border-bottom: 1px solid var(--grid); }
    .kpi:nth-child(odd) { border-right: 1px solid var(--grid); }
    .kpi:nth-last-child(-n+2) { border-bottom: none; }
    .place, .bar-cell { display: none; }
    thead th.bar-col { display: none; }
    .wrap { padding: 32px 16px 64px; }
    .controls-bar { margin: 0 -16px 4px; padding-left: 16px; padding-right: 16px; }
    .detail-content { grid-template-columns: repeat(2, 1fr); }
  }
</style>
</head>
<body>
<div class="wrap">

  <div class="header">
    <div class="header-text">
      <div class="eyebrow">Données ouvertes · OFAG 2025</div>
      <h1>Le marché suisse du vin <em>importé</em></h1>
      <p class="lede">__LEDE__</p>
    </div>
    <button class="theme-toggle" id="themeToggle" aria-label="Thème">☾</button>
  </div>

  <div class="kpis">__KPIS__</div>

  <h2 class="section-title">Explorer la base</h2>

  <div class="controls-bar">
    <div class="controls">
      <div class="search">
        <input id="q" type="text" placeholder="Rechercher un importateur, une commune…" autocomplete="off">
      </div>
      <div class="type-toggle">
        <button data-type="total" class="active">Total</button>
        <button data-type="rouge">Rouge</button>
        <button data-type="blanc">Blanc</button>
      </div>
      <button class="export-btn" id="exportBtn">⇣ Exporter CSV</button>
    </div>
  </div>

  <div class="chips" id="chips"></div>
  <div class="meta" id="meta"></div>

  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th class="rank">#</th>
          <th data-sort="n">Importateur <span class="arrow">↕</span></th>
          <th>Localité</th>
          <th>Canton</th>
          <th class="num sorted" data-sort="t"><span class="arrow">↓</span> Total (L)</th>
          <th class="num bar-col" data-sort="ratio">Rouge / Blanc <span class="arrow">↕</span></th>
        </tr>
      </thead>
      <tbody id="tbody"></tbody>
    </table>
  </div>

  <div class="footer">
    <div>Source : Office fédéral de l'agriculture (OFAG) · Contingents d'importation 2025.</div>
    <div><a href="../dashboard/dashboard.html">→ Voir le dashboard interactif D3</a></div>
  </div>
</div>

<script>
const DATA = __DATA__;
const CANTON_ORDER = ['ZH','VD','BE','GE','TI','AG','LU','GR','SG','VS','ZG','NE','BL','BS','FR','SZ','SO','TG','FL','SH','NW','JU','AR','OW','UR','GL','AI'];

const state = { search: '', canton: null, type: 'total', sortKey: 't', sortDir: 'desc', expanded: new Set() };
const tbody = document.getElementById('tbody');
const meta = document.getElementById('meta');
const chipsEl = document.getElementById('chips');
const themeBtn = document.getElementById('themeToggle');

themeBtn.addEventListener('click', () => {
  const cur = document.documentElement.getAttribute('data-theme');
  const next = cur === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  themeBtn.textContent = next === 'dark' ? '☀' : '☾';
  try { localStorage.setItem('winestat-theme', next); } catch (e) {}
});
try {
  const saved = localStorage.getItem('winestat-theme');
  if (saved) { document.documentElement.setAttribute('data-theme', saved); themeBtn.textContent = saved === 'dark' ? '☀' : '☾'; }
} catch (e) {}

function renderChips() {
  const counts = {};
  for (const r of DATA) counts[r.c] = (counts[r.c] || 0) + 1;
  const ordered = CANTON_ORDER.filter(c => counts[c]);
  chipsEl.innerHTML = `<button class="chip ${state.canton === null ? 'active' : ''}" data-canton="">Tous les cantons</button>` +
    ordered.map(c => `<button class="chip ${state.canton === c ? 'active' : ''}" data-canton="${c}">${c} · ${counts[c]}</button>`).join('');
  chipsEl.querySelectorAll('.chip').forEach(el => {
    el.addEventListener('click', () => {
      const v = el.dataset.canton;
      state.canton = v === '' ? null : v;
      state.expanded.clear();
      renderChips(); render();
    });
  });
}

function fmt(n) {
  if (n >= 1e6) return (n/1e6).toFixed(1) + ' M';
  if (n >= 1e3) return (n/1e3).toFixed(0) + ' k';
  return n.toFixed(0);
}

function filteredRows() {
  let rows = DATA.filter(r => {
    if (state.canton && r.c !== state.canton) return false;
    if (state.search) {
      const q = state.search.toLowerCase();
      if (!r.n.toLowerCase().includes(q) && !r.co.toLowerCase().includes(q)) return false;
    }
    return true;
  });
  const metric = state.type === 'rouge' ? (r => r.r) : state.type === 'blanc' ? (r => r.b) : (r => r.r + r.b);
  if (state.sortKey === 't') rows.sort((a, b) => metric(b) - metric(a));
  else if (state.sortKey === 'n') rows.sort((a, b) => a.n.localeCompare(b.n, 'fr'));
  else if (state.sortKey === 'ratio') {
    const ratio = r => (r.r + r.b) ? r.r / (r.r + r.b) : 0;
    rows.sort((a, b) => ratio(b) - ratio(a));
  }
  if (state.sortDir === 'asc') rows.reverse();
  return rows;
}

function render() {
  const rows = filteredRows();
  meta.textContent = `${rows.length.toLocaleString('fr-CH')} importateur${rows.length > 1 ? 's' : ''} affiché${rows.length > 1 ? 's' : ''}`
                   + (state.canton ? ` · canton ${state.canton}` : '')
                   + (state.search ? ` · « ${state.search} »` : '');

  const displayed = rows.slice(0, 200);
  const parts = [];
  displayed.forEach((r, i) => {
    const total = r.r + r.b;
    const wr = total ? (r.r / total) * 100 : 0;
    const wb = total ? (r.b / total) * 100 : 0;
    const value = state.type === 'rouge' ? r.r : state.type === 'blanc' ? r.b : total;
    const key = `${r.n}__${r.co}`;
    const isExpanded = state.expanded.has(key);
    parts.push(`
      <tr class="${isExpanded ? 'expanded' : ''}" data-key="${key}">
        <td class="rank">${i + 1}</td>
        <td class="name">${r.n}${r.g ? `<span class="group-tag">${r.g}</span>` : ''}</td>
        <td class="place">${r.co}</td>
        <td><span class="canton-tag">${r.c}</span></td>
        <td class="num">${fmt(value)}</td>
        <td class="bar-cell">
          <div class="bar"><div class="bar-r" style="width:${wr}%"></div><div class="bar-b" style="width:${wb}%"></div></div>
        </td>
      </tr>
    `);
    if (isExpanded) {
      parts.push(`
        <tr class="detail-row"><td colspan="6">
          <div class="detail-content">
            <div><div class="label">Vin rouge</div><div class="value">${r.r.toLocaleString('fr-CH')} L</div></div>
            <div><div class="label">Vin blanc</div><div class="value">${r.b.toLocaleString('fr-CH')} L</div></div>
            <div><div class="label">Total</div><div class="value">${(r.r + r.b).toLocaleString('fr-CH')} L</div></div>
            <div><div class="label">Ratio rouge</div><div class="value">${total ? (r.r/total*100).toFixed(0) : 0}%</div></div>
            <div><div class="label">Commune</div><div class="value">${r.co}</div></div>
            <div><div class="label">Canton</div><div class="value">${r.c}</div></div>
            ${r.g ? `<div><div class="label">Groupe</div><div class="value">${r.g}</div></div>` : ''}
            <div><div class="label">Part du marché</div><div class="value">${((r.r + r.b)/127442489*100).toFixed(2)}%</div></div>
          </div>
        </td></tr>
      `);
    }
  });
  tbody.innerHTML = parts.join('');

  if (rows.length > 200) {
    tbody.innerHTML += `<tr><td colspan="6" style="padding: 24px 12px; text-align: center; color: var(--muted); font-style: italic;">+ ${(rows.length - 200).toLocaleString('fr-CH')} autres lignes — affinez la recherche pour les voir.</td></tr>`;
  }

  tbody.querySelectorAll('tr:not(.detail-row)').forEach(tr => {
    tr.addEventListener('click', () => {
      const key = tr.dataset.key;
      if (!key) return;
      if (state.expanded.has(key)) state.expanded.delete(key);
      else state.expanded.add(key);
      render();
    });
  });
}

document.getElementById('exportBtn').addEventListener('click', () => {
  const rows = filteredRows();
  const header = ['importateur','commune','canton','litres_rouge','litres_blanc','litres_total','groupe'];
  const csv = [header.join(',')].concat(
    rows.map(r => [
      `"${r.n.replace(/"/g, '""')}"`,
      `"${r.co.replace(/"/g, '""')}"`,
      r.c, r.r, r.b, r.r + r.b,
      r.g ? `"${r.g.replace(/"/g, '""')}"` : ''
    ].join(','))
  ).join('\n');
  const blob = new Blob([csv], {type: 'text/csv;charset=utf-8'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `winestat_export_${new Date().toISOString().slice(0,10)}.csv`;
  document.body.appendChild(a); a.click(); document.body.removeChild(a);
  URL.revokeObjectURL(url);
});

document.getElementById('q').addEventListener('input', e => {
  state.search = e.target.value.trim();
  state.expanded.clear();
  render();
});

document.querySelectorAll('.type-toggle button').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.type-toggle button').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    state.type = btn.dataset.type;
    state.sortKey = 't';
    render();
  });
});

document.querySelectorAll('th[data-sort]').forEach(th => {
  th.addEventListener('click', () => {
    const key = th.dataset.sort;
    if (state.sortKey === key) state.sortDir = state.sortDir === 'desc' ? 'asc' : 'desc';
    else { state.sortKey = key; state.sortDir = 'desc'; }
    document.querySelectorAll('th[data-sort]').forEach(t => {
      t.classList.toggle('sorted', t.dataset.sort === state.sortKey);
      const arrow = t.querySelector('.arrow');
      if (arrow) arrow.textContent = t.dataset.sort === state.sortKey ? (state.sortDir === 'desc' ? '↓' : '↑') : '↕';
    });
    render();
  });
});

renderChips(); render();
</script>
</body>
</html>
"""


def main():
    df = pd.read_csv("data/processed/importateurs.csv")
    records = [{
        "n": r.importateur,
        "c": r.canton,
        "co": r.commune,
        "r": int(r.litres_rouge),
        "b": int(r.litres_blanc),
        "g": r.groupe if isinstance(r.groupe, str) else None,
    } for r in df.itertuples()]

    out_dir = Path("assets/interactive")
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "data.json").write_text(
        json.dumps(records, separators=(",", ":"), ensure_ascii=False)
    )

    canton_agg = (df.groupby("canton")
                    .agg(total=("litres_total", "sum"),
                         rouge=("litres_rouge", "sum"),
                         blanc=("litres_blanc", "sum"),
                         n=("importateur", "count"))
                    .reset_index()
                    .sort_values("total", ascending=False)
                    .to_dict("records"))
    (out_dir / "cantons.json").write_text(
        json.dumps(canton_agg, separators=(",", ":"))
    )

    total_l = df["litres_total"].sum()
    total_r = df["litres_rouge"].sum()
    n = len(df)
    sorted_t = df["litres_total"].sort_values(ascending=False)
    top2_share = sorted_t.head(2).sum() / total_l * 100

    kpis_html = f"""
    <div class="kpi"><div><span class="kpi-value">{n:,}</span></div>
      <div class="kpi-label">Importateurs actifs</div></div>
    <div class="kpi"><div><span class="kpi-value">{total_l/1e6:.0f}</span><span class="kpi-unit">M L</span></div>
      <div class="kpi-label">Volume total contingenté</div></div>
    <div class="kpi"><div><span class="kpi-value">{top2_share:.0f}</span><span class="kpi-unit">%</span></div>
      <div class="kpi-label">Part des 2 premiers</div></div>
    <div class="kpi"><div><span class="kpi-value">{total_r/total_l*100:.0f}</span><span class="kpi-unit">% rouge</span></div>
      <div class="kpi-label">Rouge vs blanc</div></div>
    """.replace(",", " ")

    lede = (f"{n:,} importateurs, {total_l/1e6:.0f} millions de litres, "
            "des géants qui pèsent la moitié du marché à eux deux. "
            "Explorez la base entière.").replace(",", " ")

    html = (HTML_TEMPLATE
            .replace("__DATA__", json.dumps(records, separators=(",", ":"), ensure_ascii=False))
            .replace("__KPIS__", kpis_html)
            .replace("__LEDE__", lede))

    (out_dir / "explorer.html").write_text(html)

    print(f"✓ {out_dir}/explorer.html ({(out_dir/'explorer.html').stat().st_size/1024:.0f} KB)")
    print(f"✓ {out_dir}/data.json    ({(out_dir/'data.json').stat().st_size/1024:.0f} KB)")
    print(f"✓ {out_dir}/cantons.json")


if __name__ == "__main__":
    main()
