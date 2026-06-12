"""Generate a static, decision-ready portfolio report from the mock event data."""

from __future__ import annotations

from datetime import date
from html import escape
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import load_events


REPORT_DIR = PROJECT_ROOT / "reports"
ASSET_DIR = REPORT_DIR / "assets"
DATA_PATH = PROJECT_ROOT / "data" / "mock_events.csv"

CANVAS = "#F7F4EF"
PAPER = "#FFFFFF"
INK = "#17212B"
MUTED = "#5F6B76"
GRID = "#DDE3E8"
BLUE = "#2F6690"
TEAL = "#3A7D78"
AMBER = "#D99A2B"
RED = "#B5413C"
GREEN = "#56876D"
LOW = "#8CA6A3"

RISK_COLORS = {
    "Critical": RED,
    "High": AMBER,
    "Medium": BLUE,
    "Low": LOW,
}


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Load a readable system font with a portable fallback."""
    candidates = [
        (
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
            if bold
            else "/System/Library/Fonts/Supplemental/Arial.ttf"
        ),
        (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            if bold
            else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        ),
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def chart_canvas(title: str, subtitle: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (1600, 900), CANVAS)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((35, 35, 1565, 865), radius=24, fill=PAPER)
    title_size = 50
    if len(title) > 55:
        title_size = 44
    if len(title) > 70:
        title_size = 40
    draw.text((95, 80), title, fill=INK, font=font(title_size, bold=True))
    draw.text((95, 145), subtitle, fill=MUTED, font=font(25))
    return image, draw


def draw_source_note(draw: ImageDraw.ImageDraw, text: str) -> None:
    draw.text((95, 815), text, fill=MUTED, font=font(19))


def save_horizontal_bars(
    labels: list[str],
    values: list[float],
    colors: list[str],
    title: str,
    subtitle: str,
    output_path: Path,
    annotations: list[str] | None = None,
) -> None:
    image, draw = chart_canvas(title, subtitle)
    left, right = 470, 1460
    top, bottom = 225, 760
    row_height = (bottom - top) / max(len(labels), 1)
    max_value = max(values) if values else 1

    for index, (label, value, color) in enumerate(zip(labels, values, colors)):
        center_y = top + row_height * index + row_height / 2
        bar_height = min(48, row_height * 0.55)
        bar_top = center_y - bar_height / 2
        bar_bottom = center_y + bar_height / 2
        bar_width = (right - left) * (value / max_value)

        draw.text(
            (95, center_y - 16),
            label,
            fill=INK,
            font=font(27, bold=index < 3),
        )
        draw.rounded_rectangle(
            (left, bar_top, right, bar_bottom),
            radius=10,
            fill="#EEF1F3",
        )
        draw.rounded_rectangle(
            (left, bar_top, left + bar_width, bar_bottom),
            radius=10,
            fill=color,
        )
        label_text = annotations[index] if annotations else f"{value:g}"
        value_font = font(24, bold=True)
        text_width = draw.textbbox((0, 0), label_text, font=value_font)[2]
        text_x = left + bar_width + 18
        if text_x + text_width > right:
            text_x = left + bar_width - text_width - 18
            text_color = PAPER
        else:
            text_color = INK
        draw.text(
            (text_x, center_y - 15),
            label_text,
            fill=text_color,
            font=value_font,
        )

    draw_source_note(draw, "Source: fictional mock_events.csv; scores calculated by project logic.")
    image.save(output_path, quality=95)


def save_factor_profile(all_means, critical_means, output_path: Path) -> None:
    image, draw = chart_canvas(
        "Critical events are hardest to replace and most disruptive",
        "Average factor rating on the 1-to-5 scale: full portfolio versus Critical events",
    )
    labels = [
        "Severity",
        "Probability",
        "Time sensitivity",
        "Substitution difficulty",
        "Production impact",
    ]
    fields = [
        "severity",
        "probability",
        "time_sensitivity",
        "substitution_difficulty",
        "production_impact",
    ]
    left, right = 520, 1450
    top = 235
    row_height = 103

    for index, (label, field) in enumerate(zip(labels, fields)):
        y = top + index * row_height
        draw.text((95, y + 19), label, fill=INK, font=font(26, bold=index >= 3))
        draw.line((left, y + 58, right, y + 58), fill=GRID, width=2)

        full_width = (right - left) * float(all_means[field]) / 5
        critical_width = (right - left) * float(critical_means[field]) / 5
        draw.rounded_rectangle(
            (left, y + 10, left + full_width, y + 34),
            radius=7,
            fill=BLUE,
        )
        draw.rounded_rectangle(
            (left, y + 43, left + critical_width, y + 67),
            radius=7,
            fill=RED,
        )
        full_text = f"{all_means[field]:.2f}"
        full_font = font(20, bold=True)
        full_text_width = draw.textbbox((0, 0), full_text, font=full_font)[2]
        full_endpoint = left + full_width
        full_x = full_endpoint + 12
        full_color = BLUE
        if full_x + full_text_width > right:
            full_x = full_endpoint - full_text_width - 12
            full_color = PAPER
        draw.text(
            (full_x, y + 7),
            full_text,
            fill=full_color,
            font=full_font,
        )
        critical_text = f"{critical_means[field]:.2f}"
        critical_font = font(20, bold=True)
        critical_text_width = draw.textbbox(
            (0, 0), critical_text, font=critical_font
        )[2]
        critical_endpoint = left + critical_width
        critical_text_x = critical_endpoint + 12
        critical_color = RED
        if critical_text_x + critical_text_width > right:
            critical_text_x = critical_endpoint - critical_text_width - 12
            critical_color = PAPER
        draw.text(
            (critical_text_x, y + 40),
            critical_text,
            fill=critical_color,
            font=critical_font,
        )

    draw.rectangle((1040, 765, 1070, 785), fill=BLUE)
    draw.text((1080, 761), "All events", fill=MUTED, font=font(20))
    draw.rectangle((1240, 765, 1270, 785), fill=RED)
    draw.text((1280, 761), "Critical", fill=MUTED, font=font(20))
    draw_source_note(draw, "Source: fictional mock_events.csv; unweighted factor averages.")
    image.save(output_path, quality=95)


def metric_card(label: str, value: str, detail: str) -> str:
    return (
        '<div class="metric-card">'
        f'<div class="metric-label">{escape(label)}</div>'
        f'<div class="metric-value">{escape(value)}</div>'
        f'<div class="metric-detail">{escape(detail)}</div>'
        "</div>"
    )


def generate_report() -> Path:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    events = load_events(DATA_PATH)
    elevated = events[events["risk_level"].isin(["High", "Critical"])]
    critical = events[events["risk_level"] == "Critical"]

    level_order = ["Critical", "High", "Medium", "Low"]
    level_counts = events["risk_level"].value_counts().reindex(level_order).fillna(0)
    save_horizontal_bars(
        level_order,
        level_counts.astype(float).tolist(),
        [RISK_COLORS[level] for level in level_order],
        "More than three quarters of events are elevated",
        "Event count by risk band; High and Critical are the operational alert population",
        ASSET_DIR / "risk_level_mix.png",
        [f"{int(value)} events" for value in level_counts],
    )

    region_counts = elevated.groupby("region").size().sort_values(ascending=False)
    save_horizontal_bars(
        region_counts.index.tolist(),
        region_counts.astype(float).tolist(),
        [RED if index < 2 else BLUE for index in range(len(region_counts))],
        "East Asia and Europe carry the largest alert load",
        "High and Critical event count by region",
        ASSET_DIR / "elevated_by_region.png",
        [f"{int(value)} elevated" for value in region_counts],
    )

    component_summary = (
        events.groupby("affected_component")
        .agg(
            cumulative_score=("total_risk_score", "sum"),
            critical=("risk_level", lambda values: (values == "Critical").sum()),
        )
        .sort_values(["cumulative_score", "critical"], ascending=False)
        .head(10)
    )
    save_horizontal_bars(
        component_summary.index.tolist(),
        component_summary["cumulative_score"].astype(float).tolist(),
        [
            RED if critical_count > 0 else TEAL
            for critical_count in component_summary["critical"]
        ],
        "Component exposure combines breadth and acute bottlenecks",
        "Cumulative risk score by component; red bars include at least one Critical event",
        ASSET_DIR / "component_exposure.png",
        [
            f"{int(row.cumulative_score)} | {int(row.critical)} critical"
            for row in component_summary.itertuples()
        ],
    )

    factor_fields = [
        "severity",
        "probability",
        "time_sensitivity",
        "substitution_difficulty",
        "production_impact",
    ]
    all_means = events[factor_fields].mean()
    critical_means = critical[factor_fields].mean()
    save_factor_profile(
        all_means,
        critical_means,
        ASSET_DIR / "critical_factor_profile.png",
    )

    elevated_share = len(elevated) / len(events)
    top_two_regions = int(region_counts.iloc[:2].sum())
    top_two_share = top_two_regions / len(elevated)
    constrained_critical = critical[
        critical["affected_component"].isin(["Semiconductors", "Rare Earth Magnets"])
    ]

    critical_rows = []
    for row in critical.sort_values(
        ["total_risk_score", "date"], ascending=[False, False]
    ).itertuples():
        critical_rows.append(
            "<tr>"
            f"<td><strong>{escape(row.event_id)}</strong><br>"
            f'<span class="small">{row.date:%b %d, %Y}</span></td>'
            f"<td>{escape(row.event_title)}</td>"
            f"<td>{escape(row.region)} / {escape(row.country)}</td>"
            f"<td>{escape(row.affected_component)}<br>"
            f'<span class="small">{escape(row.risk_type)}</span></td>'
            f'<td><span class="score critical">{int(row.total_risk_score)}</span></td>'
            "</tr>"
        )

    report_date = date.today().strftime("%B %d, %Y")
    cards = "".join(
        [
            metric_card(
                "Elevated events",
                f"{len(elevated)} / {len(events)}",
                f"{elevated_share:.0%} are High or Critical",
            ),
            metric_card(
                "Critical events",
                str(len(critical)),
                "Immediate cross-functional escalation",
            ),
            metric_card(
                "Average score",
                f"{events['total_risk_score'].mean():.1f} / 25",
                "Portfolio-wide unweighted average",
            ),
            metric_card(
                "Exposed regions",
                str(events["region"].nunique()),
                "Across the full fictional portfolio",
            ),
        ]
    )

    report_html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Automotive Supply Chain Risk Portfolio Report</title>
  <style>
    :root {{
      --canvas: {CANVAS};
      --paper: {PAPER};
      --ink: {INK};
      --muted: {MUTED};
      --line: {GRID};
      --blue: {BLUE};
      --teal: {TEAL};
      --amber: {AMBER};
      --red: {RED};
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--canvas);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
        "Segoe UI", sans-serif;
    }}
    main {{ max-width: 1040px; margin: 0 auto; padding: 56px 24px 88px; }}
    header, section {{ margin-bottom: 44px; }}
    h1 {{ max-width: 900px; margin: 0 0 14px; font-size: clamp(2.35rem, 6vw, 4.6rem);
      letter-spacing: -0.055em; line-height: 0.98; }}
    h2 {{ margin: 0 0 14px; font-size: 1.75rem; letter-spacing: -0.025em; }}
    h3 {{ margin: 30px 0 10px; font-size: 1.18rem; }}
    p, li {{ line-height: 1.68; }}
    .eyebrow {{ color: var(--red); font-weight: 800; letter-spacing: 0.12em;
      text-transform: uppercase; font-size: 0.77rem; }}
    .dek {{ max-width: 760px; color: var(--muted); font-size: 1.14rem; }}
    .small {{ color: var(--muted); font-size: 0.82rem; }}
    .executive-summary-box {{
      padding: 26px 30px;
      background: linear-gradient(145deg, #fff 0%, #f1ece4 100%);
      border: 1px solid #ded6cb;
      border-radius: 20px;
      box-shadow: 0 18px 38px rgba(23, 33, 43, 0.07);
    }}
    .executive-summary-box ul {{ margin: 0; padding-left: 22px; }}
    .executive-summary-box li + li {{ margin-top: 12px; }}
    .metric-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin-top: 20px;
    }}
    .metric-card {{ padding: 19px; background: var(--paper); border: 1px solid var(--line);
      border-radius: 16px; }}
    .metric-label {{ color: var(--muted); font-size: 0.79rem; font-weight: 750;
      text-transform: uppercase; letter-spacing: 0.07em; }}
    .metric-value {{ margin: 8px 0 5px; font-size: 1.8rem; font-weight: 850;
      letter-spacing: -0.04em; }}
    .metric-detail {{ color: var(--muted); font-size: 0.82rem; line-height: 1.35; }}
    .finding {{ padding-top: 10px; }}
    figure {{ margin: 22px 0 12px; }}
    figure img {{ display: block; width: 100%; border-radius: 18px;
      box-shadow: 0 12px 30px rgba(23, 33, 43, 0.08); }}
    figcaption {{ margin-top: 9px; color: var(--muted); font-size: 0.82rem; }}
    .callout {{ padding: 20px 22px; background: #eee8df; border-left: 5px solid var(--amber);
      border-radius: 14px; }}
    .actions {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }}
    .action {{ padding: 21px; background: var(--paper); border: 1px solid var(--line);
      border-radius: 16px; }}
    .action-number {{ color: var(--red); font-weight: 850; font-size: 0.78rem;
      letter-spacing: 0.08em; }}
    .action h3 {{ margin-top: 8px; }}
    table {{ width: 100%; border-collapse: collapse; background: var(--paper);
      border: 1px solid var(--line); border-radius: 14px; overflow: hidden; }}
    th, td {{ padding: 14px 12px; text-align: left; border-bottom: 1px solid var(--line);
      vertical-align: top; font-size: 0.9rem; }}
    th {{ color: var(--muted); text-transform: uppercase; letter-spacing: 0.06em;
      font-size: 0.72rem; }}
    tr:last-child td {{ border-bottom: 0; }}
    .score {{ display: inline-flex; min-width: 38px; justify-content: center; padding: 5px 8px;
      border-radius: 999px; color: #fff; font-weight: 850; }}
    .critical {{ background: var(--red); }}
    .questions li + li {{ margin-top: 8px; }}
    footer {{ padding-top: 22px; border-top: 1px solid var(--line); color: var(--muted);
      font-size: 0.82rem; }}
    a {{ color: var(--blue); }}
    @media (max-width: 800px) {{
      .metric-grid {{ grid-template-columns: repeat(2, 1fr); }}
      .actions {{ grid-template-columns: 1fr; }}
      table {{ display: block; overflow-x: auto; }}
      main {{ padding-top: 34px; }}
    }}
    @media print {{
      body {{ background: #fff; }}
      main {{ max-width: none; padding: 18px; }}
      figure img, .executive-summary-box {{ box-shadow: none; }}
      section, figure {{ break-inside: avoid; }}
    }}
  </style>
</head>
<body>
  <main data-report-audience="automotive supply chain and operations stakeholders">
    <header data-contract-section="title">
      <div class="eyebrow">Decision-ready portfolio review</div>
      <h1>Where automotive operations should focus next</h1>
      <p class="dek">A prioritized view of the fictional supply chain risk portfolio in
      the Automotive Supply Chain Risk Intelligence Control Tower. Generated
      {escape(report_date)} from 30 mock events dated January 8 through June 10, 2026.</p>
    </header>

    <section class="executive-summary-box" data-contract-section="executive-summary">
      <h2>Executive Summary</h2>
      <ul>
        <li><strong>The portfolio requires active intervention:</strong>
        {len(elevated)} of {len(events)} events ({elevated_share:.0%}) are High or
        Critical, including {len(critical)} events requiring immediate escalation.</li>
        <li><strong>The alert workload is geographically concentrated:</strong>
        East Asia and Europe each carry seven elevated events, together representing
        {top_two_regions} of {len(elevated)} alerts ({top_two_share:.0%}).</li>
        <li><strong>The most acute bottlenecks are hard to substitute:</strong>
        semiconductor and rare-earth magnet events account for
        {len(constrained_critical)} of {len(critical)} Critical events, while every
        Critical event averages 5.0 for both substitution difficulty and production
        impact.</li>
      </ul>
      <div class="metric-grid">{cards}</div>
    </section>

    <section data-contract-section="key-findings">
      <h2>Key Findings</h2>

      <div class="finding">
        <h3>1. Elevated risk is the portfolio norm, not the exception</h3>
        <p>High and Critical events make up {elevated_share:.0%} of the current event
        set. That means the operating challenge is not simply identifying alerts; it is
        imposing a consistent triage cadence so the seven Critical events receive
        immediate attention without allowing the 16 High events to age unnoticed.</p>
        <figure>
          <img src="assets/risk_level_mix.png" alt="Risk level mix chart">
          <figcaption>Risk bands follow the documented 5-to-25 additive scoring model.</figcaption>
        </figure>
        <p>The average score is {events['total_risk_score'].mean():.1f}, already inside
        the High band. A daily review should therefore manage a queue of exposure,
        ownership, and recovery milestones rather than treat each alert as a standalone
        exception.</p>
      </div>

      <div class="finding">
        <h3>2. East Asia and Europe should have dedicated response workstreams</h3>
        <p>East Asia and Europe each contribute seven elevated events. North America is
        the next-largest cluster with five, while the remaining regions account for
        four elevated events combined.</p>
        <figure>
          <img src="assets/elevated_by_region.png" alt="Elevated events by region chart">
          <figcaption>Regional exposure counts High and Critical events only.</figcaption>
        </figure>
        <p>The geographic pattern supports separate workstreams: one focused on East
        Asian electronics, magnets, and trade exposure; another on European industrial
        capacity, quality, and labor continuity. Regional count alone does not estimate
        production loss, so these workstreams still need plant and inventory context.</p>
      </div>

      <div class="finding">
        <h3>3. Broad component exposure and acute bottlenecks are different problems</h3>
        <p>Steel has the highest cumulative score because it appears in three events, but
        none is Critical. Semiconductors and rare-earth magnets each have two Critical
        events, signaling a sharper short-term continuity risk despite fewer total
        records.</p>
        <figure>
          <img src="assets/component_exposure.png" alt="Component risk exposure chart">
          <figcaption>Cumulative score is a component exposure proxy, not supplier or
          revenue exposure.</figcaption>
        </figure>
        <p>Operations should keep steel in the broader monitoring queue while assigning
        immediate engineering and sourcing actions to semiconductors, magnets, electric
        motors, aluminum castings, and brake systems, which contain the current Critical
        events.</p>
      </div>

      <div class="finding">
        <h3>4. Critical risk is driven by constrained alternatives and direct output impact</h3>
        <p>Across Critical events, substitution difficulty and production impact both
        average the maximum 5.0 rating. Time sensitivity averages
        {critical_means['time_sensitivity']:.2f}, reinforcing that these are near-term
        continuity decisions rather than ordinary supplier-performance issues.</p>
        <figure>
          <img src="assets/critical_factor_profile.png" alt="Risk factor comparison chart">
          <figcaption>Factor averages use the original analyst-entered 1-to-5 ratings.</figcaption>
        </figure>
        <p>The response should pair commercial escalation with engineering validation.
        Capacity reservations alone will not resolve a part that cannot be substituted
        or qualified inside the disruption window.</p>
      </div>
    </section>

    <section>
      <h2>Critical Event Queue</h2>
      <p>These seven events should be reviewed first, ordered by total score and then
      event date. The project recommendation engine assigns each one same-day
      cross-functional escalation.</p>
      <table>
        <thead><tr><th>Event</th><th>Signal</th><th>Location</th><th>Exposure</th><th>Score</th></tr></thead>
        <tbody>{''.join(critical_rows)}</tbody>
      </table>
    </section>

    <section data-contract-section="recommended-next-steps">
      <h2>Recommended Next Steps</h2>
      <div class="actions">
        <div class="action">
          <div class="action-number">0-24 HOURS</div>
          <h3>Open one Critical-event response room</h3>
          <p>Assign an executive owner and functional lead to each of the seven Critical
          events. Record inventory coverage, next production impact, supplier recovery
          date, and the next irreversible decision.</p>
        </div>
        <div class="action">
          <div class="action-number">24-72 HOURS</div>
          <h3>Run regional and component mitigation tracks</h3>
          <p>Separate East Asia and Europe workstreams. Prioritize semiconductor
          allocation, rare-earth magnet alternatives, motor continuity, casting tooling,
          and brake-system containment using the rule-based action library.</p>
        </div>
        <div class="action">
          <div class="action-number">NEXT 2 WEEKS</div>
          <h3>Add operational exposure data</h3>
          <p>Link events to suppliers, sites, part numbers, plants, vehicle programs,
          inventory days, and production volume. These fields are necessary to convert
          event priority into units or revenue at risk.</p>
        </div>
      </div>
    </section>

    <section data-contract-section="further-questions">
      <h2>Further Questions</h2>
      <ul class="questions">
        <li>Which Critical events have less inventory coverage than the credible supplier
        recovery time?</li>
        <li>Do the semiconductor and magnet events affect the same vehicle programs,
        creating correlated exposure?</li>
        <li>Which alternate parts or suppliers are already approved, and which require
        engineering validation or homologation?</li>
        <li>Should factor weights differ for safety-critical components, launch programs,
        or single-source suppliers?</li>
      </ul>
    </section>

    <section data-contract-section="caveats-and-assumptions">
      <h2>Caveats and Assumptions</h2>
      <div class="callout">
        <p><strong>This is a fictional portfolio demonstration, not live operational
        intelligence.</strong> Ratings are manual and equally weighted. Events are
        evaluated independently, and the data has no supplier master, tier, plant,
        inventory, cost, recovery-time, vehicle-program, or revenue fields. Component
        cumulative score is therefore a prioritization proxy, not a forecast of business
        impact.</p>
      </div>
    </section>

    <footer>
      <p>Prepared from <code>data/mock_events.csv</code> using
      <code>src/data_loader.py</code>, <code>src/scoring.py</code>,
      <code>src/classification.py</code>, and <code>src/recommendations.py</code>.
      Audit notes are documented in <a href="source_notes.md">source_notes.md</a>.</p>
    </footer>
  </main>
</body>
</html>
"""

    output_path = REPORT_DIR / "automotive_risk_portfolio_report.html"
    output_path.write_text(report_html, encoding="utf-8")
    return output_path


if __name__ == "__main__":
    path = generate_report()
    print(path)
