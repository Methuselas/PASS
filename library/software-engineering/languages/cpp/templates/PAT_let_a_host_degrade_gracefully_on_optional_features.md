---
object_id: PAT_let_a_host_degrade_gracefully_on_optional_features
object_type: pattern
name: Let a Class Degrade Gracefully on Optional Parameter Features
library_path:
- software-engineering
- languages
- cpp
- templates
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- templates
- policy_based_design
- instantiation
- interface_design
cross_links:
- rel: related_to
  target_object_id: PAT_lift_each_varying_design_decision_to_a_parameter
- rel: related_to
  target_object_id: PAT_program_to_a_templates_implicit_interface
- rel: related_to
  target_object_id: PAT_use_template_metaprogramming
- rel: related_to
  target_object_id: AP_design_a_customization_point
reference:
  source_title: 'Modern C++ Design: Generic Programming and Design Patterns Applied'
  author: Andrei Alexandrescu
confidence: high
references: []
variants: []
---

# Let a Class Degrade Gracefully on Optional Parameter Features

## Pattern Rule
**IF** a template parameter supplies capability beyond the minimum the class requires, and you want the class to offer something built on that capability
**THEN** constrain the extra member on that capability so it participates only for arguments that provide it, while the class itself requires only the minimum contract.

## Do
- State the contract in two layers: what every argument must supply, and what an argument may additionally supply along with what the class will then offer.
- Express the richer capability as a named concept or a focused `requires` expression, then place that constraint on the extra member.
- Let the extra members a parameter carries reach clients directly, where public inheritance already puts them — clients who chose that parameter get the richer interface without the class mediating it.
- Where a client later switches to a leaner argument, expect the extra member to be unavailable at the call boundary with a failed constraint rather than an instantiation error from inside its body.

## Don't
- Don't require the full capability from every argument so the class always compiles. That forces every lean implementation to supply members that do nothing, which is the interface bloat the parameters were separated to avoid.
- Don't rely on delayed instantiation as the public contract. It can keep an unused body from failing, but it leaves the capability implicit and produces deeper diagnostics when a client does call it.
- Don't leave the optional part undocumented and let clients discover it by compiler error. The two-layer contract is the interface, and only its lower layer is enforced.

## Checklist
- Does the class compile and work when given an argument supplying only the minimum?
- Does the extra member participate only for clients whose argument satisfies its declared constraint?
- Is the optional capability written down, including what the class offers in return for it?
- When a lean argument is substituted, do the errors land at the use sites rather than inside the class?

## Notes
Delayed instantiation is what makes one class template able to span arguments from minimal to rich, but a C++20 constraint turns that implementation fact into an interface. The class can be instantiated with the minimum capability, while the richer member is present only when its own requirement is satisfied.

The result is worth naming: a class can offer more than its contract requires without penalising the implementations that supply only the contract. The alternative designs both fail — demanding the richer capability everywhere forces empty members onto lean implementations, and offering nothing extra wastes what a rich argument brought.

No runtime or compile-time branch is needed when the only consequence of a missing capability is that one member is unavailable. A member constraint expresses exactly that and gives tools and diagnostics a contract they can inspect.
