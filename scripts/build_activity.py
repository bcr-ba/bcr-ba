"""Draw the contribution graph as an isometric 3D calendar in the profile's own style.

Reads the public contribution calendar (no token needed), so it runs the same
locally and in the daily workflow:

    python scripts/build_activity.py [--user bcr-ba] [--out dist]
"""

import argparse
import re
import urllib.request
from datetime import date, timedelta
from pathlib import Path
from xml.sax.saxutils import escape

from build_assets import MONO, SANS, THEMES, frame

# Projection: one week steps right and slightly down, one weekday steps down-left.
U = (10.9, 1.9)
V = (-7.0, 7.4)
FILL = 0.84          # share of a cell the bar occupies
MAX_H = 72           # bar height for the busiest day, in px
ORIGIN = (118, 160)    # screen position of the first cell (week 0, Sunday)

# Most of my work lives in private repos, so the graph should not read as "Python only".
LANGUAGES = "PYTHON · TYPESCRIPT · JAVA · SQL"


def fetch(user):
    req = urllib.request.Request(
        f"https://github.com/users/{user}/contributions", headers={"User-Agent": "profile-activity"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        html = r.read().decode("utf-8")
    cells = re.findall(r'data-date="([\d-]+)" id="(contribution-day-component-[\d-]+)" data-level="(\d)"', html)
    tips = dict(re.findall(r'for="(contribution-day-component-[\d-]+)"[^>]*>([^<]*)</tool-tip>', html))
    if not cells:
        raise SystemExit("contribution calendar markup changed; nothing parsed")
    days = {}
    for d, cid, level in cells:
        m = re.match(r"(\d+) contribution", tips.get(cid, ""))
        days[date.fromisoformat(d)] = (int(m.group(1)) if m else 0, int(level))
    return days


def stats(days):
    ordered = sorted(days)
    total = sum(c for c, _ in days.values())
    active = sum(1 for c, _ in days.values() if c)
    longest = run = 0
    for d in ordered:
        run = run + 1 if days[d][0] else 0
        longest = max(longest, run)
    current = 0
    for d in reversed(ordered):
        if days[d][0]:
            current += 1
        elif d != ordered[-1]:  # today may still be empty
            break
    best = max(ordered, key=lambda d: days[d][0])
    return total, active, current, longest, best


def mix(a, b, k):
    a, b = a.lstrip("#"), b.lstrip("#")
    return "#" + "".join(f"{round(int(a[i:i + 2], 16) * (1 - k) + int(b[i:i + 2], 16) * k):02X}" for i in (0, 2, 4))


def palette(t, dark):
    """Top colour per contribution level; level 0 is a flat tile."""
    base = t["node"] if dark else "#E9EFF5"
    return [base, mix(t["line"], base, 0.55), t["line"], mix(t["accent"], base, 0.4), t["accent"]]


def pt(x, y):
    return f"{x:.1f},{y:.1f}"


def render(days, t, dark, user):
    w, h = 1000, 400
    ordered = sorted(days)
    start = ordered[0] - timedelta(days=(ordered[0].weekday() + 1) % 7)  # back to Sunday
    counts = sorted(c for c, _ in days.values() if c)
    cap = counts[int(len(counts) * 0.95) - 1] if counts else 1
    tops = palette(t, dark)
    shade_l, shade_r = (0.35, 0.55) if dark else (0.18, 0.32)
    ink = "#000000" if dark else t["text"]

    cells = []
    for d in ordered:
        wk, wd = (d - start).days // 7, (d - start).days % 7
        cells.append((wk, wd, d, *days[d]))
    cells.sort(key=lambda c: c[0] * U[1] + c[1] * V[1])  # painter's order, far to near

    ux, uy = U[0] * FILL, U[1] * FILL
    vx, vy = V[0] * FILL, V[1] * FILL
    bars = []
    for wk, wd, d, count, level in cells:
        x = ORIGIN[0] + wk * U[0] + wd * V[0]
        y = ORIGIN[1] + wk * U[1] + wd * V[1]
        top = tops[min(level, 4)]
        if not count:
            bars.append(f'<path d="M{pt(x, y)}L{pt(x + ux, y + uy)}L{pt(x + ux + vx, y + uy + vy)}L{pt(x + vx, y + vy)}Z" fill="{top}"/>')
            continue
        bh = 4 + min(count, cap) / cap * (MAX_H - 4)
        a, b, c, e = (x, y), (x + ux, y + uy), (x + ux + vx, y + uy + vy), (x + vx, y + vy)
        lift = lambda p: (p[0], p[1] - bh)
        front = f'M{pt(*e)}L{pt(*c)}L{pt(*lift(c))}L{pt(*lift(e))}Z'
        side = f'M{pt(*b)}L{pt(*c)}L{pt(*lift(c))}L{pt(*lift(b))}Z'
        roof = f'M{pt(*lift(a))}L{pt(*lift(b))}L{pt(*lift(c))}L{pt(*lift(e))}Z'
        bars.append(
            f'<g class="b" style="animation-delay:{wk * 22}ms"><title>{count} on {d:%b %d, %Y}</title>'
            f'<path d="{front}" fill="{mix(top, ink, shade_l)}"/><path d="{side}" fill="{mix(top, ink, shade_r)}"/>'
            f'<path d="{roof}" fill="{top}"/></g>'
        )

    # Month labels along the near edge of the grid, clear of the bars and the stats column.
    months, seen = [], set()
    for wk, wd, d, *_ in cells:
        if wd == 0 and d.day <= 7 and (d.year, d.month) not in seen:
            seen.add((d.year, d.month))
            x = ORIGIN[0] + wk * U[0] + 7 * V[0]
            y = ORIGIN[1] + wk * U[1] + 7 * V[1] + 14
            if x > 660:
                continue
            months.append(f'<text x="{x:.0f}" y="{y:.0f}" font-family="{MONO}" font-size="10" letter-spacing="1" fill="{t["subtle"]}">{d.strftime("%b").upper()}</text>')

    total, active, current, longest, best = stats(days)
    sx = 736
    rows = [
        (f"{total:,}", "contributions in the last year"),
        (f"{active}", "active days"),
        (f"{longest} d", f"longest streak, current {current} d"),
        (f"{days[best][0]}", f"busiest day, {best:%d %b %Y}"),
    ]
    stat_svg = "\n".join(
        f'  <text x="{sx}" y="{96 + i * 66}" font-family="{SANS}" font-size="{30 if i == 0 else 24}" font-weight="700" fill="{t["accent"] if i == 0 else t["text"]}">{escape(v)}</text>\n'
        f'  <text x="{sx}" y="{118 + i * 66}" font-family="{SANS}" font-size="12.5" fill="{t["subtle"]}">{escape(c)}</text>'
        for i, (v, c) in enumerate(rows)
    )
    legend = "".join(
        f'<rect x="{640 + i * 16}" y="352" width="11" height="11" rx="2" fill="{c}"/>' for i, c in enumerate(tops)
    )
    label = (f"Contribution graph for {user}: {total} contributions over {active} active days in the last year; "
             f"longest streak {longest} days; busiest day {best:%d %B %Y} with {days[best][0]}.")
    return f"""<svg viewBox="0 0 {w} {h}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{escape(label)}">
  <style>
    .b {{ transform-box: fill-box; transform-origin: 50% 100%; animation: grow .7s cubic-bezier(.2,.8,.2,1) both; }}
    @keyframes grow {{ from {{ transform: scaleY(0); opacity: 0; }} }}
    @media (prefers-reduced-motion: reduce) {{ .b {{ animation: none; }} }}
  </style>
{frame(t, w, h)}
  <text x="28" y="46" font-family="{MONO}" font-size="11.5" letter-spacing="2" fill="{t['subtle']}">CONTRIBUTIONS  ·  LAST 12 MONTHS</text>
  {''.join(months)}
  {''.join(bars)}
  <line x1="{sx - 28}" y1="64" x2="{sx - 28}" y2="320" stroke="{t['border']}" stroke-opacity="{t['border_op']}"/>
{stat_svg}
  <line x1="28" y1="334" x2="{w - 28}" y2="334" stroke="{t['border']}" stroke-opacity="{t['border_op']}"/>
  <text x="28" y="362" font-family="{MONO}" font-size="11" letter-spacing="1.5" fill="{t['subtle']}">MOST WORK IS IN PRIVATE REPOS  ·  {LANGUAGES}</text>
  <text x="632" y="362" text-anchor="end" font-family="{MONO}" font-size="10" letter-spacing="1" fill="{t['subtle']}">LESS</text>
  {legend}
  <text x="{640 + 5 * 16 + 4}" y="362" font-family="{MONO}" font-size="10" letter-spacing="1" fill="{t['subtle']}">MORE</text>
  <text x="{w - 28}" y="362" text-anchor="end" font-family="{MONO}" font-size="10" letter-spacing="1" fill="{t['subtle']}">UPDATED {date.today().strftime("%d %b %Y").upper()}</text>
</svg>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default="bcr-ba")
    ap.add_argument("--out", default="dist")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    days = fetch(args.user)
    for name, t in THEMES.items():
        (out / f"activity-{name}.svg").write_text(render(days, t, name == "dark", args.user), encoding="utf-8", newline="\n")
    print(f"wrote activity-dark.svg and activity-light.svg to {out}")


if __name__ == "__main__":
    main()
