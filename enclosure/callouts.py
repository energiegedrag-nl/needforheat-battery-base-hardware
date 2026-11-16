"""Renders of the BatteryBASE enclosure with numbered callouts, and a picture of the sliding lid half open.

Adapted from enclosure/callouts.py in needforheat-p1-base-hardware. Run with the same Python as kuip.py (CadQuery,
plus matplotlib and trimesh), after kuip.py:
    python enclosure/callouts.py
Writes docs/images/enclosure-*-callouts.png and docs/images/enclosure-lid-sliding.png. The callout positions come
from the parameters in kuip.py, so they follow the design when it changes.
"""
import os
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d import proj3d
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import kuip as K

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(os.path.dirname(HERE), "docs", "images")

ZT, ZL = K.Z_TOP, K.Z_LID
XL, XR = K.WALL / 2, K.CI_W - K.WALL / 2  # centres of the long walls
YT = -(K.WALL / 2)  # centre of the top wall (CadQuery y = -board y): the lid's open end
CX = K.CI_W / 2


def M(y):
    """CadQuery y of a lid feature drawn at board y with the open end at the bottom, after K.lid_mirror."""
    return y - K.CI_H


# (anchor x, y, z in CadQuery coordinates, label)
VIEWS = [
    ("tray-open-end", "battery-base-kuip.stl", 38, 55, [
        ((XL - 0.2, -30.0, ZT + K.GR_H / 2), "Groove in both long walls and the bottom wall: the lid's tongue runs in it"),
        ((CX, YT, ZT), "Dimple in the top wall: the lid's click bump drops in here"),
        ((CX - 8.0, YT, ZT + 1.0), "Open end at the top edge: the lid slides in from here\nand stops against the bottom wall"),
        ((36.0, -4.0, K.GAP + K.PCB_T - 0.2), "Peg in a corner block (3x): keys the PCB;\nthe top-left block has none"),
        ((K.CI_W, -30.0, 8.0), "Outside flush with the CoreInk (40 x 56 mm, R3)"),
        ((K.KEY_X, -(K.KEY_Y0 + 0.4), K.Z_TOP - 1.0), "Key groove for the cradle's lip (off centre)"),
    ]),
    ("cradle", "battery-base-cradle.stl", 40, -125, [
        ((K.CI_W / 2, -(K.WALL + K.CR_CLR + K.RIB_T / 2), K.RIB_TOP), "End rib: backs the contact plates; the spring force\ngoes through it into the tray's short wall"),
        ((K.X_STOP, -K.SADDLE_Y[1], K.Z_PCB + K.STOP_H), "Stop (3x) right of cell 3: keeps it off the bus header's\ntails; the cells lie on the PCB, no saddles"),
        ((K.CI_W - K.WALL - K.CR_CLR - K.RAIL_W / 2, -30.0, K.Z_PCB + K.RAIL_H), "Side rail: ties ribs and stops together"),
        ((K.CI_W - 3.0, -(K.CI_H - 3.0), K.Z_PCB), "Drops in on top of the PCB; the lid keeps it down"),
        ((K.KEY_X, -(K.WALL + K.CR_CLR - K.KEY_D), K.RIB_TOP - 1.0), "Key: lip on the top rib, off centre, into a groove\nin the top wall; turned round, it does not go in"),
    ]),
    ("lid-underside", "battery-base-lid.stl", -40, 120, [
        ((XR - K.GR_D, -30.0, ZT + K.TONGUE_H / 2), "Tongue along both long sides and the bottom end"),
        ((CX, M(K.DET_Y), ZT - K.DET_H), "Click bump under the flexible tab"),
        ((CX - K.TAB_W / 2 - K.TAB_SLOT / 2, M(K.CI_H - 3), ZT), "Slots: the tab flexes up when the lid slides"),
        ((3.0, M(K.CI_H - 0.5), ZT + 1.0), "Cap: full CoreInk width, forms the top of the top wall;\nturned round it cannot enter, so the lid fits one way only"),
    ]),
    ("lid-outside", "battery-base-lid.stl", 55, 120, [
        ((CX, M(K.CI_H - 5.0), ZT + K.TAB_T + 0.5), "Grip ridges on the thumb rest: push the lid up, towards the top edge"),
        ((CX - K.TAB_W / 2 - 5.0, M(K.CI_H - 6.0), ZL), "Arrow (2x): the way the lid slides out"),
        ((CX, M(18.0), ZL), "\"3x AAA\""),
    ]),
]
TITLES = {"cradle": "Cradle (separate print): ribs behind the contacts, stops beside cell 3",
          "tray-open-end": "Tray, seen from the top edge (lid removed)",
          "lid-underside": "Sliding lid, seen from below (inside)",
          "lid-outside": "Sliding lid, outside (the back of the module)"}


