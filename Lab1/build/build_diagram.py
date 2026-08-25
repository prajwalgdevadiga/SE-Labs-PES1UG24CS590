# -*- coding: utf-8 -*-
"""
Renders the UML use-case diagram to PDF + PNG (matplotlib) and emits an
editable draw.io / diagrams.net file from the same coordinates.

    python build_diagram.py
"""
import os
import textwrap
import xml.sax.saxutils as su

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyBboxPatch, Rectangle

from content import STUDENT, RELATIONSHIPS

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOCS = os.path.join(ROOT, "docs")
DIAG = os.path.join(ROOT, "diagram")

FIG_W, FIG_H = 14.0, 9.0
UX = 100.0 / FIG_W          # x data-units per inch
UY = 100.0 / FIG_H          # y data-units per inch

INK = "#1a1a1a"
LINE = "#333333"
UC_FILL = "#eef3fb"
UC_EDGE = "#2f5c9e"
INC_COL = "#1f7a4d"
EXT_COL = "#a0522d"
BOUND = "#555555"

RX, RY = 11.0, 5.2          # use-case ellipse radii, in data units

# ------------------------------------------------------------------ geometry
UC_POS = {
    "UC-02": (37.0, 82.0),
    "UC-01": (37.0, 67.0),
    "UC-03": (37.0, 52.0),
    "UC-04": (37.0, 34.0),
    "UC-05": (37.0, 16.0),
    "UC-09": (64.0, 82.0),
    "UC-06": (64.0, 59.5),
    "UC-10": (64.0, 43.0),
    "UC-07": (64.0, 28.0),
    "UC-08": (64.0, 12.0),
}

UC_LABEL = {
    "UC-01": "UC-01\nCustomize Monthly Box",
    "UC-02": "UC-02\nManage Preference Tags",
    "UC-03": "UC-03\nPause or Skip Billing Cycle",
    "UC-04": "UC-04\nProcess Renewal Billing",
    "UC-05": "UC-05\nGenerate Fulfillment Manifest",
    "UC-06": "UC-06\nValidate Customization Window",
    "UC-07": "UC-07\nAuthorize Payment",
    "UC-08": "UC-08\nExport Shipping Labels",
    "UC-09": "UC-09\nSuggest Substitute Item",
    "UC-10": "UC-10\nApply Loyalty Discount",
}

ACTOR_POS = {
    "Subscriber": (9.5, 70.0),
    "Billing Scheduler": (9.5, 39.0),
    "Fulfillment Lead": (9.5, 16.0),
    "Payment Gateway": (90.5, 28.0),
}

ACTOR_SUB = {
    "Subscriber": "«primary»",
    "Billing Scheduler": "«time actor»",
    "Fulfillment Lead": "«primary»",
    "Payment Gateway": "«external system»",
}

ASSOCIATIONS = [
    ("Subscriber", "UC-02"),
    ("Subscriber", "UC-01"),
    ("Subscriber", "UC-03"),
    ("Billing Scheduler", "UC-04"),
    ("Fulfillment Lead", "UC-05"),
    ("Payment Gateway", "UC-07"),
]

BOUNDARY = (22.0, 4.0, 78.0, 92.0)   # x0, y0, x1, y1


def edge_point(cx, cy, tx, ty):
    """Point where the line from (cx,cy) to (tx,ty) leaves the ellipse."""
    dx, dy = tx - cx, ty - cy
    n = ((dx / RX) ** 2 + (dy / RY) ** 2) ** 0.5
    if n == 0:
        return cx, cy
    return cx + dx / n, cy + dy / n


def actor_point(name, tx):
    x, y = ACTOR_POS[name]
    side = 1.0 if tx > x else -1.0
    return x + side * 3.2, y + 0.8


def draw_actor(ax, name):
    x, y = ACTOR_POS[name]
    hr_x, hr_y = 0.10 * UX, 0.10 * UY
    ax.add_patch(Ellipse((x, y + 3.8), 2 * hr_x, 2 * hr_y,
                         fill=False, ec=INK, lw=1.4, zorder=4))
    ax.plot([x, x], [y + 3.8 - hr_y, y - 2.0], color=INK, lw=1.4, zorder=4)
    ax.plot([x - 3.2, x + 3.2], [y + 1.4, y + 1.4], color=INK, lw=1.4, zorder=4)
    ax.plot([x, x - 2.6], [y - 2.0, y - 5.4], color=INK, lw=1.4, zorder=4)
    ax.plot([x, x + 2.6], [y - 2.0, y - 5.4], color=INK, lw=1.4, zorder=4)
    ax.text(x, y - 7.1, name, ha="center", va="top", fontsize=9.5,
            fontweight="bold", color=INK, zorder=4)
    ax.text(x, y - 9.6, ACTOR_SUB[name], ha="center", va="top", fontsize=7.5,
            style="italic", color="#666666", zorder=4)


