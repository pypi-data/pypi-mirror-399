"""
Dataset utilities for Ostris training.

We keep this logic in a separate file so `main.py` stays small and readable.
The main use-case is: user provides a public ZIP URL.
The ZIP contains images and matching caption `.txt` files.

Example inside the ZIP (root):
- photobelle.png
- photobelle.txt

We download, extract, then normalize into:
- image_0.png
- image_0.txt
- image_1.jpg
- image_1.txt
...
"""

from __future__ import annotations

from pathlib import Path
import shutil
import tempfile
import urllib.request
from urllib.parse import quote, urlsplit, urlunsplit
import zipfile


# Keep this list conservative. Add formats only if the training pipeline supports them.
_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}


def _normalize_public_url(url: str) -> str:
    """
    Make a public URL safe for HTTP clients.

    Some users paste URLs containing spaces or non-ASCII characters.
    Example: ".../Visage bonne qualité v2/.../dataset.zip"

    Python's `urllib` rejects those unless they are percent-encoded.
    We encode only the path/query parts and preserve already-encoded sequences.
    """
    parts = urlsplit(url)
    if parts.scheme not in {"http", "https"}:
        raise ValueError(f"URL must start with http:// or https://. Got: {url!r}")

    # Encode the path. Keep "/" and existing "%" sequences intact.
    safe_path = quote(parts.path, safe="/%")

    # Queries are rare for direct file downloads, but we handle them anyway.
    # Keep "=", "&" and existing "%" sequences intact.
    safe_query = quote(parts.query, safe="=&%")

    return urlunsplit((parts.scheme, parts.netloc, safe_path, safe_query, parts.fragment))


def _pick_extracted_root(extract_dir: Path) -> Path:
    """
    Many ZIPs contain a single top folder, e.g. dataset/myfiles...
    We transparently support that by "entering" the top folder if it is unique.
    """
    entries = [p for p in extract_dir.iterdir() if p.name not in {".DS_Store"}]
    if len(entries) == 1 and entries[0].is_dir():
        return entries[0]
    return extract_dir


def _cleanup_previous_normalized_files(output_dir: Path) -> None:
    """
    If the folder already exists, we only delete files that match the naming we create.
    This avoids mixing old and new "image_N" files.
    """
    for p in output_dir.glob("image_*"):
        # We only remove files, not directories.
        if p.is_file():
            p.unlink()


def prepare_dataset_from_zip_url(
    *,
    url_zip_dataset: object,
    output_dir: str,
    default_caption: str | None = None,
) -> tuple[int, int]:
    """
    Download a public ZIP and normalize it into `output_dir`.

    Returns:
    - imported_pairs: number of (image, caption) pairs imported
    - generated_captions: number of captions generated because the zip had no matching .txt

    Temporary files (including the downloaded ZIP) are stored in a temp folder and
    are deleted automatically when this function returns.
    """
    if not isinstance(url_zip_dataset, str) or not url_zip_dataset.strip():
        raise TypeError("url_zip_dataset must be a non-empty string URL.")

    out_dir = Path(output_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)
    _cleanup_previous_normalized_files(out_dir)

    # We use a temp directory so we never pollute the workspace with partial downloads.
    with tempfile.TemporaryDirectory(prefix="ostristraining_dataset_") as td:
        td_path = Path(td)
        zip_path = td_path / "dataset.zip"

        # Download the ZIP. `urllib` is stdlib and works in minimal environments.
        # Note: for very large files, a streaming approach is also possible.
        safe_url = _normalize_public_url(url_zip_dataset)
        urllib.request.urlretrieve(safe_url, zip_path)  # nosec B310

        # Extract.
        extract_dir = td_path / "extract"
        extract_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_dir)

        root = _pick_extracted_root(extract_dir)

        # Build maps: stem -> file path.
        # We only consider files in the root directory (as requested).
        images_by_stem: dict[str, Path] = {}
        captions_by_stem: dict[str, Path] = {}

        for p in root.iterdir():
            if not p.is_file():
                continue
            ext = p.suffix.lower()
            if ext in _IMAGE_EXTS:
                images_by_stem[p.stem] = p
            elif ext == ".txt":
                captions_by_stem[p.stem] = p

        # We iterate over images in a stable order.
        # If an image has no caption file:
        # - if `default_caption` is provided, we generate the caption
        # - otherwise we skip the image (old behavior)
        ordered_image_stems = sorted(images_by_stem.keys())
        imported_pairs = 0
        generated_captions = 0

        for stem in ordered_image_stems:
            src_img = images_by_stem[stem]
            src_txt = captions_by_stem.get(stem)

            if src_txt is None and default_caption is None:
                # Keep backward compatibility: skip images without captions
                # when no default caption is requested.
                continue

            # Keep the original image extension.
            dst_img = out_dir / f"image_{imported_pairs}{src_img.suffix.lower()}"
            dst_txt = out_dir / f"image_{imported_pairs}.txt"

            # Copy the image.
            shutil.copy2(src_img, dst_img)

            # Copy or generate the caption.
            if src_txt is not None:
                shutil.copy2(src_txt, dst_txt)
            else:
                # Generate a simple caption file.
                caption = default_caption or ""
                if caption and not caption.endswith("\n"):
                    caption += "\n"
                dst_txt.write_text(caption, encoding="utf-8", newline="\n")
                generated_captions += 1

            imported_pairs += 1

        return imported_pairs, generated_captions


