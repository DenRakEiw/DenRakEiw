"""Generate the SVG assets for the DenRakEiw GitHub profile README.

Everything here quotes the website: the palette from tailwind.config.ts, the
same two typefaces, the hero's anatomy (ambient orbs, faint grid, grain, the
pulsing eyebrow dot, the rotating role) and the `(Section Label)` convention.

Type ships as outlines because GitHub proxies README images through camo, which
strips webfonts. Sizes are chosen for GitHub's ~860px content column, so the
artwork renders close to 1:1 rather than being scaled down into illegibility.
"""

import os
import sys
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from typeset import typeset, width  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
OUT = r"F:\denrakeiw-profile\assets"

SERIF = os.path.join(FONTS, "InstrumentSerif-Regular.ttf")
MONO = os.path.join(FONTS, "JetBrainsMono-Regular.ttf")
MONO_MED = os.path.join(FONTS, "JetBrainsMono-Medium.ttf")

# tailwind.config.ts
INK_950, INK_900, INK_800, INK_700 = "#08080a", "#0c0c0f", "#141418", "#1d1d22"
BONE_50, BONE_100, BONE_200, BONE_300, BONE_400 = (
    "#fafaf7", "#f2f1eb", "#e3e1d6", "#c9c6b6", "#a8a492",
)
ACCENT, ACCENT_SOFT, ACCENT_DEEP, EMBER = "#c8ff3d", "#d8ff7a", "#9fd000", "#ff5b2e"

ULTRA, WIDE2 = 0.42, 0.18  # the site's letterSpacing tokens

W = 900  # GitHub's content column is ~860px; design at it, not above it


def svg_open(w, h, label):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">'
    )


def path(d, fill, opacity=None):
    op = f' opacity="{opacity}"' if opacity is not None else ""
    return f'<path d="{d}" fill="{fill}"{op}/>'


def mono(text, size, x, y, fill, tracking=ULTRA, font=MONO):
    return path(typeset(font, text, size, tracking, x, y)[0], fill)


def serif(text, size, x, y, fill):
    return path(typeset(SERIF, text, size, 0, x, y)[0], fill)


def ambient_defs(w, h, orbs=True):
    orb_defs = f"""
    <radialGradient id="orbLime" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{ACCENT}" stop-opacity="1"/>
      <stop offset="70%" stop-color="{ACCENT}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="orbEmber" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{EMBER}" stop-opacity="1"/>
      <stop offset="70%" stop-color="{EMBER}" stop-opacity="0"/>
    </radialGradient>
    <filter id="soften" x="-70%" y="-70%" width="240%" height="240%">
      <feGaussianBlur stdDeviation="55"/>
    </filter>
    <pattern id="grid" width="88" height="88" patternUnits="userSpaceOnUse">
      <path d="M88 0H0V88" fill="none" stroke="#ffffff" stroke-width="1"/>
    </pattern>""" if orbs else ""
    return f"""<defs>{orb_defs}
    <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch"/></filter>
    <clipPath id="card"><rect width="{w}" height="{h}" rx="16"/></clipPath>
  </defs>"""


def card_bg(w, h, fill=INK_900, orbs=False, grain=0.04):
    inner = f'<rect width="{w}" height="{h}" fill="{fill}"/>'
    if orbs:
        inner += (
            f'<circle cx="{w - 80}" cy="20" r="280" fill="url(#orbLime)" opacity="0.18" filter="url(#soften)"/>'
            f'<circle cx="40" cy="{h - 40}" r="250" fill="url(#orbEmber)" opacity="0.14" filter="url(#soften)"/>'
            f'<rect width="{w}" height="{h}" fill="url(#grid)" opacity="0.04"/>'
        )
    inner += f'<rect width="{w}" height="{h}" filter="url(#grain)" opacity="{grain}"/>'
    return (
        f'<g clip-path="url(#card)">{inner}</g>'
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="16" fill="none" '
        f'stroke="#ffffff" stroke-opacity="0.08"/>'
    )


# --------------------------------------------------------------------------
# Header banner — the site's hero, at README scale
# --------------------------------------------------------------------------

