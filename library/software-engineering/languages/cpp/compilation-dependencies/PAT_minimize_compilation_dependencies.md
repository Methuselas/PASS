---
object_id: PAT_minimize_compilation_dependencies
object_type: pattern
name: Minimize Compilation Dependencies with Handle or Interface Classes
library_path:
- software-engineering
- languages
- cpp
- compilation-dependencies
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- compilation_dependencies
- pimpl
- encapsulation
cross_links:
- rel: related_to
  target_object_id: PAT_support_nonthrowing_swap
- rel: related_to
  target_object_id: PAT_expose_clean_api_hide_implementation
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants:
- variant_id: VAR_publish_a_module_interface_instead_of_a_header
  variant_name: Publish a Module Interface Instead of a Header
  variant_basis: method_sequence
  difference_from_foundation: The foundation removes a dependency by hiding an implementation behind a pointer or abstract base, buying insulation with runtime indirection. This variant changes the publication boundary instead of the class representation. A C++20 module interface exports selected declarations and reachable template definitions through a toolchain-managed compiled interface, so importers do not textually include and preprocess the interface on every use. That can reduce repeated parsing and macro leakage without adding a pointer hop or virtual call. It does not promise a portable compiled-module format, stable ABI, or that importers never rebuild; those outcomes remain properties of the compiler and build graph.
  when_to_use: Use where the recompilation cost is driven by template-heavy headers, which the foundation's two remedies cannot address, or where macro and symbol leakage across a large header graph has become its own source of defects. It is also the better choice where the indirection the foundation introduces is genuinely unaffordable, since it removes the coupling without adding a pointer hop or a virtual call.
  when_not_to_use: Do not reach for it to decouple a single class whose implementation churns while its interface is stable — that is what the foundation is for, and restructuring a translation unit is a heavier change than introducing a handle. It is a build-system-visible decision requiring toolchain support and a module-aware build, so it is a poor fit for a codebase that must compile under toolchains you do not control. It also does not hide an implementation from a reader the way an abstract interface does; it controls what is published and recompiled, not what is visible in the source.
  absorbed_from_object_id: none
---

# Minimize Compilation Dependencies with Handle or Interface Classes

## Pattern Rule
**IF** a class exposes its implementation details in its header, forcing clients to recompile whenever the implementation changes
**THEN** depend on declarations rather than definitions — hide the implementation behind a pointer (the pimpl idiom, a Handle class) or behind an abstract Interface class with a factory — so clients recompile only when the interface changes.

## Do
- Give the class a single pointer to a forward-declared implementation class and forward its calls to that class (a Handle class), so the header needs only declarations.
- Or make the class an abstract Interface class of pure virtual functions, with a static factory returning a smart pointer to a concrete subclass.
- Ship headers in pairs — a declaration-only header and a definition header — and have clients include the declaration header rather than forward-declaring types themselves.
- Declare the special member functions in the header and define them in the implementation file when the handle is an exclusive-ownership smart pointer, even where the compiler-generated versions would be correct. Its deleter needs the complete type, and a compiler-generated destructor is inline in the header where that type is still incomplete — so accepting the default fails to compile at the client. A shared pointer does not have this problem, because its deleter is not part of its type and the complete type is captured when the pointer is constructed.

## Don't
- Don't include a definition where a declaration will do; declaring a function that passes or returns a type by value needs only that type's declaration, not its definition.
- Don't forward-declare standard-library types yourself. `std::string` is an alias of a `std::basic_string` specialization, and user declarations inside `std` are not a supported substitute for including or importing the owning standard-library facility.

## Checklist
- Does the header depend on definitions where forward declarations would suffice?
- Is the implementation hidden behind a pimpl pointer or an Interface class, so implementation changes don't recompile clients?
- Are declaration-only and definition headers provided as a pair?

## Notes
C++ couples clients to a class's implementation because the class definition carries private data whose types must be defined for the compiler to size the object. The `Person` example breaks that coupling two ways: a Handle class holds only a pointer to a forward-declared `PersonImpl` and forwards calls, or an Interface class exposes pure virtuals with a factory. Both cost an indirection and some memory and lose inlining, so use them while implementations churn and collapse to concrete classes when the cost is shown to matter. The essence is depend on declarations, not definitions.

`VAR_publish_a_module_interface_instead_of_a_header` attacks the same coupling by changing the unit of publication rather than the shape of the class. Where the two remedies above restructure a type so its definition stops appearing in client headers, a module leaves the type alone and gives importers a compiled interface rather than a textual include. Exported templates still need definitions reachable where the language requires them, but reachability through a module is not the same as reparsing a header in every importing translation unit. Modules also stop ordinary macros from being exported as part of the interface. These are build and isolation advantages, not guarantees that an implementation never rebuilds importers or that its compiled interface is portable between compiler versions. Use the variant only after verifying the project's compiler, dependency scanner, build system, and third-party boundary; keep pimpl or an abstract interface for a churning class when representation and ABI insulation are the actual need.
