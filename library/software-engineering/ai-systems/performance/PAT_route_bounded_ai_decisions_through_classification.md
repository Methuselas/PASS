---
object_id: PAT_route_bounded_ai_decisions_through_classification
object_type: pattern
name: Route Bounded AI Decisions Through Classification
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
- classification
- latency
- cost
- structured_output
cross_links: []
reference:
  source_title: The Hot New AI Model Nobody's Heard Of, But We Already Use the Concept
  author: Rob Braxman Tech Deep Dive
confidence: medium
references: []
variants: []
---

# Route Bounded AI Decisions Through Classification

## Pattern Rule
**IF** an AI-backed software decision can be stated as choosing among a fixed set of labels, producing a bounded score, or answering a binary question, and the path is sensitive to request cost or latency
**THEN** use a classification-shaped inference path whose allowed outputs are defined up front instead of asking a generative chat model to write free-form text and parsing that text back into a decision
**ELSE** keep a generative path when the task actually requires open-ended synthesis, explanation, or content whose valid answer space cannot be bounded in advance.

## Do
- Express the software decision in the smallest output space the consumer actually needs: a label, bounded score, or binary result.
- Define allowed outputs before inference so downstream code receives a constrained decision rather than prose that must be interpreted again.
- Treat latency and per-request cost as architectural inputs when the decision runs on every message, ticket, request, event, or user action.
- Preserve a generative path for tasks that genuinely need composition or explanation; classification is a different shape of work, not a universal replacement for generation.
- Include confidence or probability information when the classifier provides it and use that signal to decide whether downstream automation may proceed or should escalate.

## Don't
- Don't spend a full free-form generation call on a decision whose consumer only needs one of a few known outcomes.
- Don't create a text-generation step and then add a fragile parser merely to recover the discrete value the application needed in the first place.
- Don't assume a constrained output space makes the underlying judgment infallible. A classifier can still choose the wrong allowed label even when it cannot emit an out-of-schema string.
- Don't compare architectures only by model capability; high-frequency paths can be dominated by latency, throughput, and invocation cost.

## Checklist
- Can the required result be represented as a fixed label, bounded score, or binary outcome?
- Does the current implementation generate prose only to parse it back into a discrete value?
- Is the decision executed frequently enough that per-call latency or cost materially affects the system?
- Are the allowed outputs defined before inference and directly consumable by downstream code?
- Is there a clear fallback for low-confidence or genuinely open-ended cases?

## Notes
Classification and generation solve different interface problems. A chat-oriented model is optimized to produce sequences of tokens, while many software control decisions need only a small, explicit answer space. When that distinction is reflected in the architecture, the system can avoid paying for generation and reparsing on paths that never needed prose.

The important boundary is the shape of the required result, not the branding of a particular model. Examples include spam checks, urgency routing, department selection, and block/allow decisions. The transferable engineering move is to make bounded decisions look bounded all the way through the inference interface.
