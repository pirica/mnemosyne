#!/usr/bin/env python3
"""Verify that generated docs match the provider code.

Snapshots generated output and diffs against committed state.
Exits non-zero if generated content differs.

Usage:
    python3 scripts/verify-docs.py [--fix]
"""

import argparse
import os
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description="Verify generated docs match code")
    parser.add_argument("--fix", action="store_true", help="Auto-fix by running generator")
    args = parser.parse_args()

    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    generator = os.path.join(repo, "scripts", "generate-docs.py")

    # Check committed canonical copies first (they live in the mnemosyne repo)
    canonical = os.path.join(repo, "docs", "api")

    # Fallback: sibling mnemosyne-docs repo (for website mirror verification)
    sibling = os.path.join(os.path.dirname(repo), "mnemosyne-docs", "src")

    if not os.path.isfile(generator):
        print("ERROR: generator not found at", generator)
        sys.exit(1)

    # Determine what exists
    has_canonical = os.path.isdir(canonical)
    has_sibling = os.path.isdir(sibling)

    if not has_canonical and not has_sibling:
        print("ERROR: Neither canonical docs/ nor sibling mnemosyne-docs/ found")
        print("       Run generate-docs.py first to create committed copies.")
        sys.exit(1)

    if has_canonical:
        docs = canonical
        print(f"Checking committed copies: {canonical}")
    else:
        docs = sibling
        print(f"WARNING: No committed copies. Checking sibling repo: {sibling}")
        print(f"         Consider running generate-docs.py and committing docs/api/")

    # Run the generator (idempotent - no-op if already up to date)
    print("Running generator...")
    result = subprocess.run(
        [sys.executable, generator],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print("ERROR: generator failed:")
        print(result.stderr)
        sys.exit(1)

    # Check if git sees changes in generated files against HEAD
    print("Checking for drift against committed state...")
    generated_paths = [
        "app/(docs)/api/tool-schema/page.mdx",
        "app/(docs)/getting-started/configuration/page.mdx",
    ]

    # Use git diff HEAD for each generated path
    has_drift = False
    for rel_path in generated_paths:
        abs_path = os.path.join(docs, rel_path)
        if not os.path.isfile(abs_path):
            print("  SKIP (not found):", rel_path)
            continue
        r = subprocess.run(
            ["git", "diff", "HEAD", "--exit-code", "--", abs_path],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            print("  DRIFT:", rel_path)
            has_drift = True

    if has_drift:
        print("")
        print("FAIL: Generated docs differ from committed state.")
        print("Run: python3 scripts/generate-docs.py")
        # Show the diff summary
        r = subprocess.run(
            ["git", "diff", "HEAD", "--stat", "--", "src/"],
            capture_output=True, text=True,
        )
        if r.stdout.strip():
            print(r.stdout)
        if args.fix:
            print("Auto-fix completed. Review and commit the changes.")
            sys.exit(0)
        sys.exit(1)
    else:
        print("")
        print("OK: All generated docs match committed state.")
        sys.exit(0)


if __name__ == "__main__":
    main()
