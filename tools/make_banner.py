"""Generate a project banner SVG in the profile style (navy, bone and gold).

Usage:
    python tools/make_banner.py "WordHive" --course "Distributed Systems" -o assets/banner.svg
    python tools/make_banner.py "My Project" --description "Short description" -o banner.svg

The banner is self-contained: the SD logo is embedded as a path (read from
assets/sd-gold.svg) and the text uses system sans-serif fonts, because GitHub
does not load external images or fonts inside an SVG.
"""
import argparse
import re
from html import escape
from pathlib import Path

NAVY = "#0B1F3A"
BONE = "#F5F0E1"
GOLD = "#C9A227"

W, H = 1200, 160
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"

LOGO_SVG = Path(__file__).resolve().parent.parent / "assets" / "sd-gold.svg"
LOGO_CENTER = (155, 128)  # centre of the logo's visual bounding box (stroke included)
LOGO_SIZE = (270, 200)    # width and height of that bounding box
LOGO_HEIGHT = 76          # rendered height in the banner

TEXT_X = 56
TEXT_RIGHT = 1000         # text must stay left of the divider
DIVIDER_X = 1024


def text_width(text, size, bold):
    """Rough upper estimate of the rendered width of a sans-serif string."""
    narrow, wide = set("iljtfrI.,:;'|!() "), set("mwMWOQGDHNU@%")
    em = 0.0
    for ch in text:
        if ch in narrow:
            em += 0.34
        elif ch in wide:
            em += 0.86
        elif ch.isupper() or ch.isdigit():
            em += 0.68
        else:
            em += 0.57
    return em * size * (1.06 if bold else 1.0)


def fit(text, max_size, min_size, bold, avail):
    """Largest font size that fits; below min_size, compress with textLength."""
    size = max_size
    while size > min_size and text_width(text, size, bold) > avail:
        size -= 1
    squeeze = text_width(text, size, bold) > avail
    return size, squeeze


def text_el(text, x, y, size, weight, fill, squeeze, avail, spacing):
    extra = f' textLength="{avail}" lengthAdjust="spacingAndGlyphs"' if squeeze else ""
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" letter-spacing="{spacing}" fill="{fill}"{extra}>'
            f"{escape(text)}</text>")


def logo_path():
    d = re.search(r'<path d="([^"]+)"', LOGO_SVG.read_text(encoding="utf-8")).group(1)
    s = LOGO_HEIGHT / LOGO_SIZE[1]
    cx = (DIVIDER_X + W - 22) / 2
    return (f'<g transform="translate({cx:g} {H / 2:g}) scale({s:.4f}) '
            f'translate({-LOGO_CENTER[0]} {-LOGO_CENTER[1]})">'
            f'<path d="{d}" fill="none" stroke="{GOLD}" stroke-width="20" '
            f'stroke-linecap="butt" stroke-linejoin="round"/></g>')


def make_banner(title, subtitle):
    avail = TEXT_RIGHT - TEXT_X
    t_size, t_squeeze = fit(title, 46, 28, True, avail)
    s_size, s_squeeze = fit(subtitle, 21, 15, False, avail)
    label = escape(f"{title} · {subtitle}", quote=True)
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'role="img" aria-label="{label}">',
        f"<title>{label}</title>",
        f'<rect width="{W}" height="{H}" rx="6" fill="{NAVY}"/>',
        f'<rect x="16" y="16" width="{W - 32}" height="{H - 32}" fill="none" stroke="{GOLD}" stroke-width="1" opacity=".9"/>',
        f'<rect x="22" y="22" width="{W - 44}" height="{H - 44}" fill="none" stroke="{GOLD}" stroke-width=".5" opacity=".45"/>',
        text_el(title, TEXT_X, 84, t_size, 700, BONE, t_squeeze, avail, ".01em"),
        f'<path d="M{TEXT_X} 100H{TEXT_X + 44}" stroke="{GOLD}" stroke-width="1" opacity=".7"/>',
        text_el(subtitle, TEXT_X, 128, s_size, 400, GOLD, s_squeeze, avail, ".02em"),
        f'<path d="M{DIVIDER_X} 44V{H - 44}" stroke="{GOLD}" stroke-width="1" opacity=".45"/>',
        logo_path(),
        "</svg>",
        "",
    ])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("title", help="project title")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--course", help='course name; subtitle becomes "<course> · University of La Rioja"')
    group.add_argument("--description", help="short description, for projects outside the university")
    ap.add_argument("-o", "--output", default="banner.svg", help="output SVG path (default: banner.svg)")
    args = ap.parse_args()

    subtitle = f"{args.course} · University of La Rioja" if args.course else args.description
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(make_banner(args.title, subtitle), encoding="utf-8", newline="\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