def draw(name, stl, elev, azim, callouts):
    m = trimesh.load(os.path.join(HERE, "fabrication", stl))
    tri = m.vertices[m.faces]
    light = np.array([0.4, 0.6, 0.8]) / np.linalg.norm([0.4, 0.6, 0.8])
    shade = 0.45 + 0.55 * np.clip(np.abs(m.face_normals @ light), 0, 1)
    colors = np.c_[np.outer(shade, [0.30, 0.31, 0.34]), np.ones(len(shade))]
    fig = plt.figure(figsize=(13, 8), dpi=120)
    ax = fig.add_axes([0.2, 0.0, 0.6, 0.94], projection="3d")
    ax.add_collection3d(Poly3DCollection(tri, facecolors=colors, edgecolors="none"))
    lo, hi = m.bounds
    c, r = (lo + hi) / 2, (hi - lo).max() / 2 * 0.7
    ax.set_xlim(c[0] - r, c[0] + r); ax.set_ylim(c[1] - r, c[1] + r); ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_box_aspect((1, 1, 1)); ax.view_init(elev=elev, azim=azim); ax.set_axis_off()
    fig.canvas.draw()
    pts = []
    for (x, y, z), text in callouts:
        px, py, _ = proj3d.proj_transform(x, y, z, ax.get_proj())
        fx, fy = fig.transFigure.inverted().transform(ax.transData.transform((px, py)))
        pts.append((fx, fy, text))
    order = sorted(range(len(pts)), key=lambda i: pts[i][0])
    left, right = order[:(len(order) + 1) // 2], order[(len(order) + 1) // 2:]
    for side, idx in (("left", left), ("right", right)):
        idx = sorted(idx, key=lambda i: -pts[i][1])
        for k, i in enumerate(idx):
            fx, fy, text = pts[i]
            ty = 0.84 - k * (0.68 / max(len(idx) - 1, 1)) if len(idx) > 1 else 0.5
            tx = 0.3 if side == "left" else 0.7
            text = "\n".join(textwrap.fill(t, 32) for t in text.split("\n"))
            fig.add_artist(plt.Line2D([fx, tx], [fy, ty], transform=fig.transFigure, color="#d9480f", lw=1.1))
            fig.add_artist(plt.Circle((fx, fy), 0.004, transform=fig.transFigure, color="#d9480f"))
            fig.text(tx + (-0.005 if side == "left" else 0.005), ty, f"{i + 1}. {text}", fontsize=10.5,
                     ha="right" if side == "left" else "left", va="center",
                     bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#d9480f", lw=0.8))
    fig.text(0.5, 0.97, TITLES[name], ha="center", va="top", fontsize=14, weight="bold")
    out = os.path.join(IMG, f"enclosure-{name}-callouts.png")
    fig.savefig(out, facecolor="white")
    plt.close(fig)
    print("wrote", out)


def sliding(out_by=22.0):
    """Manual picture: tray with cells, lid slid out `out_by` mm towards the top edge."""
    import cadquery as cq
    tray = trimesh.load(os.path.join(HERE, "fabrication", "battery-base-kuip.stl"))
    lid = trimesh.load(os.path.join(HERE, "fabrication", "battery-base-lid.stl"))
    cradle = trimesh.load(os.path.join(HERE, "fabrication", "battery-base-cradle.stl"))
    _, cells, _ = K.fit_parts()
    cq.exporters.export(K.contacts(), os.path.join(HERE, "fabrication", "_cont.stl"), tolerance=0.05, angularTolerance=0.2)
    cont = trimesh.load(os.path.join(HERE, "fabrication", "_cont.stl"))
    os.remove(os.path.join(HERE, "fabrication", "_cont.stl"))
    tmp = os.path.join(HERE, "fabrication", "_cells.stl")
    cq.exporters.export(cells, tmp, tolerance=0.05, angularTolerance=0.2)
    cell = trimesh.load(tmp)
    os.remove(tmp)
    light = np.array([0.4, 0.6, 0.8]) / np.linalg.norm([0.4, 0.6, 0.8])
    fig = plt.figure(figsize=(11, 8), dpi=120)
    ax = fig.add_axes([0.0, 0.05, 1.0, 0.85], projection="3d")
    tris, cols = [], []
    for mesh, base, dy in ((tray, [0.30, 0.31, 0.34], 0.0), (lid, [0.50, 0.52, 0.56], K.LID_OUT * out_by),
                           (cradle, [0.55, 0.57, 0.62], 0.0), (cont, [0.78, 0.78, 0.82], 0.0),
                           (cell, [0.85, 0.55, 0.15], 0.0)):
        v = mesh.vertices.copy()
        v[:, 1] += dy
        shade = 0.45 + 0.55 * np.clip(np.abs(mesh.face_normals @ light), 0, 1)
        tris.append(v[mesh.faces]); cols.append(np.c_[np.outer(shade, base), np.ones(len(shade))])
    ax.add_collection3d(Poly3DCollection(np.concatenate(tris), facecolors=np.concatenate(cols), edgecolors="none"))
    r = 24
    ax.set_xlim(20 - r, 20 + r); ax.set_ylim(-18 - r, -18 + r); ax.set_zlim(-6, -6 + 2 * r)
    ax.set_box_aspect((1, 1, 1)); ax.view_init(elev=35, azim=60); ax.set_axis_off()
    fig.text(0.5, 0.95, "Replacing the cells: push the ribbed tab up; the lid clicks loose and slides out at the top",
             ha="center", va="top", fontsize=12, weight="bold")
    fig.text(0.5, 0.05, "Cells: + and - are printed on the board under each cell; the spring is always the - end. "
             "Lid back on: slide it in from the top edge until it stops and clicks.", ha="center", fontsize=9)
    out = os.path.join(IMG, "enclosure-lid-sliding.png")
    fig.savefig(out, facecolor="white")
    plt.close(fig)
    print("wrote", out)


def main():
    os.makedirs(IMG, exist_ok=True)
    for v in VIEWS:
        draw(*v)
    sliding()


if __name__ == "__main__":
    main()
