from __future__ import annotations

from collections.abc import Callable
import os
from pathlib import Path

from decoder import DECODER_ROOT


class GlobalPath:
    def __init__(self, resolver: Callable[[], Path]) -> None:
        self._resolver = resolver

    @property
    def path(self) -> Path:
        return self._resolver()


_DEFAULT_DECODER_HOME = Path.home() / ".decoder"


def _get_decoder_home() -> Path:
    if decoder_home := os.getenv("DECODER_HOME"):
        return Path(decoder_home).expanduser().resolve()
    return _DEFAULT_DECODER_HOME


DECODER_HOME = GlobalPath(_get_decoder_home)
GLOBAL_CONFIG_FILE = GlobalPath(lambda: DECODER_HOME.path / "config.toml")
GLOBAL_ENV_FILE = GlobalPath(lambda: DECODER_HOME.path / ".env")
GLOBAL_TOOLS_DIR = GlobalPath(lambda: DECODER_HOME.path / "tools")
GLOBAL_SKILLS_DIR = GlobalPath(lambda: DECODER_HOME.path / "skills")
SESSION_LOG_DIR = GlobalPath(lambda: DECODER_HOME.path / "logs" / "session")
TRUSTED_FOLDERS_FILE = GlobalPath(lambda: DECODER_HOME.path / "trusted_folders.toml")
LOG_DIR = GlobalPath(lambda: DECODER_HOME.path / "logs")
LOG_FILE = GlobalPath(lambda: DECODER_HOME.path / "decoder.log")

DEFAULT_TOOL_DIR = GlobalPath(lambda: DECODER_ROOT / "core" / "tools" / "builtins")
