---
object_id: PAT_run_packaging_from_a_machine_of_the_target_platform
object_type: pattern
name: Run Packaging from a Machine of the Target Platform
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 4 final
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- packaging
- platforms
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Run Packaging from a Machine of the Target Platform

## Pattern Rule
**IF** you need a build of the game for a desktop platform different from the one your development machine runs
**THEN** install Unreal Engine 5 on a machine running that platform, copy your project files there, and package it from that machine — no further changes to the project are required.

## Do
- Package through the Platforms button in the toolbar: hover over the target platform and choose Package Project, then pick where to store the build.
- If packaging fails, read the details of the error in the output log window before retrying.
- Verify the result by launching it from its packaged folder: WindowsNoEditor on Windows (double-click the executable) or MacNoEditor on macOS (double-click the application).

## Don't
- Don't expect a Windows machine to produce a macOS build, or vice versa — Unreal Engine 5 creates Windows builds only from an engine running on Windows and OS X builds only from one installed on macOS.
- Don't assume every listed platform is reachable: consoles require you to be a registered console developer with the appropriate development kit, and mobile targets carry higher optimization requirements.

## Checklist
- The packaged build exists in the folder you chose for it.
- The game launches and plays from its NoEditor folder on the target machine's OS.
- Any packaging error was read from the output log rather than guessed at.

## Notes
The platforms you can target are partially limited by the machine you develop on, because each desktop build must be produced by an engine installed on that platform's own operating system. The project itself does not change when it moves to the other machine — only the engine and the packaging step do. When you want to move or hand off the project rather than a build, the File menu's Zip Project option copies and compresses the essential project files.
