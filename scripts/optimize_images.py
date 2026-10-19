#!/usr/bin/env python3
"""Shrink project images for the web and keep each project's references in step.

Run from the repo root after adding or replacing images:
    python scripts/optimize_images.py            # all projects
    python scripts/optimize_images.py usb-lipo   # one project folder
    python scripts/optimize_images.py --dry-run  # show what would change

For every _projects/<folder>/:
  * images wider/taller than MAX_SIDE px are scaled down;
  * large JPEGs are recompressed;
  * large PNGs become WebP (lossy for photos and renders, lossless for flat graphics such
    as plots and schematics); the project's `image:` (used for link previews, which not every
    site supports as WebP) becomes JPEG instead. References in index.md are updated;
  * thumb.webp is (re)made from `image:` for the project cards, and `thumb:` is added to the
    front matter if missing.
Originals are copied to ../media-originals/<folder>/ (next to the repo) before anything is
changed, and are also still in git history. GIFs are never touched: convert those to MP4.

--favicons regenerates favicon.ico, assets/images/favicon-32.png and apple-touch-icon.png
from `profile_image` in _config.yml. Needs Pillow (pip install pillow).
"""
import argparse
import pathlib
import re
import shutil
import sys

from PIL import Image, ImageOps

REPO = pathlib.Path(__file__).resolve().parent.parent
ORIGINALS = REPO.parent / "media-originals"
MAX_SIDE = 2000          # px, longest side of any content image
THUMB_WIDTH = 1000       # px, project-card thumbnails
BIG_PNG = 300_000        # bytes; PNGs above this are converted
BIG_JPEG = 600_000       # bytes; JPEGs above this are recompressed
FLAT_COLOURS = 4096      # at or below this many colours an image counts as a flat graphic
PHOTO_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def kb(n):
    return f"{n / 1000:,.0f} KB"


def backup(path, dry):
    dest = ORIGINALS / path.parent.name / path.name
    if not dest.exists() and not dry:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)


def flatten(im):
    """RGBA/P -> RGB on white (for JPEG)."""
    im = im.convert("RGBA")
    bg = Image.new("RGB", im.size, "white")
    bg.paste(im, mask=im.getchannel("A"))
    return bg


def is_flat(im):
    small = im.convert("RGBA").convert("RGB")
    small.thumbnail((512, 512))
    return small.getcolors(FLAT_COLOURS) is not None


def fit(im, max_side=MAX_SIDE):
    if max(im.size) > max_side:
        im = im.copy()
        im.thumbnail((max_side, max_side), Image.LANCZOS)
    return im


def front_matter_value(text, key):
    m = re.search(rf"^{key}:\s*(\S+)\s*$", text, re.M)
    return m.group(1) if m else None


def rename_refs(text, old, new):
    """Point images="..." / file="..." / image: / markdown links at the renamed file."""
    pattern = rf'(?<![\w.-]){re.escape(old)}(?![\w.-])'
    return re.sub(pattern, new, text)


