# Fix access to a name in a templatized base class

## Practice Task

The starter contains a derived class template that calls an inherited function
from its base class template and does not compile. Make it compile in three
different ways.

## Setup

Use a standards-conforming C++17 compiler. Copy `starter/broken.cpp` into four
answer files named:

- `this_prefix.cpp`
- `using_declaration.cpp`
- `explicit_qualification.cpp`
- `missing_specialization.cpp`

Also create `RANKING.md` and an `evidence/` directory.

## Instructions

1. Compile `starter/broken.cpp` unchanged and retain the compiler diagnostic in
   `evidence/broken.txt`.
2. Fix the call with a `this->` prefix in `this_prefix.cpp`; compile and run it.
3. Fix the call with a `using` declaration in `using_declaration.cpp`; compile
   and run it.
4. Fix the call with explicit base-class qualification in
   `explicit_qualification.cpp`; compile and run it.
5. In `missing_specialization.cpp`, add a base specialization that omits the
   inherited name. Compile it, retain the diagnostic, and identify where the
   compiler reports the failed lookup.
6. In `RANKING.md`, rank the three successful fixes, state the condition that
   selects each, and explain the virtual-dispatch consequence of explicit
   qualification.

Produce these files and machine outputs. Describing what they would contain does
not complete the Drill.
