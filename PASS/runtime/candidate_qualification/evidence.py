"""CRQ evidence: Skillset Memory intake, canon reading, and candidate accounting.

Loads `PASS/tools` privately, resolves a `card_candidate` and its events, reads
only the run's domain plus metaskills, snapshots the bounded baseline closure,
accounts for every candidate change, and runs the ordinary validators on a
temporary overlay. It never writes `library/` or Skillset Memory.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

import yaml

from .schemas import (
    CANDIDATE_CARDS,
    CANDIDATE_STATUSES,
    CANDIDATE_TYPE,
    CandidateQualificationError,
    MODULE_MANIFEST,
    OBJECT_ID_RE,
    SCOPE_KEYS,
    SHARED_PACKAGE,
    TOOLS_DIR,
    WORKSPACE_BUCKET,
    contained,
    digest_bytes,
)


# ------------------------------------------------------------- PASS tools


_TOOLS: dict[str, Any] = {}


def load_pass_tool(name: str) -> Any:
    """Import one `PASS/tools` module privately, once.

    The tools import their siblings (`paths`, ...) as top-level modules. The
    tools directory is on `sys.path` only while the module loads, and sibling
    modules it pulled in are dropped again, so neither leaks into this runtime.
    """
    if name in _TOOLS:
        return _TOOLS[name]
    path = TOOLS_DIR / f"{name}.py"
    if not path.is_file():
        raise CandidateQualificationError(f"PASS tool is missing: {path}")
    tools = str(TOOLS_DIR)
    private = f"_pass_crq_tool_{name}"
    before = set(sys.modules)
    sys.path.insert(0, tools)
    try:
        spec = importlib.util.spec_from_file_location(private, path)
        if spec is None or spec.loader is None:
            raise CandidateQualificationError(f"cannot load PASS tool: {path}")
        module = importlib.util.module_from_spec(spec)
        # Registered under its private name while it executes: dataclasses
        # resolve their defining module through sys.modules.
        sys.modules[private] = module
        try:
            spec.loader.exec_module(module)
        except BaseException:
            del sys.modules[private]
            raise
    finally:
        sys.path.remove(tools)
        for leaked in set(sys.modules) - before - {private}:
            origin = getattr(sys.modules[leaked], "__file__", None)
            if origin and Path(origin).resolve().parent == TOOLS_DIR:
                del sys.modules[leaked]
    _TOOLS[name] = module
    return module


def json_safe(value: Any) -> Any:
    """Return plain JSON data; YAML dates become ISO strings."""
    return json.loads(json.dumps(value, default=str, ensure_ascii=False))


def quarantined_events(events: list[dict[str, Any]]) -> set[str]:
    """Event ids removed from capability evidence by an evidence correction."""
    return {
        str(target)
        for event in events
        if event.get("event_kind") == "evidence_correction"
        and (event.get("corrections") or {}).get("disposition") == "quarantined"
        for target in (event.get("supersedes_events") or [])
    }


def resolve_memory_candidate(memory_root: Path, domain: str, entry_id: str) -> dict[str, Any]:
    """Resolve one `card_candidate` and its cited events through `memory.py`.

    The whole store must pass `memory.py validate` first; the entry-level checks
    below then name exactly why this entry cannot start a run.
    """
    memory = load_pass_tool("memory")
    domain_dir = Path(memory_root) / domain
    if not (domain_dir / "skill_memory.yaml").is_file():
        raise CandidateQualificationError(
            f"no Skillset Memory store for domain {domain!r} under {Path(memory_root)}"
        )
    problems = memory.validate_store(domain_dir)
    if problems:
        shown = "; ".join(problems[:10]) + ("; ..." if len(problems) > 10 else "")
        raise CandidateQualificationError(
            f"memory store {domain!r} fails memory.py validate: {shown}"
        )
    try:
        store = memory.load_memory(domain_dir)
    except memory.MemoryError_ as exc:
        raise CandidateQualificationError(str(exc)) from exc
    entry = memory.find_entry(store.get("entries") or [], entry_id)
    if entry is None:
        raise CandidateQualificationError(f"memory entry {entry_id} does not exist in {domain}")
    if entry.get("type") != CANDIDATE_TYPE:
        raise CandidateQualificationError(
            f"memory entry {entry_id} is {entry.get('type')}, not {CANDIDATE_TYPE}"
        )
    if entry.get("status") not in CANDIDATE_STATUSES:
        raise CandidateQualificationError(
            f"memory entry {entry_id} is {entry.get('status')}; only active or "
            "monitoring candidates can start a run"
        )
    cited = entry.get("evidence_events") or []
    if not cited:
        raise CandidateQualificationError(
            f"memory entry {entry_id} cites no evidence event; link valid evidence "
            "with memory.py compact before starting a run"
        )
    events, _ = memory.load_events(domain_dir)
    by_id = {event.get("event_id"): event for event in events}
    quarantined = quarantined_events(events)
    selected = []
    for event_id in cited:
        event = by_id.get(event_id)
        if event is None:
            raise CandidateQualificationError(f"{entry_id} cites unknown event {event_id}")
        if event.get("validity") != "valid":
            raise CandidateQualificationError(f"{entry_id} cites invalid event {event_id}")
        if event.get("event_kind", "performance") != "performance":
            raise CandidateQualificationError(f"{entry_id} cites correction {event_id}")
        if event_id in quarantined:
            raise CandidateQualificationError(f"{entry_id} cites quarantined event {event_id}")
        selected.append(event)
    return {
        "memory_entry": json_safe(entry),
        "events": json_safe(selected),
        "memory_store": {
            "memory_schema_version": store.get("memory_schema_version"),
            "memory_version": store.get("memory_version"),
        },
    }


def exposed_card_ids(events: list[dict[str, Any]]) -> set[str] | None:
    """Cards the cited evidence declares it exposed, or None when no event says."""
    exposed: set[str] | None = None
    for event in events:
        intervention = event.get("intervention")
        if not isinstance(intervention, dict):
            continue
        components = intervention.get("components")
        card_ids = components.get("card_ids") if isinstance(components, dict) else None
        if isinstance(card_ids, list):
            exposed = (exposed or set()) | {str(item) for item in card_ids}
    return exposed
FRONTMATTER_RE = re.compile(r"\A---\n(?P<front>.*?)\n---\n", re.DOTALL)
# Relations that make one card a prerequisite of executing another. They are
# followed transitively; every other outgoing link is followed one hop.
HARD_INCOMING_RELATIONS = frozenset({"prerequisite_for", "foundation_of"})
HARD_OUTGOING_RELATIONS = frozenset({"variant_of"})


def card_text(raw: bytes) -> str:
    """A card's text for parsing: CRLF and LF read alike. Hashes use raw bytes."""
    return raw.decode("utf-8", errors="replace").replace("\r\n", "\n")


