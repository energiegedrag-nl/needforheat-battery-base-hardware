"""Sketch of the BatteryBASE cell compartment as built (top view and section), to scale, from the values in kuip.py.

Run with the same Python as kuip.py:  python enclosure/sketch_contacts.py
Writes docs/images/sketch-aaa-contacts.png.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch

import kuip as K

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "docs", "images", "sketch-aaa-contacts.png")
W, H, R, WALL = K.CI_W, K.CI_H, K.CI_R, K.WALL
RED, BLUE, GREY, CELL, PCB, CRADLE = "#c92a2a", "#1c7ed6", "#495057", "#f4c27a", "#d3f9d8", "#adb5bd"


def note(ax, xy, txt, xt, yt, color=GREY):
    ax.annotate(txt, xy=xy, xytext=(xt, yt), fontsize=7.5, color=color, ha="left" if xt > xy[0] else "right",
                va="center", arrowprops=dict(arrowstyle="-", color=color, lw=0.6))


def top_view(ax):
    ax.set_title("Top view from the lid side (lid removed)", fontsize=11, weight="bold", loc="left")
    ax.add_patch(FancyBboxPatch((0, 0), W, H, boxstyle=f"round,pad=0,rounding_size={R}", fc="#e9ecef", ec=GREY))
    ax.add_patch(Rectangle((WALL, WALL), W - 2 * WALL, H - 2 * WALL, fc="white", ec=GREY, lw=0.8))
    ax.add_patch(Rectangle((K.INSET, K.INSET), W - 2 * K.INSET, H - 2 * K.INSET, fc=PCB, ec="#2b8a3e", lw=0.6, ls="--"))
    x0, x1 = WALL + K.CR_CLR, W - WALL - K.CR_CLR
    for y0, y1 in ((x0 * 0 + WALL + K.CR_CLR, K.Y_RIB), (H - K.Y_RIB, H - WALL - K.CR_CLR)):
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=CRADLE, ec=GREY, lw=0.5, hatch="////"))
    for y in K.SADDLE_Y:
        ax.add_patch(Rectangle((x0, y - K.SADDLE_W / 2), x1 - x0, K.SADDLE_W, fc=CRADLE, ec=GREY, lw=0.5, alpha=0.8))
    for xa in (x0, x1 - K.RAIL_W):
        ax.add_patch(Rectangle((xa, K.Y_RIB - 0.5), K.RAIL_W, H - 2 * K.Y_RIB + 1, fc=CRADLE, ec=GREY, lw=0.5))
    bx, by = K.BUS[0] - K.BUS_W / 2, K.BUS[1] - K.BUS_H / 2
    ax.add_patch(Rectangle((bx, by), K.BUS_W, K.BUS_H, fc="none", ec="black", ls=":", lw=1.0))
    for i, x in enumerate(K.CELL_X):
        y0 = K.cell_y0(i)
        ax.add_patch(Rectangle((x - K.AAA_D / 2, y0), K.AAA_D, K.AAA_L, fc=CELL, ec="#b07d2b", alpha=0.85))
        top_plus = K.PLUS_TOP[i]
        ax.text(x, y0 + 3, "+" if top_plus else "−", ha="center", va="center", fontsize=14, weight="bold",
                color=RED if top_plus else BLUE)
        ax.text(x, y0 + K.AAA_L - 3, "−" if top_plus else "+", ha="center", va="center", fontsize=14, weight="bold",
                color=BLUE if top_plus else RED)
    for name, end, xc, w, z0, pts in K.contact_list():
        plus = name.startswith("+")
        yp = K.Y_RIB if end == "top" else H - K.Y_RIB - K.PLATE_T
        ax.add_patch(Rectangle((xc - w / 2, yp), w, K.PLATE_T, fc=RED if plus else BLUE, ec="none"))
        yf = K.Y_FACE[0] if end == "top" else K.Y_FACE[1]
        s = 1 if end == "top" else -1
        if plus:
            ax.add_patch(Rectangle((xc - 2, yf if s > 0 else yf - K.BTN_H), 4, K.BTN_H, fc=RED, ec="none"))
        else:
            for k in range(4):
                yy = yf + s * (0.5 + k * 0.7)
                ax.plot([xc - 2.4, xc + 2.4], [yy, yy + s * 0.3], color=BLUE, lw=0.9)
    # series links on the PCB
    ax.plot([K.CELL_X[0], K.CELL_X[1]], [K.INSET + 0.4] * 2, color="#2b8a3e", lw=2.5)
    ax.plot([K.CELL_X[1], K.CELL_X[2]], [H - K.INSET - 0.4] * 2, color="#2b8a3e", lw=2.5)
    ax.set_xlim(-26, W + 28); ax.set_ylim(H + 8, -8); ax.set_aspect("equal"); ax.axis("off")
    ax.text(W / 2, -4.5, "top edge (HAT): the lid slides in here", ha="center", fontsize=7.5, color=GREY)
    ax.text(W / 2, H + 4.5, "bottom edge: the lid stops against this wall", ha="center", fontsize=7.5, color=GREY)
    note(ax, (K.CELL_X[2] + 3, K.Y_RIB), "+ plate MY-AAA-15-J (3x)\ntab soldered in a PCB slot", W + 2, 2, RED)
    note(ax, (K.CELL_X[2] + 3, H - K.Y_RIB), "− spring MY-AAA-16-J (3x)", W + 2, H + 1, BLUE)
    note(ax, (W - WALL - 1, K.Y_RIB - 0.8), "cradle rib: backs the plates,\nreaches to just under the lid", W + 2, 9)
    note(ax, (x0 + 2, K.SADDLE_Y[1]), f"cradle saddles at y = {K.SADDLE_Y[0]:g} and\n{K.SADDLE_Y[1]:g}: cells "
         f"{K.CELL_LIFT} mm up,\nclear of the bus header", -2, 32)
    note(ax, (bx, by + 4), "2x8 bus header (underside);\nits tails ≤ 0.4 mm proud here", -2, 46, "black")
    note(ax, ((K.CELL_X[0] + K.CELL_X[1]) / 2, K.INSET + 0.4), "series links: PCB tracks", -2, -2, "#2b8a3e")


def section(ax):
    ax.set_title("Section at the top end of a cell (side view)", fontsize=11, weight="bold", loc="left")
    gap, zp = K.GAP, K.Z_PCB
    ax.plot([-1, 22], [0, 0], color=GREY, lw=0.8)
    ax.text(21.5, -0.9, "CoreInk back / P1-BASE lid", fontsize=7, ha="right")
    ax.add_patch(Rectangle((0, 0), WALL, K.Z_LID, fc="#e9ecef", ec=GREY))  # top wall (left)
    ax.add_patch(Rectangle((K.INSET, gap), 20, K.PCB_T, fc=PCB, ec="#2b8a3e"))
    for xx, ww, hh in ((6, 3.0, 1.0), (10, 2.0, 0.9), (13.5, 4.0, 2.0), (18.5, 1.6, 0.6)):
        ax.add_patch(Rectangle((xx, gap - hh), ww, hh, fc="#343a40", ec="none"))
    ax.text(12, 0.5, f"electronics on the underside, ≤ {K.BOTTOM_PART_H:.1f} mm", fontsize=7, color="white",
            ha="center", va="center", bbox=dict(fc="#343a40", ec="none", pad=1))
    rib_x0 = WALL + K.CR_CLR
    ax.add_patch(Rectangle((rib_x0, zp), K.RIB_T, K.RIB_TOP - zp, fc=CRADLE, ec=GREY, hatch="////"))
    px = K.Y_RIB
    z0 = zp + K.PLATE_Z0
    ax.add_patch(Rectangle((px, z0), K.PLATE_T, K.SINGLE_H, fc=RED, ec="none"))
    ax.add_patch(Rectangle((px + 0.1, zp - (K.SINGLE_TAB - K.PLATE_Z0)), 0.3, K.SINGLE_TAB, fc=RED, ec="none"))
    ax.add_patch(Rectangle((px + K.PLATE_T, K.AXIS_Z - 2), K.BTN_H, 4, fc=RED, ec="none"))
    cx = px + K.PLATE_T + K.BTN_H
    ax.add_patch(Rectangle((cx, K.AXIS_Z - K.AAA_D / 2), 22 - cx, K.AAA_D, fc=CELL, ec="#b07d2b"))
    ax.plot([px - 0.5, 22], [K.AXIS_Z] * 2, color="#b07d2b", ls="-.", lw=0.6)
    ax.add_patch(Rectangle((0, K.Z_TOP), 22, K.LID_T, fc="#ced4da", ec=GREY, alpha=0.8))
    ax.text(14, K.Z_TOP + 0.9, f"sliding lid (in from this end), top at {K.Z_LID:.1f} mm", fontsize=7)
    ax.text(cx + 1, K.AXIS_Z + 0.4, f"cell axis {K.CONTACT_Z:.2f} mm above the PCB", fontsize=7)
    ax.text(cx + 1, zp + 0.25, f"cell {K.CELL_LIFT} mm above the PCB (saddle)", fontsize=7)
    ax.text(px + 0.6, zp - 2.2, "tab through the PCB,\nsoldered by JLCPCB", fontsize=6.5, color=RED)
    ax.text(rib_x0 - 0.1, K.RIB_TOP + 0.3, "rib", fontsize=6.5, ha="left")
    ax.set_xlim(-1, 22.5); ax.set_ylim(-2.5, K.Z_LID + 1.5); ax.set_aspect("equal"); ax.axis("off")


def main():
    fig = plt.figure(figsize=(16, 9.5), dpi=110)
    fig.suptitle(f"BatteryBASE cell compartment as built (to scale, mm): module {K.SHIP_T:.1f} mm thick incl. posts",
                 fontsize=13, weight="bold")
    top_view(fig.add_axes([0.0, 0.02, 0.52, 0.9]))
    section(fig.add_axes([0.53, 0.42, 0.46, 0.48]))
    ax = fig.add_axes([0.55, 0.02, 0.44, 0.36]); ax.axis("off")
    ax.text(0, 1, "Contacts (JLCPCB, 15 Nov 2026; THT, wave soldering, Economic PCBA)\n"
            "  MY-AAA-15-J  C51889749  + plate    907 in stock   3 per board\n"
            "  MY-AAA-16-J  C51889750  − spring   805 in stock   3 per board\n\n"
            "Considered and dropped\n"
            "  bridge MY-AAA-5214 (+ and − on one plate): fixes the cell axis at\n"
            "    7.0 mm above the PCB; a 2nd, mirrored bridge is not in the catalogue\n"
            "  leaf contacts MY-AAA-03/-07 (SMD): no spring = minus cue\n"
            "  3xAAA holder BH-AAA-A1AJ024: 37 ± 1 mm wide, does not fit (36.8)",
            va="top", family="monospace", fontsize=8.5)
    fig.savefig(OUT, facecolor="white")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
