"""
JSON Flattening utility for ublkit.

Flattens nested JSON with support for arrays and custom separators.
"""

from __future__ import annotations

from typing import Any, Dict


class JSONFlattener:
    """
    Flattens nested JSON dictionaries with array indexing.

    Converts nested structures like:
    {"Invoice": {"cac:InvoiceLine": [{"cbc:ID": "1"}, {"cbc:ID": "2"}]}}

    Into flat structure:
    {"Invoice/cac:InvoiceLine[0]/cbc:ID": "1", "Invoice/cac:InvoiceLine[1]/cbc:ID": "2"}
    """

    def __init__(self, separator: str = "/") -> None:
        """
        Initialize JSONFlattener.

        Args:
            separator: Separator for nested keys (default: "/")
        """
        self._separator = separator

    def flatten(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Flatten nested dictionary into single-level dictionary.

        Args:
            data: Nested dictionary to flatten

        Returns:
            Flattened dictionary with paths as keys
        """
        result: Dict[str, Any] = {}
        self._flatten_recursive(data, "", result)
        return result

    def _flatten_recursive(
        self,
        value: Any,
        current_path: str,
        result: Dict[str, Any],
    ) -> None:
        """Recursively flatten nested structures."""
        if value is None:
            result[current_path] = None

        elif isinstance(value, dict):
            if not value:
                result[current_path] = {}
            elif "value" in value:
                for key, val in value.items():
                    if key == "value":
                        result[current_path] = val
                    else:
                        new_path = self._build_path(current_path, key)
                        self._flatten_recursive(val, new_path, result)
            else:
                for key, val in value.items():
                    new_path = self._build_path(current_path, key)
                    self._flatten_recursive(val, new_path, result)

        elif isinstance(value, list):
            if not value:
                result[current_path] = []
            else:
                for idx, item in enumerate(value):
                    indexed_path = f"{current_path}[{idx}]"
                    self._flatten_recursive(item, indexed_path, result)
        else:
            result[current_path] = value

    def _build_path(self, current_path: str, key: str) -> str:
        """Build path for nested key."""
        if current_path:
            return f"{current_path}{self._separator}{key}"
        return key
