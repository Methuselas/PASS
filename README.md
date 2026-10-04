# PASS Authoring System Demonstration

This demonstrates how to use the PASS (Portable Authoring Skill) system to create source studies.

Current version `1.0.0-beta.104`.

## How to Use

1. Create a preflight JSON record describing your source material
2. Validate it using the preflight gate
3. Start an authoring run with `PASS/pass.py start`
4. Follow through the phases: load, source_prep, preflight, pass1, pass2, pass3, land

## Example Process

### Step 1: Create a preflight record
I've created `example_preflight.json` which describes:
- A software engineering source study
- Two units covering variables and control structures
- Python language requirements with modernization needed

### Step 2: Validate the preflight
```bash
python PASS/runtime/pass_authoring_run.py preflight gate --input example_preflight.json
```

This validates the structure and checks for any existing card overlaps.

## Key Principles from AGENTS.md

- Source authoring runs through `PASS/pass.py`
- Cards must be valid and executable after source is gone
- Author in one domain per run
- Cards may reference their own package plus `metaskills`
- Every release ships `metaskills` and its complete prerequisite closure
