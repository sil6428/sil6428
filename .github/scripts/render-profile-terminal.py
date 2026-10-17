from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
GIF_OUT = ROOT / "assets" / "cyberglass-whoami.gif"
STATIC_OUT = ROOT / "assets" / "cyberglass-terminal-static.png"

WIDTH, HEIGHT = 1000, 610
BG = "#0a1010"
FG = "#edf4f1"
MUTED = "#82918b"
MINT = "#8fffc1"
CORAL = "#e16b61"
TRACK = "#26312d"

LOGO = """                    ⢰
                    ⢸⡄
            ⡆       ⣼⡇⡆    ⢸⣇       ⣀
     ⣀⣶⡀   ⣠⣧⣶⡀  ⣀⡄⣰⣿⣿⣿   ⣀⣸⣿⢀ ⡀ ⢀ ⢠⣿⡄⢀⡀
 ⠲⠿⠗⣿⢿⣿⢿⠗⠿⢸⣿⣿⡿⠿⠿⠺⣿⣿⣿⣿⣿⡿⣷⣿⢶⣿⣿⣿⡿⠖⡿⠿⢿⠿⣿⣿⡿⢺⡿⠿
     ⠘⠃    ⢸⡟⠃   ⠁ ⢸⣿⡿ ⠛  ⠁⢻⡇⠁      ⣿⠁
           ⠸⠃      ⢸⣿⠃     ⢸⠁       ⠉
                   ⠘⡏
                    ⡇"""


def request_json(url: str, token: str | None = None) -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "sil6428-profile-terminal",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
        headers["X-GitHub-Api-Version"] = "2022-11-28"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def load_stats() -> dict[str, str]:
    owner = os.environ.get("PROFILE_OWNER", "sil6428")
    token = os.environ.get("GH_STATS_TOKEN")
    stats_url = os.environ.get(
        "OTNOW_STATS_URL",
        "https://otnow-stats.sil6428-archtech.workers.dev/api/stats",
    )
    github = request_json(f"https://api.github.com/users/{owner}", token)
    otnow = request_json(stats_url).get("summary", {})

    rating = otnow.get("averageRating", 0)
    return {
        "repos": f"{github.get('public_repos', 0):,}",
        "followers": f"{github.get('followers', 0):,}",
        "installs": f"{otnow.get('reportingInstallations', 0):,}",
        "items": f"{otnow.get('totalItems', 0):,}",
        "rating": f"{float(rating):.1f}",
        "reviews": f"{otnow.get('ratingCount', 0):,}",
    }


def find_font(size: int, bold: bool = False, symbols: bool = False) -> ImageFont.FreeTypeFont:
    names: list[str] = []
    if os.name == "nt":
        if symbols:
            names.extend([r"C:\Windows\Fonts\seguisym.ttf", r"C:\Windows\Fonts\segoeui.ttf"])
        names.extend(
            [
                r"C:\Windows\Fonts\CascadiaMono.ttf",
                r"C:\Windows\Fonts\CascadiaCode.ttf",
                r"C:\Windows\Fonts\consolab.ttf" if bold else r"C:\Windows\Fonts\consola.ttf",
            ]
        )
    names.extend(
        [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
            if bold
            else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationMono-Bold.ttf"
            if bold
            else "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf",
        ]
    )
    for name in names:
        if Path(name).exists():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()


FONT = find_font(18)
FONT_BOLD = find_font(18, bold=True)
FONT_SMALL = find_font(15)
FONT_TINY = find_font(13)

_probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
for logo_size in range(15, 7, -1):
    LOGO_FONT = find_font(logo_size, symbols=True)
    if max(_probe.textlength(line, font=LOGO_FONT) for line in LOGO.splitlines()) <= 478:
        break


def blank() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    draw.rectangle((11, 11, WIDTH - 12, HEIGHT - 12), outline=TRACK, width=1)
    return image


def draw_lines(
    image: Image.Image,
    lines: list[tuple[str, str]],
    x: int = 28,
    y: int = 27,
    step: int = 27,
    cursor: bool = False,
) -> None:
    draw = ImageDraw.Draw(image)
    last_x, last_y = x, y
    for text, color in lines:
        draw.text((x, y), text, font=FONT, fill=color)
        last_x = x + int(draw.textlength(text, font=FONT))
        last_y = y
        y += step
    if cursor:
        draw.rectangle((last_x + 3, last_y + 3, last_x + 13, last_y + 21), fill=FG)


