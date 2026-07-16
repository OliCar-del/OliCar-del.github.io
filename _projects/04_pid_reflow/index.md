---
layout: post
title: pid-reflow
description: A real-time reflow-soldering oven simulator in C99 - a PID temperature controller with feedforward and anti-windup driving a dead-time-dominated two-mass thermal plant, with a toggleable Smith predictor, Bode analysis carrying an exact (non-Pade) delay term, relay autotuning, and solder-profile runs scored against industry pass bands. Second application on the pid-lander architecture, sharing a verified controller/UI kit.
skills:
  - Dead-Time Compensation (Smith predictor)
  - Classical Control Theory (PID, feedforward, anti-windup)
  - Thermal Systems Modelling (lumped-parameter, transfer-function derivation)
  - Frequency-Domain Analysis (Bode with exact transport delay)
  - Relay Autotuning (Astrom-Hagglund, Z-N, Tyreus-Luyben)
  - Real-Time Simulation (fixed-timestep, deterministic time scaling)
  - C Programming & Shared-Library Architecture
  - Test Harness Design (headless suites, shadow-verified self-test)

main-image: /console.png
---

---
# pid-reflow - Dead-Time Control of a Thermal Plant in C

## Project Overview & Scope

***pid-reflow*** is the second application built on the [pid-lander](../03_pid-lander) architecture: a process-control console where a PID temperature controller drives a reflow-soldering oven through a solder profile. I built it to cover the one classical-control problem the lander could not: **dead time**. The oven's temperature sensor reports the past - `T_meas(t) = T_air(t − τ_d)` - and the headline feature is a toggleable **Smith predictor** that compensates for the delay with an internal plant model. The actuator is one-sided again (a heater cannot cool; cooling comes only from ambient losses and an openable door), so the lander's saturation machinery carries over directly.

I wrote the project to a specification I drafted first (a 400-line `ROADMAP.md` treating the lander as architectural reference and parts donor), and used it to force a second design decision: the plant-agnostic modules - PID, immediate-mode UI, relay autotuner, utilities - were factored into a shared `controlkit/` library consumed by both applications via a documented `config.h` contract. The reflow-specific code is seven modules (~3,400 lines including tests): thermal plant, Smith predictor, process scoring, history chart, profile editor, analysis plots, and the console.

{% include image-gallery.html images="console.png" height="600" %}
<span style="font-size: 14px">Figure 1; The console mid-reflow: telemetry and per-term PID effort (left), oven cross-section with heater glow, temperature-mapped PCB and thermometer scale (center), controller/plant/sensor sliders (right), 120 s history chart, analysis plot and draggable solder-profile editor (bottom).</span>

{% include image-gallery.html images="smith.gif" height="600" %}
<span style="font-size: 14px">Figure 2; The AGGRESSIVE preset (Kp = 120, deliberately past the delay-limited ultimate gain) limit-cycling on a 150 °C hold; pressing SMITH: ON with the same gains collapses the oscillation.</span>

## The Plant

I modelled the oven as two lumped thermal masses - heated air coupled to the board - measured through a transport delay with optional Gaussian noise:

```
air:    C_a·dTa/dt = u − k_loss·f_door·(Ta − T_amb) − k_b·(Ta − Tb)
board:  C_b·dTb/dt = k_b·(Ta − Tb)
sensor: T_meas(t)  = Ta(t − τ_d) + N(0, σ)          u ∈ [0, P_max]
```

`f_door` is 1 closed, 4 open. I chose the default constants (C_a 150 J/K, k_loss 5 W/K, C_b 60 J/K, k_b 3 W/K, P_max 2 kW) so that the model's behavior is hand-derivable and therefore testable: full power settles at `25 + 2000/5 = 425 °C`, the air time constant is 30 s, the board coupling constant 20 s, and the initial full-power ramp is 13.3 °C/s. All four are encoded as assertions in `test_plant.c`. Eliminating `Tb` gives the transfer function the Bode plot uses - a two-pole low-pass (poles at −1/50 and −1/12 s⁻¹, always overdamped by AM-GM on the middle coefficient) with a zero at −k_b/C_b.

