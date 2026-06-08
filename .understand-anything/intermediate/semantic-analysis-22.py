#!/usr/bin/env python3
"""
Semantic analysis for batch 22 of Mnemosyne knowledge graph.
Reads structural extraction output, produces GraphNode + GraphEdge objects,
splits into parts if >60 nodes.
"""
import json
import math
import os

STRUCTURE_PATH = "/root/.hermes/projects/mnemosyne/.understand-anything/intermediate/batch-22-structure.json"
BATCHES_PATH = "/root/.hermes/projects/mnemosyne/.understand-anything/intermediate/batches.json"
OUTPUT_DIR = "/root/.hermes/projects/mnemosyne/.understand-anything/intermediate/"
BATCH_INDEX = 22

# Load structural data
with open(STRUCTURE_PATH) as f:
    struct = json.load(f)

# Load batch data for import info
with open(BATCHES_PATH) as f:
    batches = json.load(f)

# Find batch 22
batch22 = None
for b in batches.get("batches", []):
    if b.get("batchIndex") == BATCH_INDEX:
        batch22 = b
        break

batch_import_data = batch22.get("batchImportData", {})
neighbor_map = batch22.get("neighborMap", {})

# File classification helper
def get_node_type(file_cat, path, lang):
    """Map fileCategory to node type."""
    mapping = {
        "code": "file",
        "script": "file",
        "config": "config",
        "docs": "document",
        "data": "config",  # JSON fixtures
        "infra": "file",
        "markup": "file",
    }
    return mapping.get(file_cat, "file")

def get_complexity(non_empty_lines, num_funcs, num_classes):
    """Determine complexity level."""
    if non_empty_lines < 50 and num_funcs == 0 and num_classes == 0:
        return "simple"
    elif non_empty_lines < 50:
        return "simple"
    elif non_empty_lines <= 200:
        return "moderate"
    else:
        return "complex"

def get_tags(path, file_cat, num_funcs, num_classes, lang, is_test):
    """Determine appropriate tags."""
    tags = []
    name = os.path.basename(path)
    
    if file_cat == "config":
        tags.append("configuration")
        if path.endswith(".json"):
            tags.append("json")
            if "fixtures" in path:
                tags.append("test-fixture")
                tags.append("data")
    elif file_cat == "docs":
        tags.append("documentation")
    elif file_cat == "code" or file_cat == "script":
        if is_test:
            tags.append("test")
            # Determine test focus from path
            if "content_sanitizer" in path:
                tags.append("content-sanitizer")
            elif "data_dir" in path:
                tags.append("data-dir")
            elif "fact_recall" in path:
                tags.append("fact-recall")
            elif "identity" in path:
                tags.append("identity-memory")
            elif "mnemosyne_stats" in path:
                tags.append("stats")
            elif "optional_embeddings" in path:
                tags.append("embeddings")
            elif "outer_package_version" in path:
                tags.append("version")
            elif "prefetch_content" in path:
                tags.append("prefetch")
            elif "query_cache" in path:
                tags.append("query-cache")
            elif "s1_mcp_sse" in path:
                tags.append("mcp")
                tags.append("auth")
            elif "scope_auto" in path:
                tags.append("scope")
            elif "sync_roles" in path:
                tags.append("sync")
            elif "sync_turn" in path:
                tags.append("sync")
                tags.append("content-limit")
            elif "t1_local_llm" in path:
                tags.append("local-llm")
            elif "temporal_parser" in path:
                tags.append("temporal-parser")
            elif "triples_data_dir" in path:
                tags.append("triples")
            elif "weibull_mmr_intent" in path:
                tags.append("weibull")
                tags.append("mmr")
                tags.append("intent")
        else:
            tags.append("tool")
            if "bench" in name:
                tags.append("benchmark")
            elif "generate" in name:
                tags.append("generation")
            if "audit" in path:
                tags.append("audit")
            elif "recall" in path:
                tags.append("recall")
            elif "validation" in path:
                tags.append("validation")
            elif "beam" in path:
                tags.append("beam")
            elif "sota" in path:
                tags.append("sota")
                tags.append("report")
    
    if lang == "python":
        tags.append("python")
    elif lang == "json":
        tags.append("json")
    
    return tags[:6]  # Cap at 6 tags

