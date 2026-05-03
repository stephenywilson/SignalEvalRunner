import json
import dataclasses
from pathlib import Path
from typing import Optional

from .builder import BoardRow


# ── Helpers ────────────────────────────────────────────────────────────────────

def _pct(v: Optional[float]) -> str:
    if v is None:
        return "—"
    return f"{v * 100:.1f}%"


def _score_class(v: Optional[float]) -> str:
    if v is None:
        return ""
    if v >= 0.80:
        return ' class="score-high"'
    if v >= 0.60:
        return ' class="score-mid"'
    return ' class="score-low"'


def _rank_badge(rank: int) -> str:
    if rank == 1:
        return '<span class="rank-1">1</span>'
    if rank == 2:
        return '<span class="rank-2">2</span>'
    if rank == 3:
        return '<span class="rank-3">3</span>'
    return str(rank)


def _esc(s: str) -> str:
    """Minimal HTML escaping for text content."""
    return (s
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


# ── CSS ────────────────────────────────────────────────────────────────────────

def render_css() -> str:
    return """\
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background: #0d1117;
  color: #c9d1d9;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  font-size: 15px;
  line-height: 1.6;
  padding: 32px 16px 64px;
}

.container { max-width: 1280px; margin: 0 auto; }

/* ── Header ──────────────────────────────────── */
header { margin-bottom: 32px; border-bottom: 1px solid #30363d; padding-bottom: 24px; }
header h1 { font-size: 2rem; font-weight: 700; color: #e6edf3; margin-bottom: 6px; }
header .subtitle { font-size: 1rem; color: #8b949e; margin-bottom: 10px; }
header .disclaimer {
  display: inline-block;
  font-size: 0.8rem;
  color: #8b949e;
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 6px;
  padding: 4px 10px;
}

/* ── Table ───────────────────────────────────── */
.table-wrap { overflow-x: auto; margin-bottom: 40px; }

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
  min-width: 900px;
}

thead th {
  background: #161b22;
  color: #8b949e;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: 0.75rem;
  padding: 10px 14px;
  text-align: left;
  border-bottom: 1px solid #30363d;
  white-space: nowrap;
}

tbody tr { border-bottom: 1px solid #21262d; }
tbody tr:hover { background: #161b22; }

td {
  padding: 10px 14px;
  color: #c9d1d9;
  white-space: nowrap;
}

td.score-high { color: #3fb950; font-weight: 600; }
td.score-mid  { color: #e3b341; }
td.score-low  { color: #f85149; }

/* Rank badges */
.rank-1, .rank-2, .rank-3 {
  display: inline-block;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  text-align: center;
  line-height: 24px;
  font-weight: 700;
  font-size: 0.8rem;
}
.rank-1 { background: #b8860b; color: #fff; }
.rank-2 { background: #6e7681; color: #fff; }
.rank-3 { background: #7b3f00; color: #fff; }

/* ── About ───────────────────────────────────── */
.about {
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 8px;
  padding: 24px 28px;
  margin-bottom: 40px;
}
.about h2 { font-size: 1.1rem; color: #e6edf3; margin-bottom: 10px; }
.about p  { color: #8b949e; font-size: 0.9rem; }

/* ── Footer ──────────────────────────────────── */
footer {
  border-top: 1px solid #21262d;
  padding-top: 20px;
  font-size: 0.8rem;
  color: #6e7681;
}
"""


# ── HTML ───────────────────────────────────────────────────────────────────────

def _render_row(row: BoardRow) -> str:
    cols = [
        f"<td>{_rank_badge(row.rank)}</td>",
        f"<td><strong>{_esc(row.model)}</strong></td>",
        f"<td>{_esc(row.provider)}</td>",
        f"<td>{_esc(row.dataset)}</td>",
        f"<td{_score_class(row.overall)}>{_pct(row.overall)}</td>",
        f"<td{_score_class(row.direction_accuracy)}>{_pct(row.direction_accuracy)}</td>",
        f"<td{_score_class(row.event_type_accuracy)}>{_pct(row.event_type_accuracy)}</td>",
        f"<td{_score_class(row.asset_match)}>{_pct(row.asset_match)}</td>",
        f"<td{_score_class(row.time_horizon_match)}>{_pct(row.time_horizon_match)}</td>",
        f"<td{_score_class(row.reasoning_quality)}>{_pct(row.reasoning_quality)}</td>",
        f"<td>{row.total if row.total is not None else '—'}</td>",
        f"<td>{_esc(row.created_at)}</td>",
    ]
    return "    <tr>\n      " + "\n      ".join(cols) + "\n    </tr>"


def render_html(rows: list[BoardRow], generated_at: str) -> str:
    tbody = "\n".join(_render_row(r) for r in rows)
    count_label = f"{len(rows)} run{'s' if len(rows) != 1 else ''}"

    return f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SignalEvalRunner Board</title>
  <link rel="stylesheet" href="assets/style.css">
</head>
<body>
<div class="container">

  <header>
    <h1>SignalEvalRunner Board</h1>
    <p class="subtitle">Static leaderboard for financial news-to-signal model evaluation.</p>
    <p class="disclaimer">Research only. Not financial advice. No trading execution.</p>
  </header>

  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Rank</th>
          <th>Model</th>
          <th>Provider</th>
          <th>Dataset</th>
          <th>Overall</th>
          <th>Direction</th>
          <th>Event Type</th>
          <th>Asset Match</th>
          <th>Time Horizon</th>
          <th>Reasoning</th>
          <th>Examples</th>
          <th>Generated At</th>
        </tr>
      </thead>
      <tbody>
{tbody}
      </tbody>
    </table>
  </div>

  <section class="about">
    <h2>About</h2>
    <p>
      SignalEvalRunner evaluates whether models can convert market-moving news into structured
      signal predictions. The board is generated from local evaluation result files and does
      not call any model provider. All scores reflect evaluation on the configured dataset only.
    </p>
  </section>

  <footer>
    <p>Generated by <strong>SignalEvalRunner</strong> &mdash; {count_label} &mdash; {generated_at}</p>
  </footer>

</div>
</body>
</html>
"""


# ── JSON ───────────────────────────────────────────────────────────────────────

def render_json(rows: list[BoardRow], generated_at: str) -> str:
    data = {
        "generated_at": generated_at,
        "count": len(rows),
        "rows": [dataclasses.asdict(r) for r in rows],
    }
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


# ── Writer ─────────────────────────────────────────────────────────────────────

def write_site(rows: list[BoardRow], output_dir: Path, generated_at: str) -> None:
    """Write index.html, assets/style.css, and data/leaderboard.json to output_dir."""
    out = Path(output_dir)
    (out / "assets").mkdir(parents=True, exist_ok=True)
    (out / "data").mkdir(parents=True, exist_ok=True)

    (out / "index.html").write_text(render_html(rows, generated_at), encoding="utf-8")
    (out / "assets" / "style.css").write_text(render_css(), encoding="utf-8")
    (out / "data" / "leaderboard.json").write_text(render_json(rows, generated_at), encoding="utf-8")
