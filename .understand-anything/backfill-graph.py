#!/usr/bin/env python3
"""Backfill missing summary and tags on knowledge graph nodes.

Nodes that made it through the pipeline without proper summary/tags get
meaningful values based on type, path, name, and relationships.

Usage:
    python3 backfill-graph.py <path-to-knowledge-graph.json>
"""

import json
import re
import sys
from pathlib import Path


def _extract_module_hints(filepath: str) -> list[str]:
    """Derive topic hints from a file path."""
    hints = []
    parts = Path(filepath).parts
    for p in parts[:-1]:  # directories
        if p == "tests" or p == "test":
            hints.append("test")
        elif p in ("src", "source"):
            hints.append("source")
        elif p == "core":
            hints.append("core")
        elif p == "integrations":
            hints.append("integration")
        elif p == "utils" or p == "util":
            hints.append("utility")
        elif p == "api":
            hints.append("api")
        elif p == "models" or p == "model":
            hints.append("data-model")
        elif p == "config":
            hints.append("configuration")
        elif p == "scripts":
            hints.append("script")
        elif p == "docs" or p == "doc":
            hints.append("documentation")
        elif p == "migrations":
            hints.append("migration")
        elif p == "cli":
            hints.append("cli")
        elif p == "plugins" or p == "plugin":
            hints.append("plugin")
    return hints


def _filename_hints(filename: str) -> list[str]:
    """Derive tags from filename patterns."""
    hints = []
    lower = filename.lower()
    if lower.startswith("test_") or lower.startswith("test-") or ".test." in lower or "_test." in lower:
        hints.append("test")
    if lower.startswith("__init__"):
        hints.append("entry-point")
        hints.append("barrel")
    if lower == "manage.py":
        hints.append("entry-point")
    if lower.startswith("main") or lower == "app.py":
        hints.append("entry-point")
    if "config" in lower or "setting" in lower:
        hints.append("configuration")
    if "middleware" in lower:
        hints.append("middleware")
    if "handler" in lower or "controller" in lower:
        hints.append("api-handler")
    if "model" in lower:
        hints.append("data-model")
    if "schema" in lower:
        hints.append("schema-definition")
    if "migration" in lower:
        hints.append("migration")
    if "factory" in lower:
        hints.append("factory")
    if "base" in lower or "abstract" in lower:
        hints.append("abstract")
    if "singleton" in lower:
        hints.append("singleton")
    if "event" in lower:
        hints.append("event-handler")
    if "exception" in lower or "error" in lower:
        hints.append("error-handling")
    if "logger" in lower or "log" in lower:
        hints.append("logging")
    if "serial" in lower:
        hints.append("serialization")
    if "valid" in lower:
        hints.append("validation")
    if "type" in lower:
        hints.append("type-definition")
    if "hook" in lower:
        hints.append("hook")
    return hints


_PATH_CONTEXT = {
    "core": ["core", "foundation", "persistence"],
    "extraction": ["extraction", "parsing", "analysis"],
    "integrations": ["integration", "adapter"],
    "plugins": ["plugin", "extension"],
    "migrations": ["migration"],
    "dr": ["disaster-recovery", "recovery"],
    "importers": ["import"],
    "tools": ["utility", "developer-tools"],
    "scripts": ["script", "automation"],
    "tests": ["test", "testing"],
    "docs": ["documentation"],
    "cli": ["cli", "command-line"],
    "skills": ["skill", "agent"],
    "hermes_memory_provider": ["memory-provider", "hermes"],
    "hermes_plugin": ["plugin", "hermes"],
    "experiments": ["experiment", "research"],
}


def _module_context(filepath: str) -> dict:
    """Return {dir_label, tags_extra} for a file path based on project structure."""
    parts = Path(filepath).parts
    dir_label = ""
    tags_extra = []
    for p in parts:
        if p in _PATH_CONTEXT:
            ctx = _PATH_CONTEXT[p]
            if not dir_label:
                dir_label = p
            tags_extra.extend(ctx)
    if not dir_label and len(parts) >= 2:
        dir_label = parts[-2]
    return {"dir_label": dir_label, "tags_extra": tags_extra}


def _clean_name(name: str, node_id: str, ntype: str = "") -> str:
    """Extract a clean display name from various ID formats."""
    if not name:
        # Extract from ID
        return _extract_id_name(node_id)
    if name == node_id:
        return _extract_id_name(node_id)
    # For file-type nodes, name is often the relative path — use just the filename
    if ntype in ("file", "config", "document", "service", "pipeline", "schema", "resource"):
        basename = Path(name).name
        if basename:
            return basename
    return name


