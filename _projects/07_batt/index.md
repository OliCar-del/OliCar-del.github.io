---
layout: post
title: 314Ah Auxiliary Vehicle Battery
description: Large capacity 4S EVE MB31 314Ah LiFePO4 construction battery with protection, 200A JK BMS and case construction/compression for automotive and off-grid camping applications. Acts as the foundation for a future custom MPPT solar controller and integration with a 200W solar panel.
skills:
  - Battery Pack Assembly & Compression
  - Power Distribution & Fusing
  - BMS Integration (JK Active Balancing)
  - Automotive 12V Systems
main-image: /batt.png
image: /_projects/07_batt/batt.png
---
# 12V 314Ah Automotive LiFePO4 Auxiliary System

## Project Overview & Scope

Modern vehicle-based travel and off-grid camping require significant, reliable power to run 12V compressor fridges, cabin fans, lighting, and device chargers continuously. The objective of this project was to design and construct a high-capacity, heavy-duty 12V auxiliary battery system capable of sustaining these loads for extended periods without relying on the vehicle's alternator.

To achieve this, I engineered a 4S (4-series) Lithium Iron Phosphate (LiFePO4) battery pack using automotive-grade 314Ah cells. The project scope required careful consideration of mechanical compression, extreme vibration tolerance for off-road use, and robust safety mechanisms capable of managing the massive short-circuit potential of high-capacity lithium cells. This system serves as Phase 1 of a larger power-management project, laying the groundwork for a custom-built MPPT solar charge controller and solid-state load switching board.

## System Specifications

| Parameter | Specification | Note |
| --- | --- | --- |
| **Cell Chemistry & Configuration** | LiFePO4 (LFP) - 4S1P | EVE MB31 Automotive Grade Cells. |
| **Nominal System Voltage** | 12.8V | Operating range: 10.0V (cutoff) to 14.6V (max charge). |
| **Total Capacity** | 314Ah (Approx. 4000Wh) | Provides multiple days of autonomy for a 12V fridge and accessories. |
| **Battery Management** | 200A JK BMS | Includes active balancing and Bluetooth telemetry. |
| **Interconnects** | Flexible copper busbars | Absorb cell movement without transferring stress to the terminals during vehicle vibration. |

> The decision to use flexible copper busbars rather than rigid solid ones was a deliberate mechanical design choice. In an automotive environment, chassis flex and continuous vibration can cause a rigid busbar to apply lateral shear force to the internal cell terminals, leading to premature cell failure or micro-cracking. The flexible links absorb that movement, and each busbar is insulated with Kapton tape over the exposed copper.

## Hardware Construction & Mechanical Design

Raw-cell pack longevity is set by mechanics as much as electronics: EVE specifies consistent, even compression to prevent swelling (delamination of the internal electrodes), and the build was designed around that constraint.

* **Mechanical Compression:** The EVE MB31 cells require consistent, even pressure across their faces to maintain their rated lifespan. The rig clamps the four cells between 3/4" plywood end plates banded with steel tension straps. Plywood was chosen over solid timber because its cross-laminated plies are dimensionally stable and cannot split along a grain line under sustained clamping load, and the straps spread that load across the whole plate face rather than concentrating it at corner fixings.
* **Vibration Resistance:** The strap-and-plate arrangement suits a vehicle: with no threaded fasteners in the compression path there is nothing to back off under the constant high-frequency vibration of driving — the crimped strap ends permanently lock in the preload.

{% include image-gallery.html images="testfit.png" height="600" %}
<span style="font-size: 14px">Cell test-fit under compression: four MB31 cells between 3/4" plywood end plates, banded with crimped tension straps. The FR4 sheet under the straps isolates the cell cases on the outer face.</span>

## Safety Integrations & Electrical Protection

Over 4kWh of stored energy behind very low internal resistance drove several non-negotiable safety inclusions:

1. **Cell Case Isolation:** The aluminium bodies of LFP cells are electrically conductive, separated only by a thin blue PVC heat shrink. Because the compression rig forces these cells together, any friction from vehicle movement could wear through the plastic, causing a catastrophic dead short. To prevent this, 1mm FR4/G10 epoxy fiberglass sheets were installed between each cell.
2. **Catastrophic Fusing:** A Class T fuse (or high-interrupt ANL fuse) was installed immediately at the main positive terminal. Standard automotive fuses cannot safely interrupt the thousands of amps these cells can deliver in a short circuit; the arc would simply jump the gap.
3. **Thermal Management:** The JK BMS temperature probes were affixed directly to the cell bodies. The BMS was programmed to enforce a strict low-temperature charging cutoff (0°C). Charging LFP cells below freezing causes permanent lithium plating and immediate cell degradation.

{% include image-gallery.html images="batt.png" height="600" %}
<span style="font-size: 14px">Assembled pack: Kapton-insulated flexible copper busbars linking the cells, balance leads routed for the JK BMS, and the main positive terminal under its red protective cover.</span>

## Phase 2: Future Expansion (Custom MPPT & Load Distribution)

With the energy storage foundation complete, Phase 2 involves designing a custom Maximum Power Point Tracking (MPPT) solar charge controller and a load-distribution header board using KiCad. 

* **MPPT Solar Controller:** The system will be fed by a 200W, 12V nominal solar panel. While it is "12V nominal", its actual Open Circuit Voltage (Voc) is approximately 44V, with a Voltage at Maximum Power (Vmp) of ~36V. The PCB will utilize a synchronous buck converter topology to efficiently step the 36V+ input down to the precise 14.4V bulk/absorption voltage required by the LFP pack. 
* **Load Switching Header:** To eliminate standard relays and bulky fuse blocks, the design will incorporate high-side smart FETs (e.g., Infineon PROFETs). This will allow for solid-state, microcontroller-driven load switching of the fridge, lighting, and fans, complete with programmable current-limiting and short-circuit protection on every channel.

<!-- TODO image pending — uncomment when the MPPT concept schematic is exported:
{% include image-gallery.html images="mppt_schematic_draft.png" height="600" %}
<span style="font-size: 14px">Early concept schematic in KiCad for the synchronous buck MPPT logic and smart-FET load switching.</span> -->