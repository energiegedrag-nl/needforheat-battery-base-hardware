"""SPICE checks of the BatteryBASE charge control (ngspice, shipped with KiCad).

Run:  python tools/sim/run_sims.py      (needs numpy and matplotlib)
Writes plots and a summary to docs/simulation/.

What is checked
1. A full charge cycle, started by the firmware (FORCE pulse) while the CoreInk is on, then running on its own with
   the CoreInk off: the latch holds the boost on, survives the undefined STDBY output while the TP4056 powers up,
   and switches everything off when the TP4056 reports "done".
2. The safety net: with no firmware, charging starts by itself when the LiPo drops below 3.5 V (U3, TPS3840DL35)
   and stops at "done" without restarting.
3. Cells nearly empty (U4, TPS3840DL28): no start, and a running charge stops.
4. Firmware INHIBIT stops a running charge.
5. Currents with everything off (CoreInk off, not charging): from the cells, from the LiPo and into the CoreInk's
   3V3 rail (back-feeding), DC operating point.

Models (behavioural, good for levels and logic, not for exact waveforms):
* AO3401A / 2N7002: VDMOS as in the P1-BASE simulations.
* TPS61023 boost: an ideal 4.7 V source behind a 1 ms soft start, on when EN > 1.2 V, 90 % efficient; when off
  its output is disconnected (load disconnect) and it draws I_Q_BOOST_OFF from VIN.
* TP4056: constant current 60 mA up to 4.2 V, then constant voltage; STDBY (open drain) pulls low when VCC is up and
  the current fell below 6 mA (C/10), and - worst case - also while VCC is ramping between 1 V and 4 V.
* TPS3840: ideal detectors with 200 mV hysteresis (VIT- + 0.2 V), open-drain outputs, 300 nA supply current.
* LiPo: time-compressed: 2 F capacitor (so a charge takes seconds instead of hours) with 0.15 ohm ESR and a constant
  load (the CoreInk asleep and awake, averaged, also scaled).
* Unpowered I2C chips (CoreInk off): their pins as ESD diodes to the CoreInk's 3V3 rail, which is 0 V behind 1 kOhm.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ngspice  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "docs", "simulation")
os.makedirs(OUT, exist_ok=True)

I_Q_DET = 300e-9      # TPS3840 supply current (typ)
I_Q_BOOST_OFF = 0.1e-6  # TPS61023 shutdown current into VIN (VERIFY with the datasheet)
V_BOOST = 4.7
ICHG = 0.060

MODELS = """
.model N2N7002 VDMOS(Vto=1.8 Kp=0.25 Rd=1.2 Rs=0.3 Rg=10 Cgs=22p Cgdmax=12p Cgdmin=2p Cjo=15p Is=1e-14)
.model PAO3401 VDMOS(pchan Vto=-0.9 Kp=8 Rd=0.02 Rs=0.01 Rg=5 Cgs=550p Cgdmax=150p Cgdmin=40p Cjo=120p Is=1e-12)
.model DESD D(Is=1e-14 N=1.0)
.model SWOD SW(Ron=50 Roff=1e12 Vt=0.5 Vh=0.1)
"""


def circuit(vcell, lipo0, load, force_pwl="0 0", inhibit_pwl="0 0", coreink_on_pwl="0 0", cells_pwl=None):
    """The charge control, as in the schematic (references in brackets)."""
    cells = f"Vcell vbat 0 PWL({cells_pwl})" if cells_pwl else f"Vcell vbat 0 {vcell}"
    vc0 = vcell if vcell else 3.3
    return f"""* BatteryBASE charge control
{MODELS}
{cells}
Rcell vbat vbr 0.3
* reverse-polarity protection [Q1]
Mq1 vbr 0 vc vc PAO3401
* latch: Q_EN [Q2] switches EN from the cells; held by Q_H [Q3] through R4
Mq2 enp hg2 vc vc PAO3401
Rr1 hg2 vc 10Meg
Rr10 enp en 10k
Rr2 en 0 10Meg
Cen en 0 100p
Rr3 en hg 1Meg
Cc1 hg 0 100n
Mq3 hd hg 0 0 N2N7002
Rr4 hd hg2 100k
* firmware FORCE [Q4] and INHIBIT [Q5], gates from the PCA9536 (0 V when the CoreInk is off)
Vforce force 0 PWL({force_pwl})
Mq4 hd force 0 0 N2N7002
Vinh inhibit 0 PWL({inhibit_pwl})
Mq5 en inhibit 0 0 N2N7002
* safety net: U3 TPS3840DL35 on the LiPo, open drain RESET# -> R5 -> hg2
Bu3c u3c 0 V = v(u3cf) > 0.5 ? (v(lipo) > 3.7 ? 0 : 1) : (v(lipo) < 3.5 ? 1 : 0)
Ru3c u3c u3cf 1k
Cu3c u3cf 0 1n
Su3 u3od 0 u3cf 0 SWOD
Ru3s u3o u3od 1
Rr5 u3o hg2 1Meg
Iu3 lipo 0 {I_Q_DET}
* cells undervoltage: U4 TPS3840DL28 on the cells, RESET# -> gate of Q6, which pulls hg2 up to the cells
Bu4c u4c 0 V = v(u4cf) > 0.5 ? (v(vc) > 3.0 ? 0 : 1) : (v(vc) < 2.8 ? 1 : 0)
Ru4c u4c u4cf 1k
Cu4c u4cf 0 1n
Su4 uvg 0 u4cf 0 SWOD
Rr8 uvg vc 10Meg
Mq6 hg2 uvg vc vc PAO3401
Iu4 vc 0 {I_Q_DET}
* boost [U1], behavioural; output disconnected when off
Bbctl bctl 0 V = v(en) > 1.2 ? {V_BOOST} : 0
Rbs bctl bss 1k
Cbs bss 0 1u
Bbo v5i 0 V = v(bss)
Vbm v5i v5s 0
Rbo v5s v5 0.05
Cbo v5 0 20u
Rbl v5 0 1Meg
Bbin vc 0 I = v(en) > 1.2 ? (v(v5)*i(vbm))/(0.9*max(v(vc),0.5)) : {I_Q_BOOST_OFF}
* charger [U2] TP4056, behavioural: CC/CV into tpbat; STDBY open drain
Bchg v5 tpbat I = (v(v5) > 3.9 && v(v5) > v(tpbat) + 0.1) ? max(0, min({ICHG}, (4.2 - v(tpbat))*3)) : 0
Bdone dctl 0 V = (v(v5) > 1.0 && v(v5) < 4.0) ? 1 : ((v(v5) >= 4.0 && v(prog) < 0.1) ? 1 : 0)
Rdc dctl dctlf 1k
Cdc dctlf 0 1n
Sdone stdby 0 dctlf 0 SWOD
Bprog prog 0 V = (v(v5) > 3.9 && v(v5) > v(tpbat) + 0.1) ? max(0, min({ICHG}, (4.2 - v(tpbat))*3))/{ICHG} : 0
Rr7 stdby hg 100k
* charger isolation [Q7, Q8]
Mq7 tpbat isog lipo lipo PAO3401
Rr9 isog lipo 1Meg
Mq8 isog en 0 0 N2N7002
Ctp tpbat 0 10u
* LiPo (time-compressed) and the CoreInk load
Clipo lipoc 0 2
.ic v(lipoc)={lipo0}
.ic v(en)=0 v(hg)=0 v(hg2)={vc0} v(v5)=0 v(bss)=0 v(u3cf)={1 if lipo0 < 3.5 else 0} v(u4cf)={1 if vc0 < 2.8 else 0}
Rlipo lipoc lipo 0.15
Iload lipo 0 PWL({load})
* CoreInk 3V3 rail (0 V when off) and the unpowered I2C chips as ESD diodes
V3v3 v3src 0 PWL({coreink_on_pwl})
R3v3 v3src v3v3 1k
* cell divider switched by the 3V3 rail [Q9 P-FET top, Q10 N-FET gate driver], to ADS1115 AIN0
Mq10 dg v3v3 0 0 N2N7002
Rr11 dg vc 1Meg
Mq9 divt dg vc vc PAO3401
Rr12 divt ain0 1Meg
Rr13 ain0 0 1Meg
Dain0 ain0 v3v3 DESD
* PROG pass switch [Q11], to AIN1
Mq11 prog v3v3 ain1 ain1 N2N7002
Rr14 ain1 0 1Meg
Dain1 ain1 v3v3 DESD
"""


def sim_cycle():
    """1: firmware start; 2: safety net; 3: cells empty; 4: inhibit."""
    T = 60
    cases = [
        ("1  firmware starts (FORCE pulse at 2 s), CoreInk off afterwards", dict(
            vcell=4.5, lipo0=3.92, load="0 0.004 60 0.004", force_pwl="0 0 2 0 2.001 3.3 2.05 3.3 2.051 0",
            coreink_on_pwl="0 3.3 3 3.3 3.001 0")),
        ("2  no firmware: safety net at 3.5 V", dict(vcell=4.5, lipo0=3.52, load="0 0.002 60 0.002")),
        ("3  cells run down during a charge (UV at 2.8 V)", dict(
            vcell=None, lipo0=3.92, load="0 0.004 60 0.004", force_pwl="0 0 2 0 2.001 3.3 2.05 3.3 2.051 0",
            cells_pwl="0 3.3 4 3.3 7 2.6 60 2.6")),
        ("4  firmware INHIBIT at 12 s", dict(
            vcell=4.5, lipo0=3.92, load="0 0.004 60 0.004", force_pwl="0 0 2 0 2.001 3.3 2.05 3.3 2.051 0",
            inhibit_pwl="0 0 12 0 12.001 3.3 12.2 3.3 12.201 0")),
    ]
    fig, axs = plt.subplots(len(cases), 1, figsize=(11, 3.1 * len(cases)), sharex=True)
    rows = []
    for ax, (title, kw) in zip(axs, cases):
        net = circuit(**kw)
        d = ngspice.run(net, f"tran 1m {T} 0 2m")
        t = d["time"]
        lipo, en, v5, vc = d["lipo"], d["en"], d["v5"], d["vc"]
        ichg = np.interp(t, t, d.get("prog", np.zeros_like(t))) * ICHG * 1000
        ax.plot(t, lipo, label="LiPo [V]")
        ax.plot(t, en, label="EN (boost on) [V]")
        ax.plot(t, v5, label="boost out [V]", alpha=0.6)
        ax.plot(t, vc, label="cells [V]", ls="--")
        ax2 = ax.twinx()
        ax2.plot(t, ichg, color="k", lw=0.8, label="charge current [mA]")
        ax2.set_ylim(0, 130)
        ax2.set_ylabel("mA")
        ax.set_ylim(0, 5.2)
        ax.set_title(title, fontsize=10, loc="left")
        ax.grid(alpha=0.3)
        on = en > 1.2
        starts = int(np.sum(np.diff(on.astype(int)) == 1))
        stops = int(np.sum(np.diff(on.astype(int)) == -1))
        t_on = float(np.sum(np.diff(t)[on[:-1]]))
        rows.append((title, starts, stops, round(t_on, 2), round(float(lipo[-1]), 3), bool(on[-1])))
    axs[0].legend(loc="lower right", fontsize=8, ncol=4)
    axs[-1].set_xlabel("time [s] (time-compressed LiPo: one charge takes seconds instead of hours)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "charge-control.png"), dpi=110)
    plt.close(fig)
    return rows


def sim_off_currents():
    """5: everything off; currents from the cells, from the LiPo and into the 3V3 rail, at the end of a 2 s run
    that starts with the latch off (the latch is bistable, so a plain DC operating point may pick 'on')."""
    rows = []
    for name, vcell, lipo in (("cells full 4.8 V, LiPo 4.1 V", 4.8, 4.1), ("cells 3.6 V, LiPo 3.9 V", 3.6, 3.9),
                              ("cells empty 2.7 V, LiPo 3.9 V", 2.7, 3.9)):
        net = circuit(vcell, lipo, "0 0 2 0").replace("Clipo lipoc 0 2", f"Vlipo lipoc 0 {lipo}\nClipox lipoc 0 1n")
        d = ngspice.run(net, "tran 1m 2 0 5m")
        i_cells = -d["vcell#branch"][-1]
        i_lipo = -d["vlipo#branch"][-1]
        i_3v3 = -d["v3v3#branch"][-1]
        rows.append((name, i_cells * 1e9, i_lipo * 1e9, i_3v3 * 1e9, d["en"][-1]))
    return rows


def main():
    rows = sim_cycle()
    off = sim_off_currents()
    with open(os.path.join(OUT, "README.md"), "w", encoding="utf8") as f:
        f.write("# Simulation results\n\nGenerated by `tools/sim/run_sims.py` with ngspice (KiCad 10). Behavioural "
                "models (see the script's docstring): they check the logic, levels and currents, not exact "
                "waveforms. The LiPo is time-compressed (2 F), so a charge takes seconds.\n\n")
        f.write("## 1. Charge control\n\n![charge control](charge-control.png)\n\n")
        f.write("| Case | Boost starts | Boost stops | Time on [s] | LiPo at the end [V] | On at the end |\n"
                "|---|---:|---:|---:|---:|:---:|\n")
        for r in rows:
            f.write(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {'yes' if r[5] else 'no'} |\n")
        f.write("\n## 2. Everything off (CoreInk off, not charging), DC\n\n"
                "Includes the TPS3840 supply currents (300 nA typ each) and the TPS61023 shutdown current "
                f"({I_Q_BOOST_OFF * 1e9:.0f} nA, VERIFY); the discrete parts as modelled (no FET leakage).\n\n"
                "| Case | From the cells [nA] | From the LiPo [nA] | Into the CoreInk 3V3 rail [nA] | EN [V] |\n"
                "|---|---:|---:|---:|---:|\n")
        for r in off:
            f.write(f"| {r[0]} | {r[1]:.0f} | {r[2]:.0f} | {r[3]:.1f} | {r[4]:.2f} |\n")
    for r in rows:
        print(r)
    for r in off:
        print(r)


if __name__ == "__main__":
    main()
