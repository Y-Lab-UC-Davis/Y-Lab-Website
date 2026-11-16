#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────
#  Y-Lab — image asset generator (cross-platform via Python/Pillow; macOS `sips` fallback)
#
#  Generates optimized site images from local originals:
#    • assets/img/lab-photo.jpg   — lab group photo (People / Home page)
#    • assets/img/og-image.jpg    — 1200×630 social-share image
#    • assets/img/people/*.jpg    — square 600×600 headshots
#    • assets/img/lab/*.jpg       — 1600px wide lab scene photos
#
#  USAGE
#    1) Group photo:
#         bash scripts/apply-images.sh "/path/to/group-photo.jpg"
#    2) Headshots: drop originals into  assets/img/people/_raw/  (e.g.
#       "Wenzhong Yan.jpg") then run this script. Each becomes
#       assets/img/people/firstname-lastname.jpg.
#    3) Lab scenes: drop originals into  assets/img/lab/_raw/  then run this script.
#
#  AFTER RUNNING
#    • Set  lab_photo: /assets/img/lab-photo.jpg  under  assets:  in _config.yml
#    • For each headshot, add  photo: /assets/img/people/<name>.jpg  in _data/people.yml
# ─────────────────────────────────────────────────────────────────────────
set -euo pipefail
cd "$(dirname "$0")/.."          # repo root

IMG_DIR="assets/img"
PEOPLE_DIR="$IMG_DIR/people"
RAW_HEADSHOTS="$PEOPLE_DIR/_raw"
LAB_DIR="$IMG_DIR/lab"
RAW_LAB="$LAB_DIR/_raw"
mkdir -p "$PEOPLE_DIR" "$LAB_DIR"

echo "── Y-Lab image generator ──"
GROUP_PHOTO="${1:-}"

if python3 -c "import PIL" >/dev/null 2>&1; then
  python3 - "$GROUP_PHOTO" "$IMG_DIR" "$PEOPLE_DIR" "$RAW_HEADSHOTS" "$LAB_DIR" "$RAW_LAB" <<'PY'
import os, re, sys
from PIL import Image, ImageOps

group_photo, img_dir, people_dir, raw_headshots, lab_dir, raw_lab = sys.argv[1:7]

def save_jpg(im, out, quality=82):
    if im.mode in ("RGBA", "LA", "P"):
        rgba = im.convert("RGBA")
        bg = Image.new("RGB", rgba.size, (255, 255, 255))
        bg.paste(rgba, mask=rgba.split()[-1])
        im = bg
    else:
        im = im.convert("RGB")
    im.save(out, "JPEG", quality=quality, optimize=True, progressive=True)

def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

if group_photo and os.path.isfile(group_photo):
    print(f"Group photo: {group_photo}")
    with Image.open(group_photo) as src:
        src = ImageOps.exif_transpose(src)
        lab_im = src.copy()
        if lab_im.width > 1600:
            lab_im = lab_im.resize((1600, round(lab_im.height * 1600 / lab_im.width)), Image.LANCZOS)
        save_jpg(lab_im, os.path.join(img_dir, "lab-photo.jpg"), 82)
        print(f"  → {img_dir}/lab-photo.jpg")
        og_im = ImageOps.fit(src, (1200, 630), method=Image.LANCZOS)
        save_jpg(og_im, os.path.join(img_dir, "og-image.jpg"), 82)
        print(f"  → {img_dir}/og-image.jpg")
        print("  NEXT: set  lab_photo: /assets/img/lab-photo.jpg  under assets: in _config.yml")
elif group_photo:
    print(f"Group photo not found: {group_photo}", file=sys.stderr)
else:
    print("No group photo argument given (pass a path to generate lab-photo.jpg & og-image.jpg).")

if os.path.isdir(raw_headshots) and any(os.path.isfile(os.path.join(raw_headshots, f)) for f in os.listdir(raw_headshots)):
    print(f"Processing headshots in {raw_headshots} ...")
    for fname in sorted(os.listdir(raw_headshots)):
        fpath = os.path.join(raw_headshots, fname)
        if not os.path.isfile(fpath) or fname.startswith("."):
            continue
        slug = slugify(os.path.splitext(fname)[0])
        out = os.path.join(people_dir, f"{slug}.jpg")
        with Image.open(fpath) as src:
            src = ImageOps.exif_transpose(src)
            sq = ImageOps.fit(src, (600, 600), method=Image.LANCZOS)
            save_jpg(sq, out, 85)
        print(f"  → {out}   (add  photo: /assets/img/people/{slug}.jpg)")