def header():
    PAD = 48
    NAME = 116
    LINE = NAME * 0.86  # leading-[0.86]
    ROLE = 38

    meta1, meta2 = 58, 80
    eyebrow = 126
    base1 = 224
    base2 = base1 + LINE
    ry = base2 + 72
    py = ry + 50
    H = int(py + 46)

    p = [svg_open(W, H, "Dennis Schoeneberg — AI Engineer, Author, Artist"),
         ambient_defs(W, H), card_bg(W, H, INK_950, orbs=True, grain=0.045)]

    p.append(mono("KÖLN · NONG KHAI — REMOTE, WORLDWIDE", 10, PAD, meta1, BONE_400))
    p.append(mono("AVAILABLE FOR SELECT PROJECTS", 10, PAD, meta2, BONE_300))

    # Eyebrow, led by the hero's pulsing lime dot
    p.append(
        f'<circle cx="{PAD + 3}" cy="{eyebrow - 4}" r="3" fill="{ACCENT}">'
        f'<animate attributeName="opacity" values="1;0.35;1" dur="2.4s" repeatCount="indefinite"/></circle>'
    )
    p.append(mono("CREATIVE AI · GENERATIVE MEDIA · PRODUCTION", 10, PAD + 18, eyebrow, BONE_400))

    # The name, with the accent full stop
    p.append(serif("Dennis", NAME, PAD, base1, BONE_50))
    d, w_name = typeset(SERIF, "Schöneberg", NAME, 0, PAD, base2)
    p.append(path(d, BONE_50))
    p.append(serif(".", NAME, PAD + w_name, base2, ACCENT))

    # "I am an" + the roles cycling out of their mask, on the site's 2.6s beat
    p.append(mono("I AM AN", 10, PAD, ry, BONE_400))
    rx = PAD + width(MONO, "I AM AN", 10, ULTRA) + 20
    roles = ["AI Engineer", "Author", "Artist"]
    cycle = len(roles) * 2.6
    p.append(f'<clipPath id="roleMask"><rect x="{rx - 8}" y="{ry - ROLE - 4}" width="400" height="{ROLE * 1.6}"/></clipPath>')
    p.append('<g clip-path="url(#roleMask)">')
    for i, role in enumerate(roles):
        u = i * 2.6
        # The site uses AnimatePresence mode="wait": one role is fully gone
        # before the next arrives. Leaving at +2.1 keeps that, with no overlap.
        stops = [(0.0, 0, 44), (u, 0, 44), (u + 0.5, 1, 0),
                 (u + 2.1, 1, 0), (u + 2.6, 0, -44), (cycle, 0, -44)]
        clean, seen = [], set()
        for t, o, dy in stops:
            k = round(min(t, cycle) / cycle, 5)
            if k in seen:
                continue
            seen.add(k)
            clean.append((k, o, dy))
        kt = ";".join(f"{k:.5f}" for k, _, _ in clean)
        ops = ";".join(str(o) for _, o, _ in clean)
        dys = ";".join(f"0 {dy}" for _, _, dy in clean)
        p.append(
            f'<g opacity="0">'
            f'<animate attributeName="opacity" values="{ops}" keyTimes="{kt}" dur="{cycle}s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" values="{dys}" keyTimes="{kt}" dur="{cycle}s" repeatCount="indefinite"/>'
            f'{path(typeset(SERIF, role, ROLE, 0, rx, ry)[0], ACCENT)}</g>'
        )
    p.append("</g>")

    p.append(mono("I BUILD THE PIPELINES BEHIND THE PICTURES.", 11, PAD, py, BONE_200, WIDE2, MONO_MED))
    p.append("</svg>")
    return "\n".join(p)


# --------------------------------------------------------------------------
# Section labels — the site's `(Label)` with its leading rule
# --------------------------------------------------------------------------

def section_label(text):
    size, rule, gap, H = 11, 40, 12, 24
    w = int(rule + gap + width(MONO, text, size, ULTRA) + 6)
    return (
        svg_open(w, H, text)
        + f'<rect x="0" y="{H / 2 - 0.5}" width="{rule}" height="1" fill="{BONE_400}" opacity="0.5"/>'
        + mono(text, size, rule + gap, H / 2 + 4, BONE_400)
        + "</svg>"
    )


# --------------------------------------------------------------------------
# Stat strip — the Civitai numbers in the site's stat-tile register
# --------------------------------------------------------------------------

def stats_strip(items):
    H = 112
    cw = (W - 2) / len(items)
    p = [svg_open(W, H, "Civitai statistics"), ambient_defs(W, H, orbs=False),
         card_bg(W, H, INK_900)]
    for i, (value, label, hot) in enumerate(items):
        x = 1 + i * cw + 26
        if i:
            p.append(f'<rect x="{1 + i * cw:.1f}" y="22" width="1" height="{H - 44}" fill="#ffffff" opacity="0.06"/>')
        p.append(serif(value, 40, x, 62, ACCENT if hot else BONE_50))
        p.append(mono(label.upper(), 8, x, 86, BONE_400, WIDE2))
    p.append("</svg>")
    return "\n".join(p)


