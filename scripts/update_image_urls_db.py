#!/usr/bin/env python3
"""
Update image/file fields in DB: replace .png -> .webp for files under images/ (DB values only).

Usage examples:
  # Dry-run (preview only)
  python scripts/update_image_urls_db.py --path-prefix /media/images/ --exceptions logo.png,keep.png

  # Apply changes to DB and also rename files on disk
  python scripts/update_image_urls_db.py --path-prefix /media/images/ --exceptions-file exceptions.txt --apply --rename-files

Notes:
  - This updates FileField/ImageField values via Django ORM (does NOT convert image bytes unless --rename-files is used to rename files on disk).
  - By default it's a dry-run; pass --apply to write changes.
"""
from __future__ import annotations
import argparse
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict


def setup_django():
    import sys
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kijeka.settings")
    # Ensure project root is on sys.path
    here = Path(__file__).resolve()
    project_root = here.parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    import django

    django.setup()


def load_exceptions_file(p: Path) -> List[str]:
    if not p.exists():
        return []
    return [ln.strip() for ln in p.read_text(encoding="utf8").splitlines() if ln.strip()]


def normalize_prefix(prefix: str) -> str:
    # DB likely stores 'images/...' or 'media/images/...'
    p = prefix.lstrip("/")
    if p.startswith("media/"):
        p = p[len("media/"):]
        p = p.lstrip("/")
    return p


def process_instance_field(instance, field, path_prefix_db: str, exceptions: set, apply: bool, rename_files: bool, media_root: Path, changes: List[Dict]):
    val = getattr(instance, field.name)
    # FieldFile or string
    try:
        current = val.name if hasattr(val, "name") else (str(val) or "")
    except Exception:
        current = str(val) or ""
    if not current:
        return
    cur_lower = current.lower()
    if not cur_lower.startswith(path_prefix_db):
        return
    if not cur_lower.endswith('.png'):
        return
    base_filename = current.split('/')[-1]
    if base_filename in exceptions:
        return
    new = current.rsplit('.', 1)[0] + '.webp'
    changes.append({
        "model": instance.__class__.__name__,
        "pk": getattr(instance, instance._meta.pk.name),
        "field": field.name,
        "old": current,
        "new": new,
    })
    print(f"Will change: {instance.__class__.__name__}({getattr(instance, instance._meta.pk.name)}) {field.name}: {current} -> {new}")
    if apply:
        setattr(instance, field.name, new)
        instance.save(update_fields=[field.name])
        # Optionally rename file on disk
        if rename_files and media_root:
            old_path = media_root / current
            new_path = media_root / new
            if old_path.exists():
                new_path.parent.mkdir(parents=True, exist_ok=True)
                if new_path.exists():
                    print(f"Skipping file-rename: target exists {new_path}")
                else:
                    shutil.move(str(old_path), str(new_path))
                    print(f"Renamed file: {old_path} -> {new_path}")


def main():
    ap = argparse.ArgumentParser(description="Replace .png -> .webp in DB File/Image fields under given path prefix")
    ap.add_argument('--path-prefix', '-p', default='/media/images/', help='URL path prefix (e.g. /media/images/)')
    ap.add_argument('--exceptions', '-e', default='', help='Comma-separated filenames to keep (e.g. logo.png,keep.png)')
    ap.add_argument('--exceptions-file', '-E', help='File with one filename per line to keep')
    ap.add_argument('--apply', action='store_true', help='Apply changes to DB (default: dry-run)')
    ap.add_argument('--rename-files', action='store_true', help='Also rename files on disk under MEDIA_ROOT (use with care).')
    ap.add_argument('--backup-file', help='Write JSON backup of planned changes (defaults to changes_backup_TIMESTAMP.json)')
    args = ap.parse_args()

    setup_django()

    from django.conf import settings
    from django.db import models
    from api.models import Product, ProductImage, Clients, YoutubeVideo, Blog

    # support multiple comma-separated prefixes
    raw_prefixes = [p.strip() for p in args.path_prefix.split(',') if p.strip()]
    path_prefix_db_list = [normalize_prefix(p) for p in raw_prefixes]
    exc_list: List[str] = [s.strip() for s in args.exceptions.split(',') if s.strip()]
    if args.exceptions_file:
        p = Path(args.exceptions_file)
        exc_list += load_exceptions_file(p)
    exceptions = set(exc_list)

    media_root = Path(getattr(settings, 'MEDIA_ROOT', '')) if args.rename_files else None

    print('path_prefix_db_list:', path_prefix_db_list)
    print('exceptions:', exceptions)
    print('mode:', 'APPLY' if args.apply else 'DRY-RUN')
    print('rename_files:', args.rename_files)

    changes = []

    # helper to find File/Image fields on a model
    def file_fields_for_model(klass):
        return [f for f in klass._meta.get_fields() if getattr(f, 'get_internal_type', lambda: '')() in ('FileField', 'ImageField')]

    # Process Product instances
    prod_fields = file_fields_for_model(Product)
    print(f'Found file fields on Product: {[f.name for f in prod_fields]}')
    for p in Product.objects.all():
        for f in prod_fields:
            for path_prefix_db in path_prefix_db_list:
                process_instance_field(p, f, path_prefix_db, exceptions, args.apply, args.rename_files, media_root, changes)

    # Process ProductImage instances
    pi_fields = file_fields_for_model(ProductImage)
    print(f'Found file fields on ProductImage: {[f.name for f in pi_fields]}')
    for pi in ProductImage.objects.all():
        for f in pi_fields:
            for path_prefix_db in path_prefix_db_list:
                process_instance_field(pi, f, path_prefix_db, exceptions, args.apply, args.rename_files, media_root, changes)

    # Process Clients (logo), YoutubeVideo (poster), Blog (image)
    clients_fields = file_fields_for_model(Clients)
    print(f'Found file fields on Clients: {[f.name for f in clients_fields]}')
    for c in Clients.objects.all():
        for f in clients_fields:
            for path_prefix_db in path_prefix_db_list:
                process_instance_field(c, f, path_prefix_db, exceptions, args.apply, args.rename_files, media_root, changes)

    ytf_fields = file_fields_for_model(YoutubeVideo)
    print(f'Found file fields on YoutubeVideo: {[f.name for f in ytf_fields]}')
    for y in YoutubeVideo.objects.all():
        for f in ytf_fields:
            for path_prefix_db in path_prefix_db_list:
                process_instance_field(y, f, path_prefix_db, exceptions, args.apply, args.rename_files, media_root, changes)

    blog_fields = file_fields_for_model(Blog)
    print(f'Found file fields on Blog: {[f.name for f in blog_fields]}')
    for b in Blog.objects.all():
        for f in blog_fields:
            for path_prefix_db in path_prefix_db_list:
                process_instance_field(b, f, path_prefix_db, exceptions, args.apply, args.rename_files, media_root, changes)

    if not args.backup_file:
        stamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        backup_path = Path(f'changes_backup_{stamp}.json')
    else:
        backup_path = Path(args.backup_file)
    if changes:
        backup_path.write_text(json.dumps(changes, indent=2, ensure_ascii=False), encoding='utf8')
        print(f'Wrote backup of planned changes to: {backup_path}')
    else:
        print('No changes detected.')


if __name__ == '__main__':
    main()
