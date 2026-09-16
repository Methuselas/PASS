---
object_id: PAT_merge_groups_by_linking_representatives_not_relabeling_members
object_type: pattern
name: Merge Groups by Linking Representatives, Not by Relabeling Members
library_path:
- software-engineering
- core
- performance
stage_binding: 0 design
lane_fit: skill
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- performance
- data_structures
- grouping
- amortized_analysis
cross_links:
- rel: related_to
  target_object_id: PAT_bound_the_sequence_when_one_operation_is_occasionally_expensive
- rel: related_to
  target_object_id: PAT_estimate_the_order_before_you_run_it
reference:
  source_title: Introduction to Algorithms
  author: Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein
confidence: high
references: []
variants: []
---

# Merge Groups by Linking Representatives, Not by Relabeling Members

## Pattern Rule
**IF** elements are partitioned into groups that only ever merge, and the program repeatedly asks which group an element is in — connectivity as links are added, accounts found to belong to one person, cells joined into regions, equivalences discovered one at a time
**THEN** represent each group as a tree of parent references whose root names the group, merge by linking one root under the other with the shallower tree going under the deeper, and let each lookup point the elements it walked directly at the root, instead of writing a new group label into every member of one side
**ELSE** where all the merges are known before any question is asked, one traversal that labels every group at once is simpler and at least as fast; and where groups must also split, this structure does not help, because it has no cheap way to undo a merge.

## Do
- Recognise the relabeling version by its cost profile. Writing the surviving label into every member of the absorbed group makes one merge cost the size of that group, and a run of merges that keeps absorbing the large group into a single newcomer costs the square of the number of elements: measured on twenty thousand elements, 199,990,000 label writes.
- If you keep explicit member lists, always relabel the smaller group into the larger. Each time an element is relabeled the group it lands in is at least twice the size of the one it left, so no element moves more than log n times: the same twenty thousand elements took 19,999 writes merged in that adversarial order, and about forty thousand under random merges.
- Prefer the tree of parent references when merges and lookups are both frequent. A merge then costs two root lookups and one pointer write, whatever the group sizes.
- Link by rank: keep an upper bound on each tree's height at its root, and hang the root with the smaller bound under the other, incrementing the bound only when the two are equal. Without it, an unlucky order of merges builds a single path, and every lookup walks it.
- Compress paths on lookup: after finding the root, point every element on the path walked directly at it. The next lookup of any of them is one step.
- Treat the combined cost as linear in practice. With both linking by rank and path compression, a sequence of m operations costs m times an inverse of an extremely fast-growing function that is at most four for any input that could physically exist. Measured on twenty thousand elements merged into one path-shaped group and then looked up repeatedly from the deepest element, the unimproved forest took 1,398,643,567 pointer steps and the improved one about 140,000.

## Don't
- Don't recompute groups from scratch after each new link. A fresh traversal per added link costs the whole graph each time; maintaining the groups under merges costs almost nothing per link. The traversal wins only when every link is known before the first question.
- Don't expose the root as a stable name for the group. Which root survives a merge is an implementation decision, so a caller who stored yesterday's representative holds the name of an element that may now be an ordinary member; ask for the representative at the time of use.
- Don't reach for this where groups split. The parent links record merges without the information needed to reverse them, so a structure that must also separate groups needs a different representation, not a mode of this one.
- Don't skip the rank on the grounds that compression alone is enough on your data. Either heuristic alone removed the pathological case in the measurement above, but the guarantee that holds for every sequence comes from the two together.

## Checklist
- Do groups only ever merge, or must they also split?
- Are merges and membership questions interleaved, or are all merges known first?
- If member lists are kept, is the smaller group always the one relabeled?
- Does the forest link by rank and compress paths on lookup?
- Does any caller store a representative across merges rather than asking for it when needed?

## Notes
The quadratic trap is structural rather than careless. Relabeling looks proportional to the merge being performed, and on a single merge it is; the cost is in the sequence, where the same large group can be relabeled again and again as small groups join it from the wrong side. Relabeling the smaller side fixes the sequence by bounding how often any one element can move, which is the whole of that argument: an element's group at least doubles each time it moves, and a group cannot exceed the number of elements.

The forest removes the relabeling entirely by making group membership a property of where an element's parent references lead rather than of a label stored in the element. Merging then touches only the roots, and the two heuristics keep the paths to the roots short — one by never letting a merge deepen a tree unnecessarily, the other by letting each lookup repair the paths it had to walk, so that the cost of a long walk is paid once and then disappears.