# --------------------------------------------------------------------------
# Tag pills — the site's tech tags
# --------------------------------------------------------------------------

def pills(rows):
    size, padx, h, gap, lead = 10, 12, 26, 8, 10
    p, y, widest = [], 0, 0
    for row in rows:
        x = 0
        for tag in row:
            bw = width(MONO, tag.upper(), size, WIDE2) + padx * 2
            p.append(f'<rect x="{x:.1f}" y="{y}" width="{bw:.1f}" height="{h}" rx="6" fill="{INK_900}" stroke="#ffffff" stroke-opacity="0.08"/>')
            p.append(mono(tag.upper(), size, x + padx, y + h / 2 + 3.5, BONE_300, WIDE2))
            x += bw + gap
        widest = max(widest, x - gap)
        y += h + lead
    return svg_open(int(widest) + 2, y - lead, "Tech stack") + "".join(p) + "</svg>"


# --------------------------------------------------------------------------
# Repo list — the site's open-source block, row for row
# --------------------------------------------------------------------------

def repo_list(repos):
    PAD, ROW, star_col = 28, 52, 84
    H = PAD * 2 + ROW * len(repos)
    p = [svg_open(W, H, "Open-source repositories"), ambient_defs(W, H, orbs=False),
         card_bg(W, H, INK_900)]
    for i, (stars, name, desc, lang) in enumerate(repos):
        y = PAD + i * ROW
        if i:
            p.append(f'<rect x="{PAD}" y="{y}" width="{W - PAD * 2}" height="1" fill="#ffffff" opacity="0.05"/>')
        n = str(stars)
        nw = width(MONO, n, 13, 0)
        p.append(mono(n, 13, star_col - nw - 12, y + 26, ACCENT, 0))
        p.append(mono("★", 11, star_col - 8, y + 26, BONE_400, 0))
        p.append(mono(name, 13, star_col + 24, y + 22, BONE_100, 0))
        p.append(mono(desc, 11, star_col + 24, y + 40, BONE_400, 0))
        lw = width(MONO, lang.upper(), 9, WIDE2)
        p.append(mono(lang.upper(), 9, W - PAD - lw, y + 26, BONE_400, WIDE2))
    p.append("</svg>")
    return "\n".join(p)


def write(name, content):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"{name:26s} {len(content) / 1024:6.1f} KB")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    write("header.svg", header())

    for slug, text in [
        ("about", "(ABOUT)"),
        ("work", "(SELECTED WORK)"),
        ("open-source", "(OPEN SOURCE)"),
        ("stats", "(STATS)"),
        ("recognition", "(AWARDS & RECOGNITION)"),
        ("game", "(SIDE PROJECT · GAME)"),
        ("contact", "(CONTACT)"),
    ]:
        write(f"label-{slug}.svg", section_label(text))

    write("civitai.svg", stats_strip([
        ("3.9k", "Followers", False),
        ("324.3k", "Model downloads", False),
        ("746.2k", "Image generations", False),
        ("#1", "Vehicle Creators", True),
        ("#3", "Tool Creators", True),
    ]))

    # Generated here rather than pulled from github-readme-stats: that service
    # is rate-limited to the point of serving broken images, and these numbers
    # come straight from the GitHub API anyway.
    write("github.svg", stats_strip([
        ("153", "Stars earned", True),
        ("16", "Public repos", False),
        ("20", "Forks", False),
        ("24", "Followers", False),
        ("Python", "Most used", False),
    ]))

    write("repos.svg", repo_list([
        (45, "Latent_Nodes", "Latent editing nodes for ComfyUI", "Python"),
        (35, "DenRakEiw_Nodes", "ComfyUI node pack", "Python"),
        (28, "WAN_NN_Latent_Upscale", "Neural network upscaler for Wan", "Python"),
        (21, "ComfyUI-InpaintCanvas", "Krita-style inpainting editor inside a ComfyUI node", "JavaScript"),
        (7, "flux_3_api", "BFL Flux 3 video API nodes, with an LLM prompt generator", "Python"),
    ]))

    write("stack.svg", pills([
        ["ComfyUI", "Stable Diffusion", "Flux", "LoRA Training", "Python"],
        ["PyTorch", "Model Optimization", "AI/CGI Hybrid", "Godot", "MCP"],
    ]))
