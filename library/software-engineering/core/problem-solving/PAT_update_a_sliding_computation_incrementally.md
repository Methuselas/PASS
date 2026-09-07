---
object_id: PAT_update_a_sliding_computation_incrementally
object_type: pattern
name: Update a Sliding Computation Incrementally
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
- performance
- hashing
- incremental_computation
cross_links:
- rel: related_to
  target_object_id: PAT_sweep_sorted_events_and_compare_only_neighbors
- rel: related_to
  target_object_id: PAT_amortize_a_sequence_instead_of_bounding_one_operation
- rel: related_to
  target_object_id: PAT_prescreen_with_a_bounded_false_positive_filter
reference:
  source_title: 'Introduction to Algorithms, 3rd Edition'
  author: Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein
confidence: high
references: []
variants: []
---

# Update a Sliding Computation Incrementally

## Pattern Rule
**IF** a computed value depends on a fixed-size or otherwise well-defined window of input that shifts by a small, known amount between consecutive evaluations, and each evaluation would otherwise recompute the value from the whole window
**THEN** derive the relationship between one window's value and the next — what left, what entered, how each changes the running value directly — and update by that relationship alone, paying only for the change rather than recomputing from scratch
**ELSE** where consecutive windows share nothing an update can exploit, or deriving the update costs as much as recomputing would, there is nothing here to save.

## Do
- Find the relationship in one arithmetic step before writing any code: what leaves the window, what enters it, and how each one's contribution can be added to or removed from the running value without touching the elements that stayed. A rolling hash over a text window removes the outgoing character's weighted contribution, shifts the remainder, and adds the incoming character — three operations regardless of the window's size.
- Keep the running value in a representation that supports both adding and removing a contribution cheaply. A sum, a modular residue, and a count all support both; a value that can only be built up and never partially undone — most cryptographic hashes among them — cannot be maintained this way at all, which is why "cheap to compute once" and "cheap to update" are different properties worth checking separately.
- Bound the arithmetic against overflow or accumulated error before trusting a running value across a long input. A value maintained incrementally accumulates across the entire input rather than being freshly derived each time, so an error introduced early does not wash out the way an independent recomputation's error would.
- Treat the saving as changing the algorithm's asymptotic behavior, not merely its constant factor. Recomputing an m-element window from scratch at each of n positions costs O(nm); maintaining it incrementally costs O(n) — an entire factor of m disappears, not a fixed speedup.

## Don't
- Don't treat an incrementally updated value as a substitute for an exact check when it is only a proxy for the thing actually being compared. Two different windows can update to the same running value — a collision — without being equal, so a match on the running value is grounds to check the real windows, not grounds to conclude they match.
- Don't let a running value slide across a boundary the problem doesn't actually have. A window that slides off the end of one record into the next produces a value that is arithmetically well-defined and semantically meaningless; the update relationship has to be re-derived or reset at every real boundary, not carried through it.
- Don't reach for this when the window's actual contents, not a fixed-size digest of it, are needed at every step. Incremental maintenance keeps a running summary current; if the algorithm has to inspect the whole window's real elements at each position, an index into the original data costs nothing extra and a separately maintained summary is solving a problem nobody has.

## Checklist
- Is there an arithmetic, or otherwise composable, relationship between one window's value and the next that involves only what entered and what left?
- Does the running value's representation support removing an old contribution as cheaply as adding a new one?
- Has the running computation been checked for accumulated error or overflow over the full length of the input, not just one window?
- Where the running value is a proxy — a hash, a digest — rather than the real quantity, does every match still get confirmed against the real data?
- Are window boundaries the problem doesn't intend for being crossed silently?

## Notes
The name usually attached to this in the string-matching context — a rolling hash — undersells how general the underlying move is. A moving average, a checksum recomputed as a file streams past, a running total of a metric over the last N events all use the same relationship: whenever "the next answer" and "the previous answer" differ by a small, describable amount, computing the difference is cheaper than computing the answer from scratch.

It sits beside amortized analysis rather than inside it. An amortized argument bounds the total cost of a sequence of operations whose individual costs vary; this technique is one common way to make each individual operation of a sliding computation cheap enough in the first place for such an argument to even be needed. A dynamic table's doubling is amortized because most insertions are cheap on their own; a rolling hash's window update is cheap on its own because this technique makes it so — the two ideas compose rather than compete.
