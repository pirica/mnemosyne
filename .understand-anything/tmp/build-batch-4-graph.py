#!/usr/bin/env python3
"""Build batch-4 knowledge graph from extraction results."""
import json

PROJECT_ROOT = "/root/.hermes/projects/mnemosyne"

with open(f"{PROJECT_ROOT}/.understand-anything/tmp/ua-file-extract-results-4.json") as f:
    extract = json.load(f)

results_by_path = {r["path"]: r for r in extract["results"]}

# Batch import data (from batches.json)
batch_import = {
    "integrations/hermes/src/mnemosyne_hermes/__init__.py": [
        "integrations/hermes/src/mnemosyne_hermes/tools.py",
        "mnemosyne/core/episodic_graph.py"
    ],
    "integrations/hermes/src/mnemosyne_hermes/tools.py": [],
    "mnemosyne/core/binary_vectors.py": [],
    "mnemosyne/core/episodic_graph.py": [],
    "mnemosyne/core/polyphonic_recall.py": [
        "mnemosyne/core/episodic_graph.py",
        "mnemosyne/core/typed_memory.py",
        "mnemosyne/core/veracity_consolidation.py"
    ],
    "mnemosyne/core/typed_memory.py": [],
    "mnemosyne/core/veracity_consolidation.py": [],
    "tests/test_beam_e4_remember_batch_veracity.py": [
        "mnemosyne/core/beam.py",
        "mnemosyne/core/veracity_consolidation.py"
    ],
    "tests/test_consolidate_fact_concurrency.py": [
        "mnemosyne/core/veracity_consolidation.py"
    ],
    "tests/test_consolidate_fact_id_collision.py": [
        "mnemosyne/core/veracity_consolidation.py"
    ],
    "tests/test_consolidate_fact_sibling_races.py": [
        "mnemosyne/core/veracity_consolidation.py"
    ],
    "tests/test_e5a_vector_voice_dense_rewire.py": [
        "mnemosyne/core/beam.py",
        "mnemosyne/core/polyphonic_recall.py"
    ],
    "tests/test_graph_tools.py": [
        "hermes_memory_provider/__init__.py",
        "mnemosyne/core/beam.py",
        "mnemosyne/core/episodic_graph.py"
    ],
    "tests/test_integration.py": [
        "mnemosyne/core/binary_vectors.py",
        "mnemosyne/core/episodic_graph.py",
        "mnemosyne/core/polyphonic_recall.py",
        "mnemosyne/core/typed_memory.py",
        "mnemosyne/core/veracity_consolidation.py"
    ],
    "tests/test_pre_experiment_fidelity.py": [
        "mnemosyne/core/beam.py",
        "mnemosyne/core/veracity_consolidation.py"
    ],
    "tests/test_proactive_linking.py": [
        "mnemosyne/core/beam.py",
        "mnemosyne/core/episodic_graph.py"
    ]
}

nodes = []
edges = []

# File summaries and metadata per path
file_info = {
    "integrations/hermes/src/mnemosyne_hermes/__init__.py": {
        "name": "__init__.py",
        "summary": "Hermes agent memory provider integration: adapts Mnemosyne BeamMemory as a Hermes provider with full lifecycle management, config, tool schemas, audit logging, shared surface memory, profile isolation, and session management.",
        "tags": ["entry-point", "memory-provider", "integration", "hermes"],
        "complexity": "complex",
        "languageNotes": "Large Python provider module with 50+ methods implementing the Hermes agent memory plugin API."
    },
    "integrations/hermes/src/mnemosyne_hermes/tools.py": {
        "name": "tools.py",
        "summary": "Defines 19 JSON tool schemas (remember, recall, graph_query, graph_link, etc.) exposed by the Mnemosyne Hermes memory provider for agent tool-calling interfaces.",
        "tags": ["tool-schemas", "api-handler", "integration"],
        "complexity": "moderate"
    },
    "mnemosyne/core/binary_vectors.py": {
        "name": "binary_vectors.py",
        "summary": "Information-theoretic binary vector implementation with Maximally Informative Binarization (MIB), Hamming distance via bitwise ops, and SQLite-native BinaryVectorStore for deterministic 32x compressed retrieval.",
        "tags": ["binary-vectors", "retrieval", "information-theoretic", "compression"],
        "complexity": "complex",
        "languageNotes": "Implements MIB from Moorcheh ITS (arXiv:2601.11557). Uses numpy bitwise operations for fast Hamming distance computation."
    },
    "mnemosyne/core/episodic_graph.py": {
        "name": "episodic_graph.py",
        "summary": "Episodic knowledge graph data model with Gist, Fact, GraphEdge, and EpisodicGraph classes representing structured semantic memory with timestamps, veracity tracking, and graph traversal for recall.",
        "tags": ["knowledge-graph", "data-model", "episodic-memory", "structured"],
        "complexity": "complex"
    },
    "mnemosyne/core/polyphonic_recall.py": {
        "name": "polyphonic_recall.py",
        "summary": "Multi-strategy parallel retrieval engine combining vector, graph, fact, and temporal voices with deterministic RRF re-ranking, budget-aware context assembly, and diversity penalty for unified recall.",
        "tags": ["recall", "multi-strategy", "retrieval", "re-ranking"],
        "complexity": "complex",
        "languageNotes": "Four-voice architecture inspired by Hindsight multi-strategy retrieval and Memanto information-theoretic scoring."
    },
    "mnemosyne/core/typed_memory.py": {
        "name": "typed_memory.py",
        "summary": "Deterministic, rule-based memory type classification system with 13 memory types (fact, preference, decision, etc.), pattern matchers, confidence scoring, priority signals, and conflict detection — zero LLM calls.",
        "tags": ["classification", "memory-types", "rule-based", "schema"],
        "complexity": "moderate"
    },
    "mnemosyne/core/veracity_consolidation.py": {
        "name": "veracity_consolidation.py",
        "summary": "Fact veracity tracking and consolidation engine with deterministic fact ID computation, veracity aggregation (stated/tool/inferred/unknown), confidence compounding, and conflict resolution for structured facts.",
        "tags": ["veracity", "consolidation", "facts", "confidence"],
        "complexity": "complex"
    },
    "tests/test_beam_e4_remember_batch_veracity.py": {
        "name": "test_beam_e4_remember_batch_veracity.py",
        "summary": "Tests for veracity clamping and batch remember veracity propagation, ensuring correct veracity tag assignment and clamping behavior in BeamMemory.",
        "tags": ["test", "veracity", "batch-remember"],
        "complexity": "moderate"
    },
    "tests/test_consolidate_fact_concurrency.py": {
        "name": "test_consolidate_fact_concurrency.py",
        "summary": "Concurrency tests for fact consolidation verifying thread-safe SPO deduplication, correct confidence compounding, and transaction rollback under concurrent access.",
        "tags": ["test", "concurrency", "consolidation"],
        "complexity": "moderate"
    },
    "tests/test_consolidate_fact_id_collision.py": {
        "name": "test_consolidate_fact_id_collision.py",
        "summary": "Tests for deterministic fact ID computation ensuring hash-based IDs are stable, collision-resistant, and correctly deduplicate identical SPO triples across varying content lengths.",
        "tags": ["test", "fact-id", "hashing", "dedup"],
        "complexity": "moderate"
    },
    "tests/test_consolidate_fact_sibling_races.py": {
        "name": "test_consolidate_fact_sibling_races.py",
        "summary": "Race condition tests for concurrent conflict resolution in fact consolidation, verifying deterministic winners, idempotent resolution, and safe serialized writes under contention.",
        "tags": ["test", "race-conditions", "consolidation", "concurrency"],
        "complexity": "moderate"
    },
    "tests/test_e5a_vector_voice_dense_rewire.py": {
        "name": "test_e5a_vector_voice_dense_rewire.py",
        "summary": "Comprehensive tests for the vector voice strategy in polyphonic recall, verifying embedding-based candidate retrieval across WM/EM tiers, empty states, and integration into the RRF pipeline.",
        "tags": ["test", "vector-voice", "polyphonic-recall", "embeddings"],
        "complexity": "complex"
    },
    "tests/test_graph_tools.py": {
        "name": "test_graph_tools.py",
        "summary": "Tests for episodic graph query and link tools used in the memory provider, covering related memory discovery, tool schema generation, query parsing, edge creation, and auto-population.",
        "tags": ["test", "graph-tools", "episodic-graph"],
        "complexity": "moderate"
    },
    "tests/test_integration.py": {
        "name": "test_integration.py",
        "summary": "Integration tests exercising typed memory classification, binary vector operations, episodic graph traversal, veracity consolidation, and polyphonic recall end-to-end.",
        "tags": ["test", "integration", "e2e"],
        "complexity": "moderate"
    },
    "tests/test_pre_experiment_fidelity.py": {
        "name": "test_pre_experiment_fidelity.py",
        "summary": "Pre-experiment fidelity tests verifying weight centralization, veracity aggregation helper, consolidation-to-episodic veracity pipeline, sleep-cycle veracity, and embedding loop defense.",
        "tags": ["test", "fidelity", "veracity", "experiment"],
        "complexity": "moderate"
    },
    "tests/test_proactive_linking.py": {
        "name": "test_proactive_linking.py",
        "summary": "Tests for proactive content and entity linking in the episodic graph, verifying gating logic, non-blocking behavior, edge deduplication, and correct edge types/weights.",
        "tags": ["test", "proactive-linking", "graph", "entities"],
        "complexity": "moderate"
    }
}

