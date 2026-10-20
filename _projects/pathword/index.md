---
layout: post
title: Pathword — private multiplayer word puzzles
description: A browser word-path game with solo practice, private races for up to six players, adjustable board difficulty and rounds that can restart without disconnecting.
skills:
  - JavaScript and Node.js
  - WebSocket multiplayer
  - Game-state synchronisation
  - Input validation and automated testing
tags: [JavaScript, WebSockets, Game development]
areas: [software]
order: 9
image: /projects/pathword/pathword-gameplay.png
image_alt: Pathword multiplayer match with a glowing eight-letter word chain, ranked player scores and word-claim history.
thumb: /projects/pathword/pathword-gameplay.png
permalink: /projects/pathword/
published: true
---

Pathword is a browser word-path puzzle: trace adjacent letters to find words, practise solo, or invite friends to a private race for two to six players. Each word is awarded to the first valid claim received by the server.

**[Play Pathword](https://pathword.onrender.com)**

I recovered an unfinished HTML/JavaScript prototype and completed its room lifecycle, multiplayer scoring and reconnection behaviour. Boards can have two to ten rows and two to ten columns, independently, with timed or untimed rounds. A three- or four-letter word earns 100 points, with larger rewards for longer words. Short guesses receive a length explanation rather than being labelled invalid words.

Difficulty controls word abundance. Easy favours boards with more valid words, Standard selects a middle range, and Hard favours fewer options. The shared generator rejects boards below a minimum based on their dimensions and neighbouring tile connections, with a bounded search to keep generation manageable.

The host can change dimensions, difficulty, time or word-list visibility during a round and restart for everyone without losing the room or player connections. Solo practice has the same restart controls. Drag selection follows the inner area of each tile to tolerate small diagonal slips, interpolates fast pointer movement and shows the selected path; keyboard and individual-tile selection are also supported. Softer tile colours and reduced gap contrast make dense boards easier to view.

I added restrained visual feedback to make longer finds and close races easier to follow. The selected path and tiles glow, and the current chain previews its possible points while making clear that the word still needs to be valid and available. Confirmed finds trigger brief score feedback and round-best cues for longer words. Ranked player standings show the lead and score gap, with short notices when the lead changes. A quiet timer cue highlights the closing 30 seconds and warms in the final ten. Reduced-motion preferences disable decorative animation.

The multiplayer server validates tile paths and calculates scores rather than trusting client-supplied totals. It sends every player an authoritative snapshot of the puzzle, claims, scores and deadline. A private session token restores a player's position after a brief disconnect. Restart requests are restricted to the host and the current round; if generation fails, the existing puzzle and scores remain available.

The project uses vanilla HTML/CSS/JavaScript, Node.js and WebSockets. Solo practice shares its puzzle engine with the server. Automated checks cover every supported board shape and difficulty, six-player capacity, simultaneous claims, invalid moves and messages, reconnect recovery, active-round restarts, failed generation, pointer paths and static-file access. Browser checks complement these tests for layout and interaction. Physical touchscreen testing remains outstanding.

The game runs on a free Render service with one server process. It may take a little time to wake after inactivity, and free-plan quotas limit availability. Private rooms last up to 30 minutes and disappear on service restart; if a room is no longer available, create a new invitation. These limits keep the initial release suitable for casual play and a portfolio demonstration.

The screenshot above shows an actual hosted test match captured on 20 October 2026.