def _extract_id_name(node_id: str) -> str:
    """Extract a display name from a knowledge-graph node ID."""
    if "__nofilepath__" in node_id:
        # class:__nofilepath__:cls:module.ClassName  → ClassName
        parts = node_id.split(":")
        for p in parts:
            if "." in p and not p.startswith("__"):
                return p.split(".")[-1]
        return parts[-1]
    # file:path/to/file.py → file.py
    # function:path/to/file.py:func_name → func_name
    # class:path/to/file.py:ClassName → ClassName
    last = node_id.split(":")[-1]
    basename = Path(last).name
    if basename:
        return basename
    return last


def _generate_summary(node: dict) -> str:
    """Generate a concise 1-sentence summary for a node."""
    ntype = node.get("type", "node")
    raw_name = node.get("name", node.get("id", "unknown"))
    node_id = node.get("id", raw_name)
    name = _clean_name(raw_name, node_id, ntype)
    filepath = node.get("filePath", "")
    parent = node.get("parent", "")
    label = node.get("label", "")

    ctx = _module_context(filepath) if filepath else {}
    dir_label = ctx.get("dir_label", "")

    # Use parent as dir_label fallback for __nofilepath__/no-path nodes
    if not dir_label and parent:
        dir_label = parent.split("/")[-1].replace(".py", "")

    # Templates by type
    if ntype == "file":
        if dir_label:
            return f"{name} — {dir_label} module source file"
        return f"{name} — source file"

    elif ntype == "function":
        module_hint = f" in {Path(parent).name}" if parent else ""
        if dir_label:
            module_hint = f" ({dir_label} module)" if not module_hint else module_hint
        readable = name.replace("_", " ").title()
        return f"{readable} function{module_hint}"

    elif ntype == "class":
        # For nofilepath nodes, the label often has the clean class name
        cls_name = label if label else name
        module_hint = ""
        if parent:
            module_hint = f" in {Path(parent).name}"
        elif dir_label:
            module_hint = f" ({dir_label} module)"
        return f"{cls_name} class{module_hint}"

    elif ntype == "concept":
        return f"{name} — conceptual abstraction in the {dir_label or 'project'} domain"

    elif ntype == "data":
        return f"{name} — data structure/record definition"

    elif ntype == "config-entry":
        return f"{name} — configuration parameter"

    elif ntype == "fixture":
        return f"{name} — test fixture data"

    elif ntype == "endpoint":
        return f"{name} — API endpoint"

    elif ntype in ("pipeline-step",):
        return f"{name} — pipeline task step"

    elif ntype == "pipeline-job":
        return f"{name} — CI/CD pipeline job"

    # Fallback
    return f"{name} — {ntype}"


def _generate_tags(node: dict) -> list[str]:
    """Generate a set of 3-5 meaningful tags for a node."""
    ntype = node.get("type", "node")
    name = node.get("name", "")
    filepath = node.get("filePath", "")

    tags = []

    # Type-based tags
    type_tags = {
        "file": ["source"],
        "function": ["function"],
        "class": ["class"],
        "concept": ["concept"],
        "config-entry": ["configuration"],
        "data": ["data"],
        "fixture": ["fixture", "test"],
        "endpoint": ["api", "endpoint"],
        "pipeline-step": ["pipeline"],
        "pipeline-job": ["pipeline"],
    }
    tags.extend(type_tags.get(ntype, [ntype]))

    # File path hints from module context
    if filepath:
        ctx = _module_context(filepath)
        tags.extend([t for t in ctx.get("tags_extra", []) if t not in tags])
        filename = Path(filepath).name
        tags.extend([h for h in _filename_hints(filename) if h not in tags])

    # Name-level hints for functions/classes
    lower = name.lower()
    if ntype == "function":
        if lower.startswith("test_") or lower.startswith("test"):
            tags.append("test")
        if lower.startswith("get_") or lower.startswith("fetch_"):
            tags.append("accessor")
        if lower.startswith("set_") or lower.startswith("update_"):
            tags.append("mutator")
        if lower.startswith("is_") or lower.startswith("has_") or lower.startswith("can_"):
            tags.append("predicate")
        if lower.startswith("validate") or lower.startswith("check"):
            tags.append("validation")
        if "convert" in lower or "parse" in lower or "format" in lower:
            tags.append("transformation")
        if "init" in lower or "setup" in lower or "bootstrap" in lower:
            tags.append("initialization")
        if "handle" in lower or "process" in lower:
            tags.append("handler")
        if "dispatch" in lower or "emit" in lower:
            tags.append("event-dispatch")
        if "clean" in lower or "purge" in lower or "delete" in lower:
            tags.append("cleanup")
        if "connect" in lower or "disconnect" in lower:
            tags.append("connection")

    elif ntype == "class":
        if "Handler" in name or "Controller" in name:
            tags.append("api-handler")
        if "Manager" in name or "Registry" in name:
            tags.append("manager")
        if "Factory" in name or "Builder" in name:
            tags.append("factory")
        if "Strategy" in name or "Policy" in name:
            tags.append("strategy")
        if "Config" in name or "Settings" in name:
            tags.append("configuration")
        if "Base" in name or "Abstract" in name:
            tags.append("abstract")
        if "Singleton" in name:
            tags.append("singleton")
        if "Exception" in name or "Error" in name:
            tags.append("error-handling")
        if "Mixin" in name:
            tags.append("mixin")
        if "Adapter" in name or "Wrapper" in name:
            tags.append("adapter")
        if "Serializer" in name or "Encoder" in name or "Decoder" in name:
            tags.append("serialization")
        if "Validator" in name:
            tags.append("validation")
        if "Repository" in name or "Store" in name:
            tags.append("data-access")
        if "Service" in name:
            tags.append("service")

    # Handle nofilepath nodes — extract module from ID for better tags
    if node.get("id", "") and "__nofilepath__" in node.get("id", ""):
        tags.append("unresolved")
        # Extract module name from class:__nofilepath__:cls:module.ClassName
        parts = node.get("id", "").split(":")
        for p in parts:
            if "." in p and not p.startswith("__"):
                mod = p.split(".")[0]
                if mod in _PATH_CONTEXT:
                    tags.extend([t for t in _PATH_CONTEXT[mod] if t not in tags])
                else:
                    tags.append(mod)
                break

    # Deduplicate, preserve order, limit to 5
    seen = set()
    deduped = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            deduped.append(t)
    return deduped[:6]