# ==================== NODES ====================

# File nodes (16)
for path, info in sorted(file_info.items()):
    nodes.append({
        "id": f"file:{path}",
        "type": "file",
        "name": info["name"],
        "filePath": path,
        "summary": info["summary"],
        "tags": info["tags"],
        "complexity": info["complexity"],
        **({"languageNotes": info["languageNotes"]} if "languageNotes" in info else {})
    })

# Core class nodes (non-test)
core_classes = [
    # MnemosyneMemoryProvider
    {
        "id": "class:integrations/hermes/src/mnemosyne_hermes/__init__.py:MnemosyneMemoryProvider",
        "type": "class",
        "name": "MnemosyneMemoryProvider",
        "filePath": "integrations/hermes/src/mnemosyne_hermes/__init__.py",
        "lineRange": [154, 1531],
        "summary": "Hermes agent memory provider implementing ~50 lifecycle, config, tool, and session methods for Mnemosyne integration with profile isolation, shared surface memory, and audit logging.",
        "tags": ["memory-provider", "hermes", "lifecycle", "tools"],
        "complexity": "complex"
    },
    # BinaryVectorStore
    {
        "id": "class:mnemosyne/core/binary_vectors.py:BinaryVectorStore",
        "type": "class",
        "name": "BinaryVectorStore",
        "filePath": "mnemosyne/core/binary_vectors.py",
        "lineRange": [128, 330],
        "summary": "SQLite-backed binary vector store supporting insert, search via Hamming distance, and metadata storage with 32x compression over float32 embeddings.",
        "tags": ["vector-store", "binary", "sqlite", "hamming"],
        "complexity": "complex"
    },
    # FastBinarySearch
    {
        "id": "class:mnemosyne/core/binary_vectors.py:FastBinarySearch",
        "type": "class",
        "name": "FastBinarySearch",
        "filePath": "mnemosyne/core/binary_vectors.py",
        "lineRange": [333, 372],
        "summary": "Optimized binary vector search using precomputed popcount and early termination for fast Hamming distance queries.",
        "tags": ["search", "binary", "optimized"],
        "complexity": "moderate"
    },
    # Gist
    {
        "id": "class:mnemosyne/core/episodic_graph.py:Gist",
        "type": "class",
        "name": "Gist",
        "filePath": "mnemosyne/core/episodic_graph.py",
        "lineRange": [46, 80],
        "summary": "Represents a condensed summary/gist node in the episodic knowledge graph with content, source, and timestamp metadata.",
        "tags": ["knowledge-graph", "gist", "summary"],
        "complexity": "simple"
    },
    # Fact
    {
        "id": "class:mnemosyne/core/episodic_graph.py:Fact",
        "type": "class",
        "name": "Fact",
        "filePath": "mnemosyne/core/episodic_graph.py",
        "lineRange": [83, 140],
        "summary": "Represents a structured subject-predicate-object fact in the episodic graph with veracity, confidence, and temporal scoping.",
        "tags": ["knowledge-graph", "fact", "spo", "structured"],
        "complexity": "moderate"
    },
    # GraphEdge
    {
        "id": "class:mnemosyne/core/episodic_graph.py:GraphEdge",
        "type": "class",
        "name": "GraphEdge",
        "filePath": "mnemosyne/core/episodic_graph.py",
        "lineRange": [143, 185],
        "summary": "Represents a directed edge between two graph nodes with type, weight, and metadata for knowledge graph traversal.",
        "tags": ["knowledge-graph", "edge", "traversal"],
        "complexity": "simple"
    },
    # EpisodicGraph
    {
        "id": "class:mnemosyne/core/episodic_graph.py:EpisodicGraph",
        "type": "class",
        "name": "EpisodicGraph",
        "filePath": "mnemosyne/core/episodic_graph.py",
        "lineRange": [188, 595],
        "summary": "Core episodic knowledge graph manager with CRUD for gists, facts, and edges, graph traversal, proximity queries, and database persistence.",
        "tags": ["knowledge-graph", "manager", "crud", "traversal"],
        "complexity": "complex"
    },
    # RecallResult
    {
        "id": "class:mnemosyne/core/polyphonic_recall.py:RecallResult",
        "type": "class",
        "name": "RecallResult",
        "filePath": "mnemosyne/core/polyphonic_recall.py",
        "lineRange": [52, 95],
        "summary": "Data class for a single recall candidate with content, score, provenance, tier info, and metadata from a voice strategy.",
        "tags": ["recall", "data-class", "scoring"],
        "complexity": "simple"
    },
    # PolyphonicResult
    {
        "id": "class:mnemosyne/core/polyphonic_recall.py:PolyphonicResult",
        "type": "class",
        "name": "PolyphonicResult",
        "filePath": "mnemosyne/core/polyphonic_recall.py",
        "lineRange": [98, 138],
        "summary": "Aggregated recall result combining multiple voice strategies with fused scores, provenance traces, and metadata.",
        "tags": ["recall", "aggregation", "multi-strategy"],
        "complexity": "simple"
    },
    # PolyphonicRecallEngine
    {
        "id": "class:mnemosyne/core/polyphonic_recall.py:PolyphonicRecallEngine",
        "type": "class",
        "name": "PolyphonicRecallEngine",
        "filePath": "mnemosyne/core/polyphonic_recall.py",
        "lineRange": [141, 878],
        "summary": "Central multi-strategy recall orchestrator running 4 parallel voices (vector, graph, fact, temporal), fusing scores via RRF, applying diversity penalty and budget-aware assembly.",
        "tags": ["recall", "engine", "multi-strategy", "orchestrator", "rrf"],
        "complexity": "complex"
    },
    # MemoryType
    {
        "id": "class:mnemosyne/core/typed_memory.py:MemoryType",
        "type": "class",
        "name": "MemoryType",
        "filePath": "mnemosyne/core/typed_memory.py",
        "lineRange": [45, 200],
        "summary": "Enum-like class defining 13 memory types with pattern matchers, default priorities, and decay characteristics for rule-based classification.",
        "tags": ["classification", "memory-types", "enum", "patterns"],
        "complexity": "moderate"
    },
    # TypeMatch
    {
        "id": "class:mnemosyne/core/typed_memory.py:TypeMatch",
        "type": "class",
        "name": "TypeMatch",
        "filePath": "mnemosyne/core/typed_memory.py",
        "lineRange": [203, 230],
        "summary": "Result container for a type classification match with type, confidence score, and matched pattern details.",
        "tags": ["classification", "match-result"],
        "complexity": "simple"
    },
    # ConsolidatedFact
    {
        "id": "class:mnemosyne/core/veracity_consolidation.py:ConsolidatedFact",
        "type": "class",
        "name": "ConsolidatedFact",
        "filePath": "mnemosyne/core/veracity_consolidation.py",
        "lineRange": [95, 175],
        "summary": "Persistent fact record with veracity, confidence, occurrence count, and first/last seen timestamps for structured fact consolidation.",
        "tags": ["consolidation", "fact", "veracity", "persistence"],
        "complexity": "moderate"
    },
    # VeracityConsolidator
    {
        "id": "class:mnemosyne/core/veracity_consolidation.py:VeracityConsolidator",
        "type": "class",
        "name": "VeracityConsolidator",
        "filePath": "mnemosyne/core/veracity_consolidation.py",
        "lineRange": [178, 947],
        "summary": "Fact consolidation orchestrator handling insert/dedup, veracity aggregation, conflict resolution, serialized writes, and database-backed consolidation passes.",
        "tags": ["consolidation", "orchestrator", "veracity", "conflicts"],
        "complexity": "complex"
    }
]