def draw_uc(ax, uid):
    x, y = UC_POS[uid]
    ax.add_patch(Ellipse((x, y), 2 * RX, 2 * RY, facecolor=UC_FILL,
                         edgecolor=UC_EDGE, lw=1.3, zorder=3))
    head, title = UC_LABEL[uid].split("\n")
    wrapped = textwrap.fill(title, 20)
    ax.text(x, y + 1.9, head, ha="center", va="center", fontsize=7.4,
            fontweight="bold", color=UC_EDGE, zorder=4)
    ax.text(x, y - 1.0, wrapped, ha="center", va="center", fontsize=7.8,
            color=INK, zorder=4, linespacing=1.25)


def draw_stereotype(ax, src, dst, kind, note):
    sx, sy = edge_point(UC_POS[src][0], UC_POS[src][1], *UC_POS[dst])
    ex, ey = edge_point(UC_POS[dst][0], UC_POS[dst][1], *UC_POS[src])
    col = INC_COL if kind == "include" else EXT_COL
    ax.annotate("", xy=(ex, ey), xytext=(sx, sy),
                arrowprops=dict(arrowstyle="-|>", color=col, lw=1.2,
                                linestyle=(0, (5, 3)), shrinkA=0, shrinkB=0,
                                mutation_scale=13), zorder=5)
    mx, my = (sx + ex) / 2.0, (sy + ey) / 2.0
    ax.text(mx, my + 1.0, "«%s»" % kind, ha="center", va="bottom", fontsize=7.6,
            color=col, fontweight="bold", zorder=6,
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none"))
    if kind == "extend":
        ax.text(mx, my - 1.0, "[%s]" % note.replace("condition: ", ""),
                ha="center", va="top", fontsize=6.5, color=col, style="italic",
                zorder=6, bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))


