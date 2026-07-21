"""Internationalization module – TOML-based multilingual support, zero extra dependencies.

Pure translation engine; does not read or write config files directly. Language code is passed in by the caller.

Usage::

    from core.i18n import t, get_i18n

    # Initialize at app startup (language code from settings.json)
    i18n = get_i18n()
    i18n.init("en-US")            # or i18n.init("zh-CN")

    # Fetch translation
    msg = t("setup.status_scan_error", error="Bluetooth unavailable")

    # Switch language
    i18n.load_language("zh-CN")

    # List available languages
    langs = i18n.available_languages()  # {"en-US": "English (US)", "zh-CN": "简体中文", ...}

Language files live in ``i18n/``, named in BCP 47 format (e.g. ``en-US.toml``, ``zh-CN.toml``).
The first-line comment ``# language name: <display name>`` is shown in the Settings language picker.
"""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any


def i18n_dir() -> Path:
    """Return the i18n/ directory path; works in dev and PyInstaller bundles."""
    from core.config import PROJECT_ROOT
    return PROJECT_ROOT / "i18n"


class _I18n:
    """Not thread-safe singleton; all GUI access runs on the main thread."""

    def __init__(self) -> None:
        self._lang: str = ""
        self._strings: dict[str, str] = {}
        self._fallback: dict[str, str] = {}
        self._available: dict[str, str] = {}
        self._initialized = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def init(self, language: str) -> None:
        """Initialize with the given language code (first load). Must run before the first ``t()`` call.

        Loads ``en-US.toml`` as fallback, then the file for ``language``.
        """
        if self._initialized:
            return
        self._initialized = True

        # Load English fallback
        en_path = i18n_dir() / "en-US.toml"
        self._load_fallback(en_path)

        # Load target language
        lang = language.strip() if language else "en-US"
        if lang != "en-US" or not self._strings:
            if not self.load_language(lang):
                self._strings = dict(self._fallback)
                lang = "en-US"
        self._lang = lang
        self.available_languages()

    def t(self, key: str, **fmt_kwargs: Any) -> str:
        """Return translation for ``key``, applying ``**fmt_kwargs`` placeholder substitution.

        Fallback chain: current language → English → key itself.
        """
        template = self._strings.get(key) or self._fallback.get(key) or key
        if not fmt_kwargs:
            return template
        try:
            return template.format(**fmt_kwargs)
        except (KeyError, ValueError, IndexError):
            return template

    @property
    def language(self) -> str:
        """Current language code."""
        return self._lang

    def available_languages(self) -> dict[str, str]:
        """Scan ``i18n/`` and return ``{language_code: display_name}``."""
        d = i18n_dir()
        if not d.is_dir():
            self._available = {}
            return {}
        result: dict[str, str] = {}
        for path in sorted(d.glob("*.toml")):
            code = path.stem
            if not code:
                continue
            result[code] = self._read_lang_name(path)
        self._available = result
        return dict(result)

    def load_language(self, lang: str) -> bool:
        """Load language from ``i18n/{lang}.toml``. Returns True on success.

        Does not affect the fallback dict; on failure current strings are unchanged.
        """
        path = i18n_dir() / f"{lang}.toml"
        return self._load_toml(path, lang)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _read_lang_name(path: Path) -> str:
        """Extract language display name from the first-line TOML comment.

        Supported formats: ``# language name: English`` or ``# language name:简体中文``.
        """
        try:
            first_line = path.read_text("utf-8").split("\n", 1)[0].strip()
        except OSError:
            return path.stem
        if first_line.startswith("#") and "language name:" in first_line.lower():
            idx = first_line.lower().find("language name:")
            name = first_line[idx + len("language name:"):].strip()
            name = name.lstrip(":").strip()
            if name:
                return name
        return path.stem

    def _load_toml(self, path: Path, label: str) -> bool:
        """Load and flatten TOML file into self._strings."""
        try:
            raw = tomllib.loads(path.read_text("utf-8"))
        except (OSError, tomllib.TOMLDecodeError):
            return False
        strings = self._flatten(raw)
        if not strings:
            return False
        self._lang = label
        self._strings = strings
        return True

    def _load_fallback(self, path: Path) -> None:
        """Load English fallback dictionary."""
        try:
            raw = tomllib.loads(path.read_text("utf-8"))
            self._fallback = self._flatten(raw)
        except (OSError, tomllib.TOMLDecodeError):
            self._fallback = {}

    @staticmethod
    def _flatten(data: dict, prefix: str = "") -> dict[str, str]:
        """Recursively flatten nested TOML tables into ``section.key`` flat dict."""
        result: dict[str, str] = {}
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                result.update(_I18n._flatten(value, full_key))
            elif isinstance(value, str):
                result[full_key] = value
        return result


# ------------------------------------------------------------------
# Singleton
# ------------------------------------------------------------------

_i18n_instance: _I18n | None = None


def get_i18n() -> _I18n:
    """Get (or create) the ``_I18n`` singleton."""
    global _i18n_instance
    if _i18n_instance is None:
        _i18n_instance = _I18n()
    assert _i18n_instance is not None
    return _i18n_instance


def t(key: str, **fmt_kwargs: Any) -> str:
    """Shortcut: return translation. Same as ``get_i18n().t(key, ...)``."""
    return get_i18n().t(key, **fmt_kwargs)
