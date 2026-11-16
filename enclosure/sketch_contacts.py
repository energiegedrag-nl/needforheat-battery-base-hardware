"""Sketch of the BatteryBASE cell compartment as built (top view and two sections), to scale, from the values in
kuip.py.

Run with the same Python as kuip.py:  python enclosure/sketch_contacts.py
Writes docs/images/sketch-aaa-contacts.png.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle

import kuip as K

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "docs", "images", "sketch-aaa-contacts.png")
W, H, R, WALL = K.CI_W, K.CI_H, K.CI_R, K.WALL
RED, BLUE, GREY, CELL, PCB, CRADLE = "#c92a2a", "#1c7ed6", "#495057", "#f4c27a", "#d3f9d8", "#adb5bd"
METAL = "#868e96"
TRAY, LID, DARK = "#e9ecef", "#ced4da", "#343a40"


def note(ax, xy, txt, xt, yt, color=GREY, fs=7.5):
    ax.annotate(txt, xy=xy, xytext=(xt, yt), fontsize=fs, color=color, ha="left" if xt > xy[0] else "right",
                va="center", arrowprops=dict(arrowstyle="-", color=color, lw=0.6))


def pins():
    return [(K.BUS[0] + (c - 0.5) * 2.54, K.BUS[1] + (r - 3.5) * 2.54) for c in range(2) for r in range(8)]


def top_view(ax):
    ax.set_title("Top view from the lid side (lid removed)", fontsize=11, weight="bold", loc="left")
    ax.add_patch(FancyBboxPatch((0, 0), W, H, boxstyle=f"round,pad=0,rounding_size={R}", fc=TRAY, ec=GREY))
    ax.add_patch(Rectangle((WALL, WALL), W - 2 * WALL, H - 2 * WALL, fc="white", ec=GREY, lw=0.8))
    ax.add_patch(Rectangle((K.X_LEFT, K.Y_RIB), WALL - K.X_LEFT, H - 2 * K.Y_RIB, fc="white", ec=GREY, lw=0.6, ls="--"))
    ax.add_patch(Rectangle((K.INSET, K.INSET), W - 2 * K.INSET, H - 2 * K.INSET, fc=PCB, ec="#2b8a3e", lw=0.6, ls="--"))
    for (x, y) in K.PEGS:
        ax.add_patch(Circle((x, y), 1.1, fc="white", ec="#2b8a3e", lw=0.6))
    x0, x1 = WALL + K.CR_CLR, W - WALL - K.CR_CLR
    for y0, y1 in ((WALL + K.CR_CLR, K.Y_RIB), (H - K.Y_RIB, H - WALL - K.CR_CLR)):
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=CRADLE, ec=GREY, lw=0.5, hatch="////"))
    for y in K.SADDLE_Y:
        ax.add_patch(Rectangle((K.X_STOP, y - K.SADDLE_W / 2), x1 - K.X_STOP, K.SADDLE_W, fc=CRADLE, ec=GREY, lw=0.5))
    kx = K.KEY_W / 2 + K.KEY_CLR
    ax.add_patch(Rectangle((K.KEY_X - kx, K.KEY_Y0), 2 * kx, WALL - K.KEY_Y0, fc="white", ec=GREY, lw=0.5))
    ax.add_patch(Rectangle((K.KEY_X - K.KEY_W / 2, WALL + K.CR_CLR - K.KEY_D), K.KEY_W, K.KEY_D, fc=CRADLE, ec=GREY,
                           lw=0.5, hatch="////"))
    ax.add_patch(Rectangle((x1 - K.RAIL_W, K.Y_RIB - 0.5), K.RAIL_W, H - 2 * K.Y_RIB + 1, fc=CRADLE, ec=GREY, lw=0.5))
    for xb in K.BAR_X:  # low bars between the cells (drawn over the cells: they lie in the wedge under them)
        ax.add_patch(Rectangle((xb - K.BAR_W / 2, K.Y_RIB - 0.5), K.BAR_W, H - 2 * K.Y_RIB + 1, fc=CRADLE, ec=GREY,
                               lw=0.5, zorder=3))
    bx, by = K.BUS[0] - K.BUS_W / 2, K.BUS[1] - K.BUS_H / 2
    ax.add_patch(Rectangle((bx, by), K.BUS_W, K.BUS_H, fc="none", ec="black", ls=":", lw=1.0))
    for (px, py) in pins():
        ax.add_patch(Rectangle((px - 0.32, py - 0.32), 0.64, 0.64, fc="black", ec="none"))
    for i, x in enumerate(K.CELL_X):
        y0 = K.cell_y0(i)
        ax.add_patch(Rectangle((x - K.AAA_D / 2, y0), K.AAA_D, K.AAA_L, fc=CELL, ec="#b07d2b", alpha=0.75))
        top_plus = K.PLUS_TOP[i]
        ax.text(x, y0 + 3, "+" if top_plus else "−", ha="center", va="center", fontsize=14, weight="bold",
                color=RED if top_plus else BLUE)
        ax.text(x, y0 + K.AAA_L - 3, "−" if top_plus else "+", ha="center", va="center", fontsize=14, weight="bold",
                color=BLUE if top_plus else RED)
    for end, xc, pol, yo, yi in K.contact_list():  # leaf contacts: foot under the cell, leaf at the bend, two pins
        k = 0 if end == "top" else 1
        sgn = 1 if end == "top" else -1
        yb = K.Y_BEND[k]
        col = RED if pol == "+" else BLUE
        yf = yo - sgn * K.FTAB_OUT + sgn * K.FOOT_L  # inner end of the foot
        yt = yo - sgn * K.FTAB_OUT  # outer end of the tab behind the leaf
        ax.add_patch(Rectangle((xc - K.LEAF_W / 2, min(yb, yf)), K.LEAF_W, abs(yf - yb), fc=METAL,
                               ec=col, lw=0.8, alpha=0.35, zorder=2))
        ax.add_patch(Rectangle((xc - K.FTAB_W / 2, min(yb, yt)), K.FTAB_W, abs(yb - yt), fc=METAL,
                               ec=col, lw=0.8, alpha=0.6, zorder=4))
        ax.plot([xc - K.LEAF_W / 2, xc + K.LEAF_W / 2], [yb] * 2, color=col, lw=2.2, zorder=4)
        for y in (yo, yi):
            ax.add_patch(Circle((xc, y), K.PIN_D / 2, fc=col, ec="none", zorder=4))
    ax.plot([K.CELL_X[0], K.CELL_X[1]], [K.INSET + 0.4] * 2, color="#2b8a3e", lw=2.5)
    ax.plot([K.CELL_X[1], K.CELL_X[2]], [H - K.INSET - 0.4] * 2, color="#2b8a3e", lw=2.5)
    ax.plot([0, W], [K.BUS[1]] * 2, color="black", lw=0.8, ls="-.")
    ax.text(W + 0.5, K.BUS[1], "A", fontsize=10, weight="bold", va="center")
    ax.text(-0.5, K.BUS[1], "A", fontsize=10, weight="bold", va="center", ha="right")
    ax.set_xlim(-24, W + 25); ax.set_ylim(H + 8, -8); ax.set_aspect("equal"); ax.axis("off")
    ax.text(W / 2, -4.5, "top edge (HAT): the lid slides in here", ha="center", fontsize=7.5, color=GREY)
    ax.text(W / 2, H + 4.5, "bottom edge: the lid stops against this wall", ha="center", fontsize=7.5, color=GREY)
    note(ax, (K.CONTACT_X[2] + 2, K.Y_BEND[0]), f"leaf contact {K.LEAF_PART} (6x, same part\nat both ends; red +, blue −):"
         "\nleaf at the end, foot under the cell,\ntwo pins through the PCB", W + 2, 1, RED)
    note(ax, (K.CONTACT_X[2] + K.LEAF_W / 2, H - 10), "cell 3's contacts sit "
         f"{K.CELL_X[2] - K.CONTACT_X[2]:.2f} mm left\nof its axis: foot clear of the\nheader's tails", W + 2, H - 4,
         BLUE)
    note(ax, (W - WALL - 1, K.Y_RIB - 0.6), f"cradle rib ({K.RIB_T} mm): stop for\na leaf pushed too far; low notch\n"
         "over each contact's tab", W + 2, 8)
    note(ax, (K.KEY_X, WALL - 0.4), "key: lip on the rib in a groove\nin the top wall (off centre)", W + 2, -5)
    note(ax, (W - WALL - 1, K.SADDLE_Y[1]), "cradle stops right of\ncell 3 (y = " +
         ", ".join(f"{y:g}" for y in K.SADDLE_Y) + ")\nand side rail", W + 2, 20)
    note(ax, (K.BAR_X[0], 20), f"cradle bars between the cells\n({K.BAR_W:g} x {K.BAR_H:g} mm, rib to rib,\n"
         "between the contacts' feet)", -2, 20)
    note(ax, (K.X_LEFT + 0.2, 30), f"left wall {K.WALL_THIN:g} mm thin\nwhere cell 1 bulges", -2, 30)
    note(ax, (bx + 1, by + 3), "2x8 bus header (underside, THT);\nits tails 1.4 mm proud, under cell 3", -2, 42, "black")
    note(ax, (K.PEGS[1][0], K.PEGS[1][1]), "pegs as on the P1-BASE v3", -2, 51, "#2b8a3e")
    note(ax, ((K.CELL_X[0] + K.CELL_X[1]) / 2, K.INSET + 0.4), "series links: PCB tracks", -2, -2, "#2b8a3e")


def side_section(ax):
    ax.set_title("Section along a cell, at its top end", fontsize=11, weight="bold", loc="left")
    gap, zp = K.GAP, K.Z_PCB
    ax.plot([-1, 22], [0, 0], color=GREY, lw=0.8)
    ax.text(21.5, -0.9, "CoreInk back / P1-BASE lid", fontsize=7, ha="right")
    ax.add_patch(Rectangle((0, 0), WALL, K.Z_LID, fc=TRAY, ec=GREY))
    ax.add_patch(Rectangle((K.INSET, gap), 20.5, K.PCB_T, fc=PCB, ec="#2b8a3e"))
    for xx, ww, hh in ((9.5, 3.0, 1.0), (13.5, 2.0, 0.9), (16.5, 4.0, 2.0)):
        ax.add_patch(Rectangle((xx, gap - hh), ww, hh, fc=DARK, ec="none"))
    ax.text(15, 0.45, f"electronics underneath, ≤ {K.BOTTOM_PART_H:.1f} mm", fontsize=6.5, color="white",
            ha="center", va="center", bbox=dict(fc=DARK, ec="none", pad=1))
    rib_x0 = WALL + K.CR_CLR
    nh = K.FTAB_T + K.TAB_NOTCH_CLR  # notch over the contact's tab
    ax.add_patch(Rectangle((rib_x0, zp + nh), K.RIB_T, K.RIB_TOP - zp - nh, fc=CRADLE, ec=GREY, hatch="////"))
    yb, yo = K.Y_BEND[0], K.Y_PIN_OUT[0]
    z0 = zp + K.FOOT_T
    ce = K.cell_y0(0)  # the cell's end; the leaf pressed back so that its dimple touches it
    lean = ce - yb - K.DIMPLE_H
    top = lean * K.LEAF_H / K.DIMPLE_Z
    yf = yo - K.FTAB_OUT + K.FOOT_L  # inner end of the foot
    ax.add_patch(Rectangle((yb, z0 - K.LEAF_T), yf - yb, K.LEAF_T, fc=RED, ec="none"))  # raised foot
    ax.add_patch(Rectangle((yo - K.FTAB_OUT, zp), yb - (yo - K.FTAB_OUT), K.FTAB_T, fc=RED, ec="none"))  # tab
    ax.add_patch(Rectangle((yf - 3.5, zp), 3.5, K.FTAB_T, fc=RED, ec="none"))  # inner end on the PCB
    ax.plot([yb, yb], [zp, z0], color=RED, lw=1.2)
    ax.add_patch(Polygon([(yb, zp), (yb - K.LEAF_T, zp), (yb - K.LEAF_T + top, z0 + K.LEAF_H), (yb + top, z0 + K.LEAF_H)],
                         closed=True, fc=RED, ec="none"))
    yd = yb + lean
    ax.add_patch(Rectangle((yd, z0 + K.DIMPLE_Z - 1.25), K.DIMPLE_H, 2.5, fc=RED, ec="none"))
    for y in (yo, yo + K.PIN_PITCH):
        ax.add_patch(Rectangle((y - K.PIN_D / 2, zp - K.PIN_LEN), K.PIN_D, K.PIN_LEN, fc=RED, ec="none"))
        ax.add_patch(Polygon([(y - 1.0, gap), (y + 1.0, gap), (y + 0.5, gap - 0.4), (y - 0.5, gap - 0.4)], closed=True,
                             fc="#adb5bd", ec="none"))
    ax.add_patch(Rectangle((ce, z0), 22 - ce, K.AAA_D, fc=CELL, ec="#b07d2b"))
    ax.add_patch(Rectangle((ce - 0.8, K.AXIS_Z - 1.9), 0.8, 3.8, fc=CELL, ec="#b07d2b"))  # + nub
    ax.plot([yb - 1, 22], [K.AXIS_Z] * 2, color="#b07d2b", ls="-.", lw=0.6)
    ax.plot([yb - 1, ce + 7], [zp + K.CONTACT_C] * 2, color=RED, ls=":", lw=0.8)
    ax.add_patch(Rectangle((0, K.Z_TOP), 22, K.LID_T, fc=LID, ec=GREY, alpha=0.8))
    ax.text(14, K.Z_TOP + 0.9, f"sliding lid, top at {K.Z_LID:.1f} mm", fontsize=7)
    ax.text(ce + 7.3, K.AXIS_Z - 0.6, f"cell axis {K.CONTACT_Z:.2f} above the PCB", fontsize=7)
    ax.text(ce + 7.3, zp + K.CONTACT_C + 0.3, f"dimple centre {K.CONTACT_C:.2f}", fontsize=7, color=RED)
    ax.text(ce + 1, z0 + 0.5, f"cell lies on the raised foot ({K.FOOT_T:g} mm)", fontsize=7)
    ax.text(WALL + 0.3, gap - 1.0, f"pins {K.PIN_D:g} x 0.25 x {K.PIN_LEN:g} in the PCB,\nsoldered underneath", fontsize=6.5,
            color=RED)
    ax.text(rib_x0 - 0.1, K.RIB_TOP + 0.3, "rib", fontsize=6.5, ha="left")
    ax.text(yb + top + 0.4, z0 + K.LEAF_H - 0.6, f"leaf {K.LEAF_PART}, gives way\n{K.LEAF_DEFL[0]:.1f}–{K.LEAF_DEFL[1]:.1f} mm",
            fontsize=6.5, color=RED)
    ax.set_xlim(-1, 22.5); ax.set_ylim(-2.5, K.Z_LID + 1.5); ax.set_aspect("equal"); ax.axis("off")


def cross_section(ax):
    ax.set_title(f"Section A–A across the cells at y = {K.BUS[1]:.1f} (through the bus header), "
                 "seen towards the bottom edge", fontsize=11, weight="bold", loc="left")
    gap, zp = K.GAP, K.Z_PCB
    ax.plot([-1, W + 1], [0, 0], color=GREY, lw=0.8)
    # tray: long walls (thin part on the left), lid in its grooves
    for xa, xb in ((0, WALL), (W - WALL, W)):
        ax.add_patch(Rectangle((xa, 0), xb - xa, K.Z_TOP, fc=TRAY, ec=GREY, lw=0.8))
    ax.add_patch(Rectangle((K.X_LEFT, K.THIN_Z[0]), WALL - K.X_LEFT, K.THIN_Z[1] - K.THIN_Z[0], fc="white", ec=GREY,
                           lw=0.6))
    lid = [(0, K.Z_TOP + K.GR_H), (WALL - K.GR_D, K.Z_TOP + K.GR_H), (WALL - K.GR_D, K.Z_TOP), (W - WALL + K.GR_D, K.Z_TOP),
           (W - WALL + K.GR_D, K.Z_TOP + K.GR_H), (W, K.Z_TOP + K.GR_H), (W, K.Z_LID), (0, K.Z_LID)]
    ax.add_patch(Polygon(lid, closed=True, fc=LID, ec=GREY, lw=0.8))
    # PCB, electronics and the bus header underneath
    ax.add_patch(Rectangle((K.INSET, gap), W - 2 * K.INSET, K.PCB_T, fc=PCB, ec="#2b8a3e"))
    for xx, ww, hh in ((9, 3.0, 1.0), (14, 3.0, 1.6), (19, 4.0, 2.0), (24.5, 2.0, 0.9)):
        ax.add_patch(Rectangle((xx, gap - hh), ww, hh, fc=DARK, ec="none"))
    ax.add_patch(Rectangle((K.BUS[0] - K.BUS_W / 2, 0), K.BUS_W, gap, fc="#212529", ec="none"))
    for c in range(2):
        px = K.BUS[0] + (c - 0.5) * 2.54
        ax.add_patch(Rectangle((px - 0.32, -1.2), 0.64, gap + 1.2 + K.PCB_T + K.HDR_TAIL, fc="#fab005", ec="#e67700",
                               lw=0.4))
        ax.add_patch(Polygon([(px - 0.85, zp), (px + 0.85, zp), (px + 0.32, zp + K.HDR_FILLET),
                              (px - 0.32, zp + K.HDR_FILLET)], closed=True, fc="#adb5bd", ec="none"))
    ax.text(K.BUS[0], -1.9, "pins on into the CoreInk", fontsize=6.5, ha="center")
    # leaf contacts at the bottom end (behind the section) with their dimples; their feet reach in under the cells
    # past the section (cut, filled)
    for end, xc, pol, yo, yi in K.contact_list():
        if end != "bottom":
            continue
        col = RED if pol == "+" else BLUE
        ax.add_patch(Rectangle((xc - K.LEAF_W / 2, zp), K.LEAF_W, K.FOOT_T + K.LEAF_H, fc="none", ec=col, lw=0.9,
                               ls="--"))
        ax.add_patch(Circle((xc, zp + K.CONTACT_C), 1.25, fc="none", ec=col, lw=0.9, ls="--"))
        if yo + K.FTAB_OUT - K.FOOT_L < K.BUS[1]:
            ax.add_patch(Rectangle((xc - K.LEAF_W / 2, zp), K.LEAF_W, K.FOOT_T, fc=col, ec="none", zorder=4))
    # cradle: side rail (cut) and the stop at y = 48 (behind)
    x1 = W - WALL - K.CR_CLR
    ax.add_patch(Rectangle((x1 - K.RAIL_W, zp), K.RAIL_W, K.RAIL_H, fc=CRADLE, ec=GREY, hatch="////", lw=0.5))
    ax.add_patch(Rectangle((K.X_STOP, zp), x1 - K.X_STOP, K.STOP_H, fc="none", ec=GREY, lw=0.9, ls="--"))
    for xb in K.BAR_X:  # low bars between the cells (cut)
        ax.add_patch(Rectangle((xb - K.BAR_W / 2, zp), K.BAR_W, K.BAR_H, fc=CRADLE, ec=GREY, hatch="////", lw=0.5,
                               zorder=4))
    # cells: nominal (solid), the tolerance cases (dashed)
    for x in K.CELL_X:
        ax.add_patch(Circle((x, K.AXIS_Z), K.AAA_D / 2, fc=CELL, ec="#b07d2b", alpha=0.85))
        ax.plot([x], [K.AXIS_Z], marker="+", color="#b07d2b")
    dm, dn = K.AAA_D_MAX, K.AAA_D_MIN
    rr = K._bar_reach(dm / 2) + K.BAR_W / 2  # thick cells rolled left, each in its own lane (wall or bar)
    for xc in [K.X_LEFT + dm / 2] + [xb + rr for xb in K.BAR_X]:
        ax.add_patch(Circle((xc, zp + K.CELL_LIFT + dm / 2), dm / 2, fc="none", ec="#e8590c", lw=0.7, ls=(0, (3, 2))))
    ax.add_patch(Circle((K.X_STOP - dn / 2, zp + K.CELL_LIFT + dn / 2), dn / 2, fc="none", ec="#5f3dc4", lw=0.7,
                        ls=(0, (3, 2))))
    ax.set_xlim(-14, W + 16); ax.set_ylim(-3, K.Z_LID + 1.2); ax.set_aspect("equal"); ax.axis("off")
    note(ax, (K.X_LEFT + 0.3, K.AXIS_Z), f"left wall {K.WALL_THIN:g} mm\n(else {WALL:g}) where\ncell 1 bulges", -1.5,
         K.AXIS_Z + 1.0)
    note(ax, (K.CELL_X[0] - 3.5, zp + 1), "cells lie on the contacts'\nfeet (cut, filled);\neach rolls in its lane",
         -1.5, zp + 1.5)
    note(ax, (K.CELL_X[0] - 2, zp + K.CONTACT_C + 2), "leaves at the bottom end\n(behind, dashed), dimple\n"
         "against the cell's end", -1.5, K.Z_LID - 0.3, RED)
    note(ax, (x1 - 0.6, zp + 3.5), f"cradle side rail\nand stop at x = {K.X_STOP:.2f}\n(dashed: behind, y = 48)",
         W + 1.5, zp + 7.5)
    note(ax, (K.BAR_X[1] + K.BAR_W / 2, zp + K.BAR_H - 0.3), f"cradle bars ({K.BAR_W:g} x {K.BAR_H:g} mm), cut,\n"
         "in the wedge under two cells", W + 1.5, zp + 4.3)
    note(ax, (K.BUS[0] + 1.27, zp + K.HDR_TAIL), "header tails 1.4 mm proud,\nsolder fillets", W + 1.5, zp + 1.0,
         "black")
    note(ax, (K.CELL_X[0] - 4.2, K.AXIS_Z + 3.5), f"dashed orange: {dm:g} mm cells rolled\nleft, each in its lane",
         -1.5, K.AXIS_Z + 4.8, "#e8590c")
    note(ax, (K.X_STOP - dn / 2 + 3, zp + dn - 1.5), f"dashed purple: a {dn:g} mm cell 3\nagainst the stop", W + 1.5,
         K.Z_LID - 1.5, "#5f3dc4")


def pin_zoom(ax):
    ax.set_title("A–A, detail at the header's tails", fontsize=10, weight="bold", loc="left")
    zp = K.Z_PCB
    ax.add_patch(Rectangle((K.BUS[0] - 3, zp - 0.6), 6.5, 0.6, fc=PCB, ec="#2b8a3e"))
    for c in range(2):
        px = K.BUS[0] + (c - 0.5) * 2.54
        ax.add_patch(Rectangle((px - 0.32, zp - 0.6), 0.64, 0.6 + K.HDR_TAIL, fc="#fab005", ec="#e67700", lw=0.4))
        ax.add_patch(Polygon([(px - 0.85, zp), (px + 0.85, zp), (px + 0.32, zp + K.HDR_FILLET),
                              (px - 0.32, zp + K.HDR_FILLET)], closed=True, fc="#adb5bd", ec="none"))
    rows = []
    for d, col, ls in ((K.AAA_D, "#b07d2b", "-"), (K.AAA_D_MIN, "#5f3dc4", "--"), (K.AAA_D_MAX, "#e8590c", ":")):
        r = d / 2
        xc = K.X_STOP - r
        ax.add_patch(Circle((xc, zp + K.CELL_LIFT + r), r, fc="none", ec=col, lw=1.0, ls=ls))
        dx = K.PIN_X_IN - K.HDR_PIN_W / 2 - xc
        clr = K.CELL_LIFT + r - (r * r - dx * dx) ** 0.5 - K.HDR_TAIL
        rows.append(f"{d:g} mm cell: {clr:.2f} mm")
    x1 = K.CI_W - K.WALL - K.CR_CLR
    ax.add_patch(Rectangle((K.X_STOP, zp), x1 - K.X_STOP, K.STOP_H, fc="none", ec=GREY, lw=0.9, ls="--"))
    ax.text(K.BUS[0] + 2.5, zp + 3.6, "stop\n(behind)", fontsize=6.5, ha="center")
    ax.text(K.BUS[0] - 5.4, zp + 4.4, "cell 3 against the stop,\nvertically above the\ninner tail:\n" +
            "\n".join(rows), fontsize=7, va="top")
    ax.set_xlim(K.BUS[0] - 5.5, K.BUS[0] + 3.5); ax.set_ylim(zp - 0.6, zp + 4.5); ax.set_aspect("equal"); ax.axis("off")


def main():
    fig = plt.figure(figsize=(17, 15), dpi=110)
    fig.suptitle(f"BatteryBASE cell compartment as built (to scale, mm): module {K.SHIP_T:.1f} mm thick incl. posts",
                 fontsize=13, weight="bold")
    top_view(fig.add_axes([0.0, 0.40, 0.50, 0.56]))
    side_section(fig.add_axes([0.52, 0.66, 0.46, 0.28]))
    pin_zoom(fig.add_axes([0.55, 0.42, 0.20, 0.22]))
    ax = fig.add_axes([0.77, 0.42, 0.22, 0.22]); ax.axis("off")
    ax.text(0, 1, f"Cells: {K.AAA_D_MIN:g}–{K.AAA_D_MAX:g} mm thick,\n  {K.AAA_L_MIN:g}–{K.AAA_L_MAX:g} mm long\n"
            f"Axes x = {', '.join(f'{x:.2f}' for x in K.CELL_X)}\n"
            f"Play: {K.CELL_FREE:.2f} mm ({K.X_STOP - K.X_LEFT - 3 * K.AAA_D_MAX:.2f} with\n  {K.AAA_D_MAX:g} mm cells),\n  split over three lanes by the bars\n"
            f"Leaves give way {K.LEAF_DEFL[0]:.2f}–{K.LEAF_DEFL[1]:.2f} mm each\n"
            f"  ({K.AAA_L_MIN:g}–{K.AAA_L_MAX:g} mm cells)\n\n"
            "Contacts (VERIFY with samples):\n"
            f"  {K.LEAF_PART}  C964855  6x, + and −\n"
            "  shape measured from the vendor\n  3D model; spring travel and\n  force to check",
            va="top", family="monospace", fontsize=7.8)
    cross_section(fig.add_axes([0.0, 0.0, 1.0, 0.40]))
    fig.savefig(OUT, facecolor="white")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
