#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


VIDEO_EXTENSIONS = {
    ".mkv",
    ".mp4",
    ".avi",
    ".m4v",
    ".mov",
    ".webm",
}

IGNORED_NAMES = {
    ".DS_Store",
    "Thumbs.db",
    "desktop.ini",
}

SEASON_DIRECTORY_PATTERN = re.compile(
    r"^Season (?P<season>\d{1,2})$",
    re.IGNORECASE,
)

ORGANIZED_EPISODE_PATTERN = re.compile(
    r"^(?P<show>.+) "
    r"\((?P<year>\d{4})\) - "
    r"S(?P<season>\d{2})"
    r"E(?P<episode>\d{2,3})"
    r"(?P<extension>\.[^.]+)$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class MoveOperation:
    source: Path
    destination: Path
    season: int
    episode: int
    size: int


def is_ignored(path: Path) -> bool:
    return path.name.startswith("._") or path.name in IGNORED_NAMES


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Safely organize TV series for Jellyfin.",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    organize_parser = subparsers.add_parser(
        "organize",
        help="Move and rename episodes into a media library.",
    )

    organize_parser.add_argument(
        "source",
        type=Path,
        help="Directory containing source episode files.",
    )
    organize_parser.add_argument(
        "--library",
        type=Path,
        required=True,
        help="Series library root, for example ~/Videos/Series.",
    )
    organize_parser.add_argument(
        "--show",
        required=True,
        help='Show name, for example "Silicon Valley".',
    )
    organize_parser.add_argument(
        "--year",
        type=int,
        required=True,
        help="Year when the show started.",
    )
    organize_parser.add_argument(
        "--season",
        type=int,
        required=True,
        help="Season number.",
    )
    organize_parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually move files. The default is dry-run.",
    )

    verify_parser = subparsers.add_parser(
        "verify",
        help="Verify an already organized series directory.",
    )

    verify_parser.add_argument(
        "show_directory",
        type=Path,
        help='Show directory, for example "Silicon Valley (2014)".',
    )

    return parser.parse_args()


def extract_season_episode(filename: str) -> tuple[int, int] | None:
    patterns = (
        re.compile(
            r"(?i)"
            r"(?<![A-Z0-9])"
            r"S(?P<season>\d{1,2})"
            r"[\s._-]*"
            r"E(?P<episode>\d{1,3})"
            r"(?!\d)"
        ),
        re.compile(
            r"(?i)"
            r"(?<![A-Z0-9])"
            r"E(?P<episode>\d{1,3})"
            r"[\s._-]*"
            r"S(?P<season>\d{1,2})"
            r"(?!\d)"
        ),
    )

    for pattern in patterns:
        match = pattern.search(filename)

        if match:
            return (
                int(match.group("season")),
                int(match.group("episode")),
            )

    return None


def build_destination_directory(
    library: Path,
    show_name: str,
    show_year: int,
    season: int,
) -> Path:
    return (
        library
        / f"{show_name} ({show_year})"
        / f"Season {season:02d}"
    )


def collect_operations(
    source_dir: Path,
    destination_dir: Path,
    show_name: str,
    show_year: int,
    expected_season: int,
) -> tuple[list[MoveOperation], list[str], list[Path]]:
    operations: list[MoveOperation] = []
    warnings: list[str] = []
    ignored: list[Path] = []

    source_files = sorted(
        source_dir.iterdir(),
        key=lambda path: path.name.casefold(),
    )

    for source_file in source_files:
        if not source_file.is_file():
            continue

        if is_ignored(source_file):
            ignored.append(source_file)
            continue

        if source_file.suffix.lower() not in VIDEO_EXTENSIONS:
            continue

        parsed = extract_season_episode(source_file.name)

        if parsed is None:
            warnings.append(
                f"Cannot determine season and episode: "
                f"{source_file.name}"
            )
            continue

        season, episode = parsed

        if season != expected_season:
            warnings.append(
                f"Skipping season {season:02d}, expected "
                f"season {expected_season:02d}: "
                f"{source_file.name}"
            )
            continue

        destination_name = (
            f"{show_name} ({show_year}) - "
            f"S{season:02d}E{episode:02d}"
            f"{source_file.suffix.lower()}"
        )

        operations.append(
            MoveOperation(
                source=source_file,
                destination=destination_dir / destination_name,
                season=season,
                episode=episode,
                size=source_file.stat().st_size,
            )
        )

    return operations, warnings, ignored