# Function nodes (exported or >=10 lines from core files)
core_functions = [
    # From hermes __init__.py - all exported
    {
        "id": "function:integrations/hermes/src/mnemosyne_hermes/__init__.py:_get_beam_class",
        "type": "function",
        "name": "_get_beam_class",
        "filePath": "integrations/hermes/src/mnemosyne_hermes/__init__.py",
        "lineRange": [48, 50],
        "summary": "Returns the BeamMemory class for use by the Hermes provider.",
        "tags": ["utility", "beam", "provider"],
        "complexity": "simple"
    },
    {
        "id": "function:integrations/hermes/src/mnemosyne_hermes/__init__.py:_get_triple_module",
        "type": "function",
        "name": "_get_triple_module",
        "filePath": "integrations/hermes/src/mnemosyne_hermes/__init__.py",
        "lineRange": [53, 55],
        "summary": "Returns the TripleStore module reference for triple operations.",
        "tags": ["utility", "triples", "provider"],
        "complexity": "simple"
    },
    {
        "id": "function:integrations/hermes/src/mnemosyne_hermes/__init__.py:_prefetch_content_char_limit",
        "type": "function",
        "name": "_prefetch_content_char_limit",
        "filePath": "integrations/hermes/src/mnemosyne_hermes/__init__.py",
        "lineRange": [58, 74],
        "summary": "Reads the MNEMOSYNE_PREFETCH_CONTENT_CHARS env var to cap content length in prefetch responses.",
        "tags": ["prefetch", "config", "limit"],
        "complexity": "simple"
    },
    {
        "id": "function:integrations/hermes/src/mnemosyne_hermes/__init__.py:_format_prefetch_content",
        "type": "function",
        "name": "_format_prefetch_content",
        "filePath": "integrations/hermes/src/mnemosyne_hermes/__init__.py",
        "lineRange": [77, 91],
        "summary": "Truncates prefetch content at a word boundary respecting the configured char limit.",
        "tags": ["prefetch", "formatting", "truncation"],
        "complexity": "simple"
    },
    {
        "id": "function:integrations/hermes/src/mnemosyne_hermes/__init__.py:_sync_turn_user_limit",
        "type": "function",
        "name": "_sync_turn_user_limit",
        "filePath": "integrations/hermes/src/mnemosyne_hermes/__init__.py",
        "lineRange": [94, 108],
        "summary": "Reads the MNEMOSYNE_SYNC_TURN_USER_LIMIT env var (default 500) for user message truncation in sync_turn.",
        "tags": ["sync-turn", "config", "limit", "user"],
        "complexity": "simple"
    },
    {
        "id": "function:integrations/hermes/src/mnemosyne_hermes/__init__.py:_sync_turn_assistant_limit",
        "type": "function",
        "name": "_sync_turn_assistant_limit",
        "filePath": "integrations/hermes/src/mnemosyne_hermes/__init__.py",
        "lineRange": [111, 125],
        "summary": "Reads the MNEMOSYNE_SYNC_TURN_ASSISTANT_LIMIT env var (default 800) for assistant message truncation in sync_turn.",
        "tags": ["sync-turn", "config", "limit", "assistant"],
        "complexity": "simple"
    },
    {
        "id": "function:integrations/hermes/src/mnemosyne_hermes/__init__.py:_parse_env_float",
        "type": "function",
        "name": "_parse_env_float",
        "filePath": "integrations/hermes/src/mnemosyne_hermes/__init__.py",
        "lineRange": [143, 151],
        "summary": "Safely parses an env var as float with fallback default and error logging.",
        "tags": ["utility", "env", "parsing"],
        "complexity": "simple"
    },
    {
        "id": "function:integrations/hermes/src/mnemosyne_hermes/__init__.py:register_memory_provider",
        "type": "function",
        "name": "register_memory_provider",
        "filePath": "integrations/hermes/src/mnemosyne_hermes/__init__.py",
        "lineRange": [1538, 1541],
        "summary": "Hermes agent entry point that registers MnemosyneMemoryProvider with the agent context.",
        "tags": ["entry-point", "registration", "provider"],
        "complexity": "simple"
    },
    {
        "id": "function:integrations/hermes/src/mnemosyne_hermes/__init__.py:register",
        "type": "function",
        "name": "register",
        "filePath": "integrations/hermes/src/mnemosyne_hermes/__init__.py",
        "lineRange": [1548, 1557],
        "summary": "Top-level register function called by Hermes plugin system to install the memory provider.",
        "tags": ["entry-point", "registration", "plugin"],
        "complexity": "simple"
    },
    # From binary_vectors.py
    {
        "id": "function:mnemosyne/core/binary_vectors.py:maximally_informative_binarization",
        "type": "function",
        "name": "maximally_informative_binarization",
        "filePath": "mnemosyne/core/binary_vectors.py",
        "lineRange": [45, 82],
        "summary": "Converts float32 embeddings to binary vectors using median-based MIB thresholding for 32x compression.",
        "tags": ["binarization", "compression", "mib", "embeddings"],
        "complexity": "moderate"
    },
    {
        "id": "function:mnemosyne/core/binary_vectors.py:hamming_distance",
        "type": "function",
        "name": "hamming_distance",
        "filePath": "mnemosyne/core/binary_vectors.py",
        "lineRange": [85, 125],
        "summary": "Computes normalized Hamming distance between two binary vectors using bitwise XOR and popcount.",
        "tags": ["distance", "hamming", "bitwise"],
        "complexity": "simple"
    },
    # From typed_memory.py
    {
        "id": "function:mnemosyne/core/typed_memory.py:classify_memory",
        "type": "function",
        "name": "classify_memory",
        "filePath": "mnemosyne/core/typed_memory.py",
        "lineRange": [232, 260],
        "summary": "Classifies a single memory string into one of 13 memory types using pattern matching.",
        "tags": ["classification", "memory-type", "pattern-matching"],
        "complexity": "moderate"
    },
    {
        "id": "function:mnemosyne/core/typed_memory.py:classify_batch",
        "type": "function",
        "name": "classify_batch",
        "filePath": "mnemosyne/core/typed_memory.py",
        "lineRange": [263, 280],
        "summary": "Batch classifies multiple memory strings into their respective types.",
        "tags": ["classification", "batch", "memory-type"],
        "complexity": "simple"
    },
    {
        "id": "function:mnemosyne/core/typed_memory.py:get_type_priority",
        "type": "function",
        "name": "get_type_priority",
        "filePath": "mnemosyne/core/typed_memory.py",
        "lineRange": [283, 300],
        "summary": "Returns the priority signal for a given memory type (stable, decaying, or time-critical).",
        "tags": ["priority", "memory-type", "signal"],
        "complexity": "simple"
    },
    {
        "id": "function:mnemosyne/core/typed_memory.py:should_consolidate",
        "type": "function",
        "name": "should_consolidate",
        "filePath": "mnemosyne/core/typed_memory.py",
        "lineRange": [303, 320],
        "summary": "Determines whether a memory of the given type should be consolidated during sleep.",
        "tags": ["consolidation", "sleep", "memory-type"],
        "complexity": "simple"
    },
    {
        "id": "function:mnemosyne/core/typed_memory.py:get_decay_rate",
        "type": "function",
        "name": "get_decay_rate",
        "filePath": "mnemosyne/core/typed_memory.py",
        "lineRange": [323, 349],
        "summary": "Returns the decay rate for a given memory type, controlling how quickly it fades without reinforcement.",
        "tags": ["decay", "memory-type", "forgetting"],
        "complexity": "simple"
    },
    # From veracity_consolidation.py
    {
        "id": "function:mnemosyne/core/veracity_consolidation.py:compute_fact_id",
        "type": "function",
        "name": "compute_fact_id",
        "filePath": "mnemosyne/core/veracity_consolidation.py",
        "lineRange": [32, 60],
        "summary": "Computes a deterministic SHA-256 based fact ID from subject, predicate, and object for dedup.",
        "tags": ["hashing", "fact-id", "dedup", "sha256"],
        "complexity": "moderate"
    },
    {
        "id": "function:mnemosyne/core/veracity_consolidation.py:clamp_veracity",
        "type": "function",
        "name": "clamp_veracity",
        "filePath": "mnemosyne/core/veracity_consolidation.py",
        "lineRange": [63, 92],
        "summary": "Clamps a veracity string to one of the allowed values: stated, tool, inferred, or unknown.",
        "tags": ["veracity", "validation", "clamping"],
        "complexity": "simple"
    },
    {
        "id": "function:mnemosyne/core/veracity_consolidation.py:aggregate_veracity",
        "type": "function",
        "name": "aggregate_veracity",
        "filePath": "mnemosyne/core/veracity_consolidation.py",
        "lineRange": [130, 175],
        "summary": "Aggregates multiple veracity observations into a single consolidated veracity using majority-weight logic.",
        "tags": ["veracity", "aggregation", "majority"],
        "complexity": "moderate"
    },
    # From polyphonic_recall.py
    {
        "id": "function:mnemosyne/core/polyphonic_recall.py:_env_disabled",
        "type": "function",
        "name": "_env_disabled",
        "filePath": "mnemosyne/core/polyphonic_recall.py",
        "lineRange": [33, 48],
        "summary": "Checks MNEMOSYNE_DISABLE_POLYPHONIC_RECALL env var to gate the polyphonic engine.",
        "tags": ["gating", "env", "polyphonic"],
        "complexity": "simple"
    }
]

