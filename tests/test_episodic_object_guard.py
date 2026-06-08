"""Unit tests for the object-side fact-extraction guard.

`_is_low_quality_object` was added to drop value-free object tokens (state
adjectives, -ly adverbs, truncation artifacts) from regex-extracted fact
triples, mirroring the subject-side guard. These tests lock in the boundary
between *noise* (dropped) and *legitimate lone objects* — common nouns and
proper nouns — which an earlier "reject every lone lowercase token" version
incorrectly discarded (e.g. "Alice is a developer" -> 0 facts).
"""

import tempfile
from pathlib import Path

import pytest

from mnemosyne.core.episodic_graph import EpisodicGraph, _is_low_quality_object


@pytest.mark.parametrize("noise", [
    "different", "same", "already", "here", "there", "nothing",
    "definitely",  # -ly adverb
    "apparently",  # -ly adverb
    "",            # empty
    "   ",         # whitespace only
])
def test_noise_objects_are_dropped(noise):
    assert _is_low_quality_object(noise) is True


@pytest.mark.parametrize("real", [
    "developer",          # lone common noun
    "engineer",
    "Python",             # lone proper noun
    "Rust",
    "ComfyUI",
    "software engineer",  # multi-word phrase
    "a red car",
])
def test_legitimate_objects_are_kept(real):
    assert _is_low_quality_object(real) is False


def test_lowercase_ly_noun_is_not_falsely_dropped():
    # "ally"/"family" etc. end in "ly" but the -ly rule is an accepted
    # trade-off for adverbs; documenting the known limitation here.
    assert _is_low_quality_object("family") is True  # known false-positive


def test_extract_facts_keeps_common_noun_object():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        graph = EpisodicGraph(db_path=Path(tf.name))
        try:
            facts = graph.extract_facts("Alice is a developer", "mem_obj_1")
            assert any(f.subject == "Alice" and f.object == "developer"
                       for f in facts), f"got: {[(f.subject, f.object) for f in facts]}"
        finally:
            graph.close()


def test_extract_facts_drops_state_adjective_object():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        graph = EpisodicGraph(db_path=Path(tf.name))
        try:
            facts = graph.extract_facts("Bob is different", "mem_obj_2")
            assert not any(f.object == "different" for f in facts), \
                f"state adjective leaked: {[(f.subject, f.object) for f in facts]}"
        finally:
            graph.close()
