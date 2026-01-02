from __future__ import annotations

from decoder.core.config import Backend
from decoder.core.llm.backend.generic import GenericBackend

BACKEND_FACTORY = {Backend.GENERIC: GenericBackend}
