---
object_id: PAT_specify_publication_job_before_requesting_print_estimates
object_type: pattern
name: Specify the Publication Job Before Requesting Print Estimates
library_path:
- art
- publication-design
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- publication_design
- print_estimate
- production_specification
- printing
- manufacturing
cross_links:
- rel: related_to
  target_object_id: PAT_choose_publication_reproduction_process_from_run_content_resources_and_time
- rel: related_to
  target_object_id: PAT_choose_publication_format_from_content_physical_feel_and_production_constraints
- rel: related_to
  target_object_id: PAT_test_publication_stock_and_binding_with_physical_dummy
reference:
  source_title: 'Indie Publishing: How to Design and Produce Your Own Book'
  author: Joseph Galbreath
confidence: high
references: []
variants: []
---

# Specify the Publication Job Before Requesting Print Estimates

## Pattern Rule
**IF** a publication will be priced by one or more commercial printers
**THEN** define the same production specification for every estimate, including quantity options, timing, trim size, page count, color plan, image burden, paper, cover, binding, and special processes

## Do
- Ask for more than one quantity when run size is still flexible so the estimate exposes how unit cost changes with scale.
- Give a realistic deadline because printing and binding require physical preparation and production time.
- State trim size and page count together, including any page-count increments imposed by folded signatures or single-sheet binding.
- Specify the number of process or spot colors, approximate image count and reproduction scale, intended paper stock, cover construction, binding method, and special processes such as varnish, foil, or die cutting when they apply.
- Use the same specification when comparing printers so a lower price is not merely the result of omitted materials, finishing, or production steps.

## Don't
- Do not request a price from a vague description such as page size and total pages while leaving color, stock, binding, or finishing unstated.
- Do not compare estimates that assume different quantities, papers, bindings, or special processes as though they price the same object.
- Do not give an impossible deadline and treat the resulting rush cost or production compromise as a printer failure.
- Do not lock an uneconomical trim size without checking how it fits the printer's press and available paper.

## Checklist
- Every printer received the same intended quantity range and deadline.
- Trim size and page count describe a construction the selected binding can actually use.
- Color, image burden, paper, cover, binding, and special processes are stated explicitly.
- Differences between estimates can be traced to provider or production choices rather than missing specifications.

## Notes
A commercial print estimate is only meaningful when the printer knows what object is being priced. Quantity, schedule, size, pagination, color, imagery, stock, cover, binding, and finishing all change cost and production time. Describe the job consistently before comparing estimates; otherwise the numbers may represent different publications rather than competing ways to make the same one.
