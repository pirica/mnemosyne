#!/usr/bin/env python3
"""
Cleanup script for noisy mention annotations in Mnemosyne DB.

Removes annotations whose values are meta-system noise words that leaked
in before the entity extraction stopword fix (PR #120).

Imports the canonical stopword set from entities.py so any future additions
to the stopword list are automatically picked up.

Usage:
    python3 scripts/cleanup_noisy_mentions.py [--dry-run] [--db PATH]
"""
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from mnemosyne.core.entities import ENTITY_EXTRACTION_STOP_WORDS

DB_DEFAULT = Path.home() / ".hermes" / "mnemosyne" / "data" / "mnemosyne.db"


def _is_noisy(value: str) -> bool:
    """Return True if the value is a known noisy mention (single or multi-word)."""
    words = value.split()
    if len(words) == 1:
        return words[0].lower() in ENTITY_EXTRACTION_STOP_WORDS
    return any(w.lower() in ENTITY_EXTRACTION_STOP_WORDS for w in words)


def main():
    dry_run = "--dry-run" in sys.argv

    db_path = DB_DEFAULT
    if "--db" in sys.argv:
        idx = sys.argv.index("--db")
        if idx + 1 < len(sys.argv):
            db_path = Path(sys.argv[idx + 1])

    if not db_path.exists():
        print(f"Error: database not found at {db_path}")
        sys.exit(1)

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM annotations WHERE kind='mentions'")
    total = cursor.fetchone()[0]
    print(f"Total mentions before cleanup: {total}")

    cursor.execute("SELECT id, value FROM annotations WHERE kind='mentions'")
    all_rows = cursor.fetchall()

    noisy_ids = [row_id for row_id, val in all_rows if _is_noisy(val)]
    noisy_total = len(noisy_ids)

    if not noisy_total:
        print("No noisy annotations found. Database is clean.")
        conn.close()
        return

    # Breakdown
    from collections import Counter
    noisy_vals = Counter()
    for row_id, val in all_rows:
        if _is_noisy(val):
            noisy_vals[val] += 1
    print(f"Noisy annotations to remove: {noisy_total}")
    print("\nBreakdown by value:")
    for val, cnt in noisy_vals.most_common():
        print(f"  {val}: {cnt}")

    if dry_run:
        print(f"\n[DRY RUN] Would delete {noisy_total} annotations from {db_path}")
        conn.close()
        return

    # Backup
    backup_path = db_path.with_suffix(
        f".pre_stopword_cleanup.{datetime.now().strftime('%Y%m%d%H%M%S')}{db_path.suffix}"
    )
    import shutil
    shutil.copy2(str(db_path), str(backup_path))
    print(f"\nBackup created: {backup_path}")

    # Delete noisy annotations
    cursor.execute(
        "DELETE FROM annotations WHERE id IN ({})".format(
            ",".join("?" for _ in noisy_ids)
        ),
        noisy_ids,
    )
    conn.commit()
    print(f"Deleted {cursor.rowcount} noisy annotations")

    # Verify
    cursor.execute("SELECT COUNT(*) FROM annotations WHERE kind='mentions'")
    remaining = cursor.fetchone()[0]
    print(f"Remaining mentions: {remaining}")

    print("\nTop 15 surviving mentions:")
    cursor.execute(
        "SELECT value, COUNT(*) as cnt FROM annotations "
        "WHERE kind='mentions' GROUP BY value ORDER BY cnt DESC LIMIT 15"
    )
    for val, cnt in cursor.fetchall():
        print(f"  {val}: {cnt}")

    conn.close()
    print(f"\nCleanup complete. Backup: {backup_path}")


if __name__ == "__main__":
    main()