Integration is forward Euler at the lander's fixed 120 Hz timestep behind an accumulator. I documented the stability margin rather than assuming it: the shortest time constant at the harshest slider corner is ~0.7 s, still 85 steps. The sensor delay is a ring buffer of `Ta` sampled every physics step, with the read tap computed from τ_d - index arithmetic I treated as hazardous from the outset, for reasons covered below.

A reflow cycle is six real minutes, so I added **1× / 4× / 16× speed**. The implementation choice matters: the accumulator receives `wall_frame × speed` while the physics step stays exactly 1/120 s, so determinism, the instruments, autotune and profile playback are all speed-invariant - nothing needed a second code path.

## The Controller

The wiring mirrors the lander, re-dimensioned into watts: `u = u_ff + PID(e)` with feedforward `u_ff = k̂_loss·(T_set − T_amb)`, the steady holding power, computed from the *believed* loss coefficient. A "loss estimate ×" slider lets the model lie, and the I-term bar shows the integrator absorbing the shortfall; the test suite pins this at **i_term = 124.8 W against a predicted 0.2 × 5 W/K × 125 K = 125 W** for a 0.8× lie at 150 °C. The shared `pid.c` came across unmodified: conditional-integration anti-windup against output limits set to the actuator range *remaining after feedforward*, derivative on measurement through a low-pass (I set 1 s here - slow plant, slower filter), bumpless live tuning.

Two numbers changed in translation from newtons to watts, both by measurement rather than judgment:

* The roadmap's provisional default gains failed the acceptance test I had written for them (19.96 % overshoot on the 25 → 150 °C step, never settled), so I grid-searched the gain space headless and shipped Kp 50 / Ki 2 / Kd 50: **1.53 % overshoot, settled in 17 s**, ripple-free, still passing under the loss-estimate lie.
* I cut the roadmap's Kd slider ceiling from 2000 to 500 after verification showed that with 2 s of dead time plus the 1 s filter, derivative gain beyond ~400 only destabilises the loop.

## The Smith Predictor

The predictor runs an internal model of the oven with its own (possibly wrong) parameters `Ĉ_a, k̂_loss, τ̂_d`, plus a second delay line to delay its own prediction, and feeds the PID:

```
y_fb = T̂a(t) + [ T_meas(t) − T̂a(t − τ̂_d) ]
```

- the model's undelayed "now", corrected by the model error observed where comparison is fair, in the past. With a good model the delay leaves the loop; the model-error sliders degrade it measurably, and a SMITH plot mode exposes all three internal signals.

One deliberate design decision: the internal model is **first-order - one mass, no board**. A matched-structure model would perform better, but I wanted the correction term to carry visible, honest work even at "perfect" slider settings, because a structurally exact internal model is not something a real plant ever grants. The cost of that choice is recorded in the weaknesses table.

The acceptance demonstration is an assertion in `test_pid.c` - gains past the delay-limited ultimate gain (Kp = 120, Ki = 2) on a 25 → 150 °C step with τ_d = 4 s:

| | overshoot | sustained oscillation (tail p2p) | settles |
| --- | --- | --- | --- |
| plain PID | 23.1 % | 38.6 K | never |
| **Smith ON** (same gains) | **1.3 %** | **0.09 K** | 25 s |

## Analysis Instruments

The Bode plot draws the open loop `L(jω) = C(jω)·G(jω)·e^(−jωτ_d)` with the delay's phase **exact - I refused a Padé approximation**. Dragging the delay slider tilts the phase floor down without bound and collapses the margins, which is the behavior the app exists to show.

{% include image-gallery.html images="bode_delay.gif" height="500" %}
<span style="font-size: 14px">Figure 3; Dragging the sensor-delay slider 0 → 8 s on the BODE view: gain unchanged, phase falling without bound, margins collapsing, verdict flipping to UNSTABLE.</span>

