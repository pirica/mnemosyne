#!/usr/bin/env python3
"""
Semantic analysis for batch 22 — split into exactly 2 parts as task specifies.
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

def get_node_type(file_cat, path, lang):
    mapping = {"code": "file", "script": "file", "config": "config", "docs": "document", "data": "config", "infra": "file", "markup": "file"}
    return mapping.get(file_cat, "file")

def get_complexity(non_empty_lines, num_funcs, num_classes):
    if non_empty_lines < 50 and num_funcs == 0 and num_classes == 0:
        return "simple"
    elif non_empty_lines < 50:
        return "simple"
    elif non_empty_lines <= 200:
        return "moderate"
    else:
        return "complex"

def get_tags(path, file_cat, lang, is_test):
    tags = []
    name = os.path.basename(path)
    if file_cat == "config":
        tags.append("configuration")
        if "fixtures" in path:
            tags.append("test-fixture")
            tags.append("json")
    elif file_cat == "code" or file_cat == "script":
        if is_test:
            tags.append("test")
            domain = name.replace("test_", "").replace(".py", "").replace("_", "-")
            tags.append(domain)
        else:
            tags.append("tool")
            if "bench" in name:
                tags.append("benchmark")
            elif "generate" in name:
                tags.append("generation")
    if lang == "python":
        tags.append("python")
    elif lang == "json":
        tags.append("json")
    return tags[:5]

def get_summary(path, file_cat, is_test):
    name = os.path.basename(path)
    test_target = name.replace("test_", "").replace(".py", "")
    if is_test:
        domain = test_target.replace("_", " ").replace("-", " ")
        return f"Tests for {domain} functionality in the Mnemosyne memory system."
    elif "bench" in path:
        return f"Benchmark script measuring performance of {name.replace('.py', '').replace('bench_', '')} operations."
    elif "generate_beam_charts" in path:
        return "Tool for generating visualization charts of beam metrics and memory retrieval performance data."
    elif "generate_sota_report" in path:
        return "Tool for generating state-of-the-art comparison reports benchmarking memory retrieval performance."
    elif "fixtures" in path:
        return f"Test fixture containing {name.replace('.json', '')} data for importer testing."
    return f"File: {name}"

def is_test_file(path):
    return path.startswith("tests/") and not path.startswith("tests/test_importers/fixtures/")

# ---- Build Nodes ----
nodes = []
edges = []
file_node_ids = {}

# File-level nodes
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
    tags = get_tags(path, file_cat, lang, is_test)
    summary = get_summary(path, file_cat, is_test)
    
    nodes.append({
        "id": node_id, "type": node_type, "name": name,
        "filePath": path, "summary": summary, "tags": tags, "complexity": complexity,
    })

# Function/class nodes + edges
for result in struct["results"]:
    path = result["path"]
    is_test = is_test_file(path)
    file_cat = result["fileCategory"]
    file_node_id = file_node_ids[path]
    
    if file_cat not in ("code", "script"):
        continue
    
    exported_names = {e["name"] for e in result.get("exports", [])}
    
    # Classes
    for cls_data in result.get("classes", []):
        cls_name = cls_data["name"]
        num_methods = len(cls_data.get("methods", []))
        if num_methods >= 2:
            cls_id = f"class:{path}:{cls_name}"
            nodes.append({
                "id": cls_id, "type": "class", "name": cls_name,
                "filePath": path, "lineRange": [cls_data["startLine"], cls_data["endLine"]],
                "summary": f"Test class {cls_name} with {num_methods} methods.",
                "tags": ["test", "class"], "complexity": "moderate" if num_methods > 5 else "simple",
            })
            edges.append({"source": file_node_id, "target": cls_id, "type": "contains", "direction": "forward", "weight": 1.0})
            if cls_name in exported_names:
                edges.append({"source": file_node_id, "target": cls_id, "type": "exports", "direction": "forward", "weight": 0.8})
    
    # Functions (only exported/visible test functions)
    for func_data in result.get("functions", []):
        func_name = func_data["name"]
        func_id = f"function:{path}:{func_name}"
        nodes.append({
            "id": func_id, "type": "function", "name": func_name,
            "filePath": path, "params": func_data.get("params", []),
            "summary": f"Function {func_name}.",
            "tags": ["test", "function"], "complexity": "simple",
        })
        edges.append({"source": file_node_id, "target": func_id, "type": "contains", "direction": "forward", "weight": 1.0})
        if func_name in exported_names:
            edges.append({"source": file_node_id, "target": func_id, "type": "exports", "direction": "forward", "weight": 0.8})

# Import edges
for result in struct["results"]:
    path = result["path"]
    file_cat = result["fileCategory"]
    if file_cat not in ("code", "script"):
        continue
    file_node_id = file_node_ids[path]
    for imp_path in batch_import_data.get(path, []):
        target_id = file_node_ids.get(imp_path, f"file:{imp_path}")
        edges.append({"source": file_node_id, "target": target_id, "type": "imports", "direction": "forward", "weight": 0.7})

# tested_by edges
for result in struct["results"]:
    path = result["path"]
    if is_test_file(path):
        test_node_id = file_node_ids[path]
        for imp_path in batch_import_data.get(path, []):
            prod_node_id = file_node_ids.get(imp_path, f"file:{imp_path}")
            edges.append({"source": prod_node_id, "target": test_node_id, "type": "tested_by", "direction": "forward", "weight": 0.5})

# Neighbor-map edges
for file_path, neighbors in neighbor_map.items():
    if file_path in file_node_ids:
        src_id = file_node_ids[file_path]
        for neighbor in neighbors:
            n_path = neighbor["path"]
            if n_path:
                tgt_id = file_node_ids.get(n_path, f"file:{n_path}")
                existing = any(e["source"] == src_id and e["target"] == tgt_id and e["type"] == "imports" for e in edges)
                if not existing:
                    edges.append({"source": src_id, "target": tgt_id, "type": "imports", "direction": "forward", "weight": 0.7})

# ---- Split into exactly 2 parts ----
node_count = len(nodes)
edge_count = len(edges)
parts = 2  # Task specifies exactly 2 parts

print(f"Total nodes: {node_count}")
print(f"Total edges: {edge_count}")
print(f"Splitting into {parts} parts (as per task specification)")

# Sort files alphabetically
all_files = sorted([r["path"] for r in struct["results"]])
chunk_size = math.ceil(len(all_files) / parts)

for part_idx in range(parts):
    start = part_idx * chunk_size
    end = min(start + chunk_size, len(all_files))
    part_files = set(all_files[start:end])
    
    # Collect nodes whose filePath is in this part
    part_node_ids = set()
    part_nodes = []
    file_nodes_in_part = {}
    
    for node in nodes:
        if node.get("filePath", "") in part_files:
            part_nodes.append(node)
            part_node_ids.add(node["id"])
            if node.get("type") in ("file", "config"):
                file_nodes_in_part[node["filePath"]] = node["id"]
    
    # Collect edges where source is in this part's file nodes
    part_edges = []
    seen_edge_keys = set()
    
    for edge in edges:
        key = (edge["source"], edge["target"], edge["type"])
        if key in seen_edge_keys:
            continue
        src_in_part = edge["source"] in part_node_ids
        tgt_in_part = edge["target"] in part_node_ids
        
        if src_in_part or tgt_in_part:
            seen_edge_keys.add(key)
            part_edges.append(edge)
    
    out_file = os.path.join(OUTPUT_DIR, f"batch-{BATCH_INDEX}-part-{part_idx + 1}.json")
    
    output = {"nodes": part_nodes, "edges": part_edges}
    with open(out_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"  Part {part_idx+1}: {out_file} -> {len(part_nodes)} nodes, {len(part_edges)} edges")

# Validate: sum of nodes should equal total
total_parts_nodes = 0
for part_idx in range(parts):
    f = os.path.join(OUTPUT_DIR, f"batch-{BATCH_INDEX}-part-{part_idx + 1}.json")
    with open(f) as fh:
        d = json.load(fh)
        total_parts_nodes += len(d["nodes"])
        print(f"  Validated part {part_idx+1}: {len(d['nodes'])} nodes, {len(d['edges'])} edges")

print(f"\nSummary: {parts} parts written, {node_count} total nodes, {edge_count} total edges")
print(f"Total across parts: {total_parts_nodes} nodes (should equal {node_count})")
