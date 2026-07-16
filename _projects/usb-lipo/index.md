---
layout: post
title: Uninterruptible 3.3V Power Management & Charging PCB
description: A miniaturised, highly robust power supply board featuring USB-C input, single-cell LiPo charging, and seamless power-path hot-swapping to a regulated 3.3V logic supply.
skills:
 - PCB Design & Routing
 - Power Path Management (Hot-Swapping)
 - Circuit Simulation (LTspice)
 - Schematic Capture & BOM Management

main-image: /render.png
---

# Uninterruptible 3.3V Power Management PCB

## Project Overview

This project outlines the design and verification of a dedicated power management sub-system. The core objective was to design a highly reliable circuit capable of arbitrating between a 5V USB-C power source and a 3.7V single-cell LiPo battery, stepping the active source down to a clean, continuous 3.3V output. Crucially, the system required "hot-swapping" capabilities—allowing the user to plug or unplug the USB-C cable without browning out the downstream 3.3V logic.

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

## Board Layout & Routing

The layout prioritized thick power traces and substantial copper pours to handle necessary current and aid in thermal dissipation from the LDO and Charging IC. A unified ground plane ensures a low-impedance return path for the entire board.

{% include image-gallery.html images="copper_art.png" height="500" %}
PCB Copper Artwork: Highlighting the high-current 5V (yellow) and 3.3V (blue) routing, with a continuous ground plane for thermal relief.

{% include image-gallery.html images="render.png" height="600" %}
Final 3D Render of the populated board, demonstrating the physical layout, robust USB-C mounting, and strategically placed test points.