def validate_operations(
    operations: list[MoveOperation],
) -> list[str]:
    errors: list[str] = []
    destinations: dict[Path, Path] = {}
    episodes: dict[tuple[int, int], Path] = {}

    for operation in operations:
        existing_source = destinations.get(operation.destination)

        if existing_source is not None:
            errors.append(
                "Multiple source files would produce the same "
                "destination:\n"
                f"  {existing_source}\n"
                f"  {operation.source}\n"
                f"  -> {operation.destination}"
            )
        else:
            destinations[operation.destination] = operation.source

        episode_key = (
            operation.season,
            operation.episode,
        )
        existing_episode = episodes.get(episode_key)

        if existing_episode is not None:
            errors.append(
                f"Duplicate episode "
                f"S{operation.season:02d}"
                f"E{operation.episode:02d}:\n"
                f"  {existing_episode}\n"
                f"  {operation.source}"
            )
        else:
            episodes[episode_key] = operation.source

        if operation.destination.exists():
            errors.append(
                f"Destination already exists: "
                f"{operation.destination}"
            )

    return errors


def find_missing_episodes(
    operations: list[MoveOperation],
) -> list[int]:
    episodes = sorted(
        {operation.episode for operation in operations}
    )

    if not episodes:
        return []

    expected = set(range(episodes[0], episodes[-1] + 1))
    return sorted(expected - set(episodes))


def print_episode_summary(
    operations: list[MoveOperation],
) -> None:
    episodes = sorted(
        {operation.episode for operation in operations}
    )

    if not episodes:
        return

    formatted = ", ".join(
        f"E{episode:02d}" for episode in episodes
    )

    print(f"Episodes found: {formatted}")

    missing = find_missing_episodes(operations)

    if missing:
        formatted_missing = ", ".join(
            f"E{episode:02d}" for episode in missing
        )
        print(
            f"Warning: missing episodes inside detected range: "
            f"{formatted_missing}",
            file=sys.stderr,
        )
    else:
        print("No internal episode gaps detected.")


def print_plan(
    operations: list[MoveOperation],
) -> None:
    print(f"Planned operations: {len(operations)}")
    print()

    for operation in operations:
        print(f"  {operation.source}")
        print(f"    -> {operation.destination}")


def apply_operations(
    operations: list[MoveOperation],
    destination_dir: Path,
) -> None:
    destination_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    for operation in operations:
        if not operation.source.is_file():
            raise FileNotFoundError(
                f"Source disappeared before move: "
                f"{operation.source}"
            )

        if operation.destination.exists():
            raise FileExistsError(
                f"Refusing to overwrite existing file: "
                f"{operation.destination}"
            )

        current_size = operation.source.stat().st_size

        if current_size != operation.size:
            raise RuntimeError(
                f"Source size changed before move: "
                f"{operation.source}"
            )

        print(f"Copying: {operation.source.name}")
        print(f"     -> {operation.destination.name}")

        shutil.copy2(
            str(operation.source),
            str(operation.destination),
        )

        if not operation.destination.is_file():
            raise RuntimeError(
                f"Destination was not created: "
                f"{operation.destination}"
            )

        destination_size = operation.destination.stat().st_size

        if destination_size != operation.size:
            raise RuntimeError(
                f"Size verification failed for: "
                f"{operation.destination}\n"
                f"Expected: {operation.size} bytes\n"
                f"Actual:   {destination_size} bytes"
            )

        operation.destination.chmod(0o644)


