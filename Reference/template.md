---
# New project: copy this file to _projects/<folder-name>/index.md (the folder name becomes the
# page address, e.g. _projects/mppt-controller/ -> /projects/mppt-controller/), put the project's
# images, videos and PDFs in that same folder, then run (from the repo folder):
#   python scripts/optimize_images.py <folder-name>
# which shrinks the images, makes the card thumbnail and adds the `thumb:` line below.
layout: post
title: Project name - what it is in a few words
description: >-
  One or two sentences: what you built, the hard part, and the result. Shown on the project
  card, at the top of the page, and in search results and link previews.
skills:                      # full list, shown on the project page
  - Skill or tool
  - Another skill
tags: [Short label, Another, Third]   # 3-4 short labels on the project card
areas: [power, pcb]          # filter buttons: power, pcb, embedded, control, rf, software
order: 9                     # position on the site, lowest first (decimals like 2.5 slot in between)
image: /projects/folder-name/main-photo.jpg   # page header and link-preview picture
permalink: /projects/folder-name/             # the page's address: don't change it once shared
# published: false                            # uncomment to keep a draft off the live site
---

## Background & My Role

Why the project exists, who was involved (solo, or team of N and which part was yours), and the
headline result with numbers.

{% include image-gallery.html images="photo.webp" height="500" caption="Figure 1: What the reader is looking at." %}

## Design

Requirements, key decisions and trade-offs. Two images side by side:

{% include image-gallery.html images="schematic.webp, layout.webp" height="400" caption="Figure 2: Schematic (left) and copper layout (right)." %}

## Build & Testing

A short looping clip (convert screen recordings and GIFs to MP4 first; see README):

{% include video.html file="demo.mp4" height="500" caption="Figure 3: What the clip shows." %}

## Results

Measured performance against the targets.

## What I'd Do Differently

## Files & Links

* [Schematic (PDF)](schematic.pdf)
* [Source code on GitHub](https://github.com/OliCar-del/REPO)
