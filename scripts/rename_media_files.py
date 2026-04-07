#!/usr/bin/env python3
"""
Rename image files on disk: .png/.jpg/.jpeg -> .webp under media/images and media/mimages.
Skips files when the target .webp already exists. Logs actions to a JSON file.

Usage:
  python scripts/rename_media_files.py
  python scripts/rename_media_files.py --dry-run
  python scripts/rename_media_files.py --paths media/images,media/mimages --apply
"""
from __future__ import annotations
import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import List


def find_files(paths: List[Path], exts=('.png', '.jpg', '.jpeg')):
    for p in paths:
        if not p.exists():
            continue
        for fp in p.rglob('*'):
            if fp.is_file() and fp.suffix.lower() in exts:
                yield fp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--paths', default='media/images,media/mimages', help='Comma-separated dirs to search')
    ap.add_argument('--apply', action='store_true', help='Perform renames (default dry-run)')
    ap.add_argument('--dry-run', dest='apply', action='store_false', help='Dry-run (default)')
    args = ap.parse_args()

    paths = [Path(p.strip()) for p in args.paths.split(',') if p.strip()]
    files = list(find_files(paths))
    print(f'Found {len(files)} files to consider')

    results = []
    for f in files:
        rel = f.as_posix()
        new = f.with_suffix('.webp')
        if new.exists():
            results.append({'old': rel, 'new': new.as_posix(), 'action': 'skipped_target_exists'})
            continue
        if args.apply:
            try:
                new.parent.mkdir(parents=True, exist_ok=True)
                f.rename(new)
                results.append({'old': rel, 'new': new.as_posix(), 'action': 'renamed'})
            except Exception as e:
                results.append({'old': rel, 'new': new.as_posix(), 'action': 'error', 'error': str(e)})
        else:
            results.append({'old': rel, 'new': new.as_posix(), 'action': 'preview'})

    stamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    out = Path(f'rename_changes_{stamp}.json')
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding='utf8')
    print(f'Wrote log to {out}');
    # Print short summary
    from collections import Counter
    ctr = Counter(r['action'] for r in results)
    for k, v in ctr.items():
        print(f'{k}: {v}')


if __name__ == '__main__':
    main()