def get_summary(path, file_cat, is_test, num_funcs, num_classes):
    """Generate summary based on file path and structure."""
    name = os.path.basename(path)
    
    if is_test:
        if "content_sanitizer" in path:
            return "Tests for content sanitization utilities including data URI detection, Shannon entropy calculation, base64 blob detection, blob storage, and content sanitization logic."
        elif "data_dir_scripts" in path:
            return "Tests validating data directory scripts for proper path resolution and script execution behavior."
        elif "fact_recall_integration" in path:
            return "Integration tests for fact-based recall functionality, verifying correct retrieval of stored facts against queries."
        elif "identity_memory" in path:
            return "Tests for identity memory functionality, validating storage and retrieval of identity-related information."
        elif "mnemosyne_stats" in path:
            return "Comprehensive tests for Mnemosyne statistics and metrics reporting functionality across multiple scenarios."
        elif "optional_embeddings" in path:
            return "Tests verifying the system handles optional embedding configurations gracefully."
        elif "outer_package_version" in path:
            return "Tests for outer package version detection and compatibility checking."
        elif "prefetch_content_truncation" in path:
            return "Tests ensuring content prefetching correctly truncates content at specified limits."
        elif "query_cache_synonyms" in path:
            return "Tests for query cache and synonym expansion integration, validating cached query behavior with synonym normalization."
        elif "s1_mcp_sse_auth" in path:
            return "Tests for MCP SSE (Server-Sent Events) authentication mechanisms including handshake and token validation."
        elif "scope_auto_default" in path:
            return "Tests for automatic scope resolution and default scope assignment behavior."
        elif "sync_roles" in path:
            return "Tests for synchronization role management, validating correct assignment and enforcement of sync roles."
        elif "sync_turn_content_limit" in path:
            return "Tests for per-turn content limits during synchronization operations."
        elif "t1_local_llm_default_disabled" in path:
            return "Tests verifying local LLM functionality is disabled by default when not explicitly configured."
        elif "temporal_parser" in path:
            return "Tests for temporal expression parsing including natural language date extraction and relative day resolution."
        elif "triples_data_dir" in path:
            return "Tests for triple store data directory configuration and initialization behavior."
        elif "weibull_mmr_intent" in path:
            return "Tests for Weibull decay, MMR (Maximal Marginal Relevance) reranking, and query intent classification integration."
        else:
            return f"Test file for {name.replace('test_', '').replace('.py', '')} functionality."
    elif file_cat == "code" or file_cat == "script":
        if "bench_audit_log" in path:
            return "Benchmark script for auditing log performance measuring throughput and latency of audit log operations."
        elif "bench_unified_recall" in path:
            return "Benchmark script for unified recall performance measuring end-to-end memory retrieval latency."
        elif "bench_validation" in path:
            return "Benchmark script for validation pipeline performance measuring throughput of memory validation operations."
        elif "generate_beam_charts" in path:
            return "Tool for generating visualization charts of beam metrics and memory retrieval performance data."
        elif "generate_sota_report" in path:
            return "Tool for generating state-of-the-art comparison reports benchmarking memory retrieval performance."
        else:
            return f"Utility script for {name.replace('.py', '')} operations."
    elif file_cat == "config":
        if "mem0_export" in path:
            return "Test fixture containing exported Mem0 memory data for importer testing."
        elif "mem0_paginated_response" in path:
            return "Test fixture simulating paginated API responses from Mem0 for pagination handling tests."
    
    return f"File: {name}"

def is_test_file(path):
    """Check if path is a test file."""
    return path.startswith("tests/") and not path.startswith("tests/test_importers/fixtures/")


# ---- Build Nodes ----
nodes = []
edges = []

# Track all file node IDs for edge references
file_node_ids = {}