else:
    print(f"No headshots to process (drop originals in {raw_headshots}/ and re-run).")

if os.path.isdir(raw_lab) and any(os.path.isfile(os.path.join(raw_lab, f)) for f in os.listdir(raw_lab)):
    print(f"Processing lab scenes in {raw_lab} ...")
    for fname in sorted(os.listdir(raw_lab)):
        fpath = os.path.join(raw_lab, fname)
        if not os.path.isfile(fpath) or fname.startswith("."):
            continue
        slug = slugify(os.path.splitext(fname)[0])
        out = os.path.join(lab_dir, f"{slug}.jpg")
        with Image.open(fpath) as src:
            src = ImageOps.exif_transpose(src)
            if src.width > 1600:
                src = src.resize((1600, round(src.height * 1600 / src.width)), Image.LANCZOS)
            save_jpg(src, out, 82)
        print(f"  → {out}   (set ready: true for it in _data/gallery.yml)")
else:
    print(f"No lab scenes to process (drop originals in {raw_lab}/ and re-run).")
PY
  echo "Done. Preview with ./serve.sh"
  exit 0
fi

command -v sips >/dev/null 2>&1 || { echo "ERROR: install Pillow (`pip install Pillow`) or run on macOS with `sips`."; exit 1; }

if [ -n "$GROUP_PHOTO" ] && [ -f "$GROUP_PHOTO" ]; then
  echo "Group photo: $GROUP_PHOTO"
  sips -s format jpeg -s formatOptions 82 "$GROUP_PHOTO" \
       --resampleWidth 1600 --out "$IMG_DIR/lab-photo.jpg" >/dev/null
  echo "  → $IMG_DIR/lab-photo.jpg"
  cp "$IMG_DIR/lab-photo.jpg" /tmp/ylab-og-src.jpg
  sips -s format jpeg -s formatOptions 82 -c 630 1200 /tmp/ylab-og-src.jpg \
       --out "$IMG_DIR/og-image.jpg" >/dev/null
  echo "  → $IMG_DIR/og-image.jpg"
  echo "  NEXT: set  lab_photo: /assets/img/lab-photo.jpg  under assets: in _config.yml"
else
  echo "No group photo argument given."
fi

if [ -d "$RAW_HEADSHOTS" ] && [ -n "$(ls -A "$RAW_HEADSHOTS" 2>/dev/null || true)" ]; then
  echo "Processing headshots in $RAW_HEADSHOTS ..."
  for f in "$RAW_HEADSHOTS"/*; do
    [ -f "$f" ] || continue
    name="$(basename "${f%.*}")"
    slug="$(echo "$name" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-')"
    sips -s format jpeg -s formatOptions 85 "$f" -c 600 600 \
         --out "$PEOPLE_DIR/$slug.jpg" >/dev/null
    echo "  → $PEOPLE_DIR/$slug.jpg   (add  photo: /assets/img/people/$slug.jpg)"
  done
else
  echo "No headshots to process (drop originals in $RAW_HEADSHOTS/ and re-run)."
fi

if [ -d "$RAW_LAB" ] && [ -n "$(ls -A "$RAW_LAB" 2>/dev/null || true)" ]; then
  echo "Processing lab scenes in $RAW_LAB ..."
  for f in "$RAW_LAB"/*; do
    [ -f "$f" ] || continue
    base="$(basename "${f%.*}" | tr '[:upper:] ' '[:lower:]-')"
    sips -s format jpeg -s formatOptions 82 "$f" --resampleWidth 1600 \
         --out "$LAB_DIR/$base.jpg" >/dev/null
    echo "  → $LAB_DIR/$base.jpg   (set ready: true for it in _data/gallery.yml)"
  done
else
  echo "No lab scenes to process (drop originals in $RAW_LAB/ and re-run)."
fi

echo "Done. Preview with ./serve.sh"
