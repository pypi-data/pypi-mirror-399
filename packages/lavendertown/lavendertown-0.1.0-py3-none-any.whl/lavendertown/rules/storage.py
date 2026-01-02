"""Rule persistence and storage utilities."""

from __future__ import annotations

import json
from pathlib import Path

from lavendertown.rules.models import RuleSet


def save_ruleset(ruleset: RuleSet, file_path: str | Path) -> None:
    """Save a RuleSet to a JSON file.

    Args:
        ruleset: RuleSet to save
        file_path: Path to save the ruleset to
    """
    path = Path(file_path)
    ruleset_dict = ruleset.to_dict()

    with open(path, "w", encoding="utf-8") as f:
        json.dump(ruleset_dict, f, indent=2, ensure_ascii=False)


def load_ruleset(file_path: str | Path) -> RuleSet:
    """Load a RuleSet from a JSON file.

    Args:
        file_path: Path to load the ruleset from

    Returns:
        RuleSet object loaded from file

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file format is invalid
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Ruleset file not found: {file_path}")

    with open(path, "r", encoding="utf-8") as f:
        try:
            ruleset_dict = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in ruleset file: {e}") from e

    try:
        return RuleSet.from_dict(ruleset_dict)
    except (KeyError, TypeError) as e:
        raise ValueError(f"Invalid ruleset format: {e}") from e


def ruleset_to_json(ruleset: RuleSet) -> str:
    """Convert a RuleSet to JSON string.

    Args:
        ruleset: RuleSet to convert

    Returns:
        JSON string representation
    """
    return json.dumps(ruleset.to_dict(), indent=2, ensure_ascii=False)


def ruleset_from_json(json_str: str) -> RuleSet:
    """Create a RuleSet from a JSON string.

    Args:
        json_str: JSON string representation

    Returns:
        RuleSet object

    Raises:
        ValueError: If the JSON format is invalid
    """
    try:
        ruleset_dict = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}") from e

    try:
        return RuleSet.from_dict(ruleset_dict)
    except (KeyError, TypeError) as e:
        raise ValueError(f"Invalid ruleset format: {e}") from e
