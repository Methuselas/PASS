---
object_id: PAT_measure_python_speed_with_timeit_and_perf_counter
object_type: pattern
name: Measure Python Speed with timeit and perf_counter, Not a Handrolled Clock
library_path:
- software-engineering
- languages
- python
- performance
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- performance
- benchmarking
- timeit
- standard-library
cross_links:
- rel: related_to
  target_object_id: PAT_report_the_spread_not_just_the_number
- rel: related_to
  target_object_id: PAT_make_benchmarked_work_observable
- rel: related_to
  target_object_id: PAT_reproduce_the_real_context_before_believing_a_microbenchmark
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Measure Python Speed with timeit and perf_counter, Not a Handrolled Clock

## Pattern Rule
**IF** you need to time a Python call, statement, or small code fragment
**THEN** reach for the standard library's `timeit` module (`timeit.timeit`, `timeit.repeat`, or `python -m timeit`) for the comparison itself, and `time.perf_counter()` (wall-clock) or `time.process_time()` (CPU-only, excludes sleep) when you need a bare timestamp of your own
**ELSE** where the question is where a whole program's time actually goes rather than comparing two short fragments, reach for a profiler instead — see `AP_locate_a_performance_bottleneck_by_measurement`

## Do
- Call `timeit.repeat(stmt=..., number=N, repeat=R)` and take the `min()` of the returned list for the number you report; `timeit` already runs the statement in a loop and insulates it from most interpreter-startup and name-lookup overhead.
- Use `time.perf_counter()` for a hand-timed interval: it is a monotonic, highest-resolution clock meant exactly for measuring a short duration, and its only valid use is subtracting two of its own readings.
- Use `time.process_time()` instead when the question is CPU time this process consumed, not wall time inflated by another process, I/O wait, or system sleep.
- Pass setup code through `timeit`'s `setup` argument (or `-s` on the command line) to exclude one-time costs — an import, building test data — from the timed statement.
- State which Python, which machine, and which release a number was measured on beside anything reported; none of these tools make a result portable to a different interpreter or version.

## Don't
- Don't call `time.clock()`; it was deprecated in Python 3.3 and removed in 3.8, and `perf_counter`/`process_time` are its full replacements — one for wall time, one for CPU time.
- Don't write a loop-and-subtract timer as the default move; `timeit` already handles disabling the garbage collector during the run, isolating loop overhead, and reporting the best of several repeats, all mistakes a first-cut homegrown timer is prone to.
- Don't read a `timeit` result for one Python version or implementation as predicting another; relative rankings between constructs are not guaranteed to survive from one interpreter release to the next.
- Don't time a construct that calls a function (e.g. `map` with a lambda) against one that doesn't (a plain comprehension) and conclude the first is slower "in general"; the function-call overhead, not the construct, is usually what the result is measuring.

## Checklist
- Is the comparison between two short fragments, or a question about where a whole program spends its time? The second calls for a profiler, not `timeit`.
- Is `min()` of several repeats being reported, rather than a single run or a plain average?
- Does the timed statement exclude one-time setup that `timeit`'s `setup` argument could carry instead?
- Is `time.clock()` absent from the code? If present, it will raise `AttributeError` under the target version.
- Is the Python version, implementation, and machine stated beside any number drawn from this measurement?

## Notes
`timeit.default_timer` is `time.perf_counter` on every current platform, so the module no longer needs the Windows/Unix clock-selection dance a pre-3.3 homegrown timer required. Reach for a profiler rather than `timeit` once the question changes from "which of these two fragments is faster" to "where does this program actually spend its time" — the two tools answer different questions, and `AP_locate_a_performance_bottleneck_by_measurement` owns the second one.