Exactness has a consequence I had to design around: the closed-loop characteristic equation becomes transcendental, so the lander's Routh-Hurwitz verdict is mathematically unavailable - there is no polynomial to give it. Margins alone were already ruled out (the lander's conditional-stability episode showed a positive phase margin on a provably unstable loop). So the stability verdict here is computed by the method the lander used only as a *validator*: the linearized closed loop - exact discrete PID, the real delay line, the derivative filter, the Smith predictor when enabled - is simulated over six dominant time constants and tested for amplitude decay. To keep that affordable per frame, every parameter the verdict depends on sits in one padding-free struct and a `memcmp` decides whether anything changed since the last frame; the simulation reruns only when a slider actually moves. The same linear simulation drives the predicted-STEP plot, with predicted and measured overshoot/settling printed side by side as in the lander.

## Relay Autotuning

The shared Åström-Hägglund relay experiment transferred with **one documented deviation from "copy unchanged"**: its hardcoded 30 s give-up horizon became a `config.h` override (240 s), because a thermal plant's ultimate period is tens of seconds. That constant was the only casualty of moving the controlkit between plants, and finding it was part of the point of building a second application. Run at a 150 °C hold, the relay swings ±500 W around the feedforward and measures **Ku = 93.8, Tu = 8.2 s**; the unlocked Ziegler-Nichols preset (Kp 56.3 / Ki 10 / Kd 57.5) holds the setpoint with 0.00 K peak-to-peak ripple. At 16× speed the tens-of-seconds limit cycle is watchable.

## The Process Game

The profile editor is the lander's sequence editor with one substantive change: **ramp interpolation** between points (solder profiles are ramps; step mode remains behind a toggle). Runs are scored on the **board** temperature, not the air and not the sensor - I chose the scoring target to make a specific failure mode visible: a controller can track the air perfectly and still produce a cold joint, because the payload lags the air it sits in.

| metric | pass band | failure verdict |
| --- | --- | --- |
| peak board temperature | 235–250 °C | `COLD JOINT` / `SCORCHED` |
| time above liquidus (217 °C) | 45–90 s | `COLD JOINT` / `OVERBAKED` |
| max board ramp rate | ≤ 3 °C/s | `THERMAL SHOCK` |
| soak time in 150–200 °C | 60–150 s | advisory |

plus IAE / ITAE / max error / heater effort kept per run in a four-slot scoreboard with the gains that flew them. Three presets ship: `SAC305` (the standard lead-free profile; earns `GOOD SOLDER` with the shipped gains), `LEADED` (Sn63/Pb37 - flown well it still scores `COLD JOINT`, because the pass bands judge lead-free solder and its 183 °C alloy never needs to reach 217; I kept that mismatch deliberately), and `SLOW` (long-soak, wide margins).

<!-- TODO recording pending — uncomment when sac305_run.gif is added:
{% include image-gallery.html images="sac305_run.gif" height="600" %}
<span style="font-size: 14px">Figure 4; A SAC305 run at 16×: gold staircase is the recipe, white the air, amber the board lagging it; the solder bead melts above the liquidus line, the door opens on the cooldown segment, and the run posts peak/TAL/ramp scores and a GOOD SOLDER verdict.</span> -->

## Challenges & Bugs

### The Delay Tap That Read the Future

The lander project paid a week for a float-truncation buffer overrun, so the roadmap ordered that lesson banked: round instead of truncating, and bounds-guard every computed index. I wrote the delay-line tests to probe absurd inputs anyway, and they caught a subtler cousin on first run. For a huge τ, `τ/dt` overflows the `int` range, and **float→int overflow is undefined behavior** - on x86 it lands on `INT_MIN`, which a *post-conversion* clamp would dutifully "fix" to 0, silently reading the **newest** sample instead of the oldest. A sensor asked for the distant past would report the present, with no crash and no warning. The fix is to clamp in float space, before the conversion:

```c
// Bounds-guard IN FLOAT, before the int conversion: a wild tau makes
// tau/dt overflow int range, and float->int overflow is undefined
// behavior (on x86 it lands on INT_MIN, which a post-conversion clamp
// would "fix" to 0 - the newest sample instead of the oldest).
float fn = tau / dt + 0.5f;
int n;
if      (fn <= 0.0f)                    n = 0;
else if (fn >= (float)(DELAY_BUF - 1))  n = DELAY_BUF - 1;
else                                    n = (int)fn;
```

> The guard and the conversion look interchangeable in review; their order is the entire bug. The failing assertion (`delay tap clamps huge tau to ring capacity`) cost three lines to fix; the suite additionally pins the tap bit-exact across 3,600 live steps including a mid-run τ_d change.

