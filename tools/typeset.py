"""Shape text with HarfBuzz and emit SVG path data.

GitHub proxies README images through camo, which strips external font loads, so
every piece of type in these banners has to ship as outlines. This turns a
string into a `<path d="...">` using the same two faces the website uses:
Instrument Serif for display, JetBrains Mono for the mono labels.
"""

from functools import lru_cache

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont


@lru_cache(maxsize=None)
def _load(path):
    with open(path, "rb") as fh:
        data = fh.read()
    face = hb.Face(data)
    font = hb.Font(face)
    tt = TTFont(path, fontNumber=0, lazy=True)
    upem = tt["head"].unitsPerEm
    font.scale = (upem, upem)
    return font, tt.getGlyphSet(), upem, tt


def typeset(path, text, size, tracking=0.0, x=0.0, y=0.0):
    """Return (path_d, advance) for `text` laid out with the baseline at y.

    `tracking` is in em, matching the site's letter-spacing tokens
    (0.42em for `tracking-ultra`, 0.18em for `tracking-wide2`).
    """
    font, glyphset, upem, tt = _load(path)

    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True, "liga": True})

    order = tt.getGlyphOrder()
    scale = size / upem
    extra = tracking * size

    pen_out = []
    cursor = x
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        name = order[info.codepoint]
        gx = cursor + pos.x_offset * scale
        gy = y - pos.y_offset * scale
        # Flip the y axis: fonts grow upward, SVG grows downward.
        pen = SVGPathPen(glyphset, ntos=lambda v: f"{v:.2f}")
        glyphset[name].draw(TransformPen(pen, (scale, 0, 0, -scale, gx, gy)))
        d = pen.getCommands()
        if d:
            pen_out.append(d)
        cursor += pos.x_advance * scale + extra

    return " ".join(pen_out), cursor - x


def width(path, text, size, tracking=0.0):
    return typeset(path, text, size, tracking)[1]
