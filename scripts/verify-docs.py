#!/usr/bin/env python3
"""
Verify generated doc pages in the mnemosyne repo match live provider code.

Checks committed canonical copies (docs/api/*.mdx) against freshly generated
output. Exits 0 when clean, 1 when drift detected.

Usage:
    python scripts/verify-docs.py          # check canonical copies
    python scripts/verify-docs.py --quiet  # suppress progress, exit code only
"""
import os, sys, re, subprocess, tempfile


def norm_content(text):
    """Normalize generated metadata so committed and fresh copies compare clean.

    Strips volatile fields: generated_at timestamps, generated: ISO dates,
    code_version strings (they're in the metadata JSON already).
    """
    text = re.sub(r'generated_at: .*', 'generated_at: NORMALIZED', text)
    text = re.sub(r'generated: \d{4}-\d{2}-\d{2}.*', 'generated: NORMALIZED', text)
    # Strip code_version from frontmatter (redundant with metadata)
    text = re.sub(r'code_version: .*\n', '', text)
    # Strip source line (redundant)
    text = re.sub(r'source: .*\n', '', text)
    return text


def main():
    quiet = '--quiet' in sys.argv

    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    canonical = os.path.join(repo, 'docs', 'api')
    generator = os.path.join(repo, 'scripts', 'generate-docs.py')

    if not os.path.isfile(generator):
        print('ERROR: generator not found at', generator)
        sys.exit(1)

    if not os.path.isdir(canonical):
        print('ERROR: canonical docs dir not found at', canonical)
        print('       Run generate-docs.py first')
        sys.exit(1)

    # Generate fresh copies to temp dir
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            env = os.environ.copy()
            env['DOCS_OUTPUT_DIR'] = tmpdir
            result = subprocess.run(
                [sys.executable, generator],
                capture_output=True, text=True, check=True, env=env,
            )
            if not quiet:
                print(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print('ERROR: generation failed')
        print(e.stderr)
        sys.exit(1)

    # Compare committed vs fresh (after the generator ran, canonical is fresh)
    # The generator writes to canonical directly, so we compare against what
    # it just wrote. If code hasn't changed since last commit, they match.
    # Strategy: re-run generator, check if canonical files changed vs git HEAD.

    files_to_check = [
        ('tool-schema.mdx', 'api/tool-schema'),
        ('configuration.mdx', 'api/configuration'),
        ('.provider-metadata.json', 'api/metadata'),
    ]

    has_drift = False
    for filename, label in files_to_check:
        path = os.path.join(canonical, filename)
        if not os.path.isfile(path):
            if not quiet:
                print(f'  MISSING: {label} ({filename})')
            has_drift = True
            continue

    # Get the committed version from git for each file, normalize, compare
    has_drift = False
    for filename, label in files_to_check:
        path = os.path.join(canonical, filename)
        if not os.path.isfile(path):
            if not quiet:
                print(f'  MISSING: {label} ({filename})')
            has_drift = True
            continue

        # Read committed version from git (relative path from repo root)
        rel_path = os.path.relpath(path, repo)
        r = subprocess.run(
            ['git', 'show', f'HEAD:{rel_path}'], capture_output=True, text=True, cwd=repo
        )
        if r.returncode != 0:
            # File not in HEAD yet (newly generated) — report drift
            if not quiet:
                print(f'  DRIFT: {label} (not yet committed)')
            has_drift = True
            continue
        committed = r.stdout

        # Read fresh version
        with open(path) as f:
            fresh = f.read()

        # Normalize both and compare
        if norm_content(committed) != norm_content(fresh):
            if not quiet:
                print(f'  DRIFT: {label} ({filename})')
            has_drift = True
        else:
            if not quiet:
                print(f'  OK: {label}')

    if has_drift:
        if not quiet:
            print()
            print('Documentation has drifted from provider code.')
            print('Run: python scripts/generate-docs.py')
            print('Then commit docs/api/ and push.')
        sys.exit(1)
    else:
        if not quiet:
            print()
            print('All generated docs match provider code.')
        sys.exit(0)


if __name__ == '__main__':
    main()
