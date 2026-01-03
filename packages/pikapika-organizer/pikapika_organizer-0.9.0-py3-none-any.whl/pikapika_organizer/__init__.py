from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Optional: safer than permanent delete (moves to Recycle Bin/Trash)
try:
    from send2trash import send2trash
except Exception:
    send2trash = None


# Basic extension -> folder mapping (edit to your preference)
CATEGORIES: dict[str, set[str]] = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff", ".heic"},
    "Videos": {".mp4", ".mkv", ".mov", ".avi", ".webm"},
    "Audio": {".mp3", ".wav", ".m4a", ".flac", ".aac"},
    "Documents": {
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".txt",
        ".csv",
    },
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Installers": {".exe", ".msi", ".dmg", ".pkg", ".apk"},
    "Code": {
        ".py",
        ".ipynb",
        ".js",
        ".ts",
        ".html",
        ".css",
        ".json",
        ".xml",
        ".yml",
        ".yaml",
    },
}

JUNK_EXTENSIONS = {".tmp", ".crdownload", ".part", ".log"}
DEFAULT_TARGET_NAME = "Other"
FOLDERS_TO_SKIP = {".git", "__pycache__"}


def default_downloads_dir() -> Path:
    # Common default; users can override with --path
    return Path.home() / "Downloads"


def category_for_extension(ext: str) -> str:
    ext = ext.lower()
    for cat, exts in CATEGORIES.items():
        if ext in exts:
            return cat
    return DEFAULT_TARGET_NAME


def unique_destination(dest: Path) -> Path:
    """Avoid overwriting: file.txt -> file (1).txt, file (2).txt, ..."""
    if not dest.exists():
        return dest
    stem, suffix = dest.stem, dest.suffix
    i = 1
    while True:
        candidate = dest.with_name(f"{stem} ({i}){suffix}")
        if not candidate.exists():
            return candidate
        i += 1


def is_older_than(path: Path, days: int) -> bool:
    cutoff = datetime.now() - timedelta(days=days)
    mtime = datetime.fromtimestamp(path.stat().st_mtime)
    return mtime < cutoff


def clean_downloads(
    downloads: Path,
    dry_run: bool,
    recursive: bool,
    quarantine_junk: bool,
    junk_days: int,
    use_trash: bool,
) -> None:
    downloads = downloads.expanduser().resolve()
    if not downloads.exists() or not downloads.is_dir():
        raise SystemExit(f"Not a directory: {downloads}")

    iterator = downloads.rglob("*") if recursive else downloads.glob("*")

    # Put “junk” somewhere visible instead of deleting by default
    quarantine_dir = downloads / "_Quarantine"
    if quarantine_junk and not dry_run:
        quarantine_dir.mkdir(exist_ok=True)

    for p in iterator:
        # Skip directories (and skip inside category folders if recursive)
        if p.is_dir():
            if p.name in FOLDERS_TO_SKIP:
                continue
            # If recursive, avoid reorganizing already-created category folders
            if (
                recursive
                and p.parent == downloads
                and p.name
                in set(CATEGORIES.keys()) | {DEFAULT_TARGET_NAME, "_Quarantine"}
            ):
                continue
            continue

        # Never move the script itself if it lives in Downloads
        if p.name == Path(__file__).name:
            continue

        ext = p.suffix.lower()

        # Handle junk files (optional)
        if quarantine_junk and ext in JUNK_EXTENSIONS and is_older_than(p, junk_days):
            if use_trash and send2trash is not None:
                action = f"TRASH junk: {p.name}"
                if not dry_run:
                    send2trash(str(p))
            else:
                dest = unique_destination(quarantine_dir / p.name)
                action = f"QUARANTINE junk: {p.name} -> {dest.relative_to(downloads)}"
                if not dry_run:
                    p.replace(dest)
            print(action)
            continue

        # Determine category folder
        cat = category_for_extension(ext)
        dest_dir = downloads / cat
        dest = unique_destination(dest_dir / p.name)

        # Create category directory and move
        if dry_run:
            print(f"MOVE: {p.name} -> {dest.relative_to(downloads)}")
        else:
            dest_dir.mkdir(exist_ok=True)
            p.replace(dest)  # pathlib move/rename semantics; works well for same drive
            print(f"MOVED: {p.name} -> {dest.relative_to(downloads)}")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Cleanser - A tool to organize your Downloads folder by extension. "
        "Supports dry-run, recursive processing, and junk file handling.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cleanser                    # Organize current user's Downloads
  cleanser --path /path/to/dl # Organize specific folder
  cleanser --dry-run          # Show what would be done
  cleanser --recursive        # Also process subfolders
  cleanser --quarantine-junk  # Handle junk files
        """,
    )
    ap.add_argument(
        "--path",
        type=str,
        default=str(default_downloads_dir()),
        help="Downloads folder path",
    )
    ap.add_argument(
        "--dry-run", action="store_true", help="Show actions without changing anything"
    )
    ap.add_argument(
        "--recursive", action="store_true", help="Also organize files in subfolders"
    )
    ap.add_argument(
        "--quarantine-junk",
        action="store_true",
        help="Handle junk extensions (.tmp, .crdownload, etc.)",
    )
    ap.add_argument(
        "--junk-days",
        type=int,
        default=7,
        help="Only junk older than N days is quarantined/trashed",
    )
    ap.add_argument(
        "--trash-junk",
        action="store_true",
        help="Send junk to Recycle Bin/Trash (requires send2trash)",
    )
    args = ap.parse_args()

    clean_downloads(
        downloads=Path(args.path),
        dry_run=args.dry_run,
        recursive=args.recursive,
        quarantine_junk=args.quarantine_junk,
        junk_days=args.junk_days,
        use_trash=args.trash_junk,
    )


if __name__ == "__main__":
    main()