def card_frontmatter(path: Path) -> dict[str, Any] | None:
    try:
        match = FRONTMATTER_RE.match(card_text(path.read_bytes()))
        data = yaml.safe_load(match.group("front")) if match else None
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        return None
    return data if isinstance(data, dict) else None


def card_index(library_root: Path, packages: Iterable[str]) -> dict[str, dict[str, Any]]:
    """Index the cards of the named packages only; other domains are never read."""
    index: dict[str, dict[str, Any]] = {}
    library_root = Path(library_root)
    for package in sorted(set(packages)):
        base = library_root / package
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.md")):
            if path.name in {"README.md", "INDEX.md"}:
                continue
            data = card_frontmatter(path)
            if not data or not isinstance(data.get("object_id"), str):
                continue
            object_id = data["object_id"]
            if object_id in index:
                raise CandidateQualificationError(f"duplicate object_id in canon: {object_id}")
            index[object_id] = {
                "relative_path": path.relative_to(library_root).as_posix(),
                "package": package,
                "object_type": data.get("object_type"),
                "data": data,
            }
    return index


def card_links(data: dict[str, Any]) -> list[tuple[str, str]]:
    links = []
    foundation = data.get("foundation_object_id")
    if isinstance(foundation, str) and foundation and foundation != "none":
        links.append(("foundation", foundation))
    for link in data.get("cross_links") or []:
        if isinstance(link, dict) and isinstance(link.get("target_object_id"), str):
            links.append((str(link.get("rel")), link["target_object_id"]))
    return links


def support_closure(
    targets: Iterable[str], index: dict[str, dict[str, Any]], domain: str
) -> set[str]:
    """The bounded bundle needed to execute the targets, excluding the targets.

    Hard prerequisites (foundation, variant_of, and incoming prerequisite_for or
    foundation_of) are followed transitively; a target's other outgoing links
    are followed one hop. The release closure follows every link transitively
    and would freeze most of a domain.
    """
    targets = set(targets)
    incoming: dict[str, set[str]] = {}
    for source, info in index.items():
        for rel, target in card_links(info["data"]):
            if rel in HARD_INCOMING_RELATIONS:
                incoming.setdefault(target, set()).add(source)

    def require(object_id: str, owner: str) -> None:
        if object_id not in index:
            raise CandidateQualificationError(
                f"{owner} needs {object_id}, which is not a card in {domain} or {SHARED_PACKAGE}"
            )

    selected = set(targets)
    pending = list(targets)
    while pending:
        current = pending.pop()
        hard = set(incoming.get(current, set()))
        for rel, target in card_links(index[current]["data"]):
            if rel == "foundation" or rel in HARD_OUTGOING_RELATIONS:
                hard.add(target)
        for object_id in sorted(hard):
            require(object_id, current)
            if object_id not in selected:
                selected.add(object_id)
                pending.append(object_id)
    for target in sorted(targets):
        for _rel, object_id in card_links(index[target]["data"]):
            require(object_id, target)
            selected.add(object_id)
    return selected - targets


def module_manifest_for(library_root: Path, relative_path: str) -> str | None:
    """The nearest `MODULE.yaml` at or above a card, inside its package."""
    parts = PurePosixPath(relative_path).parts[:-1]
    for depth in range(len(parts), 0, -1):
        candidate = PurePosixPath(*parts[:depth], MODULE_MANIFEST)
        if (Path(library_root) / candidate).is_file():
            return candidate.as_posix()
    return None


def resolve_owners(
    likely_owners: Iterable[Any], index: dict[str, dict[str, Any]], domain: str
) -> list[dict[str, Any]]:
    """Classify each likely owner; an object id that does not resolve fails."""
    owners = []
    for label in likely_owners:
        label = str(label)
        if not OBJECT_ID_RE.fullmatch(label):
            owners.append({"label": label, "object_id": None, "resolution": "label"})
            continue
        info = index.get(label)
        if info is None:
            raise CandidateQualificationError(
                f"likely owner {label} is not a card in {domain} or {SHARED_PACKAGE}; a "
                "CRQ run authors one domain and never couples to another"
            )
        resolution = "target" if info["package"] == domain else "metaskills"
        owners.append({"label": label, "object_id": label, "resolution": resolution})
    return owners


def baseline_objects(root: Path, manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Frozen baseline cards by object id, typed from their snapshot bytes."""
    objects = {}
    for entry in manifest["entries"]:
        if entry["role"] == "module-manifest":
            continue
        data = card_frontmatter(contained(root, f"baseline/cards/{entry['relative_path']}", "snapshot"))
        objects[entry["object_id"]] = {
            "relative_path": entry["relative_path"],
            "role": entry["role"],
            "package": PurePosixPath(entry["relative_path"]).parts[0],
            "object_type": (data or {}).get("object_type"),
        }
    return objects


def admissible_event_ids(memory_root: Path, domain: str) -> set[str]:
    """Events a case may cite: valid, performance, not quarantined."""
    memory = load_pass_tool("memory")
    events, _ = memory.load_events(Path(memory_root) / domain)
    quarantined = quarantined_events(events)
    return {
        str(event["event_id"])
        for event in events
        if isinstance(event.get("event_id"), str)
        and event.get("validity") == "valid"
        and event.get("event_kind", "performance") == "performance"
        and event["event_id"] not in quarantined
    }


# ------------------------------------------------------- candidate freezing


# An identifier shaped like a run, memory entry or history event never belongs in a card.
EVIDENCE_ID_RE = re.compile(r"\b[A-Z][A-Z0-9]*_(?:CRQ|MEM|EV)_[0-9]+\b")
CARD_HEADING_RE = re.compile(r"(?m)^## ([^\r\n]+?)\s*$")
CARD_TITLE_RE = re.compile(r"(?m)^# ([^\r\n]+?)\s*$")


def card_parts(raw: bytes) -> tuple[dict[str, Any] | None, str | None, dict[str, str]]:
    """Frontmatter, H1 and `##` sections of a card's bytes."""
    text = card_text(raw)
    match = re.match(r"\A---\n(?P<front>.*?)\n---\n(?P<body>.*)\Z", text, re.DOTALL)
    if not match:
        return None, None, {}
    try:
        front = yaml.safe_load(match.group("front"))
    except yaml.YAMLError:
        front = None
    body = match.group("body")
    title = CARD_TITLE_RE.search(body)
    headings = list(CARD_HEADING_RE.finditer(body))
    sections = {}
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(body)
        sections[heading.group(1)] = " ".join(body[heading.end():end].split())
    return front if isinstance(front, dict) else None, title.group(1) if title else None, sections


def changed_sections(before: bytes | None, after: bytes) -> list[str]:
    """Which parts of a card changed: Frontmatter, Title, and each `##` section."""
    new_front, new_title, new_sections = card_parts(after)
    if before is None:
        return ["Frontmatter", "Title", *new_sections]
    old_front, old_title, old_sections = card_parts(before)
    changed = []
    if old_front != new_front:
        changed.append("Frontmatter")
    if old_title != new_title:
        changed.append("Title")
    for heading in [*new_sections, *(h for h in old_sections if h not in new_sections)]:
        if old_sections.get(heading) != new_sections.get(heading):
            changed.append(heading)
    return changed


def candidate_file_list(cards: Path) -> tuple[list[str], list[str]]:
    """(files, problems) under `candidate/cards/`, refusing symlinks."""
    files, problems = [], []
    if not cards.is_dir():
        return files, ["candidate/cards/ is missing"]
    for path in sorted(cards.rglob("*")):
        relative = path.relative_to(cards).as_posix()
        if path.is_symlink():
            problems.append(f"{relative}: symlinks are not allowed in a candidate")
        elif path.is_file():
            files.append(relative)
    return files, problems


def account_candidate(
    root: Path,
    actions: list[dict[str, str]],
    baseline_ids: set[str],
) -> tuple[list[dict[str, Any]], list[dict[str, str]], dict[str, int]]:
    """Match every authorized action to a real change and every file to an action.

    Returns (applied changes, unmatched actions, scope counts). Anything
    unmatched blocks the freeze; nothing is silently dropped.
    """
    cards = contained(root, CANDIDATE_CARDS, "candidate cards")
    files, problems = candidate_file_list(cards)
    unmatched = [{"object_id": None, "relative_path": None, "problem": text} for text in problems]
    scope = {key: 0 for key in SCOPE_KEYS}
    applied = []
    expected = {action["relative_path"] for action in actions}

    def miss(action: dict[str, str], text: str) -> None:
        unmatched.append({
            "object_id": action["object_id"], "relative_path": action["relative_path"], "problem": text,
        })

    for action in actions:
        relative = action["relative_path"]
        path = contained(cards, relative, "candidate path")
        before = (
            contained(root, f"baseline/cards/{relative}", "snapshot").read_bytes()
            if action["action"] == "revise" else None
        )
        if not path.is_file():
            if action["action"] == "revise":
                scope["deleted_cards"] += 1
                miss(action, "the revised card is missing; deleting a card is never allowed")
            else:
                miss(action, "the new-card action created no card")
            continue
        after = path.read_bytes()
        front, _title, _sections = card_parts(after)
        if front is None:
            miss(action, "the file is not a card with readable frontmatter")
            continue
        if front.get("object_id") != action["object_id"]:
            if action["action"] == "revise":
                scope["renamed_object_ids"] += 1
            miss(action, f"object_id is {front.get('object_id')!r}; renaming is never allowed")
            continue
        if front.get("object_type") != action["object_type"]:
            miss(action, f"object_type is {front.get('object_type')!r}, not {action['object_type']}")
            continue
        if before is not None and after == before:
            miss(action, "the staged card is byte-identical to the baseline")
            continue
        sections = changed_sections(before, after)
        if not sections:
            miss(action, "only whitespace or line endings changed")
            continue
        scope["changed_existing_cards" if action["action"] == "revise" else "new_cards"] += 1
        applied.append({
            "action": action["action"],
            "object_id": action["object_id"],
            "relative_path": relative,
            "baseline_sha256": digest_bytes(before) if before is not None else None,
            "candidate_sha256": digest_bytes(after),
            "changed_sections": sections,
            "accounting": "applied-to-candidate",
        })
    for relative in files:
        if relative in expected:
            continue
        front, _title, _sections = card_parts(contained(cards, relative, "candidate file").read_bytes())
        object_id = front.get("object_id") if front else None
        if object_id in baseline_ids:
            scope["moved_existing_cards"] += 1
            text = f"a copy of existing card {object_id} at an unauthorized path; moving or changing an unauthorized card is never allowed"
        else:
            text = "this file was never authorized by the frozen assessment"
        unmatched.append({"object_id": object_id, "relative_path": relative, "problem": text})
    return applied, unmatched, scope


def evidence_references(
    root: Path, files: Iterable[str], forbidden: Iterable[str]
) -> list[str]:
    """Candidate files that name the run's evidence instead of standing alone."""
    tokens = sorted({token for token in forbidden if token})
    patterns = [re.compile(r"(?<![A-Za-z0-9_])" + re.escape(token) + r"(?![A-Za-z0-9_])") for token in tokens]
    problems = []
    for relative in files:
        text = card_text(contained(root, f"{CANDIDATE_CARDS}/{relative}", "candidate file").read_bytes())
        found = set(EVIDENCE_ID_RE.findall(text))
        found |= {token for token, pattern in zip(tokens, patterns) if pattern.search(text)}
        if PurePosixPath(WORKSPACE_BUCKET).name in text:
            found.add("a candidate-qualification workspace path")
        if found:
            problems.append(f"{relative} names run evidence ({', '.join(sorted(found))}); a card must stand alone")
    return problems


def run_tool_cli(name: str, argv: list[str]) -> tuple[int, str]:
    """Run a PASS tool's own `main()` in-process with `argv`; return (code, output)."""
    module = load_pass_tool(name)
    output = io.StringIO()
    saved = sys.argv
    sys.argv = [f"{name}.py", *argv]
    try:
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            try:
                code = module.main()
            except SystemExit as exc:
                code = exc.code if isinstance(exc.code, int) else 1
    finally:
        sys.argv = saved
    return int(code or 0), output.getvalue()


OVERLAY_PREFIX = "pass-crq-overlay-"
OVERLAY_VALIDATORS = ("validate", "verify_references")


def overlay_problems(library_root: Path, cards: Path, files: Iterable[str]) -> list[str]:
    """Validate the live library with the candidate files laid over it.

    The overlay is a temporary copy named `library/` (the reference checker
    finds its repo root by that name). It is removed on success and failure,
    and the canonical library is only ever read.
    """
    problems = []
    with tempfile.TemporaryDirectory(prefix=OVERLAY_PREFIX) as temporary:
        overlay = Path(temporary) / "library"
        shutil.copytree(library_root, overlay, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
        for relative in files:
            destination = overlay.joinpath(*PurePosixPath(relative).parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(contained(cards, relative, "candidate file"), destination)
        for tool in OVERLAY_VALIDATORS:
            code, output = run_tool_cli(tool, ["--library", str(overlay)])
            if code:
                shown = "\n".join(output.strip().splitlines()[-40:]).replace(str(overlay), "<overlay>")
                problems.append(f"{tool}.py --library <overlay> failed:\n{shown}")
    return problems
