---
object_id: PAT_escalate_python_debugging_from_traceback_to_postmortem
object_type: pattern
name: Escalate Python Debugging From Traceback to Post-Mortem
library_path:
- software-engineering
- languages
- python
- debugging
stage_binding: 3 rough
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- debugging
- pdb
- traceback
cross_links:
- rel: related_to
  target_object_id: AP_find_a_defect_by_hypothesis_not_by_guessing
- rel: related_to
  target_object_id: PAT_build_a_way_to_see_inside_the_running_system
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Escalate Python Debugging From Traceback to Post-Mortem

## Pattern Rule
**IF** a Python program fails or misbehaves and the cause is not yet known
**THEN** start with the cheapest evidence Python already gives you and climb only as far as needed: read the whole traceback, then add targeted prints, then inspect the failed program's final state post-mortem, and only then step through it under `pdb`
**ELSE** when the process cannot be restarted — a long-running service or a hang you cannot reproduce on demand — attach the debugger to the live process instead of rerunning it.

## Do
- Read the traceback from the bottom up: the last line names the exception type and message, the frame above it is where it was raised, and the frames further up show which of your calls led there. Fix the named line before reaching for any tool.
- Add prints (or temporary logging) at the points that would confirm or kill your current guess, rerun, and remove them before the change is committed.
- Run the script with `python -i script.py` to land at an interactive prompt after it ends — normally or by an uncaught exception — with its module-level variables intact, then call `import pdb; pdb.pm()` to open the debugger in the frame where the exception was raised.
- Put `breakpoint()` in the code to stop at a chosen line; it starts `pdb` by default, and setting `PYTHONBREAKPOINT=0` disables every such call without editing the code.
- Use `python -m pdb script.py` to run a whole script under the debugger from its first line, and `python -m pdb -p PID` (Python 3.14 and later) to attach to a process that is already running.

## Don't
- Don't stop at the first line of the traceback or skim only the exception name; the frames show which caller passed the bad value, and that is usually where the fix belongs.
- Don't set up a stepping session for an error whose traceback already names the failing line and the reason.
- Don't leave diagnostic prints or `breakpoint()` calls in shipped code; a forgotten `breakpoint()` halts the program waiting for debugger input.
- Don't debug a program launched by double-clicking its file on Windows: the console that shows the traceback closes as the program dies. Run it from a terminal or an IDE while developing.

## Checklist
- Has the full traceback been read, including the frames above the one that raised?
- Does each added print test a specific hypothesis rather than dump everything?
- Was the post-mortem state (`python -i` plus `pdb.pm()`) examined before resorting to stepping?
- Are all prints and `breakpoint()` calls gone from the committed change?

## Notes
Python reports errors as exceptions with a traceback instead of crashing silently, and that report is enough for most defects in code you wrote yourself. The escalation order is about cost: every rung gives more context but takes more setup, so each is used only when the rung below failed to explain the failure.

The post-mortem rung is the one most often skipped. After an uncaught exception the program's final state still exists; `python -i` keeps the interpreter alive so you can print variables, and `pdb.pm()` reopens the stack as it was at the moment of the error, so you can move between frames with `up` and `down` and inspect locals without rerunning anything.
