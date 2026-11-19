---
layout: post
title: Charger Puck - 135W 10 Port USB-C/USB-A Fast-Charging Panel from a Car Battery
description: A compact, independently switchable, ten-port USB charging panel for a car, supplied from a fused auxiliary nominal-12 V LiFePO4 battery charged by a DC–DC charger and/or solar. The panel serves phones, portable power banks, watches, lights and other small USB devices. Small form factor and dense board, with added benefit of local/remote switching for controlling lighting/charging.
skills:
  - PCB Design & Routing
  - ESP32 programming
  - Bluetooth & Wi-Fi connectivity
  - Power Pathing & Battery Management
  - Switchmode power supplies
  - Hardware Debugging & Validation
  - IO extenders and repeatable layouts
  - High Density Manufacturing

tags: [PCB (KiCad 10.0), ESP32, Battery power, Power Design, Manufacturing]   # short labels on the project card
areas: [pcb, embedded, power]   # filter buttons: power, pcb, embedded, control, rf, software
order: 5   # position on the site, lowest first
image: /projects/ChargerPuck/charger_puck_fabircated+top.png
thumb: /projects/ChargerPuck/charger_puck_fabircated+top.png
permalink: /projects/ChargerPuck/
redirect_from:   # older addresses for this page, kept working
  # - /projects/01_tap-mania/
  # - /projects/01_tap-mania/index/
  # - /_projects/01_tap-mania/
---

## Project Overview & Scope

***ChargerPuck*** is a cost optimised, 100mm<sup>2</sup> charging panel design to fast-charge up to 10 USB-C/A devices, running from an auxillary car LiFePO4 battery (nominal 12.8V). The design features five 5V/3A USB-C ports and five 5V/2.4A USB-A ports, independetly locally/remotely switchable via ESP32. Each port is powered by its own buck converter.

