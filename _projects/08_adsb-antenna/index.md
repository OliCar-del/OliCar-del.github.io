---
layout: post
title: 1090 MHz ADS-B Antenna - NEC2 Modelling
description: NEC2 models of a quarter-wave groundplane for 1090 MHz aircraft reception, tuned by sweeping radial droop and then radiator length, with a three-element Yagi modelled for comparison. Simulation only, with solver output and convergence checks retained for a later build.
skills:
  - Antenna Modelling (NEC2 / Method of Moments)
  - Impedance Matching & S-Parameters
  - RF Test Planning (VNA / SDR)
  - Numerical Verification & Configuration Control
image: /projects/08_adsb-antenna/input_match.png
thumb: /projects/08_adsb-antenna/thumb.webp
permalink: /projects/08_adsb-antenna/
redirect_from:   # older addresses for this page, kept working
  - /projects/08_adsb-antenna/index/
  - /_projects/08_adsb-antenna/
---
# Modelling a 1090 MHz ADS-B Antenna

## Why I did this

Aircraft transponders broadcast position and identity on 1090 MHz. I want to receive them, and before cutting any wire I wanted to know what length to cut and why that length rather than another.

So this is the modelling stage. Two geometries in NEC2, a design decision, and enough retained solver output that I can check the work later or hand it to someone else. No antenna has been built and nothing has been measured. That is the next stage, and doing the modelling first means the measurements will have a prediction to test rather than just a result to report.

## Method

| Parameter | Value | Note |
| --- | --- | --- |
| Solver | NEC2dXS Build 2.7 | From the author-distributed 4nec2 5.9.3 package. 500-segment engine, batch interface verified against its bundled dipole example. |
| Formulation | Method of moments | Wires are segmented, the tangential E-field is forced to zero on each conductor, and the resulting matrix is solved for the current distribution. |
| Conductor | PEC, 0.5 mm radius | Perfectly conducting circular wire. No connector, coax, mast or surroundings. |
| Environment | Free space | Finite radials, not an infinite ground plane. |
| Reference | Real 50 Ω | S11 is computed from the NEC complex impedance. None of it is measured. |
| Source | 6 mm voltage segment | Centred 3 mm above the radial junction. A finite numerical stand-in for a physical feed. |

Coarse sweeps ran 950 to 1250 MHz in 5 MHz steps, with 1 MHz refinement near the candidate. Mesh convergence and repeatability gates were applied to every configuration that supports a claim.

{% include image-gallery.html images="geometry.png" height="420" %}
<span style="font-size: 14px">Figure 1: Candidate geometry and source placement, drawn from the same geometry function that writes the solver input.</span>

## Interactive model browser

The controls below read the retained solver output directly. Moving a slider shows the actual NEC2 result for that configuration rather than an interpolation.

<iframe src="{{ page.url }}interactive.html"
        style="width:100%; height:760px; border:1px solid #d6dce2; border-radius:10px; background:#fff;"
        loading="lazy" title="Interactive 1090 MHz antenna bench"></iframe>

<span style="font-size: 14px">Figure 2: Radiator length, radial droop, frequency sweep and pattern cuts. <a href="{{ page.url }}interactive.html" target="_blank">Open full screen</a>.</span>

## Radial droop

I started from the usual advice, that a quarter-wave groundplane sits near 36 Ω and drooping the radials toward 45 degrees brings it up to 50 Ω. To test it I held the radiator and radials both at 69 mm and changed only the angle.

Resistance behaved as described. It climbed from 25.73 to 62.86 Ω and passed through 50 Ω near 30 degrees. Reactance climbed with it though, from +9.43 to +41.72 Ω, and the match depends on both. The best S11 in that fixed-length family is at 15 degrees rather than 45, and even that only reaches -11.17 dB. Droop on its own does not produce a good match.

The radials carry return current and are part of the radiating structure. Tilting them gives that current a vertical component, so the geometry drifts toward a vertical dipole and resistance, reactance and resonance all move together. Neither the quarter-wavelength estimate nor a nominal bend angle lands you on 50 + j0 Ω.

That is why I ended up treating droop and length as two separate controls. Droop sets the resistance and the horizon response. Length then cancels whatever reactance is left.

## Radiator length

Across 63 to 72 mm at 30 degrees, resistance moves only from 42 to 56 Ω while reactance sweeps -3 to +51 Ω. That is close to 6 Ω per millimetre. Trimming an antenna is a reactance adjustment, and the match improves because the resistance was already near 50 Ω before you started.

64 mm leaves +2.83 Ω and takes S11 to -22.28 dB, against -10.24 dB for the 69 mm baseline at the same angle. The same gradient is a build instruction: 1 mm away from the optimum costs 2 to 3 dB, so cut long and trim in small steps.

