"""Export functionality for findings."""

from __future__ import annotations

from lavendertown.export.csv import (
    export_summary_to_csv,
    export_summary_to_csv_file,
    export_to_csv,
    export_to_csv_file,
)
from lavendertown.export.json import export_to_json, export_to_json_file

__all__ = [
    "export_to_json",
    "export_to_json_file",
    "export_to_csv",
    "export_to_csv_file",
    "export_summary_to_csv",
    "export_summary_to_csv_file",
]

# Optional exports - only available if dependencies are installed
try:
    from lavendertown.export.pandera import (  # noqa: F401
        export_ruleset_to_pandera,
        export_ruleset_to_pandera_file,
    )

    __all__.extend(["export_ruleset_to_pandera", "export_ruleset_to_pandera_file"])
except ImportError:
    pass

try:
    from lavendertown.export.great_expectations import (  # noqa: F401
        export_ruleset_to_great_expectations,
        export_ruleset_to_great_expectations_file,
        export_ruleset_to_great_expectations_json,
    )

    __all__.extend(
        [
            "export_ruleset_to_great_expectations",
            "export_ruleset_to_great_expectations_json",
            "export_ruleset_to_great_expectations_file",
        ]
    )
except ImportError:
    pass
