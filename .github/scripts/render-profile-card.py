from __future__ import annotations

import html
import json
import os
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets"
WIDTH, HEIGHT = 1000, 360

LOGO = """                    ⢰
                    ⢸⡄
            ⡆       ⣼⡇⡆    ⢸⣇       ⣀
     ⣀⣶⡀   ⣠⣧⣶⡀  ⣀⡄⣰⣿⣿⣿   ⣀⣸⣿⢀ ⡀ ⢀ ⢠⣿⡄⢀⡀
 ⠲⠿⠗⣿⢿⣿⢿⠗⠿⢸⣿⣿⡿⠿⠿⠺⣿⣿⣿⣿⣿⡿⣷⣿⢶⣿⣿⣿⡿⠖⡿⠿⢿⠿⣿⣿⡿⢺⡿⠿
     ⠘⠃    ⢸⡟⠃   ⠁ ⢸⣿⡿ ⠛  ⠁⢻⡇⠁      ⣿⠁
           ⠸⠃      ⢸⣿⠃     ⢸⠁       ⠉
                   ⠘⡏
                    ⡇"""

THEMES = {
    "dark": {
        "page": "#0d1117",
        "panel": "#0d1117",
        "border": "#30363d",
        "text": "#f0f6fc",
        "muted": "#8b949e",
        "soft": "#161b22",
        "mint": "#8fffc1",
        "coral": "#e16b61",
        "blue": "#79c0ff",
    },
    "light": {
        "page": "#ffffff",
        "panel": "#ffffff",
        "border": "#d0d7de",
        "text": "#1f2328",
        "muted": "#59636e",
        "soft": "#f6f8fa",
        "mint": "#137a48",
        "coral": "#b84f45",
        "blue": "#0969da",
    },
}


def request_json(url: str, token: str | None = None) -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "sil6428-profile-card",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
        headers["X-GitHub-Api-Version"] = "2022-11-28"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def load_stats() -> dict[str, str]:
    stats_url = os.environ.get(
        "OTNOW_STATS_URL",
        "https://otnow-stats.sil6428-archtech.workers.dev/api/stats",
    )
    otnow = request_json(stats_url).get("summary", {})
    return {
        "items": f"{otnow.get('totalItems', 0):,}",
        "installs": f"{otnow.get('reportingInstallations', 0):,}",
        "rating": f"{float(otnow.get('averageRating', 0)):.1f}",
        "reviews": f"{otnow.get('ratingCount', 0):,}",
        "tests": "72",
    }


def braille_circles(color: str) -> str:
    cell_width = 7.1
    cell_height = 16.5
    radius = 1.65
    x_origin, y_origin = 40, 88
    dots = {
        0: (1.7, 2.8),
        1: (1.7, 6.4),
        2: (1.7, 10.0),
        3: (5.3, 2.8),
        4: (5.3, 6.4),
        5: (5.3, 10.0),
        6: (1.7, 13.6),
        7: (5.3, 13.6),
    }
    circles: list[str] = []
    for row, line in enumerate(LOGO.splitlines()):
        for column, character in enumerate(line):
            codepoint = ord(character)
            if not 0x2800 <= codepoint <= 0x28FF:
                continue
            pattern = codepoint - 0x2800
            for bit, (dx, dy) in dots.items():
                if pattern & (1 << bit):
                    x = x_origin + column * cell_width + dx
                    y = y_origin + row * cell_height + dy
                    circles.append(
                        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius}" fill="{color}"/>'
                    )
    return "\n    ".join(circles)


def render(theme_name: str, stats: dict[str, str]) -> str:
    theme = THEMES[theme_name]
    circles = braille_circles(theme["text"])
    description = html.escape(
        "Affan Shaikh, Networking and IT Security student. "
        f"OTNow has organized {stats['items']} Canvas items across "
        f"{stats['installs']} opt-in reporting installations."
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title description">
  <title id="title">Affan Shaikh</title>
  <desc id="description">{description}</desc>
  <rect width="{WIDTH}" height="{HEIGHT}" fill="{theme['page']}"/>
  <rect x="1" y="1" width="998" height="358" rx="18" fill="{theme['panel']}" stroke="{theme['border']}"/>
  <g font-family="ui-monospace,SFMono-Regular,Consolas,Liberation Mono,monospace">
    <text x="32" y="38" fill="{theme['muted']}" font-size="14">~/affan</text>
    <text x="968" y="38" text-anchor="end" fill="{theme['mint']}" font-size="13">open to co-op</text>
    {circles}
    <text x="40" y="276" fill="{theme['muted']}" font-size="13">guess the game</text>

    <text x="500" y="78" fill="{theme['text']}" font-size="31" font-weight="600">Affan Shaikh</text>
    <text x="500" y="107" fill="{theme['mint']}" font-size="15">Networking &amp; IT Security · Ontario Tech</text>
    <text x="500" y="143" fill="{theme['muted']}" font-size="15">I build useful tools, test them, then document</text>
    <text x="500" y="165" fill="{theme['muted']}" font-size="15">what actually happened.</text>

    <rect x="500" y="195" width="143" height="91" rx="10" fill="{theme['soft']}" stroke="{theme['border']}"/>
    <rect x="500" y="195" width="143" height="3" rx="2" fill="{theme['coral']}"/>
    <text x="518" y="220" fill="{theme['muted']}" font-size="11">IMPACT</text>
    <text x="518" y="249" fill="{theme['text']}" font-size="20" font-weight="700">{stats['items']}</text>
    <text x="561" y="249" fill="{theme['muted']}" font-size="12">items</text>
    <text x="518" y="271" fill="{theme['muted']}" font-size="12">{stats['installs']} opt-in installs</text>

    <rect x="654" y="195" width="143" height="91" rx="10" fill="{theme['soft']}" stroke="{theme['border']}"/>
    <rect x="654" y="195" width="143" height="3" rx="2" fill="{theme['mint']}"/>
    <text x="672" y="220" fill="{theme['muted']}" font-size="11">TRUST</text>
    <text x="672" y="249" fill="{theme['text']}" font-size="20" font-weight="700">{stats['rating']}</text>
    <text x="713" y="249" fill="{theme['muted']}" font-size="12">/ 5</text>
    <text x="672" y="271" fill="{theme['muted']}" font-size="12">{stats['reviews']} reviews</text>

    <rect x="808" y="195" width="147" height="91" rx="10" fill="{theme['soft']}" stroke="{theme['border']}"/>
    <rect x="808" y="195" width="147" height="3" rx="2" fill="{theme['blue']}"/>
    <text x="826" y="220" fill="{theme['muted']}" font-size="11">RIGOR</text>
    <text x="826" y="249" fill="{theme['text']}" font-size="20" font-weight="700">{stats['tests']}</text>
    <text x="852" y="249" fill="{theme['muted']}" font-size="12">tests</text>
    <text x="826" y="271" fill="{theme['muted']}" font-size="12">P2P test suite</text>

    <text x="500" y="321" fill="{theme['coral']}" font-size="14">$</text>
    <text x="518" y="321" fill="{theme['text']}" font-size="14">currently: networks · security · systems</text>
    <rect x="856" y="307" width="8" height="17" fill="{theme['mint']}"/>
  </g>
</svg>
'''


def main() -> None:
    stats = load_stats()
    ASSETS.mkdir(parents=True, exist_ok=True)
    for theme_name in THEMES:
        (ASSETS / f"profile-{theme_name}.svg").write_text(
            render(theme_name, stats),
            encoding="utf-8",
            newline="\n",
        )
    print(json.dumps(stats))


if __name__ == "__main__":
    main()
