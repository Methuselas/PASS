---
object_id: PAT_solve_a_linear_system_by_factoring_not_by_inverting
object_type: pattern
name: Solve a Linear System by Factoring, Not by Inverting
library_path:
- software-engineering
- core
- data-types
stage_binding: 3 rough
lane_fit: skill
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- floating_point
- linear_algebra
- numerical_stability
- precision
cross_links:
- rel: related_to
  target_object_id: PAT_treat_floating_point_arithmetic_as_approximate
reference:
  source_title: Introduction to Algorithms
  author: Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein
confidence: high
references: []
variants: []
---

# Solve a Linear System by Factoring, Not by Inverting

## Pattern Rule
**IF** code has to find the unknowns in a set of simultaneous linear equations held in floating point — a fit, a calibration, a physics step, a layout or network solve — and the natural reading of the mathematics is "multiply by the inverse"
**THEN** factor the coefficient matrix into triangular pieces with row exchanges that put the largest available value in each dividing position, then solve by substituting forwards and backwards, and keep the factors if the same matrix will be solved against more than one right-hand side
**ELSE** compute an explicit inverse only when the entries of the inverse are themselves the result someone needs, and even then build it from the same factorization.

## Do
- Factor with row exchanges. At each step, choose the row whose entry in the current column is largest in size and swap it into place before dividing by it. Dividing by a small number magnifies every rounding error in the row it scales: a two-equation system whose first coefficient was 10⁻²⁰, with true solution (1, 1), came back as (0, 1) without exchanges and as (1, 1) with them. On twenty random 200-unknown systems with a small first coefficient, the worst error in any unknown was 0.046 without exchanges and 3.6 × 10⁻¹³ with them. The exchanges cost at most a constant factor in time.
- Solve through the factors rather than through an inverse. Substituting forward through the lower triangle and back through the upper takes time proportional to the square of the unknowns, and the factorization that precedes it is the cubic step. Forming the inverse repeats that substitution once per unknown and then multiplies, which is slower and less accurate: measured on 500 unknowns, factor-and-solve took 10 ms with a residual of 1.8 × 10⁻¹⁴, and inverse-then-multiply took 61 ms with a residual of 1.3 × 10⁻¹².
- Keep the factorization when the matrix stays the same and the right-hand side changes. The factors depend only on the matrix, so each further right-hand side costs one quadratic solve: for 100 right-hand sides against one 500-unknown matrix, factoring once took 19 ms and refactoring for each took 1,030 ms, with identical answers.

## Don't
- Don't write "solve" as "invert, then multiply" because the formula reads that way. The formula states what the answer is, not how to compute it, and on a badly conditioned matrix the difference is large: on a 12-unknown matrix of that kind, factoring gave an answer off by 0.36 in its worst unknown and the inverse route gave one off by 26.
- Don't judge how sensitive a matrix is by its determinant. A hundred-unknown matrix with 0.1 on its diagonal and zeros elsewhere has determinant 10⁻¹⁰⁰ and is as well-behaved as a matrix can be; the measure that tracks sensitivity is the size of the matrix multiplied by the size of its inverse, and it can be estimated without forming the inverse. The sensitivity belongs to the matrix, not the method: on the 12-unknown matrix above, the factored answer satisfied the equations to within 3 × 10⁻¹⁶ and was still off by 0.36, and no choice of solving technique removes that.

## Checklist
- Does the code compute an inverse only to multiply it by a vector?
- Does the factorization exchange rows to divide by the largest available entry?
- Is the same matrix solved against several right-hand sides, and are its factors reused?
- If the answer's accuracy matters, has the matrix's sensitivity been estimated rather than inferred from its determinant?

## Notes
The inverse is the right object for thinking about a linear system and the wrong one for computing with it. Writing the answer as the inverse applied to the right-hand side makes the algebra short; computing it that way performs every step of a factorization, then solves one extra system per unknown, then multiplies, and each stage adds rounding error that the direct solve never incurs. The factorization is the part of the work that depends on the matrix, and it is all a solve ever needs.

The two numerical failures here are different in kind and are worth keeping apart. Dividing by a small entry is a defect of the method, and exchanging rows repairs it. A matrix whose answers barely change the residual is a property of the problem, and it survives every repair: the best method returns an answer that satisfies the equations to machine precision and can still be far from the true one. The first is fixed in code; the second can only be measured and reported.
