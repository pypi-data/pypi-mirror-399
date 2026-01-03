# Copyright (C) 2021-2025, University of Porto and Tau Toolbox developers.
#
# This file is part of Tautoolbox package.
#
# Tautoolbox is free software: you can redistribute it and/or modify it
# under the terms of version 3 of the GNU Lesser General Public License as
# published by the Free Software Foundation.
#
# Tau Toolbox is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
# General Public License for more details.

from contextlib import contextmanager
from copy import deepcopy
from typing import Any

import numpy as np

from ..polynomial.bases import BASES

eps = np.spacing(1)  # the same as sys.float_info.epsilon


class Settings:
    """Immutable snapshot of options with specific values."""

    def __init__(self, values: dict[str, Any]):
        """Initialize with a dictionary of values."""
        # Store values as private attributes to prevent modification
        object.__setattr__(self, "_values", values.copy())

    def __getattr__(self, name: str) -> Any:
        """Get option value."""
        if name.startswith("_"):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

        if name in self._values:
            return self._values[name]
        else:
            raise AttributeError(f"No option named '{name}'")

    def __setattr__(self, name: str, value: Any):
        """Prevent modification of options after creation."""
        if name.startswith("_"):
            object.__setattr__(self, name, value)
        else:
            raise AttributeError(f"Settings is immutable. Cannot set '{name}'.")

    def get(self, name: str, default: Any = None) -> Any:
        """Get option value with optional default."""
        return self._values.get(name, default)

    def to_dict(self) -> dict[str, Any]:
        """Get dictionary representation of all option values."""
        return self._values.copy()

    def __repr__(self) -> str:
        lines = [f"{self.__class__.__name__}("]
        for key, value in sorted(self._values.items()):
            lines.append(f"    {key}={value!r}")
        lines.append(")")
        return "\n".join(lines)

    def __eq__(self, other) -> bool:
        """Compare two Settings objects."""
        if not isinstance(other, Settings):
            return False
        return self._values == other._values

    def copy(self):
        return deepcopy(self)


class SettingsFactory:
    """Tautoolbox solver settings."""

    # Define known parameters as class-level defaults
    _ORIGINAL_DEFAULTS = {
        "basis": "ChebyshevT",
        "degree": 31,
        "pieces": 1,
    }

    # Define validators for each parameter
    _VALIDATORS = {
        "basis": lambda x: isinstance(x, str) and x in set(BASES),
        "degree": lambda x: isinstance(x, int) and x > 0,
        "pieces": lambda x: isinstance(x, int) and x > 0,
    }

    def __init__(self, **default_overrides):
        """Initialize with default values, optionally overriding some defaults."""
        # Keep original defaults immutable
        self._original_defaults = self._ORIGINAL_DEFAULTS.copy()

        # Current effective defaults (can be modified by session)
        self._current_defaults = self._original_defaults.copy()

        # Session overrides that change the default behavior
        self._session_overrides = {}

        # Validate and apply any constructor default overrides
        for key, value in default_overrides.items():
            if key not in self._original_defaults:
                raise ValueError(f"Unknown setting: '{key}'")
            self._validate_parameter(key, value)
            self._original_defaults[key] = value
            self._current_defaults[key] = value

    def _validate_parameter(self, key: str, value: Any) -> None:
        """Validate a parameter value using the appropriate validator."""
        if key not in self._VALIDATORS:
            # No validator defined - accept any value
            return

        validator = self._VALIDATORS[key]
        try:
            if not validator(value):
                raise ValueError(f"Invalid value for '{key}': {value!r}")
        except Exception as e:
            # Validator itself failed (e.g., type error in lambda)
            raise ValueError(f"Validation failed for '{key}' with value {value!r}: {e}")

    def _get_effective_defaults(self) -> dict[str, Any]:
        """Get the current effective defaults (original + session overrides)."""
        result = self._current_defaults.copy()
        result.update(self._session_overrides)
        return result

    def __call__(self, **kwargs) -> Settings:
        """
        Create an options snapshot.

        - settings() -> returns snapshot with current effective defaults
        - settings(param=value, ...) -> returns snapshot with specified overrides
        """
        # Start with effective defaults (original + session overrides)
        result_values = self._get_effective_defaults()

        # Apply and validate any call-specific overrides
        for key, value in kwargs.items():
            if key not in self._original_defaults:
                available = ", ".join(sorted(self._original_defaults.keys()))
                raise ValueError(f"Unknown setting: '{key}'. Available settings: {available}")

            self._validate_parameter(key, value)
            result_values[key] = value

        return Settings(result_values)

    def session(self, **kwargs) -> Settings:
        """
        Set session defaults and return snapshot with those defaults.

        This changes the default behavior of future settings() calls.
        """
        # Validate and set session overrides
        for key, value in kwargs.items():
            if key not in self._original_defaults:
                available = ", ".join(sorted(self._original_defaults.keys()))
                raise ValueError(f"Unknown setting: '{key}'. Available settings: {available}")

            self._validate_parameter(key, value)
            self._session_overrides[key] = value

        # Return snapshot with new effective defaults
        return Settings(self._get_effective_defaults())

    def reset(self, *args) -> Settings:
        """
        Reset specified session parameters to original defaults, or all if no args.
        Returns snapshot with reset defaults.
        """
        if not args:
            # Reset all session overrides
            self._session_overrides.clear()
        else:
            # Reset specific parameters
            for param in args:
                if param in self._session_overrides:
                    del self._session_overrides[param]
                elif param not in self._original_defaults:
                    available = ", ".join(sorted(self._original_defaults.keys()))
                    raise ValueError(
                        f"Unknown setting: '{param}'. Available settings: {available}"
                    )

        # Return snapshot with reset defaults
        return Settings(self._get_effective_defaults())

    def get_defaults(self) -> dict[str, Any]:
        """Get dictionary of current effective default values."""
        return self._get_effective_defaults()

    def get_original_defaults(self) -> dict[str, Any]:
        """Get dictionary of original default values (before any session changes)."""
        return self._original_defaults.copy()

    def get_session_overrides(self) -> dict[str, Any]:
        """Get dictionary of current session overrides."""
        return self._session_overrides.copy()

    def has_session_overrides(self) -> bool:
        """Check if any session overrides are currently active."""
        return bool(self._session_overrides)

    def validate_all_defaults(self) -> None:
        """Validate all current effective default values. Useful for debugging."""
        effective_defaults = self._get_effective_defaults()
        for key, value in effective_defaults.items():
            try:
                self._validate_parameter(key, value)
            except ValueError as e:
                print(f"Validation error in effective defaults: {e}")

    @contextmanager
    def temporary_session(self, **kwargs):
        """Context manager for temporarily overriding session defaults."""
        # Backup current session overrides
        old_session_overrides = self._session_overrides.copy()

        try:
            # Apply temporary session overrides (with validation)
            for key, value in kwargs.items():
                if key not in self._original_defaults:
                    raise ValueError(f"Unknown setting: '{key}'")
                self._validate_parameter(key, value)
                self._session_overrides[key] = value
            yield self
        finally:
            # Restore previous session overrides
            self._session_overrides = old_session_overrides

    def __repr__(self) -> str:
        effective = self._get_effective_defaults()
        overrides = self._session_overrides

        lines = [f"{self.__class__.__name__}("]
        lines.append("  effective_defaults={")
        for key, value in sorted(effective.items()):
            override_marker = " *" if key in overrides else ""
            lines.append(f"    {key}={value!r}{override_marker}")
        lines.append("  }")
        lines.append(")")

        if overrides:
            lines.append("(* = session override)")

        return "\n".join(lines)


settings = SettingsFactory()