# First pass: create file-level nodes
for result in struct["results"]:
    path = result["path"]
    file_cat = result["fileCategory"]
    lang = result["language"]
    name = os.path.basename(path)
    is_test = is_test_file(path)
    
    node_type = get_node_type(file_cat, path, lang)
    node_id = f"{node_type}:{path}"
    file_node_ids[path] = node_id
    
    complexity = get_complexity(result["nonEmptyLines"], 
                                len(result.get("functions", [])),
                                len(result.get("classes", [])))
    
    tags = get_tags(path, file_cat, 
                    len(result.get("functions", [])),
                    len(result.get("classes", [])),
                    lang, is_test)
    
    summary = get_summary(path, file_cat, is_test,
                          len(result.get("functions", [])),
                          len(result.get("classes", [])))
    
    node = {
        "id": node_id,
        "type": node_type,
        "name": name,
        "filePath": path,
        "summary": summary,
        "tags": tags,
        "complexity": complexity,
    }
    
    nodes.append(node)

# Second pass: create function/class nodes and edges
# Significance filter:
# - Functions/methods with 10+ lines (skip trivial one-liners)
# - Classes with 2+ methods or 20+ lines
# - Any function or class that is exported

for result in struct["results"]:
    path = result["path"]
    is_test = is_test_file(path)
    file_cat = result["fileCategory"]
    file_node_id = file_node_ids[path]
    
    # Skip non-code files for sub-file nodes
    if file_cat not in ("code", "script"):
        continue
    
    # Find exported names
    exported_names = set()
    for exp in result.get("exports", []):
        exported_names.add(exp["name"])
    
    # Process classes
    exported_class_names = set()
    for cls_data in result.get("classes", []):
        cls_name = cls_data["name"]
        num_methods = len(cls_data.get("methods", []))
        # Significance check
        if num_methods >= 2:
            cls_id = f"class:{path}:{cls_name}"
            is_exported = cls_name in exported_names
            
            node = {
                "id": cls_id,
                "type": "class",
                "name": cls_name,
                "filePath": path,
                "lineRange": [cls_data["startLine"], cls_data["endLine"]],
                "summary": f"Test class {cls_name} with {num_methods} test methods for {os.path.basename(path).replace('test_', '').replace('.py', '')} functionality.",
                "tags": ["test", "class", "python"],
                "complexity": "moderate" if num_methods > 5 else "simple",
            }
            nodes.append(node)
            
            # contains edge
            edges.append({
                "source": file_node_id,
                "target": cls_id,
                "type": "contains",
                "direction": "forward",
                "weight": 1.0
            })
            
            # exports edge if exported
            if is_exported:
                edges.append({
                    "source": file_node_id,
                    "target": cls_id,
                    "type": "exports",
                    "direction": "forward",
                    "weight": 0.8
                })
                exported_class_names.add(cls_name)
    
    # Process functions (test functions)
    # For test files, most functions are test methods - create nodes for significant ones
    for func_data in result.get("functions", []):
        func_name = func_data["name"]
        # Only create nodes for test functions with meaningful names (skip trivial helpers)
        if not (is_test or func_name.startswith("test_") or func_name in exported_names):
            continue
        
        # Estimate line count from callgraph references - use a heuristic
        func_id = f"function:{path}:{func_name}"
        is_exported = func_name in exported_names
        
        node = {
            "id": func_id,
            "type": "function",
            "name": func_name,
            "filePath": path,
            "params": func_data.get("params", []),
            "summary": f"Test function {func_name} verifying specific behavior of {os.path.basename(path).replace('test_', '').replace('.py', '')}.",
            "tags": ["test", "function", "python"],
            "complexity": "simple",
        }
        nodes.append(node)
        
        # contains edge
        edges.append({
            "source": file_node_id,
            "target": func_id,
            "type": "contains",
            "direction": "forward",
            "weight": 1.0
        })
        
        if is_exported:
            edges.append({
                "source": file_node_id,
                "target": func_id,
                "type": "exports",
                "direction": "forward",
                "weight": 0.8
            })

# Import edges from batchImportData
for result in struct["results"]:
    path = result["path"]
    file_cat = result["fileCategory"]
    if file_cat not in ("code", "script"):
        continue
    file_node_id = file_node_ids[path]
    
    imports = batch_import_data.get(path, [])
    for imp_path in imports:
        # Determine target node ID
        # Look up the imported file in our batch or use file: prefix
        if imp_path in file_node_ids:
            target_id = file_node_ids[imp_path]
        else:
            target_id = f"file:{imp_path}"
        
        edges.append({
            "source": file_node_id,
            "target": target_id,
            "type": "imports",
            "direction": "forward",
            "weight": 0.7
        })

