---
layout: post
title: loggy - Optically Isolated Industrial Data Logger (Sensor Unit)
description: A two-board industrial DAQ with a fully floating, battery-powered sensor unit linked to its control unit over a single TOSLINK fibre. Four 16-bit voltage channels with per-channel ±1V/±10V analog range switching, acceleration and temperature logging, latching alarms, and 10µA/200µA precision current sources. This entry covers the sensor unit hardware, alarm indicator firmware, optical link bring-up and BOM engineering.
skills:

 - Analog Front-End Design (protection, buffering, conditioning)
 - PCB Design & Layout (Altium)
 - Circuit Simulation & Verification (LTspice)
 - Optical Transceiver Design (TOSLINK)
 - Embedded C (STM32)
 - BOM Management & Cost Engineering

main-image: /AltiumRender.png
---

<!-- TODO: constructed-board photos pending. Replace the placeholder filenames
     `sensor_board_constructed.jpg` and `toslink_bench.jpg` below with the real
     photo filenames once taken. -->

# loggy - Industrial Data Logger, Sensor Unit

## Project Overview

***loggy*** is an industrial data logger (DAQ) built as a four-person university team project. The instrument is split into two custom PCBs: a USB-powered control unit (display, controls, SD logging, PC link) and a battery-powered sensor unit that performs all measurement. The only connection between them is a single TOSLINK fibre optic cable, so the measurement side is totally electrically isolated — a multi-kilovolt fault at the input terminals can never reach the operator or the PC.

Headline requirements on the sensor unit:

* Four voltage channels (CH1-4): 16-bit resolution over user-selectable ±1V or ±10V ranges, switched per channel in analog circuitry, with >1MΩ input impedance and ±11V input withstand
* 3-axis acceleration (CH5-7) and ambient temperature (CH8); all eight channels sampled at ≥2Hz
* 10µA and 200µA constant current sources (±5%) supporting resistive temperature measurement (thermistor / Pt1000)
* 16 red alarm LEDs (two per channel) implementing disabled/live/latching alarm modes
* A custom optical transceiver built from a bare 3mm LED and a BPW34 photodiode — no off-the-shelf TOSLINK modules
* Whole-product BOM under $125 AUD

Work split four ways: sensor unit hardware, sensor unit firmware, control unit hardware and firmware, and PC GUI. This entry covers my scope — the sensor unit hardware end-to-end (circuit design, simulation, schematic capture, PCB layout, construction), testing of the sensor board and TOSLINK transceiver, integration testing against the control board, firmware for the alarm indicators, and the project BOM.

## Architecture

The signal chain runs: terminal blocks → protection → buffering → channel MUX → range selection → conditioning → ADC → MCU → optical link. Every analog block followed the same pipeline before touching copper: design, LTspice simulation, breadboard prototype, then schematic capture.

{% include image-gallery.html images="Preliminary_design_flow.png" height="450" %}
<span style="font-size: 14px">Figure 1: Preliminary sensor unit block diagram, from input terminal blocks through conditioning and digitisation to the optical link, including MCU pin allocations per peripheral.</span>

| Subsystem | Selected Component | Justification |
| --- | --- | --- |
| **MCU** | STM32L433CCT6 (48-LQFP) | Same part as the control unit — one toolchain and HAL across the team, and stocked locally. Two I2C buses, SPI and USARTs cover every peripheral, though the pin map ends up fully committed. |
| **ADC** | ADS1119 (16-bit, I2C) | Internal input mux doubles as the range selector — both conditioned range outputs land on separate ADC inputs, so range switching costs no extra analog switch. Rail-referenced FSR (GND-3.3V) eliminates a separate precision reference IC. |
| **Channel MUX** | ADG1404 (4:1, 3Ω on) | One shared conditioning chain instead of four — fewer precision op-amps, less board area, lower cost. On-resistance is irrelevant inside a buffered chain. |
| **Input protection** | SMBJ11CA TVS + buffered follower | Follower as the first active stage satisfies the >1MΩ input impedance requirement; 11V TVS clamps at the terminals meet the ±11V withstand spec and keep faults away from the op-amps. |
| **Conditioning** | OPA4192 (quad, RRIO) | Precision gain/offset stages for both ranges; quad package keeps the count down. |
| **Alarm drive** | TLC5927IDWR | 16-channel constant-current LED sink driver — all 16 alarm LEDs from a 4-wire serial interface, one external resistor sets every LED current. |
| **Accelerometer** | LIS3DH (I2C) | Three axes at 12-bit comfortably exceeds the 8-bit/axis requirement. |
| **±12V analog rails** | MC34063AP boost/inverter | Op-amp headroom rails from the 6×AAA (9V nominal) pack; immediately available and breadboard-verified before committing to layout. |

## Analog Front End

