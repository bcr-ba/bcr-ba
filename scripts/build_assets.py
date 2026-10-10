"""Generate the profile's SVG assets (banner + project cards) in dark and light themes.

Run from the repo root:  python scripts/build_assets.py
Edit THEMES / CARDS below, re-run, commit the files in assets/.
"""

from pathlib import Path
from textwrap import wrap
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"

SANS = "'Segoe UI', system-ui, -apple-system, 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, 'SF Mono', 'Cascadia Code', 'JetBrains Mono', Consolas, monospace"

THEMES = {
    "dark": {
        "bg0": "#0A1729", "bg1": "#0F2035", "halo": "#1E4A63",
        "border": "#74B4C7", "border_op": "0.18",
        "text": "#EDF3F9", "muted": "#9FC1CE", "subtle": "#6E8AA0",
        "accent": "#F2AC4E", "line": "#74B4C7", "node": "#0A1729",
    },
    "light": {
        "bg0": "#FFFFFF", "bg1": "#F3F7FB", "halo": "#DCEAF2",
        "border": "#0F2035", "border_op": "0.12",
        "text": "#0F2035", "muted": "#2F5E73", "subtle": "#5B7487",
        "accent": "#C77A14", "line": "#3D7F94", "node": "#FFFFFF",
    },
}

# Motion is decorative only, so it is switched off for people who ask for reduced motion.
MOTION_CSS = """
  <style>
    .pulse { transform-box: fill-box; transform-origin: center; animation: pulse 2.4s ease-in-out infinite; }
    .packet { animation: travel 3.2s linear infinite; }
    @keyframes pulse { 50% { transform: scale(1.25); opacity: .75; } }
    @keyframes travel {
      0% { transform: translateX(0); opacity: 0; } 10% { opacity: 1; }
      90% { opacity: 1; } 100% { transform: translateX(400px); opacity: 0; }
    }
    @media (prefers-reduced-motion: reduce) { .pulse, .packet { animation: none; } }
  </style>"""


def frame(t, w, h, rx=18):
    return f"""  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{t['bg0']}"/><stop offset="1" stop-color="{t['bg1']}"/>
    </linearGradient>
    <radialGradient id="halo" cx="0.5" cy="0.35" r="0.6">
      <stop offset="0" stop-color="{t['halo']}" stop-opacity="0.55"/>
      <stop offset="1" stop-color="{t['bg1']}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="{rx}" fill="url(#bg)"/>
  <rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="{rx}" fill="url(#halo)"/>
  <rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="{rx}" fill="none" stroke="{t['border']}" stroke-opacity="{t['border_op']}"/>"""


def banner(t):
    nodes = "\n".join(
        f'    <circle cx="{x}" cy="232" r="6.5" fill="{t["node"]}" stroke="{t["line"]}" stroke-width="2"/>'
        for x in (300, 367, 433, 567, 633, 700)
    )
    return f"""<svg viewBox="0 0 1000 300" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Bocar Ba. Junior AI Engineer: LLM agents, applied ML.">{MOTION_CSS}
{frame(t, 1000, 300)}
  <defs>
    <linearGradient id="wire" x1="300" y1="0" x2="700" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{t['line']}" stop-opacity="0.2"/>
      <stop offset="0.5" stop-color="{t['line']}" stop-opacity="0.6"/>
      <stop offset="1" stop-color="{t['accent']}" stop-opacity="0.6"/>
    </linearGradient>
  </defs>
  <text x="500" y="122" text-anchor="middle" font-family="{SANS}" font-size="64" font-weight="700" letter-spacing="10" fill="{t['text']}">BOCAR BA</text>
  <rect x="456" y="142" width="88" height="3" rx="1.5" fill="{t['accent']}"/>
  <text x="500" y="182" text-anchor="middle" font-family="{MONO}" font-size="17" letter-spacing="4" fill="{t['muted']}">JUNIOR AI ENGINEER  ·  LLM AGENTS  ·  APPLIED ML</text>
  <line x1="300" y1="232" x2="700" y2="232" stroke="url(#wire)" stroke-width="2"/>
{nodes}
  <circle class="pulse" cx="500" cy="232" r="8.5" fill="{t['accent']}"/>
  <circle class="packet" cx="300" cy="232" r="3.5" fill="{t['accent']}"/>
  <text x="500" y="272" text-anchor="middle" font-family="{MONO}" font-size="12" letter-spacing="3" fill="{t['subtle']}">MULTI-AGENT SYSTEMS  ·  LOCAL INFERENCE  ·  EVALUATION</text>
</svg>
"""