def typed_frames(lines: list[tuple[str, str]]) -> tuple[list[Image.Image], list[int]]:
    frames: list[Image.Image] = []
    durations: list[int] = []
    visible: list[tuple[str, str]] = []
    for text, color in lines:
        if not text:
            visible.append((text, color))
            continue
        for count in range(2, len(text) + 2, 2):
            image = blank()
            draw_lines(image, visible + [(text[:count], color)], cursor=True)
            frames.append(image)
            durations.append(62)
        visible.append((text, color))
    return frames, durations


def info_rows(stats: dict[str, str]) -> list[tuple[str, str, str]]:
    return [
        ("ROLE", "Networking & IT Security", FG),
        ("SCHOOL", "Ontario Tech University", FG),
        ("FOCUS", "networks / security / systems", FG),
        ("SHELL", "PowerShell 7", FG),
        ("TERMINAL", "CyberGlass", FG),
        ("STATUS", "open to co-op", MINT),
        ("", "", FG),
        ("GITHUB", "", CORAL),
        ("REPOS", f"{stats['repos']} public", FG),
        ("FOLLOWERS", stats["followers"], FG),
        ("", "", FG),
        ("OTNOW", "", CORAL),
        ("INSTALLS", f"{stats['installs']} opt-in", FG),
        ("ITEMS", f"{stats['items']} organized", FG),
        ("RATING", f"{stats['rating']} / 5  ({stats['reviews']} reviews)", FG),
    ]


def fastfetch_frame(stats: dict[str, str], row_count: int, cursor: bool = False) -> Image.Image:
    image = blank()
    draw = ImageDraw.Draw(image)
    draw.text((28, 27), "affan@cyberglass ~ $ whoaml", font=FONT, fill=FG)

    logo_y = 105
    logo_step = max(23, LOGO_FONT.getbbox("Hg")[3] + 7)
    for line in LOGO.splitlines():
        draw.text((26, logo_y), line, font=LOGO_FONT, fill=FG)
        logo_y += logo_step

    draw.text((548, 76), "affan@github", font=find_font(23, bold=True), fill=MINT)
    draw.line((548, 107, 955, 107), fill=TRACK, width=1)

    rows = info_rows(stats)
    y = 124
    for label, value, value_color in rows[:row_count]:
        if not label:
            y += 10
            continue
        if not value:
            draw.text((548, y), label, font=FONT_BOLD, fill=value_color)
            y += 26
            continue
        draw.text((548, y), label.ljust(9), font=FONT_TINY, fill=MUTED)
        draw.text((650, y - 3), value, font=FONT_SMALL, fill=value_color)
        y += 26

    draw.line((28, 510, 955, 510), fill=TRACK, width=1)
    draw.text((28, 528), "affan@cyberglass ~ $ ls projects/", font=FONT_SMALL, fill=FG)
    draw.text(
        (28, 558),
        "OTNow   P2P-messaging   file-integrity-monitor   CyberGlass",
        font=FONT_SMALL,
        fill=MINT,
    )
    prompt = "affan@cyberglass ~ $"
    draw.text((28, 582), prompt, font=FONT_TINY, fill=MUTED)
    if cursor:
        cursor_x = 28 + int(draw.textlength(prompt, font=FONT_TINY)) + 6
        draw.rectangle((cursor_x, 585, cursor_x + 9, 600), fill=FG)
    return image


def render() -> None:
    stats = load_stats()
    boot_lines = [
        ("CYBERGLASS OS v1.0 (tty1)", FG),
        ("", FG),
        ("login: affan", FG),
        ("password: ************", FG),
        ("", FG),
        ("Session restored from ~/.cyberglass", MUTED),
        ("affan@cyberglass ~ $ whoaml", MINT),
    ]
    frames, durations = typed_frames(boot_lines)
    durations[-1] = 700

    rows = info_rows(stats)
    for row_count in range(0, len(rows) + 1):
        frames.append(fastfetch_frame(stats, row_count))
        durations.append(95 if row_count else 240)

    for index in range(12):
        frames.append(fastfetch_frame(stats, len(rows), cursor=(index % 4 < 2)))
        durations.append(180)

    final = fastfetch_frame(stats, len(rows), cursor=True)
    STATIC_OUT.parent.mkdir(parents=True, exist_ok=True)
    final.save(STATIC_OUT, optimize=True)

    palette = final.quantize(colors=56, method=Image.Quantize.MEDIANCUT)
    paletted = [frame.quantize(palette=palette) for frame in frames]
    paletted[0].save(
        GIF_OUT,
        save_all=True,
        append_images=paletted[1:],
        duration=durations,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(json.dumps({"gif": str(GIF_OUT), "bytes": GIF_OUT.stat().st_size, **stats}))


if __name__ == "__main__":
    render()
