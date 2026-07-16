---
layout: post
title: pid-reflow
description: A real-time reflow-soldering oven simulator in C, built to demonstrate classical control of a dead-time-dominated thermal plant - Smith-predictor dead-time compensation, PID with feedforward and anti-windup, Bode analysis with an exact (non-Pade) delay term, relay autotuning, and a solder-profile process game scored against industry pass bands - sharing a verified controller/UI kit with its sibling project pid-lander.
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

***pid-reflow*** is the second application in a control-theory sandbox family (the first is [pid-lander](../03_pid-lander)): a process-control console where the user tunes a PID temperature controller to fly a reflow-soldering oven through a solder profile. Where the lander teaches saturation and tuning, the oven teaches **dead time**. The temperature sensor reports the past - `T_meas(t) = T_air(t − τ_d)` - so every feedback decision acts on stale information, and no amount of derivative gain can buy the lost phase back. The headline feature is a toggleable **Smith predictor** that removes the delay from the loop by feeding the PID a model's prediction of *now*, corrected by how wrong the model was *then*.

The actuator is one-sided again, in a new costume: a heater cannot cool. Descent authority came free with gravity in the lander; here, cooling comes only from losses to ambient and an openable door - so overshoot at the solder peak costs real process time and can scorch the board.

The project was built to a written specification (a 400-line `ROADMAP.md` treating the lander as architectural reference and parts donor) and deliberately factors the plant-agnostic modules - PID, immediate-mode UI, relay autotuner, utilities - into a shared `controlkit/` library used verbatim by both applications. The reflow-specific code is seven modules (~3,400 lines with tests): thermal plant, Smith predictor, process scoring, history chart, profile editor, analysis plots, and the console itself.

{% include image-gallery.html images="console.png" height="600" %}
<span style="font-size: 14px">Figure 1; The console mid-reflow: telemetry and per-term PID effort (left), oven cross-section with glowing elements, temperature-mapped PCB and thermometer scale (center), controller/plant/sensor sliders (right), 120 s history chart, analysis plot and the draggable solder-profile editor (bottom).</span>

{% include image-gallery.html images="smith_toggle.gif" height="600" %}
<span style="font-size: 14px">Figure 2; The thesis demo. The AGGRESSIVE preset (Kp = 120, deliberately past the delay-limited ultimate gain) limit-cycles on a 150 °C hold - then SMITH: ON is pressed with the same gains and the oscillation collapses. Same controller, same plant; only the dead time has left the loop.</span>

## The Plant: Two Thermal Masses and a Sensor That Reports the Past

The oven is a lumped-parameter model: heated air coupled to the board it is soldering, measured through a transport delay with optional Gaussian noise:

```
air:    C_a·dTa/dt = u − k_loss·f_door·(Ta − T_amb) − k_b·(Ta − Tb)
board:  C_b·dTb/dt = k_b·(Ta − Tb)
sensor: T_meas(t)  = Ta(t − τ_d) + N(0, σ)          u ∈ [0, P_max]
```

`f_door` is 1 closed and 4 open - the door is forced cooling, and the only downward authority the process has. At the default constants (C_a 150 J/K, k_loss 5 W/K, C_b 60 J/K, k_b 3 W/K, P_max 2 kW) the model reproduces hand-derivable sanity numbers that are all encoded as test assertions: full power settles at `25 + 2000/5 = 425 °C`, the air time constant is 30 s, the board coupling constant 20 s, and the initial full-power ramp is 13.3 °C/s - deliberately near the 3 °C/s board thermal-shock limit once the coupling filters it.

Eliminating `Tb` gives the transfer function the Bode plot uses - a two-pole low-pass (poles at −1/50 and −1/12 s⁻¹, provably always overdamped by AM-GM on the middle coefficient) with a zero at −k_b/C_b. Physics runs at the lander's fixed 120 Hz timestep behind an accumulator; forward Euler suffices here (documented margin: the shortest time constant at the harshest slider corner is ~0.7 s, still 85 steps).

