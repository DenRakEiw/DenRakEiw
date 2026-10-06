"""Generate the SVG assets of the terminal-style profile README (2026-10-06).

    python build_nerd.py            -> ../assets/terminal.svg, ../assets/neofetch.svg

Scumble's palette (its icon: ink #1B1714, orange #C4643A, light orange #D08967, chalk #EFE7DA) on a dark terminal.
Type ships as outlines (GitHub's camo strips webfonts) in Roboto Mono (OFL-1.1, the copy Scumble bundles in
renderer/editor/fonts/), instanced at 400 and 700 into tools/fonts/ (gitignored):

    python -c "from fontTools.ttLib import TTFont; from fontTools.varLib import instancer; [instancer.instantiateVariableFont(TTFont('RobotoMono[wght].ttf'), {'wght': w}).save(f'fonts/RobotoMono-{n}.ttf') for w, n in ((400, 'Regular'), (700, 'Bold'))]"

The terminal types its commands with SMIL (a clip rect per command that grows one character at a time, discrete),
which GitHub's image proxy keeps; it plays once and the last cursor keeps blinking.
"""

import os
import re
import sys
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from typeset import typeset  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets")
MONO = os.path.join(HERE, "fonts", "RobotoMono-Regular.ttf")
BOLD = os.path.join(HERE, "fonts", "RobotoMono-Bold.ttf")
ICON = r"F:\canvas\build\icon.svg"

INK, INK2, LINE = "#1B1714", "#241e1a", "#3a302a"
ORANGE, ORANGE2, CHALK, MUTED, DIM = "#C4643A", "#D08967", "#EFE7DA", "#b3a596", "#7d7067"
W = 900
FS = 16.5
CW = FS * 0.6          # Roboto Mono advances 0.6 em


def text(s, x, y, fill, bold=False, size=FS, extra=""):
    d, adv = typeset(BOLD if bold else MONO, s, size, x=x, y=y)
    return (f'<path d="{d}" fill="{fill}"{extra}/>' if d else ""), adv


def terminal():
    PAD, TOP, LH = 26, 36, 29
    PROMPT = "~ $ "
    # (kind, parts): parts are (text, colour, bold); "cmd" lines are typed, "out" lines appear at once
    lines = [
        ("cmd", [("whoami", CHALK, False)]),
        ("out", [("denrakeiw", ORANGE2, True), ("  ·  open-source tools for people who make pictures with AI", MUTED, False)]),
        ("cmd", [("scumble --help", CHALK, False)]),
        ("out", [("Scumble", ORANGE2, True), (" — an AI-native image editor for ComfyUI and the models", MUTED, False)]),
        ("out", [("          you already use. Inpaint, edit, upscale, generate:", MUTED, False)]),
        ("out", [("          every edit comes back as a layer of its own.", MUTED, False)]),
        ("cmd", [("git clone https://github.com/DenRakEiw/scumble", CHALK, False)]),
        ("out", [("Cloning into 'scumble'...  ", MUTED, False), ("done.", ORANGE2, True)]),
        ("end", []),
    ]
    H = TOP + PAD + LH * len(lines) + 8
    body, defs, t = [], [], 0.5
    TYPE, OUT_GAP, CMD_GAP = 0.055, 0.35, 0.45
    for i, (kind, parts) in enumerate(lines):
        y = TOP + PAD + LH * i + FS * 0.35 + 6
        x0 = PAD
        if kind in ("cmd", "end"):
            p, adv = text(PROMPT, x0, y, ORANGE, bold=True)
            body.append(f'<g opacity="0">{p}<set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/></g>')
            x0 += adv
        if kind == "end":
            # the last prompt: a blinking block cursor
            body.append(f'<rect x="{x0 + 1:.1f}" y="{y - FS * 0.8:.1f}" width="{CW:.1f}" height="{FS * 1.05:.1f}" fill="{ORANGE2}" opacity="0">'
                        f'<set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/>'
                        f'<animate attributeName="fill-opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.05s" begin="{t:.2f}s" repeatCount="indefinite"/></rect>')
            break
        x = x0
        segs = []
        for s, col, b in parts:
            p, adv = text(s, x, y, col, bold=b)
            segs.append(p)
            x += adv
        n = sum(len(s) for s, _, _ in parts)
        if kind == "cmd":
            cid = f"c{i}"
            vals = ";".join(f"{k * CW:.1f}" for k in range(n + 1))
            dur = TYPE * n
            start = t + 0.25
            defs.append(f'<clipPath id="{cid}"><rect x="{x0:.1f}" y="{y - FS:.1f}" width="0" height="{FS * 1.5:.1f}">'
                        f'<animate attributeName="width" values="{vals}" calcMode="discrete" dur="{dur:.2f}s" begin="{start:.2f}s" fill="freeze"/>'
                        f'</rect></clipPath>')
            body.append(f'<g clip-path="url(#{cid})">{"".join(segs)}</g>')
            # the cursor rides along while typing, then goes
            xs = ";".join(f"{x0 + k * CW + 1:.1f}" for k in range(n + 1))
            body.append(f'<rect x="{x0 + 1:.1f}" y="{y - FS * 0.8:.1f}" width="{CW:.1f}" height="{FS * 1.05:.1f}" fill="{ORANGE2}" opacity="0">'
                        f'<set attributeName="opacity" to="1" begin="{t:.2f}s"/>'
                        f'<animate attributeName="x" values="{xs}" calcMode="discrete" dur="{dur:.2f}s" begin="{start:.2f}s" fill="freeze"/>'
                        f'<set attributeName="opacity" to="0" begin="{start + dur + 0.2:.2f}s" fill="freeze"/></rect>')
            t = start + dur + OUT_GAP
        else:
            body.append(f'<g opacity="0">{"".join(segs)}<set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/></g>')
            t += 0.12
            if i + 1 < len(lines) and lines[i + 1][0] in ("cmd", "end"):
                t += CMD_GAP
    title, tw = text("denrakeiw@github: ~", 0, 0, DIM, size=13)
    tx = (W - tw) / 2
    title = text("denrakeiw@github: ~", tx, 23, DIM, size=13)[0]
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="{escape("A terminal: whoami prints denrakeiw, open-source tools for people who make pictures with AI; scumble --help prints an AI-native image editor for ComfyUI and the models you already use; git clone https://github.com/DenRakEiw/scumble")}">',
        f'<defs>{"".join(defs)}</defs>',
        f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12" fill="{INK}" stroke="{LINE}" stroke-width="2"/>',
        f'<path d="M1 13 a12 12 0 0 1 12 -12 h{W - 26} a12 12 0 0 1 12 12 v{TOP - 12} h-{W - 2} z" fill="{INK2}"/>',
        f'<line x1="1" y1="{TOP}" x2="{W - 1}" y2="{TOP}" stroke="{LINE}" stroke-width="1.5"/>',
        "".join(f'<circle cx="{22 + 20 * k}" cy="{TOP / 2 + 0.5}" r="6" fill="{c}"/>' for k, c in enumerate(("#ff5f57", "#febc2e", "#28c840"))),
        title,
        "".join(body),
        "</svg>",
    ]
    return "".join(svg)


