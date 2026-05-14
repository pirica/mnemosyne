# Mnemosyne — Session Continuation Reference

## Branch
`fix/mention-entity-extraction-quality` (fork: ether-btc/mnemosyne)

## PR
**Open**: https://github.com/AxDSan/mnemosyne/pull/120

## What was done (4 commits)

### Commit 1: `65e23c9` — Write-time entity extraction fix
- Expanded `ENTITY_EXTRACTION_STOP_WORDS` with 40+ meta/system words
- Made stopword filter case-insensitive (`.lower()`)
- Added any-word-stopword filter (drops entities if ANY word is a stopword)
- Changes: `mnemosyne/core/entities.py` only

### Commit 2: `0f0db2c` — Retrieval-time noisy-mention filter
- Added `_is_noisy_mention()` and `filter_clean_mentions()` to `annotations.py`
- Added `filter_noise=True` parameter to `AnnotationStore.query_by_kind()` — filters
  noise at retrieval time instead of requiring destructive SQL DELETE from the DB
- Updates `CONTINUE_HERE.md` with verified test results

### Commit 3: `3bea98e` — Non-destructive defense-in-depth
- Updated test cases to match new any-word-stopword behavior
- Added `scripts/cleanup_noisy_mentions.py` for optional post-merge DB cleanup

### Commit 4: `e9c1c9b` — Trim aggressive meta stopword list per PR review
- Trimmed `_META_STOP_WORDS` from 46 → 23 words per PR #120 review feedback
- Removed: ai, memory, mnemosyne, conversation, fact, hermes, agent, model, system,
  note, task, project, result, output, input, data, step, process, point, way, thing,
  time, work
- These are legitimate entity candidates (project names, technical terms) that were
  incorrectly filtered out by the initial overly-aggressive list
- Verification: 40/40 tests pass (32 entity tests + 8 integration tests)

## Verification (tested)
- All 40 tests pass ✓ (32 entities + 8 integration)
- Stopword sets synchronized between entities.py and annotations.py (94 words, identical)

## Git state
- Local branch: `fix/mention-entity-extraction-quality`
- Pushed to: `origin/fix/mention-entity-extraction-quality`
- Commits ahead of `origin/main`: 4
- PR review comment posted confirming the fix
