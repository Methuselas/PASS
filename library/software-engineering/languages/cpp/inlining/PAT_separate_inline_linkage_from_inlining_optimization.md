---
object_id: PAT_separate_inline_linkage_from_inlining_optimization
object_type: pattern
name: Separate Inline Linkage from Inlining Optimization
library_path:
- software-engineering
- languages
- cpp
- inlining
stage_binding: 3 rough
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- inlining
- optimization
- linkage
- build
cross_links:
- rel: related_to
  target_object_id: PAT_prefer_inline_functions_to_macro_functions
- rel: related_to
  target_object_id: PAT_let_measurement_decide_what_to_tune
reference:
  source_title: Modern C++ correction of accepted inline guidance
  author: PASS software-engineering synthesis
confidence: high
references: []
variants: []
---

# Separate Inline Linkage from Inlining Optimization

## Pattern Rule
**IF** a function or variable definition must appear in multiple translation units, or a call is being considered for inlining as an optimization
**THEN** make two decisions: use C++ inline/templated/constant-evaluation rules to keep repeated definitions legal, and let measurement plus the optimizer, link-time optimization, or profile guidance decide whether code is actually substituted at call sites
**ELSE** keep a stable out-of-line boundary when it improves build time, ABI control, or code organization.

## Do
- Use `inline` for a non-template function or variable definition placed in a header when the same definition must be accepted across translation units. Remember that functions defined inside a class definition and `constexpr` functions already receive the relevant inline semantics.
- Treat actual call-site substitution as an optimizer choice. Inspect optimized builds and measure the workload; compilers may inline a function with no `inline` specifier and decline one that has it.
- Use link-time and profile-guided optimization when profitable substitutions cross translation-unit boundaries. Those facilities give the optimizer evidence and visibility that a source keyword cannot guarantee.
- Keep non-trivial implementation out of public headers when rebuild cost, implementation hiding, ABI stability, or code size matters more than exposing the body.

## Don't
- Don't add `inline` as a command to make code faster. Its normative job is to permit repeated reachable definitions under the one-definition rule; optimization remains independent.
- Don't add the specifier to a template merely because its definition is in a header. Templates have their own ODR rules, and the keyword does not solve visibility or instantiation by itself.
- Don't force-inline broadly with implementation-specific attributes. They are non-portable, may enlarge hot instruction working sets, and can make debugging and optimization worse; reserve them for measured target-specific cases.
- Don't assume moving a large body into a header is free. Every dependent translation unit may need to recompile when it changes, whether or not the optimizer substitutes the call.

## Checklist
- Is this a language/ODR decision, an optimizer decision, or both?
- Does the definition need to be reachable from multiple translation units?
- What optimized-build measurement shows that call overhead or cross-call optimization matters?
- Would an out-of-line boundary improve rebuild time, ABI stability, code size, or diagnostics?
- If a non-standard force-inline control is proposed, which measured target justifies it?

## Notes
Older guidance described `inline` as an optimization request and then advised rationing the request to small hot functions. Modern optimizing compilers do not need that hint to substitute ordinary calls, and they routinely ignore it when substitution is unprofitable. The language keyword still matters, but for a different reason: it permits equivalent definitions of an inline entity in multiple translation units while preserving one entity with external linkage.

Visibility still affects optimization. A compiler can reason more easily about a visible body, and link-time optimization can provide that visibility without placing every implementation in a public header. Keep the questions separate: choose the source boundary for ownership, build, and ABI reasons; choose optimization from evidence produced by the actual release toolchain.
