---
layout: post
title: 1090 MHz ADS-B Antenna - NEC2 Design Study
description: A bounded method-of-moments study tuning a quarter-wave groundplane for 1090 MHz ADS-B reception, with a three-element Yagi comparator quantifying the gain-versus-coverage tradeoff. Simulation only - retained solver output, mesh convergence checks and an explicit VNA/SDR measurement handoff.
skills:
  - Antenna Modelling (NEC2 / Method of Moments)
  - Impedance Matching & S-Parameters
  - RF Test Planning (VNA / SDR)
  - Numerical Verification & Configuration Control
main-image: /input_match.png
image: /_projects/08_adsb-antenna/input_match.png
---
# Tuning a 1090 MHz ADS-B Antenna in NEC2

## Project Overview & Scope

Aircraft transponders broadcast position and identity on **1090 MHz**. Receiving them well is an antenna problem long before it is a receiver problem, so this study answers a single bounded question: **what should I actually cut, and why?**

The deliverable is a design decision with the evidence attached - not a built antenna. Every number below is read from retained NEC2dXS solver output. **No hardware has been built and no measurement has been taken.** The study ends at a documented handoff to a VNA and SDR campaign that has not yet begun.

A quarter-wave groundplane was selected as the build candidate, and a three-element Yagi was modelled as a comparator to put a number on what directivity costs in coverage.

## Method

| Parameter | Value | Note |
| --- | --- | --- |
| **Solver** | NEC2dXS Build 2.7 | From the author-distributed 4nec2 5.9.3 package; 500-segment engine, batch interface verified against its bundled dipole example. |
| **Formulation** | Method of Moments | Wires segmented, tangential E-field forced to zero on each conductor, resulting matrix solved for the current distribution. |
| **Conductor** | PEC, 0.5 mm radius | Perfectly conducting circular wire. No connector, coax, mast or surroundings. |
| **Environment** | Free space | Finite radials, **not** an infinite ground plane. |
| **Reference** | Real 50 Ω | All S11 values computed from NEC complex impedance, not measured. |
| **Source** | 6 mm voltage segment | Centred 3 mm above the radial junction; a finite numerical stand-in for a physical feed. |

Coarse sweeps ran 950-1250 MHz in 5 MHz steps, with local 1 MHz refinement around the candidate. Mesh convergence and repeatability gates were applied to every configuration that informs a claim.

{% include image-gallery.html images="geometry.png" height="420" %}
<span style="font-size: 14px">Figure 1: Resolved candidate geometry and source placement, generated from the same geometry function that writes the solver input. Not a solver screenshot.</span>

## Interactive: walk the search yourself

The controls below drive the retained solver data directly - moving a slider reads out the actual NEC2 result for that configuration, not an interpolation or a formula.

<iframe src="{{ page.url }}interactive.html"
        style="width:100%; height:760px; border:1px solid #d6dce2; border-radius:10px; background:#fff;"
        loading="lazy" title="Interactive 1090 MHz antenna bench"></iframe>

<span style="font-size: 14px">Figure 2: Interactive bench. Radiator length, radial droop, frequency sweep and pattern cuts, all driven by the retained NEC2 output. <a href="{{ page.url }}interactive.html" target="_blank">Open full screen</a>.</span>

## Result: what to cut

The selected build candidate is a **64 mm vertical radiator with four 69 mm radials drooped 30 degrees**.

| Configuration | Radiator | Droop | Z at 1090 MHz | S11 | VSWR | Realised gain, horizon |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| GP fixed | 69 mm | 0&deg; | 25.73 + j9.43 Ω | −9.34 dB | 2.036 | 0.77 dBi |
| GP fixed | 69 mm | 15&deg; | 37.97 + j21.99 Ω | −11.17 dB | 1.764 | 1.18 dBi |
| GP fixed | 69 mm | 30&deg; | 50.79 + j32.57 Ω | −10.24 dB | 1.888 | 1.43 dBi |
| GP fixed | 69 mm | 45&deg; | 62.86 + j41.72 Ω | −8.81 dB | 2.139 | 1.68 dBi |
| **GP selected** | **64 mm** | **30&deg;** | **43.39 + j2.83 Ω** | **−22.28 dB** | **1.167** | **1.78 dBi** |
| Yagi comparator | 128 mm driven | n/a | 31.91 + j4.37 Ω | −12.89 dB | 1.587 | 8.09 dBi |

Shortening the radiator alone, from the preserved 69 mm baseline, improved simulated S11 from **−10.24 dB to −22.28 dB**.

{% include image-gallery.html images="input_match.png" height="560" %}
<span style="font-size: 14px">Figure 3: Input match to a real 50 Ω reference, 950-1250 MHz. The selected candidate (heavy navy) places its notch on 1090 MHz; the 45&deg; fixed-length case reaches −34 dB but does it near 1003 MHz.</span>

## What the droop experiment actually showed

The common account is that a groundplane sits near 36 Ω and drooping the radials to 45 degrees brings it to 50 Ω. The controlled experiment - radiator and radials both held at 69 mm, only the angle changing - shows that is only half true.