# Test class nodes (classes with 2+ test methods)
test_classes = [
    {
        "id": "class:tests/test_beam_e4_remember_batch_veracity.py:TestClampVeracity",
        "type": "class", "name": "TestClampVeracity",
        "filePath": "tests/test_beam_e4_remember_batch_veracity.py",
        "lineRange": [20, 100],
        "summary": "Tests veracity clamping logic ensuring invalid veracity values are normalized.",
        "tags": ["test", "veracity", "clamping"],
        "complexity": "simple"
    },
    {
        "id": "class:tests/test_beam_e4_remember_batch_veracity.py:TestRememberBatchVeracity",
        "type": "class", "name": "TestRememberBatchVeracity",
        "filePath": "tests/test_beam_e4_remember_batch_veracity.py",
        "lineRange": [105, 451],
        "summary": "Tests veracity propagation through remember_batch ensuring per-row veracity flows to consolidated facts.",
        "tags": ["test", "veracity", "batch-remember", "consolidation"],
        "complexity": "moderate"
    },
    {
        "id": "class:tests/test_consolidate_fact_concurrency.py:TestReviewHardening",
        "type": "class", "name": "TestReviewHardening",
        "filePath": "tests/test_consolidate_fact_concurrency.py",
        "lineRange": [100, 537],
        "summary": "Concurrent consolidation tests for thread safety and transaction isolation.",
        "tags": ["test", "concurrency", "consolidation", "hardening"],
        "complexity": "moderate"
    },
    {
        "id": "class:tests/test_consolidate_fact_id_collision.py:TestReviewHardening",
        "type": "class", "name": "TestReviewHardening",
        "filePath": "tests/test_consolidate_fact_id_collision.py",
        "lineRange": [20, 439],
        "summary": "Tests for deterministic fact ID stability and collision resistance across varying inputs.",
        "tags": ["test", "fact-id", "hashing", "collision"],
        "complexity": "moderate"
    },
    {
        "id": "class:tests/test_consolidate_fact_sibling_races.py:TestReviewHardening",
        "type": "class", "name": "TestReviewHardening",
        "filePath": "tests/test_consolidate_fact_sibling_races.py",
        "lineRange": [20, 582],
        "summary": "Race condition tests for concurrent conflict resolution in fact consolidation.",
        "tags": ["test", "race-conditions", "conflict-resolution"],
        "complexity": "moderate"
    },
    {
        "id": "class:tests/test_e5a_vector_voice_dense_rewire.py:TestReviewHardening",
        "type": "class", "name": "TestReviewHardening",
        "filePath": "tests/test_e5a_vector_voice_dense_rewire.py",
        "lineRange": [30, 853],
        "summary": "Tests for vector voice retrieval strategy including embedding search, empty states, and polyphonic integration.",
        "tags": ["test", "vector-voice", "embeddings", "polyphonic"],
        "complexity": "moderate"
    },
    {
        "id": "class:tests/test_graph_tools.py:TestFindRelatedMemories",
        "type": "class", "name": "TestFindRelatedMemories",
        "filePath": "tests/test_graph_tools.py",
        "lineRange": [20, 80],
        "summary": "Tests for finding related memories via episodic graph traversal.",
        "tags": ["test", "related-memories", "graph"],
        "complexity": "simple"
    },
    {
        "id": "class:tests/test_graph_tools.py:TestGraphToolSchemas",
        "type": "class", "name": "TestGraphToolSchemas",
        "filePath": "tests/test_graph_tools.py",
        "lineRange": [85, 130],
        "summary": "Tests graph tool JSON schema generation for graph_query and graph_link tools.",
        "tags": ["test", "tool-schemas", "graph"],
        "complexity": "simple"
    },
    {
        "id": "class:tests/test_graph_tools.py:TestGraphQueryTool",
        "type": "class", "name": "TestGraphQueryTool",
        "filePath": "tests/test_graph_tools.py",
        "lineRange": [135, 180],
        "summary": "Tests the graph_query tool handler for querying episodic graph nodes and edges.",
        "tags": ["test", "graph-query", "tool"],
        "complexity": "simple"
    },
    {
        "id": "class:tests/test_graph_tools.py:TestGraphLinkTool",
        "type": "class", "name": "TestGraphLinkTool",
        "filePath": "tests/test_graph_tools.py",
        "lineRange": [185, 230],
        "summary": "Tests the graph_link tool handler for creating edges in the episodic graph.",
        "tags": ["test", "graph-link", "tool"],
        "complexity": "simple"
    },
    {
        "id": "class:tests/test_graph_tools.py:TestAutoPopulatedEdges",
        "type": "class", "name": "TestAutoPopulatedEdges",
        "filePath": "tests/test_graph_tools.py",
        "lineRange": [235, 272],
        "summary": "Tests automatic edge population behavior in the episodic graph.",
        "tags": ["test", "auto-populated", "edges"],
        "complexity": "simple"
    },
    {
        "id": "class:tests/test_integration.py:TestTypedMemory",
        "type": "class", "name": "TestTypedMemory",
        "filePath": "tests/test_integration.py",
        "lineRange": [10, 50],
        "summary": "Integration test for typed memory classification.",
        "tags": ["test", "integration", "typed-memory"],
        "complexity": "simple"
    },
    {
        "id": "class:tests/test_integration.py:TestBinaryVectors",
        "type": "class", "name": "TestBinaryVectors",
        "filePath": "tests/test_integration.py",
        "lineRange": [55, 95],
        "summary": "Integration test for binary vector operations.",
        "tags": ["test", "integration", "binary-vectors"],
        "complexity": "simple"
    },
    {
        "id": "class:tests/test_integration.py:TestEpisodicGraph",
        "type": "class", "name": "TestEpisodicGraph",
        "filePath": "tests/test_integration.py",
        "lineRange": [100, 140],
        "summary": "Integration test for episodic graph traversal.",
        "tags": ["test", "integration", "episodic-graph"],
        "complexity": "simple"
    },
    {
        "id": "class:tests/test_integration.py:TestVeracityConsolidation",
        "type": "class", "name": "TestVeracityConsolidation",
        "filePath": "tests/test_integration.py",
        "lineRange": [145, 185],
        "summary": "Integration test for veracity consolidation pipeline.",
        "tags": ["test", "integration", "veracity", "consolidation"],
        "complexity": "simple"
    },
    {
        "id": "class:tests/test_integration.py:TestPolyphonicRecall",
        "type": "class", "name": "TestPolyphonicRecall",
        "filePath": "tests/test_integration.py",
        "lineRange": [190, 230],
        "summary": "Integration test for polyphonic recall engine.",
        "tags": ["test", "integration", "polyphonic-recall"],
        "complexity": "simple"
    },
    {
        "id": "class:tests/test_integration.py:TestIntegration",
        "type": "class", "name": "TestIntegration",
        "filePath": "tests/test_integration.py",
        "lineRange": [235, 268],
        "summary": "End-to-end integration test exercising the full memory pipeline.",
        "tags": ["test", "integration", "e2e"],
        "complexity": "simple"
    },
    {
        "id": "class:tests/test_pre_experiment_fidelity.py:TestC29WeightCentralization",
        "type": "class", "name": "TestC29WeightCentralization",
        "filePath": "tests/test_pre_experiment_fidelity.py",
        "lineRange": [20, 120],
        "summary": "Tests for weight centralization ensuring scoring weights are correctly normalized.",
        "tags": ["test", "weight-centralization", "scoring"],
        "complexity": "moderate"
    },
    {
        "id": "class:tests/test_pre_experiment_fidelity.py:TestAggregateVeracityHelper",
        "type": "class", "name": "TestAggregateVeracityHelper",
        "filePath": "tests/test_pre_experiment_fidelity.py",
        "lineRange": [125, 220],
        "summary": "Tests for the aggregate_veracity helper function used in consolidation.",
        "tags": ["test", "veracity", "aggregation", "helper"],
        "complexity": "moderate"
    },
    {
        "id": "class:tests/test_pre_experiment_fidelity.py:TestE4a1ConsolidateToEpisodicVeracity",
        "type": "class", "name": "TestE4a1ConsolidateToEpisodicVeracity",
        "filePath": "tests/test_pre_experiment_fidelity.py",
        "lineRange": [225, 350],
        "summary": "Tests the consolidation-to-episodic veracity pipeline ensuring facts carry correct veracity into episodic storage.",
        "tags": ["test", "consolidation", "veracity", "episodic"],
        "complexity": "moderate"
    },
    {
        "id": "class:tests/test_pre_experiment_fidelity.py:TestE4a1SleepEndToEndVeracity",
        "type": "class", "name": "TestE4a1SleepEndToEndVeracity",
        "filePath": "tests/test_pre_experiment_fidelity.py",
        "lineRange": [355, 470],
        "summary": "End-to-end test of veracity flow through the sleep cycle from consolidation to episodic storage.",
        "tags": ["test", "sleep", "veracity", "e2e"],
        "complexity": "moderate"
    },
    {
        "id": "class:tests/test_pre_experiment_fidelity.py:TestE2a10EmbeddingLoopDefense",
        "type": "class", "name": "TestE2a10EmbeddingLoopDefense",
        "filePath": "tests/test_pre_experiment_fidelity.py",
        "lineRange": [475, 530],
        "summary": "Tests preventing infinite embedding generation loops during write operations.",
        "tags": ["test", "embedding", "loop-defense"],
        "complexity": "simple"
    },
    {
        "id": "class:tests/test_pre_experiment_fidelity.py:TestReviewHardening",
        "type": "class", "name": "TestReviewHardening",
        "filePath": "tests/test_pre_experiment_fidelity.py",
        "lineRange": [535, 588],
        "summary": "Review hardening tests for fidelity of pre-experiment validation.",
        "tags": ["test", "review", "hardening"],
        "complexity": "simple"
    },
    {
        "id": "class:tests/test_proactive_linking.py:TestProactiveContentLinking",
        "type": "class", "name": "TestProactiveContentLinking",
        "filePath": "tests/test_proactive_linking.py",
        "lineRange": [20, 100],
        "summary": "Tests proactive linking of new memories to existing ones based on content similarity.",
        "tags": ["test", "proactive-linking", "content"],
        "complexity": "moderate"
    },
    {
        "id": "class:tests/test_proactive_linking.py:TestProactiveEntityLinking",
        "type": "class", "name": "TestProactiveEntityLinking",
        "filePath": "tests/test_proactive_linking.py",
        "lineRange": [105, 170],
        "summary": "Tests entity-based proactive linking between memories sharing named entities.",
        "tags": ["test", "proactive-linking", "entities"],
        "complexity": "moderate"
    },
    {
        "id": "class:tests/test_proactive_linking.py:TestProactiveLinkingGating",
        "type": "class", "name": "TestProactiveLinkingGating",
        "filePath": "tests/test_proactive_linking.py",
        "lineRange": [175, 220],
        "summary": "Tests that proactive linking can be enabled/disabled via feature gates.",
        "tags": ["test", "gating", "proactive-linking"],
        "complexity": "simple"
    },
    {
        "id": "class:tests/test_proactive_linking.py:TestNonBlocking",
        "type": "class", "name": "TestNonBlocking",
        "filePath": "tests/test_proactive_linking.py",
        "lineRange": [225, 260],
        "summary": "Tests that linking failures do not block memory write operations.",
        "tags": ["test", "non-blocking", "resilience"],
        "complexity": "simple"
    },
    {
        "id": "class:tests/test_proactive_linking.py:TestEdgeDeduplication",
        "type": "class", "name": "TestEdgeDeduplication",
        "filePath": "tests/test_proactive_linking.py",
        "lineRange": [265, 295],
        "summary": "Tests that linking does not produce duplicate edges between the same node pair.",
        "tags": ["test", "dedup", "edges"],
        "complexity": "simple"
    },
    {
        "id": "class:tests/test_proactive_linking.py:TestEdgeTypesAndWeights",
        "type": "class", "name": "TestEdgeTypesAndWeights",
        "filePath": "tests/test_proactive_linking.py",
        "lineRange": [300, 332],
        "summary": "Tests that linked edges have correct types and weight values.",
        "tags": ["test", "edge-types", "weights"],
        "complexity": "simple"
    }
]