CARDS = [
    {
        "slug": "eldercare",
        "kicker": "THESIS  ·  OTH AMBERG-WEIDEN",
        "title": "Elderly-Care Multi-Agent System",
        "desc": "LangGraph agents link smart-home sensors to a Pepper robot; multimodal LLMs check each event before the robot acts.",
        "metric": "7", "caption": "agents, fully on-device",
        "stack": "LANGGRAPH · OLLAMA · FASTAPI · MQTT",
    },
    {
        "slug": "finaia",
        "kicker": "APPLIED ML  ·  CREDIT RISK",
        "title": "FINAIA",
        "desc": "Cost-sensitive XGBoost over 24 engineered features, tuned for the cost of a missed default rather than accuracy.",
        "metric": "80.5%", "caption": "default recall, up from 49%",
        "stack": "XGBOOST · SCIKIT-LEARN · PANDAS",
    },
    {
        "slug": "belazur",
        "kicker": "FULL-STACK  ·  LIVE",
        "title": "Bel Azur Travel",
        "desc": "Travel-booking platform with authentication, a relational data model and a production deployment.",
        "metric": "Live", "caption": "deployed on Vercel",
        "stack": "NEXT.JS · PRISMA · NEXTAUTH · TYPESCRIPT",
    },
    {
        "slug": "bocare",
        "kicker": "GENAI  ·  EDUCATIONAL DEMO",
        "title": "BoCare AI",
        "desc": "RAG triage assistant over public health sources, with jailbreak detection and hallucination filtering.",
        "metric": "5", "caption": "urgency levels, EN / FR",
        "stack": "RAG · LANGCHAIN · PYQT6",
    },
]

CARD_W, CARD_H = 480, 260


def card(t, c):
    desc = "\n".join(
        f'  <text x="28" y="{110 + i * 21}" font-family="{SANS}" font-size="14.5" fill="{t["muted"]}">{escape(line)}</text>'
        for i, line in enumerate(wrap(c["desc"], 60)[:3])
    )
    label = f"{c['title']}. {c['desc']} {c['metric']} {c['caption']}."
    return f"""<svg viewBox="0 0 {CARD_W} {CARD_H}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{escape(label, {'"': '&quot;'})}">
{frame(t, CARD_W, CARD_H, rx=14)}
  <text x="28" y="44" font-family="{MONO}" font-size="11" letter-spacing="2" fill="{t['subtle']}">{escape(c['kicker'])}</text>
  <path d="M440 34 l10 -10 M442 24 h8 v8" stroke="{t['subtle']}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="28" y="80" font-family="{SANS}" font-size="23" font-weight="700" fill="{t['text']}">{escape(c['title'])}</text>
{desc}
  <text x="28" y="194" font-family="{SANS}"><tspan font-size="30" font-weight="700" fill="{t['accent']}">{escape(c['metric'])}</tspan><tspan dx="10" font-size="13" fill="{t['subtle']}">{escape(c['caption'])}</tspan></text>
  <line x1="28" y1="214" x2="{CARD_W - 28}" y2="214" stroke="{t['border']}" stroke-opacity="{t['border_op']}"/>
  <text x="28" y="238" font-family="{MONO}" font-size="11" letter-spacing="1.5" fill="{t['subtle']}">{escape(c['stack'])}</text>
</svg>
"""


def main():
    OUT.mkdir(exist_ok=True)
    for name, t in THEMES.items():
        (OUT / f"banner-{name}.svg").write_text(banner(t), encoding="utf-8", newline="\n")
        for c in CARDS:
            (OUT / f"card-{c['slug']}-{name}.svg").write_text(card(t, c), encoding="utf-8", newline="\n")
    print(f"wrote {len(THEMES) * (1 + len(CARDS))} files to {OUT}")


if __name__ == "__main__":
    main()
