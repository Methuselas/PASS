---
object_id: PAT_end_rust_iterator_pipelines_with_the_needed_consumer
object_type: pattern
name: End Rust Iterator Pipelines with the Needed Consumer
library_path: [software-engineering, languages, rust, iterators]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_iterate_rust_collections_without_manual_index_bounds
tags: [rust, iterators, laziness, pipelines, collect]
cross_links:
- rel: related_to
  target_object_id: PAT_choose_lazy_or_eager_by_how_often_the_result_is_needed
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# End Rust Iterator Pipelines with the Needed Consumer

## Pattern Rule
**IF** a Rust iterator chain uses adaptors such as `map`, `filter`, `zip`, or `skip`
**THEN** finish it with the consumer that expresses the required result or side effect, because adaptors are lazy and do no iteration by themselves.

## Do
- Build the chain as a description of selection and transformation, then choose a consumer such as `collect`, `sum`, `find`, `fold`, `for_each`, or a `for` loop from the result the caller needs.
- Preserve laziness when the caller should decide how much of the sequence to consume; return an iterator instead of materializing a collection when the API can express that lifetime and concrete type cleanly.
- Use type context or an explicit result type when `collect` could build more than one collection.
- Read the chain in stages and extract a named function or intermediate binding when the closure or ownership changes stop being obvious.
- Benchmark the optimized build with representative data when performance determines the choice between equivalent forms.

## Don't
- Don't create an adaptor chain and discard it; its closures will not run.
- Don't call `collect` by habit when a scalar, first match, boolean, side effect, or still-lazy iterator is the actual contract.
- Don't claim an iterator spelling is inherently faster than a loop from source inspection or one historical benchmark.
- Don't compress a pipeline until its item ownership and transformation order become harder to verify than an explicit loop.

## Checklist
- Which operation actually consumes the iterator?
- Does that consumer produce exactly the caller's required shape?
- Could the API remain lazy and avoid materializing unused items?
- Are closure behavior, reference levels, and adaptor order readable at each stage?
- If speed is the deciding factor, was the release artifact measured on representative inputs?

## Notes
Iterator adaptors describe pending work. Consumption drives repeated calls to `next`, often allowing the compiler to inline and fuse the stages without intermediate collections. That optimization opportunity does not make every chain faster or clearer; the durable rule is to express the needed result, preserve laziness only where it is useful, and measure claims that matter.

