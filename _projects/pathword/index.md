---
layout: post
title: Pathword — private multiplayer word puzzles
description: A recovered browser word-path game with solo practice, private two-player races, authoritative scoring and reconnect recovery.
skills:
  - JavaScript and Node.js
  - WebSocket multiplayer
  - Game-state synchronisation
  - Input validation and automated testing
tags: [JavaScript, WebSockets, Game development]
areas: [software]
order: 9
image: /projects/pathword/pathword-gameplay.png
image_alt: Pathword two-player match with a five-by-five letter board, player scores and word-claim history.
thumb: /projects/pathword/pathword-gameplay.png
permalink: /projects/pathword/
published: true
---

Pathword is a browser word-path puzzle: trace adjacent letters to find words, practise solo, or invite a friend to race on the same board. Each word is awarded to the first valid claim received by the server.

**[Play Pathword](https://pathword.onrender.com)**

I recovered an unfinished HTML/JavaScript prototype and completed its room lifecycle, two-player scoring and reconnection behaviour. The interface supports pointer and keyboard selection, adjustable boards and timed or untimed rounds. Solo practice can be finished early to review the results and start a fresh puzzle with the same settings.

The multiplayer server validates tile paths and calculates scores rather than trusting client-supplied totals. It sends both players an authoritative snapshot of the puzzle, claims, scores and deadline. A private session token restores a player's position after a brief disconnect.

The project uses vanilla HTML/CSS/JavaScript, Node.js and WebSockets. Solo practice shares its puzzle engine with the server. All 21 local automated checks pass, covering simultaneous claims, invalid moves and messages, room isolation, reconnection, expiry, pointer cancellation and static-file access. Local browser checks cover solo and two-player rounds, score recovery, rematches, and layouts down to 320 pixels wide. The live Render deployment also passed browser verification and 19 hosted protocol assertions. Physical touchscreen testing remains outstanding.

The game runs on a free Render service with one server process. It may take a little time to wake after inactivity, and free-plan quotas limit availability. Private rooms last up to 30 minutes and disappear on service restart; if a room is no longer available, create a new invitation. These limits keep the initial release suitable for casual play and a portfolio demonstration.

The screenshot above shows an actual local two-player test match captured on 20 October 2026.