### The Door Is a Second Actuator

The auto-door began as a one-line convenience - open the door on cooldown - and consumed more design iterations than the Smith predictor. A slope trigger opens during the reflow *hold* and kills the peak; a threshold version kept time-above-liquidus at 33 s (`COLD JOINT`); and flinging the door open at 245 °C free-falls the board past 3 °C/s (`THERMAL SHOCK`). I swept nineteen hotter and longer-holding profile variants headless and every one traded one failure verdict for the other - which established that the recipe wasn't the problem, the door logic was. The shipped version treats the door as what it is, a bang-bang second actuator with its own small controller: open only on a genuine cooldown segment (profile slope < −1 °C/s) *and* only once closed-door cooling can no longer follow the falling target (air > setpoint + 3 °C), closing with hysteresis at +1.5 °C. With it the spec SAC305 profile earns **GOOD SOLDER: peak 237.1 °C, 48 s above liquidus, max ramp 2.19 °C/s** - and disabling `AUTODOOR` and opening the door at the peak still reproduces `THERMAL SHOCK` on demand.

### Smaller Fights

* MSYS2's `make` does not see the Windows `OS` environment variable the lander's build relied on, so the DLL-staging recipe silently never fired; the conditional now tests the toolchain instead of the environment. True static linking stays off the table - MSYS2's `libraylib.a` is compiled against GLFW DLL imports.

## Verification

Every number quoted on this page is reproduced by a headless check (`make test`, no graphics dependency):

* **`test_plant`** - the 425 °C / 30 s / 20 s / 13.3 °C/s sanity numbers; delay-line sample-exactness (rounding, bounds, overflow, live τ_d changes); energy sanity (never below ambient door-closed, never NaN).
* **`test_pid`** - the 1.53 % acceptance step; the 125 W loss-lie absorption; the Smith table; autotune convergence and Z-N hold quality; a full SAC305 run earning `GOOD SOLDER`.
* **`test_chart`** - the history ring verified sample-perfect against a shadow copy across heater bursts, frame stalls, 16× speed and twelve wraparounds (9,074 pushes, zero mismatches).

