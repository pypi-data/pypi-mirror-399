from __future__ import annotations

import argparse
import sys
from importlib import resources
from pathlib import Path

ASSET_PACKAGE = "arp_sts_keycloak.assets"
ASSET_FILES = ("docker-compose.yml", "realm-export.json")


def _read_asset_text(name: str) -> str:
    return resources.files(ASSET_PACKAGE).joinpath(name).read_text(encoding="utf-8")


def _ensure_writeable_targets(output_dir: Path, force: bool) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    targets = [output_dir / name for name in ASSET_FILES]
    if force:
        return targets
    existing = [path for path in targets if path.exists()]
    if existing:
        names = ", ".join(path.name for path in existing)
        raise FileExistsError(f"Refusing to overwrite existing files: {names}")
    return targets


def write_assets(output_dir: Path, force: bool) -> list[Path]:
    targets = _ensure_writeable_targets(output_dir, force)
    written: list[Path] = []
    for target in targets:
        content = _read_asset_text(target.name)
        target.write_text(content, encoding="utf-8")
        written.append(target)
    return written


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="arp-sts-keycloak",
        description=(
            "Write a Keycloak docker compose file and ARP dev realm bootstrap."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser(
        "init", help="Write docker-compose.yml and realm-export.json."
    )
    init_parser.add_argument(
        "-o",
        "--output",
        default=".",
        help="Directory to write assets (default: current directory).",
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files if they already exist.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "init":
        output_dir = Path(args.output)
        try:
            written = write_assets(output_dir, args.force)
        except FileExistsError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        for path in written:
            print(path)
        return 0

    parser.error(f"Unhandled command: {args.command}")
    return 2
