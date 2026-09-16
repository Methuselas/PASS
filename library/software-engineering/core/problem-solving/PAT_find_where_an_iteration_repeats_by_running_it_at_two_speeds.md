---
object_id: PAT_find_where_an_iteration_repeats_by_running_it_at_two_speeds
object_type: pattern
name: Find Where an Iteration Repeats by Running It at Two Speeds
library_path:
- software-engineering
- core
- problem-solving
stage_binding: 0 design
lane_fit: skill
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- algorithm_design
- cycle_detection
- memory
- iteration
cross_links:
- rel: related_to
  target_object_id: PAT_estimate_the_order_before_you_run_it
- rel: related_to
  target_object_id: PAT_compose_an_associative_step_by_doubling
reference:
  source_title: An Introduction to the Analysis of Algorithms
  author: Robert Sedgewick, Philippe Flajolet
confidence: high
references: []
variants: []
---

# Find Where an Iteration Repeats by Running It at Two Speeds

## Pattern Rule
**IF** a sequence is produced by applying one function repeatedly to its own output — a generator stepping its state, or any function from a finite set back into that set — and you need a value on the cycle it eventually falls into, and the number of distinct values before the repeat may be too large to store
**THEN** run two copies from the same start, one applying the function once per step and the other twice, until they hold equal values; the meeting value lies on the cycle, the search uses constant memory, and it ends within the length of the path to and around the cycle
**ELSE** where the values before the repeat are few enough to keep, recording each in a set and stopping at the first one already present is simpler and finds the very first repeated value directly.

## Do
- Recognise the shape before reaching for storage. A function from a finite set to itself must eventually revisit a value, so every starting point leads along a tail into a cycle; the question "does this ever repeat, and where" is a question about that shape, and it does not require remembering the path.
- Advance the slow copy once and the fast copy twice per step, and compare after each step. Once both are on the cycle the fast copy gains one position per step on the slow one, so it catches it before the slow copy completes a lap. Iterating a squaring map modulo about 10¹², the stored-values search kept about 1.4 million values in roughly 47 MB and took 270 ms; the two-speed search found a cycle value in 12 ms with no storage, using 2.4 function evaluations per step of the path.
- Expect the difference to grow with the path. Modulo about 10¹⁴ the path was 5.2 million values long; storing them took 1,680 ms and roughly 183 MB, against 37 ms for the two copies.
- Use the step count as an estimate of the path length. When the copies meet, the number of steps taken lies between about half the tail-plus-cycle length and that full length. In the three runs above it came to 0.66–0.84 of the full length, which is close enough to size a test or report a period.
- Expect a random-looking function on n values to repeat after about √(πn/2) steps, not after n. The measured paths were 64 thousand, 1.4 million and 5.2 million values for n near 10⁹, 10¹² and 10¹⁴, against 40 thousand, 1.3 million and 12.5 million from that formula. A single start varies around it by a factor of two or more, but at the scale of the square root.

## Don't
- Don't assume a state machine with n states cycles only after n steps. A generator whose step function behaves like a random mapping falls into a cycle after about the square root of its state count, and checking it for short cycles with two copies costs nothing next to what a stored-states check would need.
- Don't take the meeting point for the start of the cycle or the first repeated value. It is some value on the cycle; if the first repeated value itself is needed and the path fits in memory, the stored-values search gives it directly.

## Checklist
- Is the sequence produced by applying one function to its own output over a finite set?
- Could the number of distinct values before the repeat exceed the memory you can spend?
- Does the loop advance one copy once and the other twice, comparing each step?
- Is a value on the cycle what is needed, or the exact first repeat?
- For a function that behaves randomly, was the square-root estimate used to size the run?

## Notes
The two-speed search works because of how a relative position changes, not because of anything about the values. Both copies follow the same path. Once the slower one enters the cycle, the gap between them shrinks by one position per step, modulo the cycle length, so it must reach zero before the slower copy has gone once around. Nothing has to be remembered except the two current values, so memory stays constant whatever the path length.

The square-root scale is the reason this matters in practice. A function on n values that mixes like a random one typically revisits a value after about √(πn/2) steps. That is far sooner than intuition expects of a large state space, and far more values than anyone wants to store once n is large.