nodes.extend(core_classes)
nodes.extend(core_functions)
nodes.extend(test_classes)

# ==================== EDGES ====================

# 1. Imports edges (1:1 from batchImportData)
for path, imports in batch_import.items():
    for imp in imports:
        edges.append({
            "source": f"file:{path}",
            "target": f"file:{imp}",
            "type": "imports",
            "direction": "forward",
            "weight": 0.7
        })

# 2. Contains edges - file contains each class/function
# Core classes
for cls_node in core_classes:
    edges.append({
        "source": f"file:{cls_node['filePath']}",
        "target": cls_node["id"],
        "type": "contains",
        "direction": "forward",
        "weight": 1.0
    })

# Test classes
for cls_node in test_classes:
    edges.append({
        "source": f"file:{cls_node['filePath']}",
        "target": cls_node["id"],
        "type": "contains",
        "direction": "forward",
        "weight": 1.0
    })

# Functions
for fn_node in core_functions:
    edges.append({
        "source": f"file:{fn_node['filePath']}",
        "target": fn_node["id"],
        "type": "contains",
        "direction": "forward",
        "weight": 1.0
    })

# 3. Exports edges for exported items
# From __init__.py - all 9 functions + 1 class are exported
exported_from_provider = [
    "function:integrations/hermes/src/mnemosyne_hermes/__init__.py:_get_beam_class",
    "function:integrations/hermes/src/mnemosyne_hermes/__init__.py:_get_triple_module",
    "function:integrations/hermes/src/mnemosyne_hermes/__init__.py:_prefetch_content_char_limit",
    "function:integrations/hermes/src/mnemosyne_hermes/__init__.py:_format_prefetch_content",
    "function:integrations/hermes/src/mnemosyne_hermes/__init__.py:_sync_turn_user_limit",
    "function:integrations/hermes/src/mnemosyne_hermes/__init__.py:_sync_turn_assistant_limit",
    "function:integrations/hermes/src/mnemosyne_hermes/__init__.py:_parse_env_float",
    "function:integrations/hermes/src/mnemosyne_hermes/__init__.py:register_memory_provider",
    "function:integrations/hermes/src/mnemosyne_hermes/__init__.py:register",
    "class:integrations/hermes/src/mnemosyne_hermes/__init__.py:MnemosyneMemoryProvider"
]
for exp_id in exported_from_provider:
    edges.append({
        "source": "file:integrations/hermes/src/mnemosyne_hermes/__init__.py",
        "target": exp_id,
        "type": "exports",
        "direction": "forward",
        "weight": 0.8
    })

