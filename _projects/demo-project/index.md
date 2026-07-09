---
layout: post
title: tap-mania - Miniaturised music based rhythm and dance game
description: tpmania is a miniaturised arcade rhythm and dance game designed to be played with your fingers. The cues are synchronised to music, requiring players to accurately hit directional pads to score points. The project involves iterative custom PCB design, STM32 microcontroller firmware, audio generation, and power pathing integration.
skills: 
  - PCB Design and Fabrication
  - STM32 Microcontroller Programming
  - Firmware Development (C/C++)
  - Power Supply Design (Battery Boost, LDOs)
  - Hardware Debouncing and Filtering
  - UART Communication and Debugging
  - Embedded Systems Integration

main-image: /project2.jpg
---

---
# tap-mania - Miniaturised Rhythm Game

## Project Overview 
tpmania (pronounced "tap-mania") is a miniaturised arcade rhythm and dance game. Drawing inspiration from full-sized arcade cabinets of the early 2000s, the objective of the player is to follow rhythm cues displayed on a screen by pressing the correct arcade buttons. The game requires precise timing, scoring players based on their accuracy in hitting the pads synchronised to the music.

### Hardware & PCB Design
The hardware involves an iterative PCB design centered around an STM32L433CCT6 microcontroller. The system includes robust power pathing and battery charging with an MP2637GR-Z IC, a 3.3V LDO (AP2112K-3.3) for digital rails, audio generation via a MAX98357A DAC + Amplifier, SD card interfacing, and a 1.3” OLED display. 


## Embedding images 
### External images
{% include image-gallery.html images="https://live.staticflickr.com/65535/52821641477_d397e56bc4_k.jpg, https://live.staticflickr.com/65535/52822650673_f074b20d90_k.jpg" height="400"%}
<span style="font-size: 10px">"Starship Test Flight Mission" from https://www.flickr.com/photos/spacex/52821641477/</span>  
You can put in multiple entries. All images will be at a fixed height in the same row. With smaller window, they will switch to columns.  

### Embeed images
{% include image-gallery.html images="pcbv1_schematic.jpg" height="400" %} 
place the images in project folder/images then update the file path.   


## Embedding youtube video
The second video has the autoplay on. copy and paste the 11-digit id found in the url link. <br>
*Example* : https://www.youtube.com/watch?v={**MhVw-MHGv4s**}&ab_channel=engineerguy
{% include youtube-video.html id="MhVw-MHGv4s" autoplay= "false"%}
{% include youtube-video.html id="XGC31lmdS6s" autoplay = "true" %}

you can also set up custom size by specifying the width (the aspect ratio has been set to 16/9). The default size is 560 pixels x 315 pixels.  

The width of the video below. Regardless of initial width, all the videos is responsive and will fit within the smaller screen.
{% include youtube-video.html id="tGCdLEQzde0" autoplay = "false" width= "900px" %}  

<br>

## Adding a hozontal line
---

## Starting a new line
The team focused on developing separate aspects of the product on breakout boards before moving to prototype PCBs.  
This iterative methodology allowed for easier integration of subsystems on a single board. <br>

## Adding bold text
Oliver was primarily responsible for the **PCB design (prototype versions 1-4) and construction**, as well as the **state machine architecture and refactoring**.

## Adding italic text
The genre of rhythm games has spawned a number of different game concepts that are still popular, such as *Guitar Hero* and *Taiko no Tatsujin*.

## Adding ordered list
1. Breadboard prototyping of arcade button debouncing and interrupt architecture.
2. PCBv1 design focusing on battery charging, 5V rail generation, and initial STM32 pinout routing.
3. PCBv2 fabrication adding direct USB-C connectors and arcade pushbutton spade terminal lugs.
4. Final PCBv4 integrations with full gameplay sequencing and OLED display architecture.

## Adding unordered list
- Part selection and design for audio generation (MAX98357A DAC).
- Battery charging, boosting, and power pathing with USB.
- Queue-based arcade button handling.
- Firmware for proactive LED scheduling using a beat metronome timer.

## Adding code block
```c
// Example timer interrupt for beat metronome (TIM6)
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
  if (htim->Instance == TIM6) {
    // Prompt arcade button handling and LED scheduling on each beat
    schedule_next_beat_leds();
    process_button_queue();
  }
}