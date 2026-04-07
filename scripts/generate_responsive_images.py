#!/usr/bin/env python3
"""
Generate resized WebP derivatives for images in media/images.

Usage:
  ./scripts/generate_responsive_images.py --src media/images --out media/images/resized

This creates -{width}.webp files next to the originals (unless --out is used).
It will also create a 205x205 thumbnail with suffix -205.webp for small avatars.
"""
import os
import argparse
from PIL import Image

TARGET_WIDTHS = [320, 640, 1024, 1600]
THUMB_SIZE = (205, 205)

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def generate_derivatives(src_dir, out_dir=None, quality=80):
    out_dir = out_dir or src_dir
    ensure_dir(out_dir)
    exts = {'.png', '.jpg', '.jpeg', '.webp', '.gif'}
    for root, _, files in os.walk(src_dir):
        for f in files:
            name, ext = os.path.splitext(f)
            if ext.lower() not in exts:
                continue

            # Skip files that end in our known suffixes to avoid recursive processing
            if any(name.endswith(f"-{tw}") for tw in TARGET_WIDTHS) or name.endswith("-205"):
                continue
            src_path = os.path.join(root, f)
            rel_dir = os.path.relpath(root, src_dir)
            target_dir = os.path.join(out_dir, rel_dir) if rel_dir != '.' else out_dir
            ensure_dir(target_dir)
            try:
                with Image.open(src_path) as im:
                    w, h = im.size
                    # Create width-based derivatives
                    for tw in TARGET_WIDTHS:
                        out_name = f"{name}-{tw}.webp"
                        out_path = os.path.join(target_dir, out_name)
                        if os.path.exists(out_path):
                            continue

                        if w <= tw:
                            # If smaller than target width, just save original without resizing
                            # to ensure the file exists for the frontend srcSet
                            im.save(out_path, 'WEBP', quality=quality)
                            print('W (original size)', out_path)
                            continue

                        ratio = tw / float(w)
                        th = int(h * ratio)
                        im_resized = im.resize((tw, th), Image.LANCZOS)
                        im_resized.save(out_path, 'WEBP', quality=quality)
                        print('W', out_path)

                    # Create thumbnail 205x205 (square, center-crop)
                    thumb_name = f"{name}-205.webp"
                    thumb_path = os.path.join(target_dir, thumb_name)
                    if not os.path.exists(thumb_path):
                        im_thumb = im.copy()
                        im_thumb.thumbnail((max(THUMB_SIZE), max(THUMB_SIZE)), Image.LANCZOS)
                        # center crop to exact THUMB_SIZE
                        tw, th = im_thumb.size
                        left = max(0, (tw - THUMB_SIZE[0]) // 2)
                        top = max(0, (th - THUMB_SIZE[1]) // 2)
                        right = left + THUMB_SIZE[0]
                        bottom = top + THUMB_SIZE[1]
                        im_cropped = im_thumb.crop((left, top, right, bottom))
                        im_cropped.save(thumb_path, 'WEBP', quality=quality)
                        print('T', thumb_path)
            except Exception as e:
                print('ERR', src_path, e)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', default='media/images', help='source images folder')
    parser.add_argument('--out', default=None, help='output folder (defaults to src)')
    parser.add_argument('--quality', type=int, default=80)
    args = parser.parse_args()
    generate_derivatives(args.src, args.out, args.quality)

if __name__ == '__main__':
    main()
