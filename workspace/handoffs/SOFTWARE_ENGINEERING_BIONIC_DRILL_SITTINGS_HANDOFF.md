# Software Engineering — Bionic Drill Sittings Handoff

**Status:** continuation brief for a fresh session. Rewritten 2026-09-13, late evening.
**Release boundary:** workspace only. Never commit or ship this file.

## What this is

The C++ module's cards were compile-probed and repaired, and all seventeen C++ Drills and 9 Action
Protocols (APs) were updated. We are now **testing the updated Drills by having a local model take them
blind**. The point is to find defects in the Drills, not to score the model. Two kinds of run, never
mixed:

1. **Blind Drill sitting (current work).** The taker gets only the Drill cut before its Success Check,
   plus starter files and a build script. No skill, no repo, no card access. This tests whether the
   Drill's Instructions produce what its Success Check grades.
2. **Skill-loaded run (later).** The taker gets the SkillForge release and a task whose answer the skill
   doesn't already hold, ideally real code (`PASS/docs/SOFTWARE_CARD_FIELD_TESTS.md`). Not started.

Governing rules: `PASS/docs/PASS_CONSUMPTION.md`, sections "Taking a drill", "Optional model-neutral
Drill runner" and "Software-engineering Drill runs". Read those sections, not the whole document.

**Repo state (2026-09-14 23:15):** PASS `38dcbaa` (1.0.0-beta.23), committed, **not pushed** (user is holding the push; `44b6968` beta.22 is also unpushed, so `main` is 2 ahead). Events through `SE_EV_0110` landed; memory holds 294 events across 4 stores. SkillForge Software Engineering was last rebuilt (`e529ca9`) before beta.21, so it still ships the
pre-repair derived-copy, copy-assign and interface Drills; rebuild when the user asks.

## Taker setup (keep identical for every sitting)

- **Hardware:** RTX 4090, 24 GB.
- **Model — corrected 2026-09-14 from Bionic's server logs.** Every graded sitting (2026-09-13) actually
  ran `Qwen3.8-27B-TTURBO-Fable-C-Fusion-709-L-Uncen-NM-DAU-NEO-MTP-Q4_K_M.gguf` (15.66 GB) **with**
  the `mmproj-F32.gguf` vision projector, `n_slots = 4`, `n_ctx_slot = 160000`, `kv_unified = true`,
  on the LM Studio CUDA 12 llama.cpp engine **2.37.0**. No Q5_K_M file ever existed on this machine;
  the earlier "Q5_K_M, 18.2 GB, 32K, no mmproj" was wrong, and it was copied into events
  `SE_EV_0089`–`0097` (landed), the `0098`/`0099` candidates and the field notes. Corrected by
  `SE_EV_0105` (landed in beta.22).