Resistance does climb as described, **25.73 &rarr; 62.86 Ω**, passing through 50 Ω near 30 degrees. But reactance climbs alongside it, **+9.43 &rarr; +41.72 Ω**, and the match depends on both. The best S11 in this fixed-length family is at **15 degrees**, not 45, and even that only reaches −11.17 dB. **Drooping alone never produces a good match.**

Physically, the radials carry the return current and are part of the radiating system. Tilting them gives those currents a vertical component, so the structure drifts toward a vertical dipole and resistance, reactance and resonance all move together. Neither the quarter-wavelength estimate nor a nominal bend angle guarantees 50 + j0 Ω.

That is why droop and length were treated as **two separate controls**: droop was set first for its resistance and horizon response, then radiator length was used on its own to cancel the remaining reactance. Across the 63-72 mm search, resistance moves only 42 to 56 Ω while reactance sweeps −3 to +51 Ω - roughly **+6 Ω per millimetre**. Trimming an antenna is not adjusting its impedance in general; it is cancelling reactance.

### Resonance is not best match

The selected candidate crosses **X = 0 at 1083.8 MHz** but reaches its deepest S11 at **1088 MHz**. Those are different questions - resonance asks when reactance vanishes, match asks when the complex impedance is closest to 50 Ω - and they coincide only when R is exactly 50 Ω. The two are reported separately throughout.

## Gain against coverage

The three-element Yagi (reflector 132.569 mm, driven 128 mm, director 116.617 mm, spacings &plusmn;55.008 mm) was adapted from **NBS Technical Note 688**, with the smaller wire diameter and a straight driven element replacing the reference's folded feed.

{% include image-gallery.html images="radiation_coverage.png" height="480" %}
<span style="font-size: 14px">Figure 4: Elevation and azimuth cuts at 1090 MHz, absolute dBi, with the 50 Ω mismatch applied once. The groundplane is flat across azimuth; the Yagi trades that flatness for forward gain.</span>

Forward, the Yagi wins clearly: **8.09 dBi against 1.78 dBi**, a genuine **+6.31 dB** in the same direction with each antenna's actual mismatch included. The advantage holds across useful elevations - 6.31, 6.26, 6.13 and 5.61 dB at 0, 5, 10 and 20 degrees.

The azimuth cut is the catch. A **97 degree half-power beamwidth** and **16.6 dB front-to-back ratio** mean everything outside that sector is *worse* than the omnidirectional antenna, falling to about −12 dBi off the back. A passive antenna adds no energy; gain is redistribution, and the Yagi pays for its forward 6 dB everywhere else.

ADS-B targets arrive on every bearing, so **the groundplane remains the preferred build** despite losing on the headline number. Peak gain is not a prediction of better reception everywhere.

One more reason to care about the elevation cut: an airliner at 35,000 ft sits about **2.4 degrees above the horizon** when it is 250 km away. Maximum range is won near the horizon, not overhead, where aircraft are close and easy anyway.

## Verification, and what failed

Claims are only as good as the checks behind them, so the failures stay in the record:

* **Mesh convergence gates.** Refined meshes preserved source width and position and had to hold within 2 Ω of resistance and reactance and 0.2 dB of gain. The selected groundplane and final Yagi pass; the final comparator's changes are 0.018 Ω, 0.847 Ω and 0.02 dB.
* **The original Yagi seed failed those gates** and is retained as a diagnostic rather than deleted.
* **An overlong geometry-card attempt failed to solve** and is also preserved.
* **Independent arithmetic.** Scalar match formulas, V/I reconstruction, geometry and radial-current symmetry checks, and sphere integration were computed separately and agree with the retained output.
* **Open diagnostics, uncorrected.** The 0&deg; and 45&deg; baselines retain average-power-gain residuals of −5.45% and +9.07%. Their absolute gains therefore carry less precision than the selected pair, and no correction has been applied to conceal that.

## Limitations

The model is idealised: perfect conductors, nominal dimensions, free space, and a finite numerical feed. It omits the connector, insulation, coax common-mode current, supports, mast, roof and surrounding buildings - several of which routinely dominate real measured results.

**This study establishes a simulated design decision. It does not establish measured gain, EMC compliance, improved ADS-B message rate or range.** Scripts, execution and documentation were produced with AI assistance; the solver is the author-distributed NEC2dXS build, not a custom implementation.

## Next stage: measurement

The handoff is deliberately specific, so the later campaign tests the prediction rather than replacing it:

1. Confirm the VNA can make useful calibrated measurements near 1090 MHz, then record its reference plane, adapters and placement.
2. Build the candidate with an **adjustable** radiator so trimming is possible without rebuilding.
3. Retain before-and-after-trim Touchstone files, keeping measured curves plainly distinct from these predictions.
4. Interleave the two antennas on the same receiver, gain setting, decoder, feedline and location, recording message counts, azimuth distribution and range statistics.

Agreement would validate the model. Disagreement would be more interesting, and would most likely point at the feedline common-mode current and the mounting environment this model leaves out.

<span style="font-size: 14px">Canonical per-configuration data, including diagnostics and run pointers: <a href="{{ page.url }}design_table.csv">design_table.csv</a>.</span>
