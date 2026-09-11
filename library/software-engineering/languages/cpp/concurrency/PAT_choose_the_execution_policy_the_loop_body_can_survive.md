---
object_id: PAT_choose_the_execution_policy_the_loop_body_can_survive
object_type: pattern
name: Choose the Execution Policy the Loop Body Can Survive
library_path:
- software-engineering
- languages
- cpp
- concurrency
stage_binding: 4 final
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- concurrency
- parallelism
- algorithms
- performance
cross_links:
- rel: related_to
  target_object_id: PAT_decide_if_the_problem_is_worth_parallelizing
- rel: related_to
  target_object_id: PAT_check_for_memory_saturation_before_adding_threads
- rel: related_to
  target_object_id: PAT_do_not_create_a_thread_for_every_task
reference:
  source_title: 'The Art of Writing Efficient Programs: An Advanced Programmer''s Guide to Efficient Hardware Utilization'
  author: Fedor G. Pikus
confidence: high
references: []
variants: []
---

# Choose the Execution Policy the Loop Body Can Survive

## Pattern Rule
**IF** you are adding an execution policy to a standard algorithm call to make it run in parallel
**THEN** check the policy against what the callable actually does — anything holding a lock or otherwise unsafe to interleave rules out the unsequenced policy — and confirm by measurement that the sequence is long enough for parallelism to pay at all
**ELSE** where the sequence is short or the per-element work is trivial, the sequential policy is not a fallback but the correct answer, and it is what the call already does without a policy.

## Do
- Read the C++20 policies as four different permission sets. `std::execution::seq` prohibits parallel execution; `par` permits execution across threads; `par_unseq` additionally permits unsequenced execution within a thread; and `unseq` permits unsequenced execution without granting parallel execution. An algorithm call without a policy remains the clearest choice when no execution-policy behavior is needed.
- Treat any lock inside the callable as disqualifying an unsequenced policy. Interleaved invocations on one thread can attempt to acquire a lock before that same thread reaches an earlier release, causing deadlock; more generally, invoking vectorization-unsafe operations violates the policy's requirements.
- Establish the crossover with a benchmark rather than a rule of thumb, because it depends on three things at once: the sequence length, the cost per element, and the implementation. Thirty-two thousand elements with substantial per-element work scaled well; a thousand elements ran slower than sequential; and thirty-two thousand elements incrementing a double gained nothing at all.
- Expect the hardest algorithms to pay best. Sorting doubles — cheap comparisons, cheap swaps, and genuinely difficult to parallelize — showed strong speedup above about a thousand elements, which is a better return than a trivially parallel loop over the same data.
- Verify the implementation and build setup before promising parallel speedup. A standard-library implementation may depend on a separate parallel runtime, may use an internal pool, or may execute conservatively; toolchain documentation and deployment tests decide what is actually available.
- Check that the algorithm you want has an execution-policy overload. The set is intentionally different from the ordinary algorithm set: for example, `std::accumulate` has no such overload, while `std::reduce` was designed to permit reordered and parallel reduction when its operation satisfies the stronger requirements.

## Don't
- Don't assume an unsequenced policy is a free upgrade over a sequenced one. It permits an additional transformation that changes what the callable must tolerate, and a violation may compile cleanly before deadlocking or otherwise failing at run time.
- Don't parallelize a memory-bound loop and expect a gain. Incrementing every element of a large array is limited by memory traffic, and more threads share the same path to memory rather than adding capacity.
- Don't use a policy on short sequences inside a hot loop without measurement. Dispatch, partitioning, synchronization, and runtime scheduling costs can dominate when the work is small, even when an implementation reuses worker threads.
- Don't assume parallel algorithm calls coordinate resource use the way your application needs. Multiple calls can compete for the same processors and memory bandwidth; the standard policy API does not provide an application-level processor budget.
- Don't skip thread safety because the algorithm is standard. A policy makes the calls concurrent; whatever the callable touches is subject to the same rules as any other threaded code.

## Checklist
- Does the callable take a lock, or do anything else that breaks if interleaved within one thread?
- What is the measured crossover length for this algorithm with this per-element work?
- Is the loop limited by computation or by memory traffic?
- Is this call inside something that runs often, repeatedly paying dispatch and synchronization costs?
- Does the algorithm have an execution-policy overload at all, and has the chosen toolchain/runtime configuration been tested?

## Notes
The distinction between sequenced and unsequenced permission is easy to under-read because vectorization sounds like something the compiler does anyway. What an unsequenced policy adds is permission to interleave the *callable's* operations, which is a statement about the code you wrote rather than merely about the loop. That is why the safety requirement lands on the body.

The setup cost that makes short sequences lose is an implementation property rather than a requirement of the standard. It may come from dispatching work to an existing pool, creating workers, partitioning the range, synchronizing completion, or some combination. That is why the crossover changes between library versions and targets and has to be measured rather than inherited from an example.

Where these algorithms are strong is worth stating alongside the caveats. Given enough data, they deliver good speedups on algorithms that are awkward to parallelize by hand, with no concurrency code of your own to get wrong — which is a much better trade than it appears from a list of restrictions.

One consequence of naming a policy at all has nothing to do with which policy you name, and it is the least expected thing here: it changes what happens when the callable throws. A call without a policy propagates the exception normally, so a handler around the call catches it. A call *with* a policy does not — an exception escaping the callable calls the terminate handler, which by default aborts the program. That applies to the sequential policy too, so adding the policy that promises to change nothing about how the algorithm runs still changes how it fails. Any callable that can throw needs to catch inside itself before this is used, and code being converted to policied calls should be checked for handlers that are about to stop working.
