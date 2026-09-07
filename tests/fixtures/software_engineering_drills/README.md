# Software Engineering Drill fixtures

These are repository-only administration fixtures. They are not cards, canon,
or evidence that a model has a capability. The portable rules live in
`PASS/docs/PASS_CONSUMPTION.md`.

Each fixture keeps the taker packet separate from the grader packet. A fixture
may include reference answers solely to self-test its deterministic grader; those
answers must never be exposed to a real taker before its answer is frozen.

Inspect the live inventory without creating a second index:

```powershell
python PASS/tools/drill_inventory.py --package software-engineering --format markdown
```

The first fixture is
`cpp/templatized-base-name-access/`, derived from
`DRILL_fix_templatized_base_class_name_access`. It deliberately exercises both
successful compilation and expected compilation failure without launching a
control arm or creating capability evidence.