Each range is conditioned in parallel rather than switched: the ±10V path attenuates (gain 0.2) and the ±1V path amplifies (gain 2), and both are offset to centre the signal within the ADC's unipolar input span — keeping op-amp outputs away from the rails where linearity degrades. Diode clamps bound each stage, and ~800Hz RC filtering rolls off noise ahead of the ADC. The ADC's internal mux then picks whichever range the user has selected, under MCU control.

{% include image-gallery.html images="signal_condition.png" height="400" %}
<span style="font-size: 14px">Figure 2: LTspice simulation of the complete conditioning chain from terminal input to ADC pin — input buffer, conditioning buffer, diode clamping, and the parallel gain/offset stages for the ±1V and ±10V ranges.</span>

## Current Sources

The 10µA and 200µA sources use an improved Howland current pump built on the INA592, following TI's reference topology: the INA592's internally matched precision resistor network sets the pump's accuracy, a REF5050 provides the 5V reference, and buffered output feedback raises the output impedance so the current stays flat across the required 3V compliance range. Each source is set by a single precision resistor, which keeps the ±5% accuracy budget in one component rather than spread across a discrete resistor network. Both sources were simulated, breadboarded, and verified against a 10kΩ load before layout.

## Optical Link

The transceiver is built at component level, as the specification demands.

* **Transmit:** the MCU's UART TX drives a BC847 NPN switch; an 82Ω series resistor sets 16mA through the 3mm high-brightness LED.
* **Receive:** the BPW34 photodiode yields only ~6µA of photocurrent, far too little to threshold directly. A TLV6001 transimpedance amplifier converts it to a voltage against a resistor-divided reference, and an LM393LV comparator with a settable threshold squares the result into clean UART logic.
* Trimmers on both transmit intensity and receive threshold provide tuning margin on the bench rather than committing to fixed values on a first spin.

The transceiver was validated standalone in loopback, then end-to-end against the control unit: the final sensor board communicated with the control unit over the fibre, with the transimpedance receiver recovering UART framing reliably once the comparator threshold was tuned.

<!-- TODO photo pending — uncomment and renumber figures when added:
{% include image-gallery.html images="toslink_bench.jpg" height="500" %}
<span style="font-size: 14px">Figure X: TOSLINK transceiver bench validation against the control unit.</span> -->

## Alarms and the GPIO Budget

The 48-pin package is fully allocated — SWD, debug USART, TOSLINK USART, two I2C buses (accelerometer, ADC), three MUX select lines, SPI2 plus latch/output-enable for the LED driver, and the sampling LED account for every usable pin. Driving 16 alarm LEDs from discrete GPIOs was never an option; the TLC5927 reduces them to a 16-bit mask shifted out over SPI2, with a single 2kΩ R-EXT setting ~9.4mA per LED. The LEDs are powered from the battery rail directly, keeping their current out of the 3.3V regulator. The same squeeze applied to timers: with the 16-bit timers already committed, the sampling scheduler runs from a 12-bit timer instead, with the prescaler making up the range.

The alarm firmware implements the three per-channel modes from the specification. Each sample rebuilds the LED mask — for any configured channel exactly one LED of its pair is lit, indicating alarm or no-alarm — and latched alarms hold until an unlatch command arrives from the control unit over the fibre:

```c
/* Rebuild alarm LED mask after each sample set. Latched
   channels stay tripped until unlatched via the optical link. */
for (ch = 0; ch < NUM_CHANNELS; ch++) {
    if (cfg[ch].mode == ALARM_DISABLED) continue;

    bool trip = (sample[ch] > cfg[ch].high) || (sample[ch] < cfg[ch].low);
    if (cfg[ch].mode == ALARM_LATCHING) {
        latched[ch] |= trip;
        trip = latched[ch];
    }
    mask = trip ? (mask | LED_ALARM(ch)) & ~LED_OK(ch)
                : (mask | LED_OK(ch))    & ~LED_ALARM(ch);
}
tlc5927_write(mask);   /* SPI2 shift + LE pulse */
```

## Board Iteration: V1 to V2

The V1 board was deliberately fabricated early, before the design was final. The intent was to get firmware development off a fragile breadboard onto a stable platform, and to surface any MCU/ADC/MUX/power integration problems while there was still time for a second spin.

| V1 Decision | Justification |
| --- | --- |
| Fabricate early, pre-final | Stable platform for parallel firmware development; find integration faults while a respin is still possible |
| Condition both ranges to a mid-rail-centred span | Keeps op-amp outputs in their linear region |
| UART debug header | Debug sensor firmware without depending on the optical link |
| Trimmers in the TOSLINK circuit | Tune receive sensitivity and transmit intensity on the bench |
| Single serial LED driver for all alarms | Saves 12+ GPIOs, firmware complexity, cost and assembly time |
| ADC internal mux as range select | Digitisation and range switching in one part |
| Separate 5V reference and 5V rail | Current source accuracy decoupled from rail loading |

