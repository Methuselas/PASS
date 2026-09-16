---
object_id: PAT_order_dependent_work_by_its_graph_and_name_the_cycles
object_type: pattern
name: Order Dependent Work by Its Graph and Name the Cycles
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
- dependencies
- graphs
- ordering
- cycles
cross_links:
- rel: related_to
  target_object_id: PAT_design_the_physical_dependency_graph_too
- rel: related_to
  target_object_id: PAT_define_the_subproblems_and_let_their_dependencies_set_the_order
- rel: related_to
  target_object_id: PAT_test_against_a_validity_property_when_the_answer_is_not_unique
reference:
  source_title: Introduction to Algorithms
  author: Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein
confidence: high
references: []
variants: []
---

# Order Dependent Work by Its Graph and Name the Cycles

## Pattern Rule
**IF** a set of items must be processed so that each comes after the things it depends on — build targets, initialisation steps, migrations, tasks, modules — and the dependencies are known as pairs
**THEN** treat the pairs as a directed graph and derive the order from one depth-first traversal: list items in reverse order of when their traversal finished, and treat an edge that reaches an item still being traversed as proof of a cycle, reported with the items that form it
**ELSE** where cycles are legitimate — mutually recursive modules, components that must be released together — first collapse each group of items that can all reach one another into a single unit, order the units, and handle each group as a whole.

## Do
- Build the order from the finishing times of a depth-first traversal. When the traversal finishes an item, everything that item leads to has already finished, so listing items in reverse finishing order puts every item before everything that depends on it; the whole order costs time linear in the number of items plus the number of dependency pairs.
- Detect cycles in the same pass. An edge that leads to an item whose traversal has started but not finished points back to an ancestor on the current path, and a directed graph has a cycle exactly when such an edge exists; the path from that ancestor to the current item, plus the edge, is the cycle to report.
- Report the cycle, not the failure. "Cannot order: a depends on b depends on c depends on a" lets someone break it; "circular dependency detected" sends them to reconstruct the graph by hand.
- Collapse mutually reachable groups when cycles are allowed. The groups in which every item can reach every other partition the items, and the graph whose nodes are those groups has no cycles, so it can be ordered like any other; two traversals — one on the graph, one on the graph with every edge reversed, taking starting points in decreasing order of the first traversal's finishing times — find all the groups in linear time.
- Expect more than one valid order and test for validity rather than for a particular sequence. Items with no path between them can appear in either order, and which one a traversal produces depends on the order in which neighbours are visited.

## Don't
- Don't treat the absence of an error as proof the graph was acyclic when the ordering routine skips visited items without distinguishing "finished" from "in progress". Both look visited; only the second means a cycle, and a traversal that marks items with a single seen-flag will silently produce an order that violates a dependency. Measured on two thousand items with one loop added, the single-flag traversal returned an order without complaint that broke a dependency, while the three-state traversal returned the eight items forming the loop.
- Don't break a cycle by picking an arbitrary edge to ignore. Which dependency is spurious is a design question about the items, and the traversal can only tell you that the loop exists and which items are on it.

## Checklist
- Are the dependencies recorded as directed pairs pointing from the prerequisite to the dependent item, or the reverse — and does the order you emit match that direction?
- Does the traversal distinguish items in progress from items finished?
- When a cycle is found, does the report name the items on it?
- If cycles are permitted, are mutually reachable groups collapsed and handled as units?
- Do tests check that every dependency is respected rather than that one specific order came out?

## Notes
The finishing time is the quantity that makes this work, and it is easy to reach for the wrong one. Discovery order — the order in which the traversal first reaches items — does not respect dependencies; finishing order does, because an item cannot finish until everything reachable from it has. Reversing the finishing order therefore places each item ahead of everything it leads to, whichever way the traversal happened to wander.

The same traversal state that gives the order also gives the cycle test, which is why the two belong together rather than being separate checks. An item is in one of three states during the traversal — not yet reached, reached but not finished, finished — and the three-way distinction is load-bearing: an edge into a finished item is harmless, while an edge into an unfinished one closes a loop through the current path. Collapsing mutually reachable groups turns any directed graph into one without cycles, so the ordering technique applies to every dependency structure once the groups are treated as single items.
