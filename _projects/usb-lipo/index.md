---
layout: post
title: Uninterruptible 3.3V Supply - USB-C/LiPo Power Management and Charging
description: A miniaturised, highly robust power supply board featuring USB-C input, single-cell LiPo charging, and seamless power-path hot-swapping to a regulated 3.3V logic supply.
skills:

 - PCB Design & Routing (Altium)
 - Power Path Management (Hot-Swapping)
 - Circuit Simulation (LTspice)
 - Schematic Capture & BOM Management

tags: [Power path, USB-C, PCB (Altium), LTspice]   # short labels on the project card
areas: [power, pcb]   # filter buttons: power, pcb, embedded, control, rf, software
order: 6   # position on the site, lowest first
image: /projects/usb-lipo/constructed.jpeg
thumb: /projects/usb-lipo/thumb.webp
permalink: /projects/usb-lipo/
redirect_from:   # older addresses for this page, kept working
  - /projects/05_usb-lipo/
  - /projects/05_usb-lipo/index/
  - /_projects/05_usb-lipo/
---
## Project Overview

A dedicated power-management sub-system: arbitrate between a 5V USB-C source and a 3.7V single-cell LiPo battery, and step whichever is active down to a clean, continuous 3.3V output. The defining requirement was hot-swapping - plugging or unplugging the USB-C cable must not brown out the downstream 3.3V logic.

## Hardware Architecture & Component Selection

The architecture was engineered for simplicity and component availability, relying on standard discrete components for power switching rather than highly integrated, single-source PMICs.

| Subsystem | Selected Component | Justification |
| --- | --- | --- |
| **USB-C Input** | Molex 217179-0001 | 16-pin USB-C receptacle configured with dual 5.1kΩ pull-down resistors (CC1/CC2) to properly request 5V from modern PD chargers. |
| **Battery Charging** | MCP73831T-2ACI/OT | Industry-standard, low-cost linear charge management controller offering a simple footprint and programmable charge current. |
| **Power Path Switching** | NDT2955 (P-Channel) | Acts as the primary switch isolating the battery when USB voltage is present, preventing back-feeding while offering very low $R_{DS(on)}$. |
| **Voltage Regulation** | AP2112K-3.3TRG1 | A high-speed, low-dropout (LDO) regulator providing a clean 600mA 3.3V supply, ideal for noise-sensitive microcontrollers. |

{% include image-gallery.html images="Schematic.png" height="600" caption="Figure 1: Overall Schematic: Detailing the USB-C configuration, MCP73831 battery charger, load-sharing power path, and LDO isolation circuits." %}


{% include image-gallery.html images="bom.png" height="400" caption="Figure 2: Bill of Materials (BOM) excerpt highlighting the critical power management components." %}


## Hot-Swap Power Path Design & Simulation

To ensure the 3.3V rail would not drop during power hand-offs, the load-sharing circuit was simulated in LTspice prior to layout.

The circuit utilizes a P-Channel MOSFET and a Schottky diode. When USB 5V is present, the diode conducts power to the LDO, while the MOSFET gate is pulled high, isolating the LiPo battery. The MCP73831 is then free to charge the battery independently. When USB power is removed, the gate is pulled low, swiftly turning on the MOSFET and allowing the battery to take over the load instantaneously.

{% include image-gallery.html images="hotswap.png" height="500" caption="Figure 3: LTspice transient analysis circuit verifying the hand-off timing and voltage stability between the USB and Battery sources." %}


## Bring-up Process

The circuit was breadboarded and simulated before layout, then manufactured and brought up stage by stage. Abundant test points and solder bridges meant every net could be probed and each stage isolated while fault-finding.

{% include image-gallery.html images="copper_art.png" height="500" caption="Figure 4: 2-Layer PCB Copper Artwork" %}


{% include image-gallery.html images="render.png" height="600" caption="Figure 5: Final 3D Render of the populated board, demonstrating the physical layout, robust USB-C mounting, and strategically placed test points." %}


{% include image-gallery.html images="constructed.jpeg" height="600" caption="Figure 6: Constructed and tested final PCB. Some testpoints unpopulated. Easy access to different nets and molex terminals for off-board connections." %}


## Necessary improvements

* Ground planes on both layers
* Thicker traces for power (not an issue at 2A but wouldn't hurt)
* Too many testpoints constructed, could have left as probeable vias.
* Silkscreen alignment and orientation
* More indicator LEDs