In-app, `reflow --selftest` flies the full SAC305 profile autonomously at 16× while cross-checking the entire ring against a shadow history twice per frame (post-physics and post-render - the split that caught the lander's cross-module memory stomp), cycling every analysis plot so all draw paths execute, and exits nonzero on any mismatch. Its final line: `pushes=2340 mismatches=0 phantom_readings=0 verdict=GOOD SOLDER`.

## Strengths & Weaknesses

### This implementation

| Aspect | Strength | Weakness / limitation |
| --- | --- | --- |
| Dead-time modelling | Delay is exact everywhere: per-step ring buffer in the plant, `e^(−jωτ_d)` in the Bode math - no Padé error anywhere | Transport delay only; a real thermocouple adds a first-order lag (its own thermal mass) that is not modelled |
| Stability verdict | Works where Routh cannot (transcendental loop); includes filter, delay line and Smith predictor; `memcmp`-keyed cache makes it free until a slider moves | A numerical decay *test*, not a proof: finite horizon (≤ 900 s) and a heuristic decay criterion can misclassify a loop diverging slowly enough near the boundary |
| Verdict scope | Labelled "linear simulation" in the UI - it does not overclaim | Linearization ignores the one-sided saturation; "STABLE" is a small-signal statement, and a large step can still limit-cycle against the u ≥ 0 floor |
| Smith predictor | Structural mismatch (one mass, no board) is deliberate and visible; the SMITH plot shows the correction carrying real work | The same choice means performance degrades faster with plant changes than a matched-structure model; the internal model does not adapt |
| Process scoring | Scored on the board (the payload) against industry-shaped bands with named failure verdicts | Bands are fixed to lead-free SAC305; `LEADED` is judged against the wrong alloy's bands by design |
| Auto-door | Thermostatic with hysteresis; provably meets the shipped profile | A heuristic bolt-on outside the control law; no coordinated heater/door action; thresholds are hand-tuned constants |
| Verification | Every quoted number is an assertion; the shadow-verified self-test guards the instrumentation itself | Tests pin behavior at the default constants; the 12-slider parameter space is sampled by hand, not swept |

### Inherited from pid-lander (simulation architecture & PID stack)

| Aspect | Strength | Weakness / limitation |
| --- | --- | --- |
| Fixed-timestep core | Deterministic 120 Hz physics decoupled from render; the speed multiplier scales sim time without touching the step, so instruments and tests are speed-invariant | Forward Euler (the lander needed semi-implicit for its oscillatory plant): four orders of margin at defaults, ~85 steps at the harshest slider corner, no adaptive check |
| PID implementation | Anti-windup seeing the true post-feedforward saturation boundary, derivative on measurement, filtered D, bumpless tuning - ran unmodified in a second plant and unit system | Fixed structure: no gain scheduling although the plant is switched (door multiplies k_loss by 4) and nonlinear at the actuator floor; D filter constant is not noise-adaptive |
| Feedforward pattern | Model-based holding power with a deliberate lie slider makes the integrator's job visible and testable | Static, single-parameter (k̂_loss); no feedforward from the profile slope, which a ramp-following controller would benefit from |
| Relay autotune | Purely observational, so it survives arbitrary plant-slider changes; hysteresis widens with the noise setting | Describing-function Ku assumes a near-sinusoidal limit cycle; one hardcoded constant already needed a per-plant override, and others may lurk |
| Physics fidelity | Lumped two-mass model is fully analysable - closed-form transfer function, hand-checkable time constants, every behavior testable | No radiation (significant at 250 °C), constant convection coefficients, single-node board without joint-level gradients, heater with no element lag |
| One-sided actuator | Saturation is routine rather than exceptional, which keeps the anti-windup machinery honest | Cooling authority (door) is binary and external to the controller in both apps; the asymmetry is exposed but never solved by the control law |

## Future Work

* **Thermocouple lag** - add a first-order sensor pole alongside the transport delay; it changes the Bode phase materially and would exercise the Smith predictor's mismatch handling further.
* **A rigorous verdict** - the Nyquist criterion handles `e^(−jωτ_d)` exactly; an encirclement count over the plotted frequency sweep would replace the decay heuristic with a real stability statement, at the cost of careful contour handling near the origin poles.
* **Door in the control law** - replace the thermostat with split-range control (heater and door as one signed actuator) or a supervisory layer; the current design demonstrably works but is not optimal, and the cooldown segment is where runs lose most of their ITAE.
* **Profile-slope feedforward** - `u_ff` currently holds setpoints; adding `Ĉ_a·dT_set/dt` would cut the tracking lag on ramps that the integrator now covers.
* **Parameter-space sweeping** - the headless suites pin default-constant behavior; sweeping the slider space (the tuner and profile-sweep scratch tools already exist) would turn hand-sampled confidence into coverage.
* **An adaptive Smith model** - recursive least squares on `Ĉ_a, k̂_loss` from the correction signal would close the loop on the model-mismatch demonstration.

## Learnings

* **Dead time needed structure, not tuning.** Every gain-side remedy I tried against the delay - including derivative action up to the slider ceiling - only moved the failure; the Smith predictor removed it. Building the predictor made the block diagram feel inevitable rather than clever.
* **Exactness relocates difficulty.** Keeping the delay exact made the Bode phase honest and destroyed the Routh option in the same stroke; I traded a mathematical certainty for an engineering test and had to make that trade consciously and label it in the UI.
* **Undefined behavior hides behind plausible clamps.** A bounds guard after a float→int conversion reviews identically to one before it, and one of them reads the future. The absurd-input test found in seconds what inspection had already approved.
* **Reuse is only proven the second time.** controlkit's PID ran unmodified from meters-newtons to kelvin-watts; the autotuner needed one constant parameterized. Both facts became knowledge only by building the second application.
* **Secondary actuators deserve controllers.** "Open the door on cooldown" was one line that cost more iterations than the headline feature; the fix was admitting the door needed its own feedback law, however small.

> Full source - the thermal plant, Smith predictor, analysis plots, process scoring, the shared controlkit, and all test harnesses - is available on my [GitHub](https://github.com/OliCar-del/ReflowPID).