The sensor delay is a ring buffer of `Ta` sampled every physics step, and its index arithmetic is where the lander's hardest-won lesson was banked (see Challenges). Because a reflow cycle is six real minutes, the console has **1× / 4× / 16× speed**: the accumulator receives `wall_frame × speed` while physics still steps at exactly 1/120 s, so determinism, every instrument, autotune and playback are unaffected - fast-forward is free.

## The Controller Stack

The wiring mirrors the lander exactly, re-dimensioned into watts: `u = u_ff + PID(e)` with feedforward `u_ff = k̂_loss·(T_set − T_amb)` - the steady holding power - computed from the *believed* loss coefficient. A "loss estimate ×" slider lets the model lie (the analog of the lander's mass-estimate lie), and the I-term bar shows the integrator quietly absorbing the missing watts: with a 0.8× lie at 150 °C the test suite measures **i_term = 124.8 W against a predicted 0.2 × 5 W/K × 125 K = 125 W**.

The shared `pid.c` arrives with its industrial upgrades intact - conditional-integration anti-windup against output limits set to the actuator range *remaining after feedforward*, derivative on measurement through a low-pass (1 s here: slow plant, slower filter), bumpless live tuning. Two numbers changed in translation from newtons to watts, both verified rather than assumed:

* The shipped default gains were **grid-searched against the acceptance test**: the roadmap's provisional defaults flew the 25 → 150 °C acceptance step with 19.96 % overshoot and never settled; the search settled on Kp 50 / Ki 2 / Kd 50, which flies it with **1.53 % overshoot, settling in 17 s**, ripple-free, and still holds under the loss-estimate lie.
* The roadmap's suggested Kd slider ceiling of 2000 was cut to 500 after verification: with 2 s of dead time plus the 1 s filter, derivative gain beyond ~400 only destabilises - an early, concrete sighting of the app's whole thesis.

## The Smith Predictor

The dead-time compensator runs an internal first-order model of the oven with its own (possibly wrong) parameters `Ĉ_a, k̂_loss, τ̂_d`, plus a second delay line to delay its own prediction:

```
y_fb = T̂a(t)  +  [ T_meas(t) − T̂a(t − τ̂_d) ]
       model's       correction: the model error, observed
       "now"         in the past where the sensor lives
```

The PID sees `y_fb` instead of `T_meas`. With a perfect model the delay leaves the loop entirely; with the model-error sliders it degrades honestly, and a dedicated SMITH plot mode shows the three internal signals so the mismatch can be watched leaking error back in. The internal model is deliberately *structurally* simpler than the plant - one mass, no board - so even at "perfect" slider settings the correction term carries real work, which is the honest situation every industrial Smith predictor lives in.

The acceptance demonstration is encoded as an assertion in `test_pid.c`: gains deliberately past the delay-limited ultimate gain (Kp = 120, Ki = 2) flying a 25 → 150 °C step with τ_d = 4 s:

| | overshoot | sustained oscillation (tail p2p) | settles |
| --- | --- | --- | --- |
| plain PID | 23.1 % | 38.6 K | never |
| **Smith ON** (same gains) | **1.3 %** | **0.09 K** | 25 s |

## Analysis Instruments: When Routh Cannot Help You

The Bode plot draws the open loop `L(jω) = C(jω)·G(jω)·e^(−jωτ_d)` with the delay's phase contribution **exact, not a Padé approximation**: drag the delay slider and the phase floor tilts down without bound while the margins collapse - the visual thesis of the app.

{% include image-gallery.html images="bode_delay.gif" height="500" %}
<span style="font-size: 14px">Figure 3; Dragging the sensor-delay slider from 0 to 8 s on the BODE view: the gain curve does not move, the phase falls through the floor, the margins evaporate, and the verdict line flips to UNSTABLE - derivative action cannot buy this phase back.</span>

Exactness has a price: the closed-loop characteristic equation becomes transcendental, so the lander's **Routh-Hurwitz verdict is mathematically unavailable** - there is no polynomial to hand it. And the lander's other lesson still stands: margins alone mislead on conditional-stability loop shapes. So the stability verdict is computed the way the lander *validated* its Routh implementation - by brute force. The linearized closed loop (deviation coordinates, exact discrete PID, the real delay line, the derivative filter, and the Smith predictor when enabled) is simulated for six dominant time constants and tested for amplitude decay. Every parameter the verdict depends on is gathered into one padding-free struct so a `memcmp` answers "did anything change since last frame?" - the simulation only reruns when a slider actually moves. The same linear simulation, cached separately at full resolution, drives the predicted-STEP plot with predicted-vs-measured overshoot and settling printed side by side, lander-style.

## Relay Autotuning on a Slow Plant

The shared Åström-Hägglund relay experiment carried over with **one documented deviation from "copy unchanged"**: its hardcoded 30 s give-up horizon became a `config.h` override (240 s), because a thermal plant's ultimate period is tens of seconds - the first real test of the controlkit contract's flexibility. Run at a 150 °C hold (standard practice, noted in the UI), the relay swings ±500 W around the feedforward and measures **Ku = 93.8, Tu = 8.2 s**; the unlocked Ziegler-Nichols preset (Kp 56.3 / Ki 10 / Kd 57.5) then holds the setpoint with 0.00 K peak-to-peak ripple. Because the method is observational, it keeps working after the plant sliders have changed the oven underneath it - and at 16× speed the tens-of-seconds limit cycle is watchable.

## The Process Game: GOOD SOLDER or Bust

The profile editor (the lander's sequence editor re-skinned, with **ramp interpolation** because solder profiles are ramps, not steps) plays a recipe against sim time. The run is scored on the **board** temperature - not the air, and not the sensor - because the payload is the point: track the air perfectly and you can still ship a cold joint.

| metric | pass band | failure verdict |
| --- | --- | --- |
| peak board temperature | 235–250 °C | `COLD JOINT` / `SCORCHED` |
| time above liquidus (217 °C) | 45–90 s | `COLD JOINT` / `OVERBAKED` |
| max board ramp rate | ≤ 3 °C/s | `THERMAL SHOCK` |
| soak time in 150–200 °C | 60–150 s | advisory |

plus the comparative indices kept from the lander (IAE / ITAE / max error / heater effort) in a four-slot scoreboard with the gains that flew each run. Presets: `SAC305` (the standard lead-free profile - earns `GOOD SOLDER` with the shipped gains), `LEADED` (Sn63/Pb37: flown *well* it still scores COLD against the lead-free bands, a deliberate lesson that the bands judge the alloy), and `SLOW` (long-soak, wide margins).

{% include image-gallery.html images="sac305_run.gif" height="600" %}
<span style="font-size: 14px">Figure 4; A SAC305 run at 16×: the gold staircase is the recipe, white the air, amber the board lagging it; the solder bead melts above the liquidus line, the door pops open on the cooldown segment, and the run drops peak/TAL/ramp scores and a GOOD SOLDER verdict onto the board.</span>

## Challenges & Bugs

### The Delay Tap That Read the Future

The lander's worst bug was a float-truncation buffer overrun, and the roadmap ordered that lesson banked: round, don't truncate, and bounds-guard every computed index. The delay line's test suite went further and probed absurd inputs - and caught a subtler cousin. For a huge τ, `τ/dt` overflows the `int` range, and **float→int overflow is undefined behavior**; on x86 it lands on `INT_MIN`, which a *post-conversion* clamp would dutifully "fix" to 0 - silently reading the **newest** sample instead of the oldest. A sensor asked to report the distant past would instead report the present, with no crash and no warning.

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

> The order of the guard and the conversion is the entire bug. The lander paid a week for this class of arithmetic; here the test (`delay tap clamps huge tau to ring capacity`) failed on first run, the fix was three lines, and the suite additionally pins the tap **bit-exact across 3,600 live steps including a mid-run τ_d change**.

### The Door Is a Second Actuator

The auto-door began as a one-line convenience - open on cooldown - and turned into the project's genuine design problem. A naive slope trigger either opens during the reflow *hold* (killing the peak: the spec profile scored `COLD JOINT` with 33 s above liquidus) or flings the door open at 245 °C, free-falling the board past the 3 °C/s limit (`THERMAL SHOCK`). A headless sweep of nineteen hotter and longer-holding profile variants confirmed the trade was unwinnable by recipe-shaping alone: every variant just traded one failure verdict for the other. The fix was to treat the door as what it is - a bang-bang second actuator that needs its own controller: a small thermostat that opens only on a genuine cooldown segment (profile slope < −1 °C/s) *and* only when closed-door cooling can no longer keep up (air more than 3 °C above the falling target), closing again with hysteresis at 1.5 °C. With it, the spec SAC305 profile earns **GOOD SOLDER: peak 237.1 °C, 48 s above liquidus, max ramp 2.19 °C/s** - and turning `AUTODOOR` off and popping the door at the peak still demonstrates the shock verdict on demand.

### Smaller Fights

* **MSYS2's `make` doesn't see Windows' `OS` variable** the way the lander's Git Bash build did, so the DLL-staging recipe silently never fired; the conditional now tests the toolchain rather than the environment. (True static linking remains impossible: MSYS2's `libraylib.a` is compiled against GLFW DLL imports.)
* **Session limits mid-build** - development spanned a hard interruption between writing `test_pid.c` and first running it; the phase discipline (every phase ends green) made the resume seamless.

## Verification Culture

Every number quoted on this page is reproduced by a headless check with no graphics dependency (`make test`):

* **`test_plant`** - the 425 °C / 30 s / 20 s / 13.3 °C/s sanity numbers; delay-line sample-exactness (rounding, bounds, overflow, live τ_d changes); energy sanity (never below ambient door-closed, never NaN).
* **`test_pid`** - the 1.53 % acceptance step; the 125 W loss-lie absorption; the Smith on/off table; autotune convergence and Z-N hold quality; a full SAC305 run earning `GOOD SOLDER`.
* **`test_chart`** - the history ring verified sample-perfect against a shadow copy across heater bursts, frame stalls, 16× speed and twelve wraparounds (9,074 pushes, zero mismatches).

And in-app: `reflow --selftest` flies the full SAC305 profile autonomously at 16× while cross-checking the entire ring against a shadow history **twice per frame** (post-physics and post-render - the split that caught the lander's cross-module memory stomp), cycling every analysis plot so all draw paths execute, exiting nonzero on any mismatch. Its final line: `pushes=2340 mismatches=0 phantom_readings=0 verdict=GOOD SOLDER`.

## Strengths & Weaknesses

Honest scope statements, in two layers: what this implementation does well or cheaply, and what the architecture inherited from pid-lander brings with it - both ways.

### This implementation

| Aspect | Strength | Weakness / limitation |
| --- | --- | --- |
| Dead-time modelling | The delay is exact everywhere: a per-step ring buffer in the plant, `e^(−jωτ_d)` in the Bode math - no Padé approximation error anywhere | Transport delay only; a real thermocouple also has a first-order lag (its own thermal mass), which is not modelled |
| Stability verdict | Correct where Routh is unavailable (transcendental loop); includes the filter, delay line and Smith predictor; `memcmp`-keyed caching makes it free until a slider moves | It is a numerical decay *test*, not a proof: finite horizon (≤ 900 s), heuristic decay criterion - a loop diverging slowly enough could be misclassified near the boundary |
| Verdict scope | Honest about its own linearity: labelled "linear simulation" in the UI | Linearization ignores the one-sided saturation, so "STABLE" describes small-signal behavior; a large step can still limit-cycle against the u ≥ 0 floor |
| Smith predictor | Structural model mismatch (one mass, no board) is deliberate and visible - the SMITH plot shows the correction carrying real work | The same choice means predictor benefit degrades faster with plant changes than a matched-structure model would; there is no adaptation of the internal model |
| Process scoring | Scored on the board (the payload), with industry-shaped bands and named failure verdicts | Pass bands are fixed to lead-free SAC305; the LEADED preset is scored against the wrong alloy's bands by design (a lesson, but also a limitation) |
| Auto-door | Thermostatic with hysteresis, provably meets the profile it ships with | It is a heuristic bolt-on, not part of the control law - no coordinated heater/door optimization, and its thresholds are tuned constants |
| Verification | Every quoted number is an assertion; shadow-verified self-test guards the instrumentation itself | Tests pin behavior at the default constants; the slider space (12 sliders) is sampled by hand, not swept |

### Inherited from pid-lander (simulation architecture & PID stack)

| Aspect | Strength | Weakness / limitation |
| --- | --- | --- |
| Fixed-timestep core | Deterministic 120 Hz physics decoupled from render; the speed multiplier scales sim time without touching the step - instruments and tests are speed-invariant | Forward Euler (the lander used semi-implicit for its oscillatory plant): fine at four orders of margin, but the margin shrinks to ~85 steps at the harshest slider corner with no adaptive check |
| PID implementation | Anti-windup that sees the true post-feedforward saturation boundary; derivative on measurement; filtered D; bumpless live tuning - proven in a second plant and second unit system without modification | Fixed structure: no gain scheduling, though the plant is switched (door multiplies k_loss by 4) and nonlinear at the actuator floor; D filter time constant is a constant, not noise-adaptive |
| Feedforward pattern | Model-based holding power with a deliberate lie slider makes the integrator's job visible and testable | Static feedforward from one parameter (k̂_loss); no feedforward from the profile slope, which a ramp-following oven would benefit from |
| Relay autotune | Purely observational - survives arbitrary plant-slider changes; hysteresis widens with the noise setting | Describing-function Ku assumes a near-sinusoidal limit cycle; one hardcoded constant (the timeout) already needed a per-plant override, hinting more may lurk |
| Physics fidelity | Lumped two-mass model is fully analysable (closed-form transfer function, hand-checkable time constants) - the right fidelity for teaching control | No radiation (significant at 250 °C), constant convection coefficients, single-node board with no joint-level gradients, heater with no element thermal mass or lag |
| One-sided actuator | Keeps the central lesson of both apps honest: saturation is routine, not exceptional | Cooling authority (door) is binary and external to the controller in both apps - the asymmetry is taught but never *solved* by the control law |

## Learnings

* **Dead time is a different enemy than saturation.** The lander's problems yield to better tuning; the oven's do not - no gain schedule recovers phase lost to delay. Only structure (the Smith predictor) does, and building one made the textbook block diagram feel inevitable rather than clever.
* **Exactness moves the difficulty, it doesn't remove it.** Refusing the Padé approximation made the Bode phase honest and destroyed the Routh option; the replacement verdict (simulate and test decay) traded mathematical certainty for engineering confidence, and the trade had to be made consciously.
* **Undefined behavior hides behind plausible clamps.** A bounds guard placed *after* a float→int conversion looks identical in review to one placed before, and one of them reads the future. Probing absurd inputs in tests is what found it.
* **Code is only proven reusable the second time.** controlkit's PID ran unmodified in kelvin-watts after a life in meters-newtons; the autotuner needed one constant parameterized. Both facts - what held and what didn't - only became knowledge by building the second application.
* **Secondary actuators deserve controllers too.** The auto-door consumed more design iterations than the Smith predictor. "Just open the door on cooldown" is the kind of sentence that costs an afternoon.

> Full source - the thermal plant, Smith predictor, analysis plots, process scoring, the shared controlkit, and all test harnesses - is available on my [GitHub](https://github.com/OliCar-del/ReflowPID).