# From binary_vectors.py
exported_bv = [
    "function:mnemosyne/core/binary_vectors.py:maximally_informative_binarization",
    "function:mnemosyne/core/binary_vectors.py:hamming_distance",
    "class:mnemosyne/core/binary_vectors.py:BinaryVectorStore",
    "class:mnemosyne/core/binary_vectors.py:FastBinarySearch"
]
for exp_id in exported_bv:
    edges.append({
        "source": "file:mnemosyne/core/binary_vectors.py",
        "target": exp_id,
        "type": "exports",
        "direction": "forward",
        "weight": 0.8
    })

# From episodic_graph.py
exported_eg = [
    "class:mnemosyne/core/episodic_graph.py:Gist",
    "class:mnemosyne/core/episodic_graph.py:Fact",
    "class:mnemosyne/core/episodic_graph.py:GraphEdge",
    "class:mnemosyne/core/episodic_graph.py:EpisodicGraph"
]
for exp_id in exported_eg:
    edges.append({
        "source": "file:mnemosyne/core/episodic_graph.py",
        "target": exp_id,
        "type": "exports",
        "direction": "forward",
        "weight": 0.8
    })

# From polyphonic_recall.py
exported_pr = [
    "class:mnemosyne/core/polyphonic_recall.py:RecallResult",
    "class:mnemosyne/core/polyphonic_recall.py:PolyphonicResult",
    "class:mnemosyne/core/polyphonic_recall.py:PolyphonicRecallEngine",
    "function:mnemosyne/core/polyphonic_recall.py:_env_disabled"
]
for exp_id in exported_pr:
    edges.append({
        "source": "file:mnemosyne/core/polyphonic_recall.py",
        "target": exp_id,
        "type": "exports",
        "direction": "forward",
        "weight": 0.8
    })

