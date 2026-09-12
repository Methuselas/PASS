---
object_id: PAT_factor_parameter_independent_code_from_templates
object_type: pattern
name: Factor Parameter-Independent Code Out of Templates
library_path:
- software-engineering
- languages
- cpp
- templates
stage_binding: 3 rough
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- templates
- code_bloat
- efficiency
cross_links:
- rel: related_to
  target_object_id: PAT_use_private_inheritance_judiciously
- rel: related_to
  target_object_id: PAT_separate_inline_linkage_from_inlining_optimization
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Factor Parameter-Independent Code Out of Templates

## Pattern Rule
**IF** a template instantiates code that does not actually depend on all of its parameters (such as a non-type size parameter)
**THEN** factor that code into a less-parameterized place — a base class templatized only on the varying type, or function parameters and data members instead of non-type parameters — to avoid code bloat from repeated instantiations.

## Do
- Move size-independent logic into a base class templatized only on the element type, and have each sized derived class make inline calls into it (SquareMatrix delegating to SquareMatrixBase).
- Replace a non-type template parameter with a function parameter or a data member so one function body serves many sizes.
- Cut type-parameter bloat by having strongly-typed instantiations share one underlying implementation — pointer templates delegating to a void-pointer version.

## Don't
- Don't leave code that differs only by a constant inside the template; each instantiation duplicates it, as a 5-by-5 and a 10-by-10 invert do.
- Don't force the shared implementation to be substituted into every instantiation, which is what actually reinstates the duplication. The `inline` keyword is not that: it governs whether repeated definitions are legal, and whether a body is substituted is the optimizer's decision, which for a body large enough to be worth factoring it normally declines. Measured across eight sizes of one matrix template, moving the body out of the template cut the object by about forty percent; writing that shared body inside the class instead left it within a fraction of a percent of the out-of-line version; only a non-portable force-inline attribute brought the duplication back, and it then cost slightly more than never factoring at all. See `PAT_separate_inline_linkage_from_inlining_optimization`.

## Checklist
- Does any code in this template not depend on all of its parameters?
- Can a non-type parameter become a function parameter or a data member?
- Is the shared implementation one function reused across instantiations, with nothing forcing it to be substituted into each of them?

## Notes
Template replication is implicit: one source copy, but many instantiated bodies. The SquareMatrix invert example bloats because size is a non-type parameter, so each size gets its own copy; moving invert into a base templatized only on the element type (reached by private inheritance) shares one body. Trade-offs are real — the size-specific version can optimize a compile-time constant the shared version cannot, and a stored data pointer adds size — so measure before deciding.
