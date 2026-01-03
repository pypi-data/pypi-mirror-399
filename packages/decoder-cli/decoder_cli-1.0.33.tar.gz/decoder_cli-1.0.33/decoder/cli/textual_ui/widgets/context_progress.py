from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from textual.reactive import reactive
from textual.widgets import Static


@dataclass
class TokenState:
    max_tokens: int = 0
    current_tokens: int = 0
    session_tokens: int = 0  # Total tokens spent in session


class ContextProgress(Static):
    tokens = reactive(TokenState())

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def watch_tokens(self, new_state: TokenState) -> None:
        parts = []


        if new_state.session_tokens > 0:
            if new_state.session_tokens >= 1000:
                tokens_str = f"{new_state.session_tokens / 1000:.1f}k"
            else:
                tokens_str = str(new_state.session_tokens)
            parts.append(f" {tokens_str} токенов")

        # Show context percentage
        if new_state.max_tokens > 0:
            percentage = min(
                100, int((new_state.current_tokens / new_state.max_tokens) * 100)
            )
            parts.append(f"{percentage}% контекста")

        if parts:
            self.update(" │ ".join(parts))
        else:
            self.update("")

