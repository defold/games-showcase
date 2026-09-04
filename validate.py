#!/usr/bin/env python3

import json
import sys
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent
GAMES_DIR = ROOT / "games"
IMAGES_DIR = GAMES_DIR / "images"
GAME_ORDER = ROOT / "games_order.json"
FEATURED_FULL = ROOT / "showcase_featured_full.json"

REQUIRED_FIELDS = {"name", "description", "url", "developer", "images", "showcase"}
PLACEMENTS = {"full", "half", "more-games", "hidden"}
REQUIRED_IMAGES = {
    "full": {"full", "third"},
    "half": {"half"},
    "more-games": {"third"},
    "hidden": set(),
}
MAX_IMAGE_SIZE = {
    "full": (3200, 1100),
    "half": (1200, 601),
    "third": (800, 600),
}


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Unable to read {path.relative_to(ROOT)}: {error}") from error


def validate():
    errors = []
    games = {}
    referenced_images = set()

    for path in sorted(GAMES_DIR.glob("*.json")):
        game_id = path.stem
        try:
            game = read_json(path)
        except ValueError as error:
            errors.append(str(error))
            continue

        if not isinstance(game, dict):
            errors.append(f"{path.relative_to(ROOT)} must contain a JSON object")
            continue
        if "id" in game:
            errors.append(f"{path.relative_to(ROOT)} must not define id; the filename is the ID")

        missing_fields = REQUIRED_FIELDS - set(game)
        if missing_fields:
            errors.append(f"{game_id}: missing fields: {', '.join(sorted(missing_fields))}")

        placement = game.get("showcase")
        if placement not in PLACEMENTS:
            errors.append(f"{game_id}: invalid showcase placement {placement!r}")

        images = game.get("images")
        if not isinstance(images, dict):
            errors.append(f"{game_id}: images must be an object")
            images = {}

        for role in ("full", "half", "third"):
            filename = images.get(role, "")
            if role in REQUIRED_IMAGES.get(placement, set()) and not filename:
                errors.append(f"{game_id}: {placement} placement requires a {role} image")
            if not filename:
                continue
            if Path(filename).name != filename:
                errors.append(f"{game_id}: image must be a filename, not a path: {filename}")
                continue
            if Path(filename).suffix.lower() != ".webp":
                errors.append(f"{game_id}: only WebP showcase images are allowed: {filename}")
            referenced_images.add(filename)

        games[game_id] = game

    try:
        game_order = read_json(GAME_ORDER)
    except ValueError as error:
        errors.append(str(error))
        game_order = []
    try:
        featured_full = read_json(FEATURED_FULL)
    except ValueError as error:
        errors.append(str(error))
        featured_full = []

    for label, values in (("games_order.json", game_order), ("showcase_featured_full.json", featured_full)):
        if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
            errors.append(f"{label} must contain a JSON array of game IDs")
            continue
        if len(values) != len(set(values)):
            errors.append(f"{label} contains duplicate IDs")
        unknown = set(values) - set(games)
        if unknown:
            errors.append(f"{label} contains unknown IDs: {', '.join(sorted(unknown))}")

    missing_from_order = set(games) - set(game_order)
    if missing_from_order:
        errors.append(f"games_order.json is missing IDs: {', '.join(sorted(missing_from_order))}")

    full_ids = {game_id for game_id, game in games.items() if game.get("showcase") == "full"}
    if set(featured_full) != full_ids:
        missing = full_ids - set(featured_full)
        extra = set(featured_full) - full_ids
        if missing:
            errors.append(f"showcase_featured_full.json is missing full games: {', '.join(sorted(missing))}")
        if extra:
            errors.append(f"showcase_featured_full.json has non-full games: {', '.join(sorted(extra))}")

    image_files = {path.name for path in IMAGES_DIR.iterdir() if path.is_file()}
    missing_images = referenced_images - image_files
    orphan_images = image_files - referenced_images
    if missing_images:
        errors.append(f"Missing referenced images: {', '.join(sorted(missing_images))}")
    if orphan_images:
        errors.append(f"Unreferenced images: {', '.join(sorted(orphan_images))}")

    for filename in sorted(referenced_images & image_files):
        path = IMAGES_DIR / filename
        try:
            with Image.open(path) as image:
                if image.format != "WEBP":
                    errors.append(f"{filename}: file content is {image.format}, expected WEBP")
                for role, max_size in MAX_IMAGE_SIZE.items():
                    if f"-{role}." not in filename:
                        continue
                    if image.width > max_size[0] or image.height > max_size[1]:
                        errors.append(
                            f"{filename}: {image.width}x{image.height} exceeds the {role} limit "
                            f"of {max_size[0]}x{max_size[1]}"
                        )
        except OSError as error:
            errors.append(f"Unable to decode {filename}: {error}")

    return errors, len(games), len(referenced_images)


if __name__ == "__main__":
    validation_errors, game_count, image_count = validate()
    if validation_errors:
        for validation_error in validation_errors:
            print(f"ERROR: {validation_error}", file=sys.stderr)
        sys.exit(1)
    print(f"Validated {game_count} games and {image_count} WebP images")