| Configuration | Radiator | Droop | Z at 1090 MHz | S11 | VSWR | Realised gain, horizon |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| GP fixed | 69 mm | 0&deg; | 25.73 + j9.43 Ω | -9.34 dB | 2.036 | 0.77 dBi |
| GP fixed | 69 mm | 15&deg; | 37.97 + j21.99 Ω | -11.17 dB | 1.764 | 1.18 dBi |
| GP fixed | 69 mm | 30&deg; | 50.79 + j32.57 Ω | -10.24 dB | 1.888 | 1.43 dBi |
| GP fixed | 69 mm | 45&deg; | 62.86 + j41.72 Ω | -8.81 dB | 2.139 | 1.68 dBi |
| **GP selected** | **64 mm** | **30&deg;** | **43.39 + j2.83 Ω** | **-22.28 dB** | **1.167** | **1.78 dBi** |
| Yagi comparator | 128 mm driven | n/a | 31.91 + j4.37 Ω | -12.89 dB | 1.587 | 8.09 dBi |

{% include image-gallery.html images="input_match.png" height="560" %}
<span style="font-size: 14px">Figure 3: Input match to a real 50 Ω reference, 950 to 1250 MHz. The selected candidate is the heavy navy trace.</span>

## Resonance and best match are different frequencies

The selected model crosses X = 0 at 1083.8 MHz but reaches its deepest S11 at 1088 MHz. Resonance asks when the reactance vanishes. Match asks when the complex impedance is closest to 50 Ω. The two coincide only when R is exactly 50 Ω, so I report them separately throughout.

The 45 degree fixed-length trace shows the same thing from the other direction. It drops below -35 dB, but it does that near 1003 MHz, which is no use at 1090.

## The Yagi comparison

The three-element Yagi is adapted from NBS Technical Note 688. Reflector 132.569 mm, driven 128 mm, director 116.617 mm, element centres at &plusmn;55.008 mm. The smaller wire diameter and a straight driven element replace the reference's folded feed, so the reference geometry is a starting point rather than a specification I met.

{% include image-gallery.html images="radiation_coverage.webp" height="480" %}
<span style="font-size: 14px">Figure 4: Elevation and azimuth cuts at 1090 MHz in absolute dBi, with the 50 Ω mismatch applied once.</span>

Forward, it is clearly better: 8.09 dBi against 1.78 dBi, a difference of 6.31 dB in the same direction with each antenna's own mismatch included. The advantage holds through the elevations that matter, at 6.31, 6.26, 6.13 and 5.61 dB for 0, 5, 10 and 20 degrees.

Azimuth is where it gives that back. A 97 degree half-power beamwidth and 16.6 dB front-to-back ratio mean everything outside the forward sector is worse than the omnidirectional antenna, falling to around -12 dBi off the back. A passive antenna adds no energy, so the forward 6 dB is paid for in every other direction.

ADS-B traffic arrives on all bearings, so the groundplane is what I would build. Peak gain on its own does not predict better reception.

One number worth keeping next to the elevation cut: an airliner at 35,000 ft sits about 2.4 degrees above the horizon when it is 250 km away. Useful range is won close to the horizon, not overhead, where aircraft are near enough to receive on anything.

## Checks, including the ones that failed

* Refined meshes had to preserve source width and position and hold within 2 Ω of resistance and reactance and 0.2 dB of gain. The selected groundplane and the final Yagi pass. The final comparator moved 0.018 Ω, 0.847 Ω and 0.02 dB.
* The original NBS-adapted Yagi seed failed those gates. It is still in the repository as a diagnostic rather than deleted.
* An early geometry card exceeded the 80-column limit and would not solve. That run is retained too.
* Scalar match formulas, V/I reconstruction, geometry and radial-current symmetry checks and sphere integration were computed separately and agree with the retained output.
* The 0 and 45 degree baselines keep average-power-gain residuals of -5.45% and +9.07%, which is roughly -0.24 and +0.38 dB on the sphere average. Their absolute gains are therefore less precise than the selected pair. I have not applied a correction to hide that.

## Limitations

The model is idealised. Perfect conductors, nominal dimensions, free space, and a numerical approximation to the feed. It leaves out the connector, insulation, coax common-mode current, the mast, the roof and the surrounding buildings, and several of those routinely dominate what a real antenna measures.

This establishes a simulated design decision. It does not establish measured gain, EMC compliance, or any improvement in ADS-B message rate or range. The solver is the author-distributed NEC2dXS build rather than anything I wrote.

## Next stage

1. Confirm the VNA gives useful calibrated measurements near 1090 MHz, then record its reference plane, adapters and placement.
2. Build the candidate with an adjustable radiator so it can be trimmed without rebuilding.
3. Keep before and after-trim Touchstone files, with measured curves clearly separated from these predictions.
4. Interleave both antennas on the same receiver, gain setting, decoder, feedline and location, recording message counts, azimuth distribution and range.

If the measurements agree, the model holds. If they do not, the most likely causes are the feedline common-mode current and the mounting environment, neither of which is in the model.

<span style="font-size: 14px">Per-configuration data, including diagnostics and run pointers: <a href="{{ page.url }}design_table.csv">design_table.csv</a>.</span>
