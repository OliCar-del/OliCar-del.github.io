---
layout: post
title: tpmania - Miniaturised music based rhythm and dance game
description: An embedded systems project to design and build a miniaturised arcade rhythm and dance game played with fingers, based on STM32 architecture. The project involved multi-stage PCB prototyping, power management, audio generation, and modular firmware development.
skills:
  - PCB Design & Routing
  - Embedded C Programming
  - STM32 Microcontroller Architecture
  - Power Pathing & Battery Management
  - Audio Generation (I2S/SAI)
  - Hardware Debugging & Validation
  - State Machine (FSM) Implementation

main-image: /mainpicture_final.png
---

---
# tpmania - Miniaturised Music Based Rhythm Game

## Project Overview & Scope

***tap-mania*** is a miniaturised arcade rhythm and dance game played with the fingers, drawing heavy inspiration from full-sized arcade cabinets like *Dance Dance Revolution* and *StepmaniaX*. The core objective is for players to follow rhythm cues displayed on a screen by hitting the correct arcade pushbuttons. The cues are perfectly synchronised to music, and the player's timing accuracy determines their score.

The scope of this project required building a fully functional embedded system from the ground up, compliant with strict technical standards. This involved designing a custom Printed Circuit Board (PCB), managing complex power constraints (3.7V LiPo battery, USB charging, 5V/3.3V rails), generating high-fidelity audio, parsing sequence files from a microSD card, outputting gameplay data to a 1.3" OLED screen, and driving an LED matrix alongside individual arcade button LEDs while monitoring for millisecond precise presses.

## Hardware Architecture & Component Selection

Developing a robust hardware baseline was crucial for the seamless integration of all sub-systems. I chose the **STM32L433CCT6** microcontroller as the system's brain due to its expansive peripheral support, including a Serial Audio Interface (SAI) for audio control, I2C for the OLED, SPI for the microSD card, and hardware timers/PWM for LED matrix control.

| Subsystem | Selected Component | Justification |
| --- | --- | --- |
| **Microcontroller** | STM32L433CCT6 | Familiar architecture, highly capable peripheral set, and sufficient GPIOs for complex I/O mapping and interrupt scheduling. |
| **Audio Generation** | MAX98357A (DAC + Amp) | Fully integrated DAC (up to 32-bit) and amplifier. Greatly reduces hardware complexity by eliminating output filters. |
| **Power Pathing & Charging** | MP2637GR-Z | Handles battery charging and boosts the 3.7V LiPo to a robust 5V output (at 2.2A), exceeding specification requirements. |
| **Logic Power (3.3V Rail)** | AP2112K-3.3 (LDO) | Provides a clean, low-noise 3.3V supply stepped down from the 5V boost, crucial for the MCU and audio DAC. |

> The "boost-then-LDO" topology was a simple, cost-effective design choice that provided a highly reliable, low-noise 3.3V supply for critical logic components while simultaneously satisfying the 5V requirement for the LED matrix.

## Iterative Prototyping Stages

Given the strict design guidelines and dense integration requirements, the hardware was developed iteratively across four distinct PCB versions, moving from initial concept verification to a fully polished product.

1. **PCB Version 1 (PCBv1):** Expedited and completed by Week 4. The focus was validating power pathing and battery charging via the MP2637 TQFN package. It integrated the audio IC, 3.3V LDO, SD card socket, and low-pass filters (-3dB @ ~340Hz) for user interface hardware debouncing. Extensive debug pins and solder bridges were included for isolated testing.
2. **PCB Version 2 (PCBv2):** Introduced a direct USB-C connector with a TPD8S300 protection IC (for ESD/overvoltage protection) and terminal lugs for direct arcade button interfacing. A backup SEEEDUINO socket was added for redundancy.
3. **PCB Version 3 (PCBv3):** Major compliance and functional overhauls. Audio pins were re-routed to SAI1 (LCLOCK, BCLOCK) for proper I2S function. Arcade button LEDs were shifted to the 5V rail and controlled via BSS138 N-Channel MOSFETs to comply with standards. Spade terminals were replaced with keyed JST-PH 2.0mm connectors.
4. **PCB Version 4 (PCBv4 - Final):** Focused on final polish, mounting clearance, and standard compliance. Added a 5V rail power indicator LED, nylon spacers for OLED clearance, solder bridges to isolate the 5V system rail for safer fault finding, and a unified ground plane strategy for the arcade switches.

### Embedded Images

{% include image-gallery.html images="project2.jpg" height="400" %}
PCB Routing and copper plane design from the prototype iterations.

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

## Challenges & Team Dynamics

A major operational challenge during this project was a severe imbalance in team workload. Joining the group at the end of Week 4 meant I was significantly behind the initial planning curve. Due to a mix of member unavailability, illness, and a lack of experience among peers, the intended division of labor dissolved.

To ensure the project's success, I took on the vast majority of technical responsibilities. I was solely responsible for designing all four iterations of the PCB, implementing the power management/hot-swapping systems, selecting the components, wiring the harnesses, writing the core state machine, interfacing the SD card, parsing sequence data, and managing the integration between the GUI and the device. This experience underscored the importance of *defensive engineering*—using solder bridges, isolation headers, and verbose UART debug logging—to guarantee that if one sub-system failed, it wouldn't stall the development of the rest of the board.

---

## Sustainability & Future Recommendations

While the device operates flawlessly as a prototype, evaluating the design through a commercial sustainability lens highlights areas for potential iteration:

* **Energy Efficiency vs. Complexity:** The current "boost-then-LDO" topology is excellent for mitigating noise on the 3.3V rail, but introduces slight thermal and energy inefficiencies.
* **Supply Chain Stability:** The project relies heavily on highly integrated, single-source ICs (like the MP2637 for power pathing and the MAX98357A for audio). From a commercial manufacturing perspective, this poses a massive supply chain risk.

**Recommendation:** For a production-ready model, the power and audio sub-systems should be redesigned utilizing discrete, multi-source components. Replacing the integrated MP2637 with a dedicated battery charging IC, a separate boost converter, and diode-based power pathing would increase the BOM component count, but dramatically improve long-term business sustainability, part substitution flexibility, and end-user repairability.

{% include youtube-video.html id="tGCdLEQzde0" autoplay = "false" width= "900px" %}