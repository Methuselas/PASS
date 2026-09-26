"""PASS Candidate Refinement & Qualification (CRQ).

A CRQ run compares one bounded candidate change to ordinary PASS cards against a
frozen canonical baseline. The package owns only administration: the run state
machine, atomic state writes, path containment, frozen-file hashes, the
controller fingerprint, baseline-drift detection, intake of one Skillset Memory
`card_candidate`, the structural checks on a defect assessment and a
qualification plan, candidate staging, mutation accounting, and ordinary PASS
validation of a temporary candidate overlay. It never writes `library/` or
Skillset Memory, never calls a model, and never judges domain semantics.

Modules: `schemas` (vocabularies and document validation), `evidence` (memory
intake, canon reading, candidate accounting, overlay validation), `gate` (the
per-case delta and final gate), and `controller` (run state and the lifecycle
commands). `PASS/runtime/pass_candidate_qualification.py` is the command line.
Run directories live under `workspace/candidate-qualification/<domain>/<run-id>/`.
"""
