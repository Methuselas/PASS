---
object_id: PAT_choose_inference_models_by_task_conformance_before_speed
object_type: pattern
name: Choose Inference Models by Task Conformance Before Speed
library_path:
- software-engineering
- ai-systems
- performance
stage_binding: 0 design
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: none
tags:
- ai
- inference
- benchmarking
- correctness
- performance
cross_links: []
reference:
  source_title: The Hot New AI Model Nobody's Heard Of, But We Already Use the Concept
  author: Rob Braxman Tech Deep Dive
confidence: medium
references: []
variants: []
---

# Choose Inference Models by Task Conformance Before Speed

## Pattern Rule
**IF** several models or inference architectures can serve the same software decision and a smaller or faster candidate is attractive
**THEN** first test whether each candidate reliably follows the actual decision logic and output contract, eliminate candidates that fail that task, and compare latency, throughput, and cost only among the models that remain correct enough for the application
**ELSE** if all candidates already satisfy the same verified task contract, optimize among them on measured operational cost and performance.

## Do
- Build evaluation cases from the real decision structure, including nested branches, ambiguous boundaries, and cases that exercise every route the production prompt can take.
- Treat task conformance as a gate before throughput. A model that answers faster but breaks the routing logic is not a performance improvement for that system.
- Compare model capability separately from output mechanism. Faster decoding, a constrained decoder, or a classifier-shaped API does not by itself supply reasoning the underlying model lacks.
- Record the smallest model that passes the required behavior rather than assuming parameter count, benchmark rank, or architecture predicts production suitability.
- Re-run conformance tests when prompts, routing logic, quantization, serving settings, or model versions change.

## Don't
- Don't choose a model from tokens-per-second alone.
- Don't infer that a model which succeeds on simple labels will also follow nested conditional routing or coupled decision rules.
- Don't treat a specialized output layer as a substitute for understanding the task encoded in the input.
- Don't keep an oversized model by habit either; once smaller candidates pass the same task gate, measure whether they provide a better operational tradeoff.

## Checklist
- Does the evaluation exercise the full production decision tree rather than only easy examples?
- Which candidates fail the task contract before performance is compared?
- Are model capability and serving/output mechanism being evaluated as separate variables?
- Is the selected model the smallest or cheapest candidate that still meets the required correctness threshold?
- Will the conformance suite run again after model, prompt, quantization, or router changes?

## Notes
Performance selection is constrained optimization: correctness defines the feasible set, then speed and cost choose among that set. Reversing that order produces attractive benchmarks for systems that do the wrong work quickly.

A smaller model can be faster in raw inference yet fail nested router logic that a larger model handles correctly. The durable lesson is not that a particular parameter count is required; it is that output architecture and throughput do not compensate for a model that cannot execute the application's decision contract.
