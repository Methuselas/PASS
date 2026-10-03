---
object_id: PAT_respect_the_recursion_limit_or_traverse_with_an_explicit_stack
object_type: pattern
name: Respect the Recursion Limit or Traverse with an Explicit Stack
library_path:
- software-engineering
- languages
- python
- functions
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_bound_recursion_before_you_reach_for_it
tags:
- python
- functions
- recursion
- traversal
cross_links:
- rel: related_to
  target_object_id: PAT_bound_recursion_before_you_reach_for_it
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Respect the Recursion Limit or Traverse with an Explicit Stack

## Pattern Rule
**IF** writing a recursive traversal over data whose depth is not known in advance
**THEN** treat the interpreter's call-stack ceiling as a real bound — roughly a thousand frames by default, raising `RecursionError` when crossed — and either keep the depth comfortably inside it or rewrite the traversal as a loop over an explicit stack or queue, which has no such ceiling
**ELSE** when the depth is genuinely bounded and small, a few levels of tree or a short chain, plain recursion is the clearer code and needs no hand-managed collection

## Do
- Read the current ceiling with `sys.getrecursionlimit` before assuming how deep a traversal may go, and raise it with `sys.setrecursionlimit` only deliberately, knowing the platform imposes its own maximum above which the process can die instead of raising.
- Convert an unbounded-depth traversal into a loop that pops from a list of pending items; the recursion disappears and the ceiling stops applying.
- Choose the traversal order by where pending items are placed: adding a nested group at the end makes the walk breadth-first, putting it at the front makes it depth-first.
- Carry a set of states already seen when the data may contain cycles, and test membership before descending, since the same structure that merely repeats work in a tree loops forever in a graph.

## Don't
- Don't read `RecursionError` as proof the algorithm is wrong; on data that is deep but finite it often means only that this traversal needs an explicit stack instead of the call stack.
- Don't raise the limit as the first response to hitting it; a higher ceiling postpones the same failure and converts a clean exception into a harder crash when the real limit arrives.
- Don't assume a cycle guard is unnecessary because today's data is a tree; the recursive form fails loudly on a cycle while the explicit-stack form quietly consumes memory, and neither failure names the cause.
- Don't keep an explicit stack and a recursive call for the same traversal; one of them is managing depth and the other is hiding it.

## Checklist
- Is the maximum depth of this data known, and is it well inside the interpreter's ceiling?
- If depth is unbounded, does the traversal use an explicit collection rather than the call stack?
- Does the order in which pending items are added match the traversal order intended?
- Can the data contain a cycle, and if so is there a visited set consulted before descending?

## Notes
`PAT_bound_recursion_before_you_reach_for_it` owns the prior decision — whether recursion is the right shape at all, and what stops it — including the general fact that anything recursive can be written with a stack and a loop. This card is the Python-specific consequence: here the call stack is a finite, inspectable, adjustable resource with a documented default, so "it recurses too deeply" is a concrete condition with a named exception rather than an abstract worry, and the rewrite that removes it also hands over control of traversal order.