- **Engine trap:** LM Studio auto-installed engine 2.38.0 on 2026-09-14 at 16:21, a minute before the
  model loaded. On 2.38.0 generation starts at ~55 tok/s and collapses to under 1 tok/s within a few
  minutes of a sitting (llama-server showed 2.6 GB spilled into shared system RAM). On 2.37.0 the same
  load ran 800+ replies at a median 55 tok/s. Keep the engine pinned at 2.37.0, and check
  `nvidia-smi` plus `\GPU Process Memory(*)\Shared Usage` for llama-server a few minutes into a sitting
  (the model loads on the chat's first message, and the collapse took 3–4 minutes to show).
- **Engine build:** 2026-09-13 sittings ran Bionic's **"CUDA 12 llama.cpp" (`nvidia-cuda12-avx2`) 2.37.0**.
  `interface-02` (2026-09-14) ran the plain **"CUDA llama.cpp" (`nvidia-cuda-avx2`) 2.37.0**, picked by
  mistake during the rollback. Both builds are llama.cpp release b10914 (commit `8172e6577`) and differ
  only in CUDA toolkit, so results stay comparable; record the build in that sitting's grade notes and
  switch Bionic back to the CUDA 12 build before the next sitting.
- **Corrected diagnosis (2026-09-14 evening):** a spill into shared memory is not itself the slowdown.
  The user reports about 2 GB spilled on 2026-09-13 on engine 2.37.0 at full speed; 2.38.0 spilled
  2.6 GB and collapsed below 1 tok/s; back on 2.37.0 about 1 GB spills and generation runs 48–105
  tok/s (avg 91). The factor that tracks the collapse is engine 2.38.0, most likely because it placed
  hot-path memory where Windows demoted it. Untested beyond that; keep the engine pinned at 2.37.0 and
  judge a sitting by tok/s in the server log, not by the shared-memory counter alone.
- **2.38.0 retest and memory findings (2026-09-14, 22:13–22:34, not a sitting):**
  - The user reloaded on 2.38.0 changing one setting at a time (Task Manager GPU memory, Brave hardware
    acceleration off for all three): original 23.9 GB → **mmap on 23.2 GB** (spill down to 0.4 GB) →
    **Max Draft Tokens 3→2: 22.7 GB**. Per process on the last load: llama-server 21.88 GB on the card
    + 0.36 GB shared (2.37.0 load of 18:13, mmap off, draft 3: 22.46 + 1.03).
  - The projector `mmproj-F32.gguf` (1.84 GB) is loaded and counted; LM Studio's 18.65 GB model size is
    weights 16.81 + projector 1.84. Text sittings don't use it; the base Qwen3.8's `mmproj-F16` is 0.93 GB.
    Not changed.
  - Long test on that last load (novel draft from two story treatments): 24 replies, 25.9K tokens,
    6.3 minutes of generation, context to 67K; long replies at 63–71 tok/s; spill fixed at 0.36 GB;
    **no collapse**. The afternoon collapse (2.6 GB spilled) appeared within 3–4 minutes.
  - Not attributed: the passing run differs from the collapse in engine state, mmap, draft tokens and
    Brave. Speed isn't comparable to the 2.37.0 sittings (67K vs ≤37K context, draft 2).
  - None of mmap, draft tokens or the projector changes the text produced; record whichever is used in
    each sitting's grade notes.
  - **Compaction is not guaranteed.** The user reports Bionic compacting like Claude Code and Codex
    (seen on vanilla Qwen3.8), but on this load at 22:38 the conversation went 75.7K → 83.3K → 92.6K and
    the next request (97,345 tokens) was refused twice by llama-server: "request exceeds the available
    context size (96000 tokens)". No compaction happened first. Speed held at 61–65 tok/s up to 92.6K;
    the stop was the context limit, not the engine.
  - **Saved load settings are not what the records assumed.** Bionic's per-model config
    (`~/.lmstudio/apps/bionic/.internal/user-concrete-model-default-config/DavidAU/.../...Q4_K_M.gguf.json`,
    last modified 2026-09-14 22:40) holds: context-cache K and V **`q4_0`**, **temperature 1**, top-k
    20, min-p 0, repeat penalty 1, context 96000, autoFit on, offload ratio 1, mmap on, draft max 2.
    The user confirmed these (with mmap off and draft 3) were the settings of every sitting; the earlier
    "temperature 0.6" was wrong (see Settings below). Neither the session store nor the server log records
    sampling or cache settings per sitting, so from the next sitting on copy this config file into
    `records\<sitting>-load-config.json` at freeze time.
  - Bionic's "optimize for my hardware" (22:41 load) launched with `--fit on --fit-ctx 160000` and no
    forced GPU layers: llama-server used 12 CPU threads flat out (layers on CPU), generation fell to
    16–22 tok/s, later 9.5 tok/s as context grew, 20.07 GB on the card + 0.53–0.6 GB shared, 3.2 GB
    of the card left unused. It ignored the 96K setting and chose 160K itself. Never use it for sittings.
  - Final clean run, auto-optimize off (22:51–22:58; `--ctx-size 96000 --n-gpu-layers 999999`, mmap,
    draft 2, `q4_0`, 2.38.0): one-book novel draft, 17 replies, 21.9K tokens, 5.5 minutes of generation,
    context 14K → 46K, long replies 55–76 tok/s, 0.36 GB shared, no context errors, no collapse.
    Combined with the 22:13 run: about 11.8 minutes of generation on 2.38.0 with this setup, no collapse.
  - **Head-to-head at identical settings** (mmap on, draft 3, 96K, all GPU layers, `q4_0`; same prompt,
    one-book treatment; verified from the running process): 2.37.0 23:04–23:17, 19 replies, 30.6K tokens
    in 7.6 min, long replies 57–78 tok/s (median 68), peak context 63.6K. 2.38.0 23:19–23:27, 42
    replies, 26.4K tokens in 6.2 min, long replies 65–74 tok/s (median 74; one 12,457-token reply at 74),
    peak context 65.0K. Both 22.46 GB + 0.36 GB shared, no context errors, no collapse. No measurable
    difference; the sampled run-to-run variation (reply count, context; the prologue was skipped in runs on both engines and kept in one) is
    larger than any engine effect. Sittings stay on 2.37.0 for continuity.
  - For sittings: peak so far is 28–37K of 96K. Check the server log's peak `n_tokens` for every
    sitting. A sitting that compacts may lose `task.md` or earlier observations; one that hits the hard
    limit simply stops. Record either in the grade notes; a hard stop before the task is done is a
    harness failure (invalid), not evidence.
- **Context lowered to 100K on 2026-09-14** (from 160K), to stop the spill after the rollback. Given the
  corrected diagnosis it was probably unnecessary, but it is harmless. This
  does not affect comparability: from the server log's per-request token counts, every 2026-09-13
  sitting peaked at no more than ~31K tokens of context (upper bound; largest `copy-assign-01`), and no
  single prompt exceeded 7.6K. Record the context value in each new sitting's grade notes.
- **`bionic-memory` files stay on disk when the skill is disabled.** The user's skill (a one-file
  `SKILL.md`, copy at `D:\bionic-memory.zip`) keeps an index plus one-fact files under
  `~/.bionic-memory/memory/` (`global\` and `Project\<path-key>\`, e.g. `D--Repos-PASS`) and auto-saves
  without asking. Those PASS notes are readable by any sitting shell command even with the skill off:
  reject commands touching `~/.bionic-memory`, and list it with timestamps in every exposure check.
- **Compaction evidence (2026-09-13 log):** on 160K loads, six conversations reached 141–154K and dropped
  to 7–22K (compaction at ~88–96% full), no context errors. The 2026-09-14 hard stop was on a 96K load,
  where one chapter batch added ~9K. Not yet attributed to the model; the deciding test is the two-book
  novel prompt on vanilla Qwen3.8 at 96K with identical settings.
- **Non-sitting chats share the sitting project.** The user's novel-drafting chats (2026-09-14 evening)
  ran in the same Bionic project (`d49037d8`) as the sittings, and Bionic copies attached files into
  `~/.lmstudio/scratchpads/<id>\` (scratchpad `ar` holds `Book 1 - Medusa.md`). Nothing there is
  answer-bearing for a Drill, but it widens what a stray scratchpad or workspace command could see: keep
  rejecting those commands, and list both locations with timestamps in each exposure check.
- **Vision projector (2026-09-14, 23:30–23:40, not a sitting).** GGUF metadata shows the Turbo's
  `mmproj-F32` and the base Qwen3.8's `mmproj-Qwen3.8-27B-BF16` are the same projector (`qwen3vl_merger`,
  27 vision blocks, width 1152, 768 px, patch 16, projection 5120) at different precision; both models
  have embedding length 5120, so they are interchangeable. Per llama-server process at identical
  settings (2.38.0, mmap, draft 3, 96K, `q4_0`): Turbo + F32 22.46 GB on the card; vanilla + BF16
  21.61 GB; **Turbo with no projector 20.50 GB** (2,743 MiB free), all + 0.36 GB shared. The user
  moved `mmproj-F32.gguf` out of the DavidAU folder, so the Turbo now loads text-only (no `--mmproj`).
  Text output is unaffected; record the projector state in the next sitting's grade notes, and confirm
  the running engine is back on 2.37.0 before it (this test ran on 2.38.0).
- **Bionic doesn't always apply changes.** It claims to hot-reload, but an engine or load-setting change
  takes effect only after a full model reload (it shows a "reset your model" notice at the top when one
  is needed). On 2026-09-14 a switch to 2.38.0 left the 2.37.0 process running until the user retried.
  Before every sitting, after the model loads on the chat's first message, read the running
  `llama-server.exe` path and command line (`Get-CimInstance Win32_Process -Filter
  "Name='llama-server.exe'"`: engine folder, `--ctx-size`, `--n-gpu-layers`, `--load-mode`,
  `--spec-draft-n-max`, `--cache-type-k/v`, no `--fit`) and record them in the grade notes. The
  settings screen is not evidence.
- **Sitting load from 2026-09-14 23:04 on (user's choice, verified from the llama-server command line):**
  CUDA 12 llama.cpp **2.37.0**, `--ctx-size 96000 --n-gpu-layers 999999`, no `--fit`, **`--load-mode
  mmap`**, **`--spec-draft-n-max 3`**, cache K/V `q4_0`, `mmproj-F32` still loaded. 22.46 GB on the card
  + 0.36 GB shared, 774 MiB free. Auto-optimize off. Sampling unchanged (below). Every sitting before this
  ran with mmap off; record the mmap change in the first grade notes after it. It doesn't change output.
- **Settings (corrected 2026-09-14 from Bionic's saved model config, user-confirmed as the settings every
  sitting used):** temperature **1.0**, top-k 20, min-p 0, repeat penalty 1 (off), presence penalty 0,
  context-cache K/V **`q4_0`**, autoFit on, GPU offload ratio 1, CPU threads 12, **mmap off**, **draft max
  tokens 3** (mmap and draft 2 were first set at 22:09–22:13 on 2026-09-14, after the last sitting),
  thinking on, reasoning mode identical every time. The earlier "temperature 0.6" was wrong and was
  never checked against the config. llama.cpp logs "failed to fit params to free device memory" on every load of this
  configuration; that warning is normal here and not itself the slowdown.
- **Harness:** LM Studio Bionic. **A new chat for every sitting**, pointed at that sitting's folder only.
  Reusing a chat invalidated `const-correct-01` (started in the previous sitting's chat by mistake;
  rerun clean as `const-correct-02`).
- **Shell mode must be Manual review.** It reverted to Auto review once; check it every session.
  Reject any command whose target *or working directory* is outside the sitting folder
  (`except-safe-01` had two harmless exit-127 calls with workdir `/`).
- **No skills during blind sittings.** The SkillForge skill has been removed. `bionic-memory`
  (`~/.lmstudio/skills/bionic-memory`) must stay disabled under Settings → Skills; its memory holds PASS
  project notes, including one telling the model it's the Drill subject.
- **Prompt, exactly:** *Read task.md and complete it.* Nothing else.
- **One sitting runs at a time.** Preparing the next packet while one runs is fine, and grading overlaps
  the next run. The user isn't a programmer and may ask what terms mean; explain plainly.

## Folders

- **`D:\DrillRuns\<sitting>\`**: what the taker sees — `task.md`, `starter\`, `build.bat`, empty
  `answer\`. Never put a key, card, probe or note here. `toolcheck\` and `pilot-01\` are done; leave them.
- **`D:\DrillControl\`**: private controller side. Never point Bionic at it.
  - `scenarios\<sitting>\`: `scenario.md` and `starter\` source for each packet.
  - `runs\<sitting>\`: runner folders (`controller\`, `student\`, `grader\`, candidate event).
  - `templates\build.bat`: MSVC 19.50, `/std:c++20 /permissive- /W4`, output to `out\` beside the source,
    compiler messages saved to `out\<name>.build.txt`. **Fixed 2026-09-13:** extra options come from the
    raw command line, so options containing `=` survive; an AddressSanitizer build copies
    `clang_rt.asan*.dll` into `out\` so the exe runs outside the build environment. The previous version
    is kept as `build.v2-equals-split.bat.old`.
  - `templates\scenario-template.md`: neutral scenario text. Current packets also say extra compiler
    options are accepted after the `/W4` default.
  - `records\`: `<sitting>-taker-packet.txt` and `<sitting>-taker-freeze.txt` hash lists.
  - `tools\sessions.py`, `tools\session_exposure.py`: exposure-check scripts.

## Sitting procedure

1. **Prepare.** Write `scenarios\<sitting>\starter\...` (the class the Practice Task describes; leave
   anything the Setup or Instructions ask the taker to build — counters, throwing copies, probes — to
   the taker) and `scenario.md` from the template: files, how to build, where work goes, no hints. Then:

       python PASS/runtime/skillforge_drill.py prepare --drill <DRILL_ID> --cut before-success-check --scenario <scenario.md> --out D:\DrillControl\runs\<sitting>

   Test the starter with `templates\build.bat` in a scratch folder, not the taker folder. If the Drill's
   claims depend on the starter's shape, check the shape keeps every claim reachable (derived-copy lesson).
2. **Assemble** `D:\DrillRuns\<sitting>\`: `task.md` from `runs\<sitting>\student\`, the template
   `build.bat`, the starter, empty `answer\`. Grep `task.md` for `Success Check|Common Failures|DRILL_|PAT_`
   (must be clean). Record hashes in `records\<sitting>-taker-packet.txt`.
3. **The user runs it.** Don't open the folder until they say it's done.
4. **Freeze before reading.** Hash the taker folder into `records\<sitting>-taker-freeze.txt`, confirm
   packet files unchanged, copy `answer\` to `runs\<sitting>\student\answer`, run
   `freeze --run ... --answer ...\student\answer`, then `reveal`.
5. **Exposure.** Copy `~/.lmstudio/apps/bionic/projects/*/.internal/ng-sessions.sqlite*` to scratch
   (never touch the live store).
   - `sessions.py <db>` finds the session; it truncates long calls, so also extract **every path and
     workdir argument** straight from `entry_json` with a regex.
   - `session_exposure.py <db> <session-prefix>` must show `manualReview` and no skill, memory, library or
     repo text. A tool-less session with 4 entries is Bionic's auto-naming pass.
   - Toolchain probes (`where cl`, testing for `vcvars64.bat`) are not exposure. A real reach outside the
     folder means `validity: invalid` with the reason; it never counts as evidence, no automatic retry.
6. **Grade.**
   - Rebuild and rerun every answer file from the frozen copy (plain, and under
     `/fsanitize=address /Zi` where the Drill uses one), run from a clean PATH with a timeout.
   - **Probe every Drill claim the Success Check grades with your own small programs.** This found both
     repairs.
   - When the taker overwrote a stage, recover earlier outputs from the session store's tool results.
   - Fill `grader\grade.json` (`grader_relation: separate`; criterion results pass/partial/fail/not_tested;
     scores strong/adequate/weak/failed/unproven). Then
     `finalize --run ... --event-id SE_EV_<next> --date <today> --task "..."`. It never touches `memory/`.
7. **Classify before touching a card.** Only a Drill defect justifies an edit: a step that doesn't ask for
   something the Success Check grades, a check any attempt passes, or a false claim. Taker, harness,
   scenario and toolchain failures don't. Write a field note in
   `workspace/field-tests/<date>_<sitting>_bionic_sitting.md`. Repairs need the user's approval; run the
   PASS-authoring validators and a cold third read.
8. **Land in batches** when the user says: `memory.py append --domain software-engineering --json <file>`
   for each candidate in order, then `memory.py validate`, `validate.py`, `verify_references.py`,
   `build_index.py`, the full unittest suite (about 7 minutes), version bump (`VERSION`, both `README.md`
   mentions, dated `CHANGELOG.md`), and a commit with notes (changed, preserved/excluded, validation,
   known issues). In PowerShell, write the message to a scratch file and use `git commit -F <file>`;
   `-F -` with a here-string fails. Push only when asked.

## Results

| Sitting | Drill | Result | Event |
|---|---|---|---|
| toolcheck | — | harness works | — |
| pilot-01 | old test fixture of templatized-base | valid; 5/5 on the fixture, but called the unqualified call "a dependent name" and described dispatch instead of running it | none |
| templatized-base-01 | fix_templatized_base_class_name_access | valid, 6/6 | SE_EV_0089 (landed) |
| init-list-01 | convert_constructor_assignment_to_init_list | valid, 3 pass 2 partial 1 fail | SE_EV_0090 (landed) |
| const-correct-01 | add_const_correctness_to_a_class | **invalid**, reused chat | SE_EV_0091 (landed) |
| const-correct-02 | add_const_correctness_to_a_class | valid, 4 pass 2 partial | SE_EV_0092 (landed) |
| derived-copy-01 | complete_a_derived_class_copying_functions | valid, 6 pass 1 partial; **Drill defect, repaired** | SE_EV_0093 (landed) |
| copy-assign-01 | make_copy_assignment_self_and_exception_safe | valid, 4 pass 1 partial 1 fail; **Instructions gap, repaired** | SE_EV_0094 (landed) |
| raii-01 | refactor_manual_cleanup_to_raii | valid, 3 pass 3 partial | SE_EV_0095 (landed) |
| lock-copy-01 | choose_copying_behavior_for_an_raii_class | valid, 5 pass 1 fail | SE_EV_0096 (landed) |
| except-safe-01 | make_a_function_exception_safe | valid, 4 pass 3 partial | SE_EV_0097 (landed) |
| nvi-01 | apply_the_nvi_idiom | valid, 4 pass 2 partial | **SE_EV_0098 (candidate, not landed)** |
| is-a-01 | refactor_broken_is_a_to_composition | valid (worked in Bionic scratchpad/workspace; nothing reachable), 5 pass 1 fail | **SE_EV_0099 (candidate, not landed)** |
| interface-01 | redesign_interface_to_prevent_misuse | **abandoned**: engine auto-update to 2.38.0, <1 tok/s; record as invalid (harness) | no event yet — log invalid at next landing |
| interface-02 | redesign_interface_to_prevent_misuse | valid (CUDA 2.37.0 build, 100K ctx), 6 pass 2 partial; **Drill defect: "braced call" ambiguous** (per-argument braces needed; same wording in PAT_make_interfaces_hard_to_misuse); **repaired 2026-09-14, uncommitted**, needs a fresh sitting to confirm | **SE_EV_0100 (candidate, not landed)** |
| operator-new-01 | write_a_conforming_operator_new | valid (CUDA 2.37.0 build, 100K ctx; model not reloaded after the CUDA 12 switch), 4 pass 1 partial 1 fail (false "arrays fall back to scalar new"); watch item: "optional sized form" wording vs class-scope delete selection | **SE_EV_0101 (candidate, not landed)** |
| placement-01 | pair_a_placement_new_with_placement_delete | valid (CUDA 12 2.37.0, ctx 96000), **5/5 pass**; no Drill defect | **SE_EV_0102 (candidate, not landed)** |
| swap-01 | implement_nonthrowing_swap_for_pimpl | valid (CUDA 12 2.37.0, ctx 96000), 2 pass 4 partial (wrong baseline config; "reached" printed not measured; member swap never called); no Drill defect | **SE_EV_0103 (candidate, not landed)** |
| pimpl-01 | convert_a_class_to_the_pimpl_idiom | **invalid (tool)**: every Bionic shell call failed `spawn …\Git\usr\bin\bash.exe ENOENT` (bash exists; all calls had `workdir: null`, likely a missing default cwd), so nothing was built; every Drill claim confirmed by probe; no Drill defect; rerun needs a working shell and approval | SE_EV_0106 (landed, invalid) |
| derived-copy-02 | complete_a_derived_class_copying_functions (repaired) | valid (CUDA 12 2.37.0 load of 18:13, ctx 96000), 5 pass 2 partial (compiler silence never written down; "parallel bodies"); **repair confirmed**, no Drill defect | SE_EV_0107 (landed, beta.23) |
| copy-assign-02 | make_copy_assignment_self_and_exception_safe (repaired) | valid (CUDA 12 2.37.0 load of 18:13, ctx 96000), 4 pass 1 partial 1 fail (unique_ptr moves claimed generated, "d empty" printed not measured; copy-first cost asserted); **repair confirmed**, no Drill defect; grader saw three in-progress blobs at 19:36 (one-way, noted) | SE_EV_0108 (landed, beta.23) |
| interface-03 | redesign_interface_to_prevent_misuse (repaired) | valid (CUDA 12 2.37.0 load of 18:13, ctx 96000; taker read MSVC's `<chrono>` header, classified toolchain reference), 5 pass 2 partial 1 fail (aggregate raw call swapped out; enum cast never tried + false `Month(3)` claim; final design's rejection borrowed); **braced-call repair confirmed**; **Instructions gap: enum-cast bullet graded but no step asked for a cast** (interface-02 pass, interface-03 fail); **repaired 2026-09-14, user-approved, landed in beta.23 `38dcbaa`** (enum attempt now its own step, asks for the cast and what it holds; predefined-object Month moved to the next step; invalid-month bullet now requires the compiler's rejection recorded, from the cold third read); validators pass; other third-read findings left as pre-existing, listed in the field note; needs `interface-04` to confirm | SE_EV_0109 (landed, beta.23) |
| pimpl-02 | convert_a_class_to_the_pimpl_idiom | valid (CUDA 12 2.37.0 load of 18:13, ctx 96000; shell worked: one bash exit 127, then a 13-min wait on approval during the user's break, then powershell), 4 pass 4 partial; no Drill defect; **scenario issue: starter Person had no inline or constexpr members, so bullet 8 had nothing to lose — future pimpl starters need one of each** | SE_EV_0110 (landed, beta.23) |

Field notes: `workspace/field-tests/2026-09-13_*_bionic_sitting.md`. Candidate event JSON:
`D:\DrillControl\runs\<sitting>\candidate_training_event.json`.

**Repairs landed in beta.21 (each needs a fresh sitting to confirm):**
- `DRILL_complete_a_derived_class_copying_functions`: the base-member step needed a hand-written base and
  the move bullet a generated one. Practice Task now pins `Customer` as compiler-generated; the added
  member goes on the derived class.
- `DRILL_make_copy_assignment_self_and_exception_safe`: the throwing-copy step now also asks what happens
  when the target is destroyed (reading the naive target stops ASan before the double free).

**Watch items (no repair on one sitting):**
- templatized-base bullet 4: a stated reason no step asks for on its own (same shape as `SE_MEM_017`).
- const-correctness: the `mutable` concession bullet and the parameter bullet drew partials in both
  sittings.
- nvi lock step: "write down which case you are in" doesn't name the cases; the taker answered from
  re-entrancy, not from where overrides come from.

## In flight at handoff

- **`is-a-01`** is done and graded (5 pass, 1 fail: kept mutable iterators), candidate `SE_EV_0099`.
  **New harness trap it exposed:** the taker worked in Bionic's scratchpad
  (`~\.lmstudio\scratchpads\vm\...`) and the Bionic project `workspace\`, then copied into the sitting
  folder. Nothing answer-bearing was reachable, so it stayed valid, but from now on reject any command
  targeting the scratchpad or workspace, and include both locations in the exposure check (list them on
  disk with timestamps). The workspace has an empty `memory\` folder; keep `bionic-memory` disabled.
- **`interface-01`** (`DRILL_redesign_interface_to_prevent_misuse`): packet ready, not started. Starter is
  `Date(int month, int day, int year)`. Claims to probe: converting constructors pass the raw transposed
  call; aggregates reject raw but accept a wrong-order call with each argument braced (`Date({30},{3},{1995})`; whole-list braces are rejected); only `explicit` rejects both;
  `std::chrono::month{13}` compiles with `ok() == false`; a plain int doesn't convert to a month.
- **`operator-new-01`** (`DRILL_write_a_conforming_operator_new`): packet ready at
  `D:\DrillRuns\operator-new-01`, not started (hashes in `records\operator-new-01-taker-packet.txt`).
  Starter is a plain `Widget` with no allocation functions. Claims to probe: a self-uninstalling new-handler leads to
  `std::bad_alloc`; the aligned form honors alignment; which sized delete MSVC selects; an array goes to
  global `operator new[]`.
- **2026-09-14 afternoon state:** `interface-02` and `operator-new-01` graded (candidates `SE_EV_0100`,
  `SE_EV_0101`). The model was reloaded at 17:57 on **CUDA 12 llama.cpp 2.37.0** with
  `n_ctx_slot = 96000` (about 1 GB still in shared memory, speed normal).
  - **`placement-01`** (`DRILL_pair_a_placement_new_with_placement_delete`): **graded, 5/5 pass**,
    candidate `SE_EV_0102`; every claim below confirmed by probe.
    Starter `Widget` with placement `operator new(size_t, std::ostream&)` and only a normal delete; builds
    with C4291. Claims to probe: a qualifier-only near-match delete compiles, is never called and draws
    the same warning; removing the normal delete makes `delete p` fail to compile; ordinary, nothrow and
    buffer-placement `new` are all refused before the repair.
  - **`swap-01`** (`DRILL_implement_nonthrowing_swap_for_pimpl`): **graded, 2 pass 4 partial**,
    candidate `SE_EV_0103`; every claim below confirmed by probe. Single file, `Widget` in
    namespace `WidgetStuff` holding `std::unique_ptr<WidgetImpl>`, deep-copy copy operations, no moves.
    Claims to probe: with `noexcept` moves `std::swap` copies nothing and is nothrow-swappable, with
    copies only it copies and is not; unqualified swap and `std::ranges::swap` reach the ADL swap,
    qualified `std::swap` does not.
  - **`pimpl-01`** (`DRILL_convert_a_class_to_the_pimpl_idiom`): packet ready. **New harness:**
    `templates\build_project.bat <project folder>` configures a CMake project once with Ninja and MSVC
    (`/std:c++20 /permissive- /W4 /EHsc`), then builds incrementally with `-k 0` so every failing file is
    reported; output in `<project>\out\build.txt`, executables in `out\`. Tested: no-change build does
    nothing, touching `person.cpp` rebuilds only it and relinks, touching `date.h` rebuilds all three,
    new `clients\*.cpp` are picked up by glob, a broken client fails while the others still build.
    Starter `person-project\` has `include\person.h` (with `date.h`, `address.h`), `lib\person.cpp`, and
    clients `roster.cpp` (copy construct/assign) and `transfer.cpp` (move construct/assign). Grading needs
    the same harness to rebuild.
- **Remaining after those:** the held two (`restructure_a_class_that_locks_every_member`,
  `implement_traits_based_dispatch`).
- **LANDED 2026-09-14 in PASS `44b6968` (1.0.0-beta.22), committed, NOT pushed:** events
  `SE_EV_0098`–`0106` and the interface Drill + Pattern braced-call repair. Memory now holds 290 events
  across 4 stores. The notes below describe what that commit contained.
- **(Historical) landing preparation:** append in id order `SE_EV_0098`–`0103` from each
  `D:\DrillControl\runs\<sitting>\candidate_training_event.json`, then `SE_EV_0104` (interface-01,
  invalid, harness) and `SE_EV_0105` (setup correction superseding the Q5_K_M wording in `0089`–`0097`)
  from `D:\DrillControl\records\pending-events\`. All eight pass `memory.validate_event` with no
  duplicate ids. Training history is append-oriented (MEMORY_SCHEMA §6): never edit a landed line. The
  `0098`/`0099` candidates and their `grade.json` were corrected from Q5_K_M to Q4_K_M before landing.
  Also in that commit: the uncommitted interface Drill + Pattern "braced call" repair, and
  `SE_EV_0106` (pimpl-01, **invalid**, Bionic shell tool failure) from
  `D:\DrillControl\runs\pimpl-01\candidate_training_event.json`, appended after `0105`.
- **`pimpl-01` rerun (needs the user's approval):** use a fresh folder (`pimpl-02`) with the same packet.
  Before starting, confirm the Bionic shell runs a command in the new chat; if a call fails with
  `spawn …\Git\usr\bin\bash.exe ENOENT`, stop the sitting immediately rather than letting it continue
  without a shell.
- **Drill inventory by administration class:**
  `python PASS/tools/drill_inventory.py --package software-engineering --format json` (UTF-8 BOM; read with
  `utf-8-sig`).

## Lessons worth keeping

- **A starter shape can make a Drill's bullets contradict.** If no shape keeps every claim reachable,
  that's the defect (derived-copy).
- **A graded artifact the Instructions never ask for shows up in the card text.** Compare each bullet to a
  step before the sitting, not only after (copy-assign's double free).
- **Takers fake evidence in recognizable ways:** a "second thread" that is the same thread, a stale build
  log from a rewritten file, a throw staged in `main` instead of the function under test, a move "tested"
  by printing a value that can't reveal a copy. Read the source behind every recorded output.
- **Writing "17 C++ Drills" reads as "C++17".** Write "seventeen".

## Traps already hit

- **A global Bionic skill must sit at `~/.lmstudio/skills/<name>/SKILL.md`**, folder name equal to the
  front-matter `name`. The SkillForge release was installed one level too deep and almost certainly never
  registered. For skill-loaded runs, install through Bionic's installer and confirm it's enabled.
- **Bionic triggers a skill only if the model decides to read it,** or the user types `@<name>`. Record
  which mode a skill-loaded run used.
- **`tests/fixtures/.../grader/verify.py` writes evidence into the answer folder by default,** overwriting
  the taker's. Pass `--evidence-dir` elsewhere.
- **In this machine's PowerShell tool, `cmd /c "cd /d X && build.bat"` did not find the script;** call
  `build.bat` by its full path.
- **The PowerShell tool's safety guard blocks `Remove-Item`** when the command text also contains a
  `C:\Windows` string (e.g. a clean PATH). Build into fresh folders instead of deleting.
- **PowerShell 5.1 `Get-Content` shows UTF-8 em dashes as `â€”`.** Display only.
- **Edit and Write refuse a file changed since it was read.** Other chats edit these handoffs too; reread
  and merge rather than overwrite.

## Related, separate work

- **Python track:** `workspace/handoffs/SOFTWARE_ENGINEERING_PYTHON_TRACK_HANDOFF.md`. Different
  workstream; don't mix them in one session.
- **Core sweep:** on hold until other language modules exist.

## Standing rules

- **AP means Action Protocol.**
- **Commit and push only when the user says.** Every commit advances `VERSION`, both `README.md` version
  mentions and a dated `CHANGELOG.md` entry, with notes on what changed, what was excluded, validation
  and known issues.
- **The user isn't a programmer:** make the technical call and state it.
- **Check the system clock** before anything time-sensitive.
- **Other chats share the repo.** If memory, `VERSION` or `CHANGELOG.md` change underneath you, say so and
  don't touch them.