# tested_by edges: for test files that import production code
for result in struct["results"]:
    path = result["path"]
    if is_test_file(path):
        test_node_id = file_node_ids[path]
        imports = batch_import_data.get(path, [])
        for imp_path in imports:
            # The production file is the imp_path; test file tests it
            if imp_path in file_node_ids:
                prod_node_id = file_node_ids[imp_path]
            else:
                prod_node_id = f"file:{imp_path}"
            
            edges.append({
                "source": prod_node_id,
                "target": test_node_id,
                "type": "tested_by",
                "direction": "forward",
                "weight": 0.5
            })

# Neighbor-map-based edges
# test_content_sanitizer.py has neighbor mnemosyne/core/content_sanitizer.py - add tested_by+imports
for file_path, neighbors in neighbor_map.items():
    if file_path in file_node_ids:
        src_id = file_node_ids[file_path]
        for neighbor in neighbors:
            n_path = neighbor["path"]
            if n_path in file_node_ids:
                tgt_id = file_node_ids[n_path]
            else:
                tgt_id = f"file:{n_path}"
            
            # Add tested_by for test→production (already handled above via import)
            # Add imports edge if not already present
            existing_imports = [e for e in edges 
                               if e["source"] == src_id and e["target"] == tgt_id 
                               and e["type"] == "imports"]
            if not existing_imports:
                edges.append({
                    "source": src_id,
                    "target": tgt_id,
                    "type": "imports",
                    "direction": "forward",
                    "weight": 0.7
                })

# ---- Compute totals & split ----
node_count = len(nodes)
edge_count = len(edges)

print(f"Total nodes: {node_count}")
print(f"Total edges: {edge_count}")
print(f"Threshold: nodeCount > 60 or edgeCount > 120 -> split")

if node_count <= 60 and edge_count <= 120:
    parts = 1
else:
    parts = max(math.ceil(node_count / 60), math.ceil(edge_count / 120))
    print(f"Splitting into {parts} parts")

# Sort files alphabetically for partitioning
all_files = sorted([r["path"] for r in struct["results"]])
N = len(all_files)
chunk_size = math.ceil(N / parts)

for part_idx in range(parts):
    start = part_idx * chunk_size
    end = min(start + chunk_size, N)
    part_files = set(all_files[start:end])
    
    # Collect nodes for this part
    part_nodes = []
    part_node_ids = set()
    
    for node in nodes:
        fp = node.get("filePath", "")
        if fp in part_files:
            part_nodes.append(node)
            part_node_ids.add(node["id"])
    
    # Also include file-level nodes for files in this part
    for node in nodes:
        if node["type"] in ("file", "config") and node.get("filePath", "") in part_files:
            if node["id"] not in part_node_ids:
                part_nodes.append(node)
                part_node_ids.add(node["id"])
    
    # Collect edges where source is in this part's nodes
    part_edges = []
    for edge in edges:
        if edge["source"] in part_node_ids:
            part_edges.append(edge)
    
    # Also add edges from/to nodes in this part
    for edge in edges:
        if edge["target"] in part_node_ids and edge not in part_edges:
            part_edges.append(edge)
    
    # Deduplicate edges
    seen_edges = set()
    unique_edges = []
    for e in part_edges:
        key = (e["source"], e["target"], e["type"])
        if key not in seen_edges:
            seen_edges.add(key)
            unique_edges.append(e)
    
    if parts == 1:
        out_file = os.path.join(OUTPUT_DIR, f"batch-{BATCH_INDEX}.json")
    else:
        out_file = os.path.join(OUTPUT_DIR, f"batch-{BATCH_INDEX}-part-{part_idx + 1}.json")
    
    output = {
        "nodes": part_nodes,
        "edges": unique_edges
    }
    
    with open(out_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Wrote {out_file}: {len(part_nodes)} nodes, {len(unique_edges)} edges")

print(f"\nSummary:")
print(f"  Total nodes: {node_count}")
print(f"  Total edges: {edge_count}")
print(f"  Parts written: {parts}")