def build():
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    x0, y0, x1, y1 = BOUNDARY
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False,
                           edgecolor=BOUND, lw=1.3, zorder=1))
    ax.text((x0 + x1) / 2.0, y1 - 1.6, STUDENT["system"], ha="center", va="top",
            fontsize=10.5, fontweight="bold", color=BOUND, zorder=2)

    for a in ACTOR_POS:
        draw_actor(ax, a)
    for u in UC_POS:
        draw_uc(ax, u)

    for actor, uid in ASSOCIATIONS:
        ax_, ay_ = actor_point(actor, UC_POS[uid][0])
        ex, ey = edge_point(UC_POS[uid][0], UC_POS[uid][1], ax_, ay_)
        ax.plot([ax_, ex], [ay_, ey], color=LINE, lw=1.1, zorder=2)

    for kind, src, dst, note in RELATIONSHIPS:
        draw_stereotype(ax, src, dst, kind, note)

    # title block
    ax.text(0.5, 99.5, "UML Use-Case Diagram - %s" % STUDENT["system"],
            ha="left", va="top", fontsize=13, fontweight="bold", color=INK)
    ax.text(0.5, 96.0, "%s  |  %s" % (STUDENT["ps"], STUDENT["topic"]),
            ha="left", va="top", fontsize=8.5, color="#555555")
    ax.text(99.5, 99.5, "%s  |  %s" % (STUDENT["name"], STUDENT["srn"]),
            ha="right", va="top", fontsize=8.5, color="#555555")

    # legend
    lg = FancyBboxPatch((78.6, 1.0), 21.0, 12.0,
                        boxstyle="round,pad=0.3", fc="#fafafa", ec="#cccccc", lw=0.8)
    ax.add_patch(lg)
    ax.text(79.6, 11.7, "Legend", fontsize=8.5, fontweight="bold", color=INK)
    ax.plot([79.8, 83.2], [9.0, 9.0], color=LINE, lw=1.1)
    ax.text(83.9, 9.0, "association (actor - use case)", fontsize=7, va="center", color=INK)
    ax.annotate("", xy=(83.2, 6.3), xytext=(79.8, 6.3),
                arrowprops=dict(arrowstyle="-|>", color=INC_COL, lw=1.2,
                                linestyle=(0, (5, 3)), mutation_scale=11))
    ax.text(83.9, 6.3, "«include» : base -> included", fontsize=7, va="center", color=INK)
    ax.annotate("", xy=(83.2, 3.6), xytext=(79.8, 3.6),
                arrowprops=dict(arrowstyle="-|>", color=EXT_COL, lw=1.2,
                                linestyle=(0, (5, 3)), mutation_scale=11))
    ax.text(83.9, 3.6, "«extend» : extension -> base", fontsize=7, va="center", color=INK)

    os.makedirs(DOCS, exist_ok=True)
    fig.savefig(os.path.join(DOCS, "02_UseCase_Diagram.pdf"),
                bbox_inches="tight", facecolor="white")
    fig.savefig(os.path.join(DOCS, "02_UseCase_Diagram.png"),
                dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote docs/02_UseCase_Diagram.pdf + .png")


# ------------------------------------------------------------------ draw.io
def dio(x):
    return 60 + x * 10.5


def dioy(y):
    return 50 + (100 - y) * 8.0


def xattr(value):
    """XML-escape a label and keep hard line breaks as mxGraph expects them."""
    return su.escape(value, {'"': "&quot;"}).replace(chr(10), "&#10;")


def build_drawio():
    cells = []
    nid = [2]

    def add(style, value, x, y, w, h, vid=None):
        i = vid or ("n%d" % nid[0])
        nid[0] += 1
        cells.append(
            '<mxCell id="%s" value="%s" style="%s" vertex="1" parent="1">'
            '<mxGeometry x="%.1f" y="%.1f" width="%.1f" height="%.1f" as="geometry"/>'
            "</mxCell>" % (i, xattr(value), style, x, y, w, h))
        return i

    def edge(src, dst, style, value=""):
        i = "n%d" % nid[0]
        nid[0] += 1
        cells.append(
            '<mxCell id="%s" value="%s" style="%s" edge="1" parent="1" source="%s" target="%s">'
            '<mxGeometry relative="1" as="geometry"/></mxCell>'
            % (i, xattr(value), style, src, dst))

    x0, y0, x1, y1 = BOUNDARY
    add("rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#555555;"
        "verticalAlign=top;fontSize=15;fontStyle=1;",
        STUDENT["system"], dio(x0), dioy(y1), (x1 - x0) * 10.5, (y1 - y0) * 8.0, vid="boundary")

    aid = {}
    for name, (x, y) in ACTOR_POS.items():
        aid[name] = add("shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;"
                        "html=1;outlineConnect=0;fontSize=12;",
                        name, dio(x) - 17, dioy(y) - 40, 34, 70)

    uid = {}
    for u, (x, y) in UC_POS.items():
        label = UC_LABEL[u]
        uid[u] = add("ellipse;whiteSpace=wrap;html=1;fillColor=#eef3fb;strokeColor=#2f5c9e;"
                     "fontSize=11;", label, dio(x) - RX * 10.5, dioy(y) - RY * 8.0,
                     RX * 21, RY * 16)

    for actor, u in ASSOCIATIONS:
        edge(aid[actor], uid[u],
             "endArrow=none;html=1;rounded=0;strokeColor=#333333;exitX=0.5;exitY=0.5;")

    for kind, src, dst, note in RELATIONSHIPS:
        col = "#1f7a4d" if kind == "include" else "#a0522d"
        lbl = "«%s»" % kind
        if kind == "extend":
            lbl += chr(10) + "[%s]" % note.replace("condition: ", "")
        edge(uid[src], uid[dst],
             "endArrow=open;endFill=0;dashed=1;html=1;rounded=0;strokeColor=%s;"
             "fontSize=10;fontColor=%s;" % (col, col), lbl)

    xml = (
        '<mxfile host="app.diagrams.net" modified="2026-01-01T00:00:00.000Z" '
        'agent="lab1" version="24.0.0" type="device">'
        '<diagram id="lab1-usecase" name="Use-Case Diagram">'
        '<mxGraphModel dx="1400" dy="900" grid="0" gridSize="10" guides="1" tooltips="1" '
        'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1600" '
        'pageHeight="1000" math="0" shadow="0">'
        "<root><mxCell id=\"0\"/><mxCell id=\"1\" parent=\"0\"/>"
        + "".join(cells) +
        "</root></mxGraphModel></diagram></mxfile>"
    )
    os.makedirs(DIAG, exist_ok=True)
    p = os.path.join(DIAG, "subscription_box_usecase.drawio")
    with open(p, "w", encoding="utf-8") as f:
        f.write(xml)
    print("wrote diagram/subscription_box_usecase.drawio")


if __name__ == "__main__":
    build()
    build_drawio()