def process_project(folder, dry):
    index = folder / "index.md"
    if not index.exists():
        return
    text = index.read_bytes().decode("utf-8")
    original_text = text
    nl = "\r\n" if "\r\n" in text else "\n"
    image_url = front_matter_value(text, "image")
    image_name = image_url.rsplit("/", 1)[-1] if image_url else None

    for path in sorted(folder.iterdir()):
        ext = path.suffix.lower()
        if ext == ".gif" and path.stat().st_size > 2_000_000:
            print(f"  ! {path.name}: {kb(path.stat().st_size)} GIF - convert it to MP4 (see README)")
        if ext not in PHOTO_EXTS or path.name.startswith("thumb."):
            continue
        size = path.stat().st_size
        with Image.open(path) as src:  # closed straight away so Windows lets us replace the file
            im = ImageOps.exif_transpose(src)
        oversized = max(im.size) > MAX_SIDE
        is_social = path.name == image_name

        if ext == ".png" and (size > BIG_PNG or oversized):
            if is_social:
                new_path, save = path.with_suffix(".jpg"), dict(format="JPEG", quality=85, optimize=True, progressive=True)
                out = flatten(fit(im))
            elif is_flat(im):
                new_path, save = path.with_suffix(".webp"), dict(format="WEBP", lossless=True, method=6)
                out = fit(im)
            else:
                new_path, save = path.with_suffix(".webp"), dict(format="WEBP", quality=85, method=6)
                out = fit(im)
            if new_path.exists():
                print(f"  ! {path.name}: {new_path.name} already exists, skipped")
                continue
            backup(path, dry)
            if not dry:
                out.save(new_path, **save)
                new_size = new_path.stat().st_size
                if new_size > size * 0.8 and not oversized:
                    new_path.unlink()  # not worth it
                    print(f"  = {path.name}: conversion saves too little, kept PNG")
                    continue
                path.unlink()
            text = rename_refs(text, path.name, new_path.name)
            print(f"  ~ {path.name} ({kb(size)}) -> {new_path.name}" + ("" if dry else f" ({kb(new_path.stat().st_size)})"))
        elif ext in (".jpg", ".jpeg") and (size > BIG_JPEG or oversized):
            backup(path, dry)
            out = fit(im).convert("RGB")
            if not dry:
                tmp = path.with_suffix(".tmp" + ext)
                out.save(tmp, format="JPEG", quality=82, optimize=True, progressive=True)
                if tmp.stat().st_size < size * 0.9 or oversized:
                    tmp.replace(path)
                    print(f"  ~ {path.name}: {kb(size)} -> {kb(path.stat().st_size)}")
                else:
                    tmp.unlink()
            else:
                print(f"  ~ {path.name}: would recompress ({kb(size)}, {im.size[0]}x{im.size[1]})")
        elif ext == ".webp" and oversized:
            backup(path, dry)
            if not dry:
                fit(im).save(path, format="WEBP", quality=85, method=6)
            print(f"  ~ {path.name}: scaled down to {MAX_SIDE}px")

    # Card thumbnail from the (possibly renamed) `image:`
    image_url = front_matter_value(text, "image")
    if image_url:
        source = folder / image_url.rsplit("/", 1)[-1]
        if not source.exists() and not dry:
            print(f"  ! image: {image_url} not found in {folder.name}/")
        elif source.exists() or dry:
            thumb = folder / "thumb.webp"
            if not dry and source.exists():
                with Image.open(source) as src:
                    im = ImageOps.exif_transpose(src).convert("RGB")
                w, h = im.size
                if h > w * 3 / 4:  # taller than 4:3: keep the middle band
                    band = int(w * 3 / 4)
                    top = (h - band) // 2
                    im = im.crop((0, top, w, top + band))
                if im.size[0] > THUMB_WIDTH:
                    im = im.resize((THUMB_WIDTH, round(im.size[1] * THUMB_WIDTH / im.size[0])), Image.LANCZOS)
                im.save(thumb, format="WEBP", quality=80, method=6)
                print(f"  + thumb.webp ({kb(thumb.stat().st_size)})")
            if not front_matter_value(text, "thumb"):
                thumb_url = image_url.rsplit("/", 1)[0] + "/thumb.webp"
                text = re.sub(r"^(image:[^\r\n]*)", lambda m: f"{m.group(1)}{nl}thumb: {thumb_url}",
                              text, count=1, flags=re.M)

    if text != original_text:
        if not dry:
            index.write_bytes(text.encode("utf-8"))
        print(f"  * index.md references updated")


def favicons(dry):
    config = (REPO / "_config.yml").read_text(encoding="utf-8")
    m = re.search(r"^profile_image:\s*(\S+)", config, re.M)
    if not m:
        sys.exit("profile_image not set in _config.yml")
    src = REPO / m.group(1).lstrip("./")
    with Image.open(src) as source:
        im = ImageOps.exif_transpose(source).convert("RGBA")
    side = min(im.size)
    left, top = (im.size[0] - side) // 2, (im.size[1] - side) // 2
    im = im.crop((left, top, left + side, top + side))
    targets = {
        REPO / "assets/images/favicon-32.png": 32,
        REPO / "assets/images/apple-touch-icon.png": 180,
    }
    for path, px in targets.items():
        print(f"  + {path.relative_to(REPO).as_posix()} ({px}px)")
        if not dry:
            im.resize((px, px), Image.LANCZOS).save(path, optimize=True)
    print("  + favicon.ico (16/32/48px)")
    if not dry:
        im.save(REPO / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("folders", nargs="*", help="project folder names (default: all)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--favicons", action="store_true", help="only regenerate favicons")
    args = parser.parse_args()

    if args.favicons:
        favicons(args.dry_run)
        return
    folders = [REPO / "_projects" / f for f in args.folders] or sorted(
        p for p in (REPO / "_projects").iterdir() if p.is_dir())
    for folder in folders:
        print(folder.name)
        process_project(folder, args.dry_run)
    if not args.dry_run:
        print(f"\nOriginals of changed files: {ORIGINALS}")


if __name__ == "__main__":
    main()