def icon_group(x, y, size):
    """Scumble's icon (build/icon.svg) placed at x, y, its ids prefixed."""
    s = open(ICON, encoding="utf-8").read()
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    inner = s[s.index(">", s.index("<svg")) + 1:s.rindex("</svg>")]
    inner = inner.replace('id="shape"', 'id="sc-shape"').replace('href="#shape"', 'href="#sc-shape"')
    inner = inner.replace('id="inside"', 'id="sc-inside"').replace("url(#inside)", "url(#sc-inside)")
    k = size / 1024
    return (f'<clipPath id="sc-round"><rect x="{x}" y="{y}" width="{size}" height="{size}" rx="{size * 0.18:.1f}"/></clipPath>'
            f'<g clip-path="url(#sc-round)"><g transform="translate({x} {y}) scale({k:.5f})">{inner}</g></g>')


def neofetch():
    H = 300
    X, Y0, LH = 300, 58, 27
    rows = [
        ("OS", "Windows 11, a GPU that is always warm"),
        ("Ships", "Scumble · Inpaint Canvas for ComfyUI"),
        ("Models", "324k downloads on Civitai · Hugging Face"),
        ("Stack", "Python · PyTorch · ComfyUI · Electron · Rust · MCP"),
        ("Editor", "Scumble (obviously)"),
        ("Uptime", "always rendering"),
    ]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
           f'aria-label="{escape("neofetch: " + "; ".join(f"{k}: {v}" for k, v in rows))}">',
           f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12" fill="{INK}" stroke="{LINE}" stroke-width="2"/>',
           icon_group(40, 40, 220)]
    p, adv = text("denrakeiw", X, Y0, ORANGE, bold=True)
    out.append(p)
    p2, adv2 = text("@", X + adv, Y0, DIM)
    out.append(p2)
    out.append(text("github", X + adv + adv2, Y0, ORANGE, bold=True)[0])
    out.append(f'<rect x="{X}" y="{Y0 + 10}" width="{(len("denrakeiw@github")) * CW:.1f}" height="2" fill="{LINE}"/>')
    for i, (k, v) in enumerate(rows):
        y = Y0 + 34 + LH * i
        out.append(text(k, X, y, ORANGE2, bold=True)[0])
        out.append(text(v, X + 9 * CW, y, CHALK)[0])
    # the colour blocks under it, as neofetch prints them
    cols = [INK2, ORANGE, ORANGE2, CHALK, "#3ddc84", "#ff9f1c", "#2ec4f0", DIM]
    by = Y0 + 34 + LH * len(rows) - 4
    out.append("".join(f'<rect x="{X + k * 30}" y="{by}" width="26" height="18" rx="3" fill="{c}"/>' for k, c in enumerate(cols)))
    out.append("</svg>")
    return "".join(out)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, svg in (("terminal.svg", terminal()), ("neofetch.svg", neofetch())):
        p = os.path.join(OUT, name)
        open(p, "w", encoding="utf-8", newline="\n").write(svg)
        print(name, len(svg) // 1024, "KB")
