"""Generate the README artwork for Tattletale.

Every glyph is converted to a path, so the SVGs render identically on
GitHub, in any browser, in light and dark mode, with no font loading.

Usage:
    pip install fonttools uharfbuzz
    TT_FONTS=/path/to/fonts python assets/build/build_art.py

Fonts expected in TT_FONTS (all SIL OFL, from github.com/google/fonts):
    ArchivoXBlack.ttf   Archivo  wdth=125 wght=900  (static instance)
    ArchivoBold.ttf     Archivo  wdth=100 wght=700
    ArchivoSemi.ttf     Archivo  wdth=110 wght=800
    ArchivoReg.ttf      Archivo  wdth=100 wght=450
    IBMPlexMono-Regular.ttf, IBMPlexMono-Medium.ttf, IBMPlexMono-Bold.ttf

The demo data shown in the hero is the real output of demo/demo.py.
"""

from __future__ import annotations

import os
import re
import random
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONT_DIR = Path(os.environ.get("TT_FONTS", Path.home() / ".fonts"))
OUT_DIR = Path(__file__).resolve().parents[1]


# --------------------------------------------------------------------------
# text -> path
# --------------------------------------------------------------------------
class Face:
    def __init__(self, filename: str) -> None:
        path = FONT_DIR / filename
        self.tt = TTFont(path)
        self.glyphs = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()
        self.upm = self.tt["head"].unitsPerEm
        self.hb = hb.Font(hb.Face(hb.Blob.from_file_path(str(path))))

    def _shape(self, s: str):
        buf = hb.Buffer()
        buf.add_str(s)
        buf.guess_segment_properties()
        hb.shape(self.hb, buf, {"kern": True, "liga": False})
        return buf.glyph_infos, buf.glyph_positions

    def width(self, s: str, size: float, track: float = 0) -> float:
        _, pos = self._shape(s)
        return sum(p.x_advance for p in pos) * size / self.upm + track * max(len(pos) - 1, 0)

    def d(self, s: str, x: float, y: float, size: float, track: float = 0) -> str:
        infos, pos = self._shape(s)
        k = size / self.upm
        pen = SVGPathPen(self.glyphs)
        cx = x
        for info, p in zip(infos, pos):
            name = self.order[info.codepoint]
            tp = TransformPen(pen, (k, 0, 0, -k, cx + p.x_offset * k, y - p.y_offset * k))
            self.glyphs[name].draw(tp)
            cx += p.x_advance * k + track
        return re.sub(r"-?\d+\.\d+", lambda m: f"{float(m.group()):.1f}".rstrip("0").rstrip("."), pen.getCommands())


F = {
    "xblack": Face("ArchivoXBlack.ttf"),
    "semi": Face("ArchivoSemi.ttf"),
    "bold": Face("ArchivoBold.ttf"),
    "reg": Face("ArchivoReg.ttf"),
    "mono": Face("IBMPlexMono-Regular.ttf"),
    "monom": Face("IBMPlexMono-Medium.ttf"),
    "monob": Face("IBMPlexMono-Bold.ttf"),
}


# --------------------------------------------------------------------------
# themes — two-drum risograph: blue for the rigid path, pink for blame
# --------------------------------------------------------------------------
THEMES = {
    "light": dict(
        bg="#F2EDE3", paper="#FBF8F1", ink="#1D1A22", muted="#6A6472",
        rule="#CFC7B8", blue="#0068A8", pink="#FF48B0", pinkt="#B8156A",
        onpink="#1D1A22", dot="#1D1A22", dotop=".07",
    ),
    "dark": dict(
        bg="#141217", paper="#1E1B23", ink="#EEE8DC", muted="#A29CAA",
        rule="#3A3541", blue="#4CA6EC", pink="#FF5CB8", pinkt="#FF7CC6",
        onpink="#1D1A22", dot="#EEE8DC", dotop=".05",
    ),
}