V1 proved the concept where it mattered: the digital domain was fully functional — CH5-8 read accurately, the alarm indicators drove correctly, and the TOSLINK transceiver communicated. But the ±12V analog rails failed with a persistent short that would not hold voltage even bench-supplied with the regulator circuitry desoldered. Rather than continue debugging a flawed board, the time-risk favoured a redesign that attacked the suspected weaknesses directly:

| V2 Decision | Justification |
| --- | --- |
| MC34063AP switching regulators for ±12V | Immediately available; breadboarded and verified before layout this time |
| Conditioning remapped to 0-3.3V; ADS1119 | ADC references directly off the rails — precision reference IC and 2.5V rail deleted, conversion firmware simplified. Reliability and ease of integration prioritised over the earlier, more complex approach |
| Power rail shielding | Keep switching noise off the analog chain |
| Jumper headers isolating rails and subsystems | The V1 lesson: every subsystem can be powered, probed and tested independently |
| Smaller board outline (within 100mm) | ~$10 cheaper — drops a PCB price tier and buys BOM headroom |
| Silkscreen, fiducials and test point overhaul | Drafting-standard (TP-STD) compliance |

{% include image-gallery.html images="AltiumRender.png" height="550" %}
<span style="font-size: 14px">Figure 3: V2 Altium render. Input terminal blocks and current source outputs on the left edge, labelled alarm LED banks per channel on the right, ±12V switching supplies bottom, TOSLINK socket and receive tuning top.</span>

{% include image-gallery.html images="CopperArt.png" height="500" %}
<span style="font-size: 14px">Figure 4: V2 copper artwork. Analog signal chain kept clear of the switching supplies; power, communication and signal nets labelled on silkscreen.</span>

The V2 board was fully functional: all eight channels, alarm indication, and TOSLINK communication with the control unit.

<!-- TODO photo pending — uncomment and renumber figures when added:
{% include image-gallery.html images="sensor_board_constructed.jpg" height="550" %}
<span style="font-size: 14px">Figure X: Constructed and tested V2 sensor board.</span> -->

## BOM Engineering

At the three-quarter review the estimated product BOM stood at $127.23 against the $125 cap, with the sensor board carrying $98.52 of it. The overage was closed by attacking the largest line items with footprint-compatible substitutions and a board resize:

| Line item | Original | Substituted | Saving |
| --- | --- | --- | --- |
| Input buffer quad op-amp | ADA4177-4 — $10.08 | OPA4192 — $6.33 | $3.75 |
| Channel MUX | ADG1404 — $8.82 | TMUX6104 — $5.44 | $3.38 |
| Alarm LEDs (×16) | SM0805HC — $7.88 | LTST-C150KRKT — $2.00 | $5.88 |
| Dual precision op-amp | OPA192 — $5.80 | OPA2197 — $3.70 | $2.10 |
| Sensor PCB | 96.9 × 104.8mm — $11.52 | ≤100mm outline — $2.86 | $8.66 |

The ADA4177's integrated overvoltage protection was redundant alongside the TVS clamps and series resistance already at the terminals, which made it the easiest cut. The final compiled BOM closed under the $125 cap.

## Shortcomings and Future Work

* **Pin and timer exhaustion.** The 48-pin package left zero spare GPIO and forced the 12-bit timer fallback. A 64-pin variant costs marginally more and would buy debug headroom, spare timers, and room for features like per-channel sampling LEDs.
* **Rail-referenced ADC.** Referencing the ADS1119 to the 3.3V regulator ties absolute accuracy to rail quality. It sits comfortably inside the ±2.5% full-scale budget here, but any tighter-spec revision should reinstate a dedicated precision reference.
* **Debuggability must be designed in from V1.** The analog rail fault could only be chased by desoldering. The isolation jumpers added in V2 should have been on the first spin — breadboard success does not guarantee PCB success.
* **Switching converters beside a 16-bit front end.** V2 relied on shielding and layout separation; a quieter revision would post-regulate the analog rails and split the ground pours.
* **Supply chain.** Several parts (the MC34063AP among them) were selected for same-day availability — correct for a prototype, a liability at volume. A production revision would qualify pin-compatible second sources for every critical IC, prefer long-lifecycle parts, and move to SMT-first assembly with through-hole reserved for connectors and mechanically loaded components.

## Design Artifacts

* [Sensor board schematic set (PDF)](../../SENSOR_BOARD_SCHEMATICS_EX_COPPER.pdf) — hierarchical, one sheet per subsystem (conditioning, ADC, TOSLINK, current sources, alarm control, power, mechanicals)
* [Control board schematic set (PDF)](CONTROL_BOARD_EX_COPPER.pdf)

Both schematic sets were brought to TP-STD drafting compliance as part of the final documentation pass, alongside the compiled BOM.
