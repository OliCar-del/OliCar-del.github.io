---
layout: post
title: Uninterruptible 3.3V Power Management & Charging PCB
description: A miniaturised, highly robust power supply board featuring USB-C input, single-cell LiPo charging, and seamless power-path hot-swapping to a regulated 3.3V logic supply.
skills:
 - PCB Design & Routing (Altium)
 - Power Path Management (Hot-Swapping)
 - Circuit Simulation (LTspice)
 - Schematic Capture & BOM Management

main-image: /constructed.jpeg
---

# Uninterruptible 3.3V Power Management PCB

## Project Overview

This project outlines the design and verification of a dedicated power management sub-system. The core objective was to design a highly reliable circuit capable of arbitrating between a 5V USB-C power source and a 3.7V single-cell LiPo battery, stepping the active source down to a clean, continuous 3.3V output. Crucially, the system required "hot-swapping" capabilities-allowing the user to plug or unplug the USB-C cable without browning out the downstream 3.3V logic.

## Hardware Architecture & Component Selection

The architecture was engineered for simplicity and component availability, relying on standard discrete components for power switching rather than highly integrated, single-source PMICs.

| Subsystem | Selected Component | Justification |
| --- | --- | --- |
| **USB-C Input** | Molex 217179-0001 | 16-pin USB-C receptacle configured with dual 5.1kΩ pull-down resistors (CC1/CC2) to properly request 5V from modern PD chargers. |
| **Battery Charging** | MCP73831T-2ACI/OT | Industry-standard, low-cost linear charge management controller offering a simple footprint and programmable charge current. |
| **Power Path Switching** | NDT2955 (P-Channel) | Acts as the primary switch isolating the battery when USB voltage is present, preventing back-feeding while offering very low $R_{DS(on)}$. |
| **Voltage Regulation** | AP2112K-3.3TRG1 | A high-speed, low-dropout (LDO) regulator providing a clean 600mA 3.3V supply, ideal for noise-sensitive microcontrollers. |

{% include image-gallery.html images="Schematic.png" height="600" %}
Overall Schematic: Detailing the USB-C configuration, MCP73831 battery charger, load-sharing power path, and LDO isolation circuits.

{% include image-gallery.html images="bom.png" height="400" %}
Bill of Materials (BOM) excerpt highlighting the critical power management components.

## Hot-Swap Power Path Design & Simulation

To ensure the 3.3V rail would not drop during power hand-offs, the load-sharing circuit was simulated in LTspice prior to layout.

The circuit utilizes a P-Channel MOSFET and a Schottky diode. When USB 5V is present, the diode conducts power to the LDO, while the MOSFET gate is pulled high, isolating the LiPo battery. The MCP73831 is then free to charge the battery independently. When USB power is removed, the gate is pulled low, swiftly turning on the MOSFET and allowing the battery to take over the load instantaneously.

{% include image-gallery.html images="hotswap.png" height="500" %}
LTspice transient analysis circuit verifying the hand-off timing and voltage stability between the USB and Battery sources.

## Bring-up Process

Breadboard was followed by PCB design and layout then manufacture. Abundant testpoints and bridges were included for ease of testing and troubleshooting.

{% include image-gallery.html images="copper_art.png" height="500" %}
<span style="font-size: 14px">2-Layer PCB Copper Artwork</span> 


{% include image-gallery.html images="render.png" height="600" %}
<span style="font-size: 14px">Final 3D Render of the populated board, demonstrating the physical layout, robust USB-C mounting, and strategically placed test points.</span> 

{% include image-gallery.html images="constructed.jpeg" height="600" %}
<span style="font-size: 14px">Constructed and tested final PCB. Some testpoints unpopulated. Easy access to different nets and molex terminals for off-board connections.</span> 


## Necessary improvements
 - Ground planes on both layers
 - Thicker traces for power (not an issue at 2A but wouldn't hurt)
 - Too many testpoints constructed, could have left as probe-able vias.
 - Silkscreen alignment and orientation
 - More indicator LEDs