{% include img.html src="bed-finished.jpg" cap="Bed platform for installation" align="right" %}The device is intended for installation in the vehicle cabin of a Defender 110 station wagon (see [the rebuild](https://olicar-del.github.io/projects/defender-rebuild/)) so that devices can be charged while camping/on the road. As space is at a premium in the cabin, and fabrication is far cheaper for 100mm<sup>2</sup> boards, the panel is kept small. Additionally, the panel does double duty working as a 'light switch' panel, given the availability of cheap USB-A/C supplied lighting. Cabin/exterior lights can be switched off at the panel or via ESP32 WiFi app provided by contorl of port outputs via ESP32. 

The panel was designed such that the entire board could be fabricated in one-shot - thus there are many testpoints, isolation links, staged bringup and rail checks. The board was therefore designed to be as robust as possible - where excess could be applied it was. While the board is not a production level board, it tested my assembly and construction abilities due to the sheer number of parts and connections and opportunity for things to go wrong. This was intended to be both the prototype and final model so every effort was made to enable debugging and fixes on the prototype. A polished version is doable but not worth the extra cost.

Each port can draw up to 3A and monitors for:
 - Over temperature (71<sup>o</sup>C)
 - VBUS over-voltage or over-current
 - D+/D- or CC over-voltage
 - VCONN over-current (for USB-C)
 - USB-C attachment/sink
 - Port Enable/Disable via UI/ESP32

 Designing for a vehicle installation had its own considerations. I determined appropriate wire to board choices - opting for large, spring terminals for vibration (WAGO 2-pin spring terminal), as well as thermal considerations. The board has fan control and thermal lockout due to the excessive ambient temperatures in a 'black greenhouse' (my car).

***Charger Puck*** is my first 6 layer board designed in KiCad, with high density routing to accomodate 54 IO ports on the maximum allowable 102mm x 102mm PCB before size-pricing is applied. Having 10 switching supplies (1 for each port) necessitated bottom side assembly with groundplanes and power/signal planes in between. The 150W maximum power also requires heat management and sensing, as well as safety cutouts and throttling. Assembling the PCB made use of recently constructed ToastControl PID controller on toaster oven to reflow the board correctly due to use of VQFN chips and ~600 components. 
{% include image-gallery.html images="c5_a1_routing.png" height="600" caption="Routing gets tricky in the corners balancing 32 pins/port, USB DP/DM differential signals, switching pours and EMI, Kelvin sense traces and signalling." %}

## Hardware Architecture & Component Selection
The **STM32L433CCT6** anchors the design, chosen for a peripheral set that covers every subsystem without glue logic: a Serial Audio Interface (SAI) for audio, I2C for the OLED, SPI for the microSD card, and hardware timers/PWM for LED matrix control.

| Subsystem | Selected Component | Justification |
| --- | --- | --- |
| **Microcontroller** | STM32L433CCT6 | Familiar architecture, highly capable peripheral set, and sufficient GPIOs for complex I/O mapping and interrupt scheduling. |
| **Audio Generation** | MAX98357A (DAC + Amp) | Fully integrated DAC (up to 32-bit) and amplifier. Greatly reduces hardware complexity by eliminating output filters. |
| **Power Pathing & Charging** | MP2637GR-Z | Handles battery charging and boosts the 3.7V LiPo to a robust 5V output at 2.2A - comfortable headroom over the LED matrix and audio peak load. |
| **Logic Power (3.3V Rail)** | AP2112K-3.3 (LDO) | Provides a clean, low-noise 3.3V supply stepped down from the 5V boost, crucial for the MCU and audio DAC. |

> The "boost-then-LDO" topology was a simple, cost-effective design choice that provided a highly reliable, low-noise 3.3V supply for critical logic components while simultaneously satisfying the 5V requirement for the LED matrix.

## Iterative Prototyping Stages

The hardware was developed across four PCB versions, each spin fixing what testing of the previous one exposed - from initial concept verification to the final product.

---

**PCB Version 1 (PCBv1):** The focus was validating power pathing and battery charging via the MP2637 TQFN package. It integrated the audio IC, 3.3V LDO, SD card socket, and low-pass filters (-3dB @ ~340Hz) for user interface hardware debouncing. Extensive debug pins and solder bridges were included for isolated testing.
{% include image-gallery.html images="PCBV1_render.webp" height="600" caption="PCBv1 Altium render" %}
{% include image-gallery.html images="PCBV1_copper.webp" height="600" caption="PCBv1 Altium copper artwork" %}
{% include image-gallery.html images="PCBV1_built.jpg" height="600" caption="PCBv1 fully constructed, tested and functional prototype" %}
**PCB Version 2 (PCBv2):** Introduced a direct USB-C connector with a TPD8S300 protection IC (for ESD/overvoltage protection) and terminal lugs for direct arcade button interfacing. A backup SEEEDUINO socket was added for redundancy.
{% include image-gallery.html images="PCBV2_render.webp" height="600" caption="PCBv2 Altium render" %}
{% include image-gallery.html images="PCBV2_copper.webp" height="600" caption="PCBv2 Altium copper artwork" %}
{% include image-gallery.html images="PCBV2_builtrotated.jpg" height="600" caption="PCBv2 fully constructed, tested and functional prototype. Board has distinct areas noted on the silk screen. Bottom edge (L->R) has SD card socket, UI buttons connections, Arcade button connections. Top edge (L->R) has Programming header + MCU, USB input and protection, Audio chip+jack footprint and battery charger+boost supply." %}
{% include image-gallery.html images="PCBV2_test.webp" height="600" caption="PCBv2 being tested for functionality" %}
{% include image-gallery.html images="PCBV2_batt.webp" height="600" caption="PCBv2 running off battery power" %}

---

**PCB Version 3 (PCBv3):** Major functional and robustness overhauls. Audio pins were re-routed to SAI1 (LCLOCK, BCLOCK) for proper I2S function. Arcade button LEDs were shifted to the 5V rail and switched via BSS138 N-channel MOSFETs, so the 3.3V GPIOs never source LED current directly. Spade terminals were replaced with keyed JST-PH 2.0mm connectors to make mis-wiring physically impossible.
{% include image-gallery.html images="PCBV3_render.png" height="600" caption="PCBv3 Altium render showing removal of USB input/protection and inclusion of keyed connectors" %}
{% include image-gallery.html images="PCBV3_copper.webp" height="600" caption="PCBv3 Altium copper artwork showing longer USB UART Connections and revised battery charging wiring. 3.3V rail is in aqua, 5V input is in pale yellow, Arcade button signals/power in bright yellow." %}
{% include image-gallery.html images="PCBV3_built.jpg" height="600" caption="PCBv3 fully constructed, tested and functional prototype. Full functionality was achieved at this point; the remaining work was robustness rather than features." %}
{% include image-gallery.html images="PCBV3_test.webp" height="600" caption="PCBv3 showing informative debug output via USART to PC, while playing the game on LED matrix." %}

---

**PCB Version 4 (PCBv4 - Final):** Focused on final polish, mounting clearance and robustness. Added a 5V rail power indicator LED, nylon spacers for OLED clearance, solder bridges to isolate the 5V system rail for safer fault finding, and a unified ground plane strategy for the arcade switches.
{% include image-gallery.html images="PCBV4_render.webp" height="600" caption="PCBv4 Altium render showing the final layout" %}
{% include image-gallery.html images="PCBV4_copper.webp" height="600" caption="PCBv4 Altium copper artwork showing minor changes to V3. Some trace widening and minor debug and ESD inclusions." %}
{% include image-gallery.html images="PCBV4_test.jpg" height="600" caption="PCBv4 fully constructed showing routing of wiring harness into playcase and abundance of keyed connections and mounting hardware." %}
{% include image-gallery.html images="PCBV4_play.jpg" height="600" caption="PCBv4 in situ, mounted to acrylic playcase with LED matrix and OLED displaying game information. Game currently being played." %}

---

## Software & Firmware Implementation

The firmware needed to be highly responsive to maintain perfect synchronization between the audio, the LED matrix cues, and user inputs.

* **Beat Synchronization:** A beat metronome timer generated hardware interrupts every beat period. **TIM6** was utilized as a 16-bit beat interval timer interrupt. This governed the scheduling of arcade button handling and LED lighting on the exact beat.
* **Modular Architecture:** As functionality expanded, the monolithic `main.c` (which swelled to ~3000 lines) was heavily refactored. I broke the code out into over 20 modular `.c` and `.h` files utilizing a Finite State Machine (FSM) architecture. This vastly improved readability, encapsulation, and long-term scalability.
* **Dynamic Configuration:** A dedicated system state was implemented for configuring gameplay timing windows via a PC GUI. The device enters `SYSTEM_STATE_CONFIGURATION`, validates the address, and listens over UART (e.g., `SETWIN:P,G,O,Po`) to write new configuration windows directly into non-volatile memory, displaying successful saves on the OLED.

```c
// Pseudo-code representation of the beat interrupt and FSM structure
void TIM6_DAC_IRQHandler(void) {
  if (LL_TIM_IsActiveFlag_UPDATE(TIM6)) {
    LL_TIM_ClearFlag_UPDATE(TIM6);
    
    // Precise timestamping and beat handling
    system_flags.beat_interrupt_triggered = 1;
    
    // Evaluate matrix cues and schedule arcade LEDs
    Update_Arcade_LED_Schedules();
  }
}

void Process_System_State() {
  switch(current_state) {
    case SYSTEM_STATE_PLAYING:
      Process_Gameplay();
      break;
    case SYSTEM_STATE_CONFIGURATION:
      // Wait for UART transmission from the GUI to configure window constraints
      Config_WaitForInput(); 
      break;
    case SYSTEM_STATE_REPORTING:
      Output_Score_To_OLED();
      break;
  }
}

```

## Defensive Engineering

The build was structured so that no single subsystem failure could stall the rest. Every board revision carried solder bridges and isolation headers, so each rail and IC could be powered, probed and tested independently, and verbose UART debug logging ran on every prototype — which is what made faults like the audio pins that had to move to SAI1 cheap to find and fix in the next spin.

The scope spanned the full stack: all four PCB iterations, the power management and charging path, component selection, wiring harnesses, the core state machine, SD card interfacing and sequence parsing, and the integration between the device and the PC GUI (GUI by collaborator Nanfeng Ding).

---

## Sustainability & Future Recommendations

While the device operates flawlessly as a prototype, evaluating the design through a commercial sustainability lens highlights areas for potential iteration:

* **Energy Efficiency vs. Complexity:** The current "boost-then-LDO" topology is excellent for mitigating noise on the 3.3V rail, but introduces slight thermal and energy inefficiencies.
* **Supply Chain Stability:** The project relies heavily on highly integrated, single-source ICs (like the MP2637 for power pathing and the MAX98357A for audio). From a commercial manufacturing perspective, this poses a massive supply chain risk.

**Recommendation:** For a production-ready model, the power and audio sub-systems should be redesigned utilizing discrete, multi-source components. Replacing the integrated MP2637 with a dedicated battery charging IC, a separate boost converter, and diode-based power pathing would increase the BOM component count, but dramatically improve long-term business sustainability, part substitution flexibility, and end-user repairability.

> Project files including code for the embedded device, Altium Designer files, Gerber files, schematics, other design artifacts, BOM, GUI code (written by collaborator Nanfeng Ding) and more can be found on my [GitHub](https://github.com/OliCar-del/tap-mania).