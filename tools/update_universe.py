#!/usr/bin/env python3
"""Append reviewed public concepts and pathways to both Universe scenes.

Dry run: python3 tools/update_universe.py /path/to/reviewed-additions.json
Apply:   python3 tools/update_universe.py /path/to/reviewed-additions.json --apply

The input has `concepts` and `paths` arrays using the existing scene schemas.
This command does not research, grant publication approval, push or deploy.
"""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PAGES = ("index.html", "universe/index.html")
GROUPS = {"commerce", "audience", "talent", "people", "strategy", "trust", "value"}
KINDS = {"capability", "role", "principle", "outcome"}


def script_pattern(identifier):
    return re.compile(r'(<script id="' + re.escape(identifier)
                      + r'" type="application/json">)(.*?)(</script>)', re.S)


def read_graph(text):
    result = {}
    for key, identifier in (("concepts", "scene-concepts"), ("paths", "path-data")):
        matches = list(script_pattern(identifier).finditer(text))
        if len(matches) != 1:
            raise ValueError(f"Expected exactly one {identifier} script")
        result[key] = json.loads(matches[0].group(2))
    return result


def name_key(name):
    return " ".join(name.split()).casefold()


def validate_graph(graph):
    if set(graph) != {"concepts", "paths"}:
        raise ValueError("Expected concepts and paths arrays only")
    names = set()
    for key, fields in (("concepts", {"name", "description", "group", "kind"}),
                        ("paths", {"name", "domain", "nodes", "copy", "question"})):
        if not isinstance(graph[key], list):
            raise ValueError(f"{key} must be an array")
        seen = set()
        for entry in graph[key]:
            if not isinstance(entry, dict) or set(entry) != fields:
                raise ValueError(f"Invalid {key} fields")
            for field in fields - {"nodes"}:
                value = entry[field]
                if not isinstance(value, str) or not value.strip() or value != value.strip():
                    raise ValueError(f"Invalid {key} {field}")
                if "<" in value or ">" in value:
                    raise ValueError("Use plain text without markup")
            normalized = name_key(entry["name"])
            if normalized in seen:
                raise ValueError(f"Duplicate {key} name: {entry['name']}")
            seen.add(normalized)
            if key == "concepts":
                if entry["group"] not in GROUPS or entry["kind"] not in KINDS:
                    raise ValueError(f"Invalid concept group/kind: {entry['name']}")
                names.add(entry["name"])
            elif entry["domain"] not in GROUPS:
                raise ValueError(f"Invalid pathway domain: {entry['name']}")
    routes = set()
    for path in graph["paths"]:
        nodes = path["nodes"]
        if (not isinstance(nodes, list) or len(nodes) != 4
                or any(not isinstance(name, str) for name in nodes)
                or len(set(nodes)) != 4):
            raise ValueError(f"Expected four distinct concept names: {path['name']}")
        missing = set(nodes) - names
        if missing:
            raise ValueError(f"Unknown concepts in {path['name']}: {sorted(missing)}")
        if tuple(nodes) in routes:
            raise ValueError(f"Duplicate pathway route: {path['name']}")
        routes.add(tuple(nodes))


def merge_additions(current, additions):
    if not isinstance(additions, dict) or set(additions) != {"concepts", "paths"}:
        raise ValueError("Additions require concepts and paths arrays only")
    merged = {key: list(value) for key, value in current.items()}
    for key in ("concepts", "paths"):
        if not isinstance(additions[key], list):
            raise ValueError(f"{key} additions must be an array")
        known = {name_key(item["name"]): item for item in current[key]}
        for item in additions[key]:
            if not isinstance(item, dict) or not isinstance(item.get("name"), str):
                raise ValueError(f"Invalid {key} addition")
            normalized = name_key(item["name"])
            if normalized in known:
                if item != known[normalized]:
                    raise ValueError(f"Conflicting existing {key}: {item['name']}")
                continue
            merged[key].append(item)
            known[normalized] = item
    validate_graph(merged)
    added_names = {item["name"] for item in merged["concepts"]} - {
        item["name"] for item in current["concepts"]}
    connected = {name for path in merged["paths"] for name in path["nodes"]}
    if added_names - connected:
        raise ValueError(f"New concepts need a pathway: {sorted(added_names - connected)}")
    return merged


def replace_graph(text, graph):
    for key, identifier in (("concepts", "scene-concepts"), ("paths", "path-data")):
        payload = json.dumps(graph[key], ensure_ascii=False)
        text = script_pattern(identifier).sub(
            lambda match: match.group(1) + payload + match.group(3), text)
    return text


def write_changes(changes):
    """Stage every file first and restore originals if a replacement fails."""
    changed = {name: text for name, text in changes.items()
               if (ROOT / name).read_text() != text}
    if not changed:
        return
    stage = Path(tempfile.mkdtemp(prefix=".universe-update-", dir=ROOT))
    replaced = []
    keep_recovery = False
    try:
        # Keep staging and destinations on the same filesystem for os.replace.
        for index, (name, text) in enumerate(changed.items()):
            original = ROOT / name
            shutil.copy2(original, stage / f"{index}.before")
            staged = stage / f"{index}.after"
            staged.write_text(text)
            shutil.copymode(original, staged)
        (stage / "recovery.json").write_text(json.dumps(
            {f"{index}.before": name for index, name in enumerate(changed)}, indent=2))
        try:
            for index, name in enumerate(changed):
                os.replace(stage / f"{index}.after", ROOT / name)
                replaced.append((index, name))
        except OSError as error:
            failed_recovery = []
            for index, name in reversed(replaced):
                try:
                    os.replace(stage / f"{index}.before", ROOT / name)
                except OSError:
                    failed_recovery.append(name)
            if failed_recovery:
                keep_recovery = True
                raise OSError(f"Write failed and rollback needs manual recovery for "
                              f"{failed_recovery}; original copies remain in {stage}") from error
            raise OSError("Write failed; all replaced files were restored") from error
    finally:
        if not keep_recovery:
            shutil.rmtree(stage)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("additions", type=Path, help="Reviewed, publication-safe JSON")
    parser.add_argument("--apply", action="store_true", help="Write local files; no publication")
    args = parser.parse_args()
    try:
        texts = {name: (ROOT / name).read_text() for name in PAGES}
        current = read_graph(texts[PAGES[0]])
        validate_graph(current)
        if current != read_graph(texts[PAGES[1]]):
            raise ValueError("The two scenes differ; reconcile them before updating")
        updated = merge_additions(current, json.loads(args.additions.read_text()))
        for name, text in texts.items():
            capacity = re.search(r"mobileNodes:(\d+)", text)
            if not capacity or len(updated["concepts"]) > int(capacity.group(1)):
                raise ValueError(f"Concepts exceed mobile scene capacity in {name}")
        changes = {name: replace_graph(text, updated) for name, text in texts.items()}
        readme = (ROOT / "README.md").read_text()
        readme = re.sub(r"the \d+ relationships from `#path-data`",
                        f"the {len(updated['paths'])} relationships from `#path-data`", readme)
        readme = re.sub(r"\d+ have public concept labels",
                        f"{len(updated['concepts'])} have public concept labels", readme)
        changes["README.md"] = readme
        if args.apply:
            write_changes(changes)
        print(json.dumps({"mode": "applied locally" if args.apply else "dry run",
                          "concepts": len(updated["concepts"]), "paths": len(updated["paths"]),
                          "added_concepts": len(updated["concepts"]) - len(current["concepts"]),
                          "added_paths": len(updated["paths"]) - len(current["paths"]),
                          "published": False}, indent=2))
    except (ValueError, OSError) as error:
        parser.exit(1, f"Universe update stopped: {error}\n")


if __name__ == "__main__":
    main()