class SVG:
    def __init__(self, w: int, h: int, t: dict, title: str, desc: str) -> None:
        self.w, self.h, self.t = w, h, t
        self.parts: list[str] = []
        self.head = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d">'
            f'<title id="t">{title}</title><desc id="d">{desc}</desc>'
            "<defs>"
            f'<pattern id="grain" width="7" height="7" patternUnits="userSpaceOnUse">'
            f'<circle cx="1.5" cy="1.5" r=".9" fill="{t["dot"]}" opacity="{t["dotop"]}"/></pattern>'
            f'<pattern id="half" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(30)">'
            f'<circle cx="3" cy="3" r="1.6" fill="{t["pink"]}"/></pattern>'
            f'<pattern id="halfb" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(30)">'
            f'<circle cx="3" cy="3" r="1.3" fill="{t["blue"]}"/></pattern>'
            "</defs>"
            f'<rect width="{w}" height="{h}" fill="{t["bg"]}"/>'
            f'<rect width="{w}" height="{h}" fill="url(#grain)"/>'
        )

    def add(self, s: str) -> None:
        self.parts.append(s)

    def text(self, s, x, y, font, size, fill, anchor="start", track=0, op=None):
        f = F[font]
        if anchor != "start":
            wd = f.width(s, size, track)
            x -= wd if anchor == "end" else wd / 2
        o = f' opacity="{op}"' if op else ""
        self.add(f'<path d="{f.d(s, x, y, size, track)}" fill="{fill}"{o}/>')
        return F[font].width(s, size, track)

    def done(self) -> str:
        return self.head + "".join(self.parts) + "</svg>"


def wobble(x, y, w, h, seed, amp=2.2, steps=6):
    """Hand-cut rectangle: straight-ish edges with small seeded jitter."""
    r = random.Random(seed)
    pts = []
    for i in range(steps):
        pts.append((x + w * i / steps, y + r.uniform(-amp, amp)))
    for i in range(steps):
        pts.append((x + w + r.uniform(-amp, amp), y + h * i / steps))
    for i in range(steps):
        pts.append((x + w - w * i / steps, y + h + r.uniform(-amp, amp)))
    for i in range(steps):
        pts.append((x + r.uniform(-amp, amp), y + h - h * i / steps))
    return "M" + " L".join(f"{a:.1f} {b:.1f}" for a, b in pts) + " Z"


def arrowhead(x, y, direction, color, size=11):
    s = size
    tri = {
        "right": f"M{x} {y} L{x - s} {y - s * .55} L{x - s} {y + s * .55} Z",
        "left": f"M{x} {y} L{x + s} {y - s * .55} L{x + s} {y + s * .55} Z",
        "up": f"M{x} {y} L{x - s * .55} {y + s} L{x + s * .55} {y + s} Z",
        "down": f"M{x} {y} L{x - s * .55} {y - s} L{x + s * .55} {y - s} Z",
    }[direction]
    return f'<path d="{tri}" fill="{color}"/>'