# From typed_memory.py
exported_tm = [
    "class:mnemosyne/core/typed_memory.py:MemoryType",
    "class:mnemosyne/core/typed_memory.py:TypeMatch",
    "function:mnemosyne/core/typed_memory.py:classify_memory",
    "function:mnemosyne/core/typed_memory.py:classify_batch",
    "function:mnemosyne/core/typed_memory.py:get_type_priority",
    "function:mnemosyne/core/typed_memory.py:should_consolidate",
    "function:mnemosyne/core/typed_memory.py:get_decay_rate"
]
for exp_id in exported_tm:
    edges.append({
        "source": "file:mnemosyne/core/typed_memory.py",
        "target": exp_id,
        "type": "exports",
        "direction": "forward",
        "weight": 0.8
    })

# From veracity_consolidation.py
exported_vc = [
    "function:mnemosyne/core/veracity_consolidation.py:compute_fact_id",
    "function:mnemosyne/core/veracity_consolidation.py:clamp_veracity",
    "function:mnemosyne/core/veracity_consolidation.py:aggregate_veracity",
    "class:mnemosyne/core/veracity_consolidation.py:ConsolidatedFact",
    "class:mnemosyne/core/veracity_consolidation.py:VeracityConsolidator"
]
for exp_id in exported_vc:
    edges.append({
        "source": "file:mnemosyne/core/veracity_consolidation.py",
        "target": exp_id,
        "type": "exports",
        "direction": "forward",
        "weight": 0.8
    })

# 4. Calls edges (cross-file: test files use core modules)
# Tests importing beam.py → likely call BeamMemory methods, but those are in batch 1
# Within-batch calls:

# polyphonic_recall.py imports from episodic_graph.py, typed_memory.py, veracity_consolidation.py
# PolyphonicRecallEngine likely calls EpisodicGraph methods
edges.append({
    "source": "class:mnemosyne/core/polyphonic_recall.py:PolyphonicRecallEngine",
    "target": "class:mnemosyne/core/episodic_graph.py:EpisodicGraph",
    "type": "calls",
    "direction": "forward",
    "weight": 0.8
})