def backfill(graph_path: str):
    with open(graph_path) as f:
        graph = json.load(f)

    nodes = graph.get("nodes", [])
    backfilled_count = 0
    skipped_count = 0

    for node in nodes:
        needs_fix = False

        # Fill missing name field
        if not node.get("name"):
            node["name"] = _clean_name(
                node.get("id", ""), node.get("id", ""), node.get("type", "")
            )
            needs_fix = True

        # Fill missing filePath from parent for __nofilepath__ nodes
        if not node.get("filePath") and node.get("parent"):
            parent = node.get("parent", "")
            if parent and parent != "__nofilepath__":
                node["filePath"] = parent
                needs_fix = True

        # Handle case where filePath is stored under "path" instead
        if not node.get("filePath") and node.get("path"):
            node["filePath"] = node["path"]
            needs_fix = True

        # Fill missing filePath from ID prefix for file-level nodes
        if not node.get("filePath") and node.get("id"):
            nid = node.get("id", "")
            for prefix in ("file:", "config:", "document:", "service:", "pipeline:", "schema:", "resource:"):
                if nid.startswith(prefix):
                    extracted = nid[len(prefix):]
                    if extracted and "/" in extracted:
                        node["filePath"] = extracted
                        needs_fix = True
                        break

        # Check summary
        summary = node.get("summary")
        if not summary or summary == node.get("id") or summary == node.get("name"):
            node["summary"] = _generate_summary(node)
            needs_fix = True

        # Check tags
        tags = node.get("tags")
        if not isinstance(tags, list) or len(tags) == 0:
            node["tags"] = _generate_tags(node)
            needs_fix = True
        elif tags == ["untagged"]:
            node["tags"] = _generate_tags(node)
            needs_fix = True

        if needs_fix:
            backfilled_count += 1
        else:
            skipped_count += 1

    # Write back
    with open(graph_path, "w") as f:
        json.dump(graph, f, indent=2)

    print(f"Backfilled {backfilled_count} nodes")
    print(f"Skipped {skipped_count} nodes (already had proper summary/tags)")
    print(f"Total nodes: {len(nodes)}")

    # Second pass — verify no defaults remain
    still_default = [
        n for n in nodes
        if (n.get("summary") == n.get("id")) or (n.get("tags") == ["untagged"])
    ]
    if still_default:
        print(f"WARNING: {len(still_default)} nodes still have default values:")
        for n in still_default[:5]:
            print(f"  {n.get('id')}: summary={n.get('summary')[:50]} tags={n.get('tags')}")
    else:
        print("All nodes pass — 0 auto-corrections expected on dashboard load.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 backfill-graph.py <knowledge-graph.json>")
        sys.exit(1)
    backfill(sys.argv[1])