# --------------------------------------------------------------------------
# HERO — the demo pipeline, traced
# --------------------------------------------------------------------------
def hero(t: dict) -> str:
    W, H = 1280, 800
    s = SVG(
        W, H, t,
        "Tattletale traces a fabricated quote to the agent that introduced it",
        "Real output of demo/demo.py. The contract says renews automatically every 12 "
        "months. The researcher agent claims every 24 months (claim c_005). The editor "
        "carries it forward as c_010 and the summarizer as c_013, so the final output "
        "looks clean. Tattletale fails all three with NOT_IN_SOURCE and reports "
        "inherited from: researcher (c_005).",
    )

    # masthead
    s.text("MELINRESEARCH / TATTLETALE", 48, 62, "monom", 14, t["muted"], track=2.2)
    s.text("v0.1  ·  MIT  ·  PYTHON 3.10+  ·  ZERO DEPENDENCIES", W - 48, 62, "mono", 14,
           t["muted"], anchor="end", track=1.2)

    title = "TATTLETALE"
    size = 132
    s.text(title, 54, 196, "xblack", size, t["pink"], track=-2)   # misregistered drum
    s.text(title, 48, 190, "xblack", size, t["ink"], track=-2)

    s.text("A wrong quote, traced to the agent that said it first.", 50, 254, "bold", 31, t["ink"])
    s.text("Exact match against the source. Lineage walked backward. No model in the verdict.",
           50, 290, "reg", 19, t["muted"])

    # section label
    lw0 = s.text("THE DEMO, TRACED", 48, 352, "monob", 13, t["blue"], track=2)
    s.text("$ python demo/demo.py", 48 + lw0 + 18, 352, "mono", 13, t["muted"])

    # ---- source document --------------------------------------------------
    sx, sy, sw, sh = 48, 376, 296, 300
    s.add(f'<g transform="rotate(-1.4 {sx + sw / 2} {sy + sh / 2})">')
    s.add(f'<path d="{wobble(sx + 7, sy + 8, sw, sh, 11)}" fill="url(#halfb)" opacity=".55"/>')
    s.add(f'<path d="{wobble(sx, sy, sw, sh, 3)}" fill="{t["paper"]}" stroke="{t["ink"]}" stroke-width="2"/>')
    s.text("SOURCE", sx + 22, sy + 34, "monob", 12, t["blue"], track=2)
    s.text("contract.txt", sx + 22, sy + 60, "semi", 22, t["ink"])
    s.text("sha256:f9b41769…", sx + 22, sy + 84, "mono", 12, t["muted"])
    s.add(f'<path d="M{sx + 22} {sy + 100} H{sx + sw - 22}" stroke="{t["rule"]}" stroke-width="1.5"/>')
    lines = ["1. Term. This agreement", "begins on the effective", "date and renews",
             "automatically every 12", "months unless either"]
    ly = sy + 128
    for i, ln in enumerate(lines):
        if i == 3:
            pre = "automatically every "
            w0 = F["mono"].width(pre, 15)
            w1 = F["monob"].width("12", 15)
            s.add(f'<rect x="{sx + 18}" y="{ly - 16}" width="{w0 + w1 + 10}" height="22" fill="{t["blue"]}" opacity=".16"/>')
            s.text(pre, sx + 22, ly, "mono", 15, t["ink"])
            s.text("12", sx + 22 + w0, ly, "monob", 15, t["blue"])
            twelve_x, twelve_y = sx + 22 + w0 + w1 / 2, ly
        else:
            s.text(ln, sx + 22, ly, "mono", 15, t["ink"])
        ly += 24
    for i, wd in enumerate([230, 200, 244, 120]):   # the rest of the contract, greeked
        s.add(f'<rect x="{sx + 22}" y="{ly - 6 + i * 16}" width="{wd}" height="5" rx="2" fill="{t["rule"]}"/>')
    s.add("</g>")

    # ---- agent cards ----------------------------------------------------------
    cy, ch, cw = 400, 214, 262
    xs = [404, 692, 980]
    agents = [
        ("researcher", "c_005", "new claim"),
        ("editor", "c_010", "← c_005"),
        ("summarizer", "c_013", "← c_010"),
    ]
    for i, ((name, cid, link), x) in enumerate(zip(agents, xs)):
        s.add(f'<path d="{wobble(x + 6, cy + 7, cw, ch, 40 + i, 1.6)}" fill="url(#half)" opacity="{.75 if i == 0 else .28}"/>')
        s.add(f'<path d="{wobble(x, cy, cw, ch, 20 + i, 1.6)}" fill="{t["paper"]}" stroke="{t["ink"]}" stroke-width="2"/>')
        s.text(f"AGENT {i + 1}", x + 22, cy + 32, "monob", 12, t["muted"], track=2)
        s.text(name, x + 22, cy + 66, "semi", 27, t["ink"])
        s.text(cid, x + 22, cy + 94, "monob", 14, t["ink"])
        s.text(link, x + 22 + F["monob"].width(cid, 14) + 10, cy + 94, "mono", 14, t["muted"])
        # quote
        qy = cy + 138
        s.text("“renews automatically", x + 22, qy, "mono", 16, t["ink"])
        pre = "every "
        w0 = F["mono"].width(pre, 16)
        w1 = F["monob"].width("24", 16)
        s.text(pre, x + 22, qy + 25, "mono", 16, t["ink"])
        s.add(f'<rect x="{x + 22 + w0 - 3}" y="{qy + 7}" width="{w1 + 6}" height="24" fill="{t["pink"]}"/>')
        s.text("24", x + 22 + w0, qy + 25, "monob", 16, t["onpink"])
        s.text(" months”", x + 22 + w0 + w1, qy + 25, "mono", 16, t["ink"])
        if i == 0:
            r_quote = (x, qy + 18)
        if i < 2:
            ax0, ax1, ay = x + cw + 6, xs[i + 1] - 8, cy + ch / 2
            s.add(f'<path d="M{ax0} {ay} H{ax1 - 9}" stroke="{t["blue"]}" stroke-width="3"/>')
            s.add(arrowhead(ax1, ay, "right", t["blue"]))

    s.text("FINAL OUTPUT · LOOKS CLEAN", xs[2] + cw, cy - 14, "monob", 12, t["muted"],
           anchor="end", track=1.6)
    s.text("carried forward, unchanged", xs[1] + 22, cy + ch - 18, "mono", 13, t["muted"])
    s.text("carried forward, unchanged", xs[2] + 22, cy + ch - 18, "mono", 13, t["muted"])

    # stamp on the researcher
    stx, sty = xs[0] + 150, cy + ch - 8
    s.add(f'<g transform="rotate(-7 {stx} {sty})">')
    sw_ = F["semi"].width("ORIGINATED HERE", 17, 1.2) + 26
    s.add(f'<rect x="{stx - sw_ / 2}" y="{sty - 22}" width="{sw_}" height="36" fill="{t["paper"]}" stroke="{t["pinkt"]}" stroke-width="3"/>')
    s.add(f'<rect x="{stx - sw_ / 2 + 4}" y="{sty - 18}" width="{sw_ - 8}" height="28" fill="none" stroke="{t["pinkt"]}" stroke-width="1.2"/>')
    s.text("ORIGINATED HERE", stx, sty + 2, "semi", 17, t["pinkt"], anchor="middle", track=1.2)
    s.add("</g>")

    # mismatch link: source "12" vs researcher "24"
    ex, ey = r_quote[0] - 4, r_quote[1] - 6
    mx = (sx + sw + xs[0]) / 2 + 4
    s.add(f'<path d="M{twelve_x + 14} {twelve_y - 4} H{mx} V{ey} H{ex}" '
          f'fill="none" stroke="{t["pinkt"]}" stroke-width="2" stroke-dasharray="5 5"/>')
    cyy = (twelve_y - 4 + ey) / 2
    s.add(f'<circle cx="{mx}" cy="{cyy}" r="15" fill="{t["pink"]}" stroke="{t["bg"]}" stroke-width="3"/>')
    s.text("≠", mx, cyy + 7, "monob", 20, t["onpink"], anchor="middle")

    # ---- the tattle: summarizer -> researcher -----------------------------
    by = 690
    x_from = xs[2] + cw / 2
    x_to = xs[0] + cw / 2 - 40
    s.add(f'<path d="M{x_from} {cy + ch + 10} V{by} H{x_to} V{cy + ch + 46}" fill="none" '
          f'stroke="{t["pink"]}" stroke-width="5" stroke-linejoin="round"/>')
    s.add(arrowhead(x_to, cy + ch + 30, "up", t["pink"], 16))
    label = "inherited from: researcher (c_005)"
    lw = F["monob"].width(label, 16) + 36
    lx = (x_from + x_to) / 2 + 60
    s.add(f'<rect x="{lx - lw / 2}" y="{by - 21}" width="{lw}" height="42" fill="{t["pink"]}"/>')
    s.text(label, lx, by + 6, "monob", 16, t["onpink"], anchor="middle")
    s.text("NOT_IN_SOURCE", x_from + 12, cy + ch + 40, "monob", 13, t["pinkt"], track=1)
    s.text("report line, verbatim", lx, by + 44, "mono", 12, t["muted"], anchor="middle")

    # footer
    s.add(f'<path d="M48 {H - 46} H{W - 48}" stroke="{t["rule"]}" stroke-width="1.5"/>')
    s.text("BINARY VERDICT   ·   EXACT MATCH AFTER NORMALIZATION   ·   ZERO MODEL CALLS   ·   NO PERSISTENCE",
           48, H - 18, "monom", 13, t["muted"], track=1.4)
    return s.done()