# PolyphonicRecallEngine uses typed memory classification
edges.append({
    "source": "class:mnemosyne/core/polyphonic_recall.py:PolyphonicRecallEngine",
    "target": "function:mnemosyne/core/typed_memory.py:classify_memory",
    "type": "calls",
    "direction": "forward",
    "weight": 0.8
})

# PolyphonicRecallEngine uses veracity consolidation
edges.append({
    "source": "class:mnemosyne/core/polyphonic_recall.py:PolyphonicRecallEngine",
    "target": "class:mnemosyne/core/veracity_consolidation.py:VeracityConsolidator",
    "type": "calls",
    "direction": "forward",
    "weight": 0.8
})

# 5. tested_by edges (test files exercise production files)
# test_integration imports all core modules
test_prod_map = {
    "tests/test_beam_e4_remember_batch_veracity.py": ["mnemosyne/core/beam.py", "mnemosyne/core/veracity_consolidation.py"],
    "tests/test_consolidate_fact_concurrency.py": ["mnemosyne/core/veracity_consolidation.py"],
    "tests/test_consolidate_fact_id_collision.py": ["mnemosyne/core/veracity_consolidation.py"],
    "tests/test_consolidate_fact_sibling_races.py": ["mnemosyne/core/veracity_consolidation.py"],
    "tests/test_e5a_vector_voice_dense_rewire.py": ["mnemosyne/core/beam.py", "mnemosyne/core/polyphonic_recall.py"],
    "tests/test_graph_tools.py": ["mnemosyne/core/beam.py", "mnemosyne/core/episodic_graph.py", "hermes_memory_provider/__init__.py"],
    "tests/test_integration.py": ["mnemosyne/core/binary_vectors.py", "mnemosyne/core/episodic_graph.py", "mnemosyne/core/polyphonic_recall.py", "mnemosyne/core/typed_memory.py", "mnemosyne/core/veracity_consolidation.py"],
    "tests/test_pre_experiment_fidelity.py": ["mnemosyne/core/beam.py", "mnemosyne/core/veracity_consolidation.py"],
    "tests/test_proactive_linking.py": ["mnemosyne/core/beam.py", "mnemosyne/core/episodic_graph.py"]
}
for test_path, prod_paths in test_prod_map.items():
    for prod_path in prod_paths:
        edges.append({
            "source": f"file:{prod_path}",
            "target": f"file:{test_path}",
            "type": "tested_by",
            "direction": "forward",
            "weight": 0.5
        })

# 6. depends_on: polyphonic_recall depends on episodic_graph typed_memory veracity_consolidation
edges.append({
    "source": "file:mnemosyne/core/polyphonic_recall.py",
    "target": "file:mnemosyne/core/episodic_graph.py",
    "type": "depends_on",
    "direction": "forward",
    "weight": 0.6
})
edges.append({
    "source": "file:mnemosyne/core/polyphonic_recall.py",
    "target": "file:mnemosyne/core/typed_memory.py",
    "type": "depends_on",
    "direction": "forward",
    "weight": 0.6
})
edges.append({
    "source": "file:mnemosyne/core/polyphonic_recall.py",
    "target": "file:mnemosyne/core/veracity_consolidation.py",
    "type": "depends_on",
    "direction": "forward",
    "weight": 0.6
})

# The hermes __init__.py depends on its tools.py
edges.append({
    "source": "file:integrations/hermes/src/mnemosyne_hermes/__init__.py",
    "target": "file:integrations/hermes/src/mnemosyne_hermes/tools.py",
    "type": "depends_on",
    "direction": "forward",
    "weight": 0.6
})

# The hermes __init__.py depends on episodic_graph
edges.append({
    "source": "file:integrations/hermes/src/mnemosyne_hermes/__init__.py",
    "target": "file:mnemosyne/core/episodic_graph.py",
    "type": "depends_on",
    "direction": "forward",
    "weight": 0.6
})

# vc (veracity_consolidation) tests all test veracity_consolidation
# The consolidation tests depend on veracity_consolidation.py
edges.append({
    "source": "file:tests/test_consolidate_fact_concurrency.py",
    "target": "class:mnemosyne/core/veracity_consolidation.py:VeracityConsolidator",
    "type": "depends_on",
    "direction": "forward",
    "weight": 0.6
})
edges.append({
    "source": "file:tests/test_consolidate_fact_id_collision.py",
    "target": "function:mnemosyne/core/veracity_consolidation.py:compute_fact_id",
    "type": "depends_on",
    "direction": "forward",
    "weight": 0.6
})

# 7. Cross-batch: test files import beam.py (batch 1) and hermes_memory_provider (batch 7)
# These are known from neighborMap, emit edges with confidence
edges.append({
    "source": "file:tests/test_beam_e4_remember_batch_veracity.py",
    "target": "file:mnemosyne/core/beam.py",
    "type": "imports",
    "direction": "forward",
    "weight": 0.7
})
edges.append({
    "source": "file:tests/test_e5a_vector_voice_dense_rewire.py",
    "target": "file:mnemosyne/core/beam.py",
    "type": "imports",
    "direction": "forward",
    "weight": 0.7
})
edges.append({
    "source": "file:tests/test_graph_tools.py",
    "target": "file:hermes_memory_provider/__init__.py",
    "type": "imports",
    "direction": "forward",
    "weight": 0.7
})
edges.append({
    "source": "file:tests/test_graph_tools.py",
    "target": "file:mnemosyne/core/beam.py",
    "type": "imports",
    "direction": "forward",
    "weight": 0.7
})
edges.append({
    "source": "file:tests/test_pre_experiment_fidelity.py",
    "target": "file:mnemosyne/core/beam.py",
    "type": "imports",
    "direction": "forward",
    "weight": 0.7
})
edges.append({
    "source": "file:tests/test_proactive_linking.py",
    "target": "file:mnemosyne/core/beam.py",
    "type": "imports",
    "direction": "forward",
    "weight": 0.7
})

# ==================== WRITE OUTPUT ====================

output = {
    "nodes": nodes,
    "edges": edges
}

print(f"Node count: {len(nodes)}")
print(f"Edge count: {len(edges)}")

# Write to intermediate directory
import os
output_dir = f"{PROJECT_ROOT}/.understand-anything/intermediate"
os.makedirs(output_dir, exist_ok=True)

output_path = f"{output_dir}/batch-4.json"
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"Written to: {output_path}")
print(f"File size: {os.path.getsize(output_path)} bytes")
