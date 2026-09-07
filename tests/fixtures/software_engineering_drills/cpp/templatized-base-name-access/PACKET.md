# C++ Drill administration pilot

- Source Drill: `DRILL_fix_templatized_base_class_name_access`
- Run type: deterministic packet regression
- Administration cut: before `## Success Check`
- Takers required for self-test: 0
- Takers allowed for a real sitting: 1
- Control arms: 0
- Maximum concurrent sub-agents: 1
- Automatic repetitions: 0
- Contamination boundary: the taker may receive only `taker/`

This packet tests whether the administration fixture can preserve a hidden
grader and collect real compiler evidence. Running its reference answers is not a
Drill sitting and produces no evidence about an AI or human capability.

Self-test the packet from this directory:

```powershell
python grader/verify.py --self-test
```

For a real sitting, copy only `taker/` to an isolated working directory. After
the taker's answer is frozen, run:

```powershell
python grader/verify.py PATH_TO_FROZEN_ANSWER
```