def organize(args: argparse.Namespace) -> int:
    source_dir = args.source.expanduser().resolve()
    library = args.library.expanduser().resolve()

    if not source_dir.is_dir():
        print(
            f"Error: source directory does not exist: "
            f"{source_dir}",
            file=sys.stderr,
        )
        return 1

    if args.year < 1800 or args.year > 9999:
        print(
            f"Error: invalid show year: {args.year}",
            file=sys.stderr,
        )
        return 1

    if args.season < 0 or args.season > 99:
        print(
            f"Error: invalid season number: {args.season}",
            file=sys.stderr,
        )
        return 1

    destination_dir = build_destination_directory(
        library=library,
        show_name=args.show,
        show_year=args.year,
        season=args.season,
    ).resolve()

    if source_dir == destination_dir:
        print(
            "Error: source and destination directories "
            "are identical.",
            file=sys.stderr,
        )
        return 1

    operations, warnings, ignored = collect_operations(
        source_dir=source_dir,
        destination_dir=destination_dir,
        show_name=args.show,
        show_year=args.year,
        expected_season=args.season,
    )

    for warning in warnings:
        print(
            f"Warning: {warning}",
            file=sys.stderr,
        )

    if ignored:
        print(f"Ignored metadata files: {len(ignored)}")

        for ignored_file in ignored:
            print(f"  {ignored_file.name}")

        print()

    if not operations:
        print(
            "Error: no matching episode files found.",
            file=sys.stderr,
        )
        return 1

    errors = validate_operations(operations)

    if errors:
        print(
            "\nValidation failed. Nothing was changed.\n",
            file=sys.stderr,
        )

        for error in errors:
            print(error, file=sys.stderr)
            print(file=sys.stderr)

        return 1

    print_episode_summary(operations)
    print()
    print_plan(operations)

    if not args.apply:
        print()
        print("Dry run only. Nothing was changed.")
        print(
            "Run the same command with --apply "
            "to perform the moves."
        )
        return 0

    print()
    apply_operations(
        operations=operations,
        destination_dir=destination_dir,
    )

    print()
    print(
        f"Done. Copied and verified "
        f"{len(operations)} files."
    )
    print(f"Destination: {destination_dir}")

    return 0


def verify_show_directory(
    show_directory: Path,
) -> int:
    show_directory = show_directory.expanduser().resolve()

    if not show_directory.is_dir():
        print(
            f"Error: show directory does not exist: "
            f"{show_directory}",
            file=sys.stderr,
        )
        return 1

    invalid_files: list[Path] = []
    duplicate_episodes: list[str] = []
    season_episodes: dict[int, dict[int, Path]] = {}

    for path in sorted(
        show_directory.rglob("*"),
        key=lambda item: str(item).casefold(),
    ):
        if not path.is_file():
            continue

        if is_ignored(path):
            continue

        if path.suffix.lower() not in VIDEO_EXTENSIONS:
            continue

        match = ORGANIZED_EPISODE_PATTERN.fullmatch(path.name)

        if match is None:
            invalid_files.append(path)
            continue

        season = int(match.group("season"))
        episode = int(match.group("episode"))

        expected_parent = f"Season {season:02d}"

        if path.parent.name != expected_parent:
            invalid_files.append(path)
            continue

        episodes = season_episodes.setdefault(
            season,
            {},
        )

        existing = episodes.get(episode)

        if existing is not None:
            duplicate_episodes.append(
                f"S{season:02d}E{episode:02d}:\n"
                f"  {existing}\n"
                f"  {path}"
            )
        else:
            episodes[episode] = path

    print(show_directory.name)
    print()

    if not season_episodes:
        print("No organized episode files found.")
    else:
        for season in sorted(season_episodes):
            episodes = sorted(
                season_episodes[season]
            )

            first_episode = episodes[0]
            last_episode = episodes[-1]

            expected = set(
                range(first_episode, last_episode + 1)
            )
            missing = sorted(
                expected - set(episodes)
            )

            print(
                f"Season {season:02d}: "
                f"{len(episodes)} episode(s), "
                f"E{first_episode:02d}-E{last_episode:02d}"
            )

            if missing:
                formatted = ", ".join(
                    f"E{episode:02d}"
                    for episode in missing
                )
                print(f"  Missing: {formatted}")
            else:
                print("  No internal gaps.")

    print()
    print(f"Invalid filenames: {len(invalid_files)}")
    print(
        f"Duplicate episodes: "
        f"{len(duplicate_episodes)}"
    )

    if invalid_files:
        print()
        print("Invalid files:")

        for path in invalid_files:
            print(f"  {path}")

    if duplicate_episodes:
        print()
        print("Duplicates:")

        for duplicate in duplicate_episodes:
            print(duplicate)

    if invalid_files or duplicate_episodes:
        return 1

    return 0


def main() -> int:
    args = parse_args()

    if args.command == "organize":
        return organize(args)

    if args.command == "verify":
        return verify_show_directory(
            args.show_directory,
        )

    print(
        f"Error: unsupported command: {args.command}",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
