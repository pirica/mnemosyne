#!/usr/bin/env python3
"""Split batch-4 knowledge graph into 2 parts. Each part gets ONLY its own file nodes."""
import json, math, os

PROJECT_ROOT = "/root/.hermes/projects/mnemosyne"
output_dir = f"{PROJECT_ROOT}/.understand-anything/intermediate"

with open(f"{output_dir}/batch-4.json") as f:
    graph = json.load(f)

all_nodes = graph["nodes"]
all_edges = graph["edges"]

# Sorted batch file paths
sorted_files = sorted([
    "integrations/hermes/src/mnemosyne_hermes/__init__.py",
    "integrations/hermes/src/mnemosyne_hermes/tools.py",
    "mnemosyne/core/binary_vectors.py",
    "mnemosyne/core/episodic_graph.py",
    "mnemosyne/core/polyphonic_recall.py",
    "mnemosyne/core/typed_memory.py",
    "mnemosyne/core/veracity_consolidation.py",
    "tests/test_beam_e4_remember_batch_veracity.py",
    "tests/test_consolidate_fact_concurrency.py",
    "tests/test_consolidate_fact_id_collision.py",
    "tests/test_consolidate_fact_sibling_races.py",
    "tests/test_e5a_vector_voice_dense_rewire.py",
    "tests/test_graph_tools.py",
    "tests/test_integration.py",
    "tests/test_pre_experiment_fidelity.py",
    "tests/test_proactive_linking.py"
])

N_PARTS = 2
files_per_part = math.ceil(len(sorted_files) / N_PARTS)

part_files = [
    sorted_files[i:i + files_per_part]
    for i in range(0, len(sorted_files), files_per_part)
]

for part_idx, file_list in enumerate(part_files, 1):
    part_file_set = set(file_list)
    
    # Collect nodes for this part: only those whose filePath is in this part's files
    part_nodes = []
    seen_ids = set()
    
    for node in all_nodes:
        fpath = node.get("filePath", "")
        if not fpath:
            continue
        # Check if this node belongs to a file in this part
        if fpath in part_file_set:
            if node["id"] not in seen_ids:
                part_nodes.append(node)
                seen_ids.add(node["id"])
    
    # Also ensure file nodes for all files in this part
    for fp in file_list:
        fid = f"file:{fp}"
        if fid not in seen_ids:
            for node in all_nodes:
                if node["id"] == fid:
                    part_nodes.append(node)
                    seen_ids.add(fid)
                    break
    
    # Collect edges where source is in our part's nodes
    part_edges = []
    edge_seen = set()
    for edge in all_edges:
        key = (edge["source"], edge["target"], edge["type"])
        if edge["source"] in seen_ids and key not in edge_seen:
            part_edges.append(edge)
            edge_seen.add(key)
    
    part_output = {"nodes": part_nodes, "edges": part_edges}
    part_path = f"{output_dir}/batch-4-part-{part_idx}.json"
    with open(part_path, 'w') as f:
        json.dump(part_output, f, indent=2)
    
    print(f"Part {part_idx}: {len(part_nodes)} nodes, {len(part_edges)} edges → {part_path}")
    print(f"  Files: {file_list}")
    # Verify no cross-contamination
    node_files_in_part = set(n.get("filePath","") for n in part_nodes)
    unexpected = [fp for fp in node_files_in_part if fp not in part_file_set]
    if unexpected:
        print(f"  WARNING: Unexpected files in part: {unexpected}")
    else:
        print(f"  OK: all nodes belong to this part's files")

os.remove(f"{output_dir}/batch-4.json")
print(f"\nRemoved batch-4.json (replaced by 2 parts)")