# --------------------------------------------------------------------------
# VERDICT PATH — messy inputs, rigid rail
# --------------------------------------------------------------------------
def verdict(t: dict) -> str:
    W, H = 1280, 560
    s = SVG(
        W, H, t,
        "How Tattletale decides a verdict",
        "An agent's claim and the source document both pass through the same normalize "
        "function, the source once at load with a SHA-256 hash. The claim then meets "
        "three ordered gates, first failure wins: empty quote gives EMPTY_QUOTE, unknown "
        "source gives UNKNOWN_SOURCE, quote not an exact substring gives NOT_IN_SOURCE. "
        "Claims that failed or carry derived_from then get a lineage walk; a missing "
        "parent or a cycle gives BROKEN_LINEAGE, which can overturn a pass. The verdict "
        "is PASSED or FAILED with origin_agent and origin_claim_id.",
    )
    s.text("HOW A VERDICT IS MADE", 48, 56, "monob", 13, t["blue"], track=2)
    s.text("The inputs are messy. The verdict path isn’t.", 48, 100, "semi", 34, t["ink"])

    rail_y = 268

    # messy inputs
    def blob(x, y, w, h, seed, rot, head, sub):
        s.add(f'<g transform="rotate({rot} {x + w / 2} {y + h / 2})">')
        s.add(f'<path d="{wobble(x + 6, y + 6, w, h, seed + 9, 3.5, 5)}" fill="url(#half)" opacity=".45"/>')
        s.add(f'<path d="{wobble(x, y, w, h, seed, 3.5, 5)}" fill="{t["paper"]}" stroke="{t["ink"]}" stroke-width="2"/>')
        s.text(head, x + 18, y + 36, "semi", 21, t["ink"])
        s.text(sub, x + 18, y + 62, "mono", 13, t["muted"])
        s.add("</g>")

    blob(48, 150, 236, 84, 7, -2.5, "CLAIM", "from an agent")
    s.text("id · text · source · derived_from", 52, 256, "mono", 12, t["muted"])
    blob(48, 316, 236, 84, 8, 1.8, "SOURCE", "raw document text")

    # normalize boxes (rigid)
    nx, nw = 336, 196
    for y, a, b in [(162, "normalize(quote)", "at check time"), (328, "normalize(source)", "at load · sha256")]:
        s.add(f'<rect x="{nx}" y="{y}" width="{nw}" height="62" fill="{t["paper"]}" stroke="{t["blue"]}" stroke-width="2.5"/>')
        s.text(a, nx + 16, y + 28, "monob", 15, t["ink"])
        s.text(b, nx + 16, y + 49, "mono", 12, t["muted"])
        s.add(f'<path d="M290 {y + 31} H{nx - 10}" stroke="{t["blue"]}" stroke-width="2.5"/>')
        s.add(arrowhead(nx - 2, y + 31, "right", t["blue"], 10))
    s.text("same 5 rules", nx + nw / 2, 268, "monob", 12, t["blue"], anchor="middle", track=1)
    s.text("both sides", nx + nw / 2, 286, "mono", 12, t["muted"], anchor="middle")

    # merge into rail
    mx = 562
    s.add(f'<path d="M{nx + nw} 193 H{mx} V{rail_y}" fill="none" stroke="{t["blue"]}" stroke-width="3"/>')
    s.add(f'<path d="M{nx + nw} 359 H{mx} V{rail_y}" fill="none" stroke="{t["blue"]}" stroke-width="3"/>')

    vx = 1050  # verdict block x
    s.add(f'<path d="M{mx} {rail_y} H{vx - 12}" stroke="{t["blue"]}" stroke-width="5"/>')
    s.add(arrowhead(vx - 2, rail_y, "right", t["blue"], 16))

    gates = [
        (620, "1", ["empty after", "normalize?"], "EMPTY_QUOTE", []),
        (744, "2", ["source", "loaded?"], "UNKNOWN_SOURCE", []),
        (868, "3", ["exact", "substring?"], "NOT_IN_SOURCE", []),
        (994, "4", ["lineage", "intact?"], "BROKEN_LINEAGE", ["missing parent", "or cycle"]),
    ]
    for gx, n, q, code, note in gates:
        s.add(f'<path d="M{gx} {rail_y + 18} V{rail_y + 92}" stroke="{t["pink"]}" stroke-width="3"/>')
        s.add(arrowhead(gx, rail_y + 102, "down", t["pink"], 11))
        s.add(f'<circle cx="{gx}" cy="{rail_y}" r="17" fill="{t["bg"]}" stroke="{t["blue"]}" stroke-width="3"/>')
        s.text(n, gx, rail_y + 6, "monob", 16, t["blue"], anchor="middle")
        for j, ln in enumerate(q):
            s.text(ln, gx, rail_y - 58 + j * 18, "mono", 13, t["ink"], anchor="middle")
        s.text(code, gx, rail_y + 126, "monob", 12, t["pinkt"], anchor="middle")
        for j, ln in enumerate(note):
            s.text(ln, gx, rail_y + 146 + j * 16, "mono", 12, t["muted"], anchor="middle")

    # bracket: first failure wins
    by_ = rail_y + 152
    s.add(f'<path d="M604 {by_} V{by_ + 10} H884 V{by_}" fill="none" stroke="{t["muted"]}" stroke-width="1.5"/>')
    s.text("checked in order · first failure wins", 744, by_ + 30, "mono", 12, t["muted"], anchor="middle")
    s.text("only if failed or derived_from set", 994, rail_y - 86, "mono", 11, t["muted"], anchor="middle")
    s.text("can overturn a pass", 994, rail_y + 178, "mono", 12, t["muted"], anchor="middle")

    # verdict block — the severe end
    vw, vh = 182, 156
    vy = rail_y - vh / 2
    s.add(f'<rect x="{vx + 7}" y="{vy + 7}" width="{vw}" height="{vh}" fill="{t["pink"]}"/>')
    s.add(f'<rect x="{vx}" y="{vy}" width="{vw}" height="{vh}" fill="{t["ink"]}"/>')
    s.text("VERDICT", vx + 18, vy + 30, "monob", 12, t["bg"], track=2, op=".7")
    s.text("PASSED", vx + 18, vy + 72, "xblack", 28, t["bg"], track=-0.5)
    s.text("FAILED", vx + 18, vy + 106, "xblack", 28, t["bg"], track=-0.5)
    s.text("+ origin_agent", vx + 18, vy + 130, "mono", 12, t["bg"], op=".75")
    s.text("+ origin_claim_id", vx + 18, vy + 146, "mono", 12, t["bg"], op=".75")

    # rule of attribution
    s.add(f'<path d="M48 {H - 82} H{W - 48}" stroke="{t["rule"]}" stroke-width="1.5"/>')
    s.text("Attribution rule:", 48, H - 46, "semi", 16, t["ink"])
    s.text("walk derived_from to the root; if a child's normalized quote differs from its parent's, "
           "the child owns the failure.", 48 + F["semi"].width("Attribution rule:", 16) + 10,
           H - 46, "reg", 16, t["ink"])
    s.text("No similarity scores. No thresholds. No model calls anywhere in this path.", 48, H - 20,
           "mono", 13, t["muted"])
    return s.done()


def main() -> None:
    for mode, theme in THEMES.items():
        (OUT_DIR / f"tattletale-hero-{mode}.svg").write_text(hero(theme), encoding="utf-8")
        (OUT_DIR / f"tattletale-verdict-{mode}.svg").write_text(verdict(theme), encoding="utf-8")
    print("wrote", sorted(p.name for p in OUT_DIR.glob("tattletale-*.svg")))


if __name__ == "__main__":
    main()
