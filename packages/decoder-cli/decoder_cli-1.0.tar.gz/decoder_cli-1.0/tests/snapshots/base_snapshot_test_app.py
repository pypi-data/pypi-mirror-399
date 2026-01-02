from __future__ import annotations

from rich.style import Style
from textual.widgets.text_area import TextAreaTheme

from tests.stubs.fake_backend import FakeBackend
from decoder.cli.textual_ui.app import DecoderApp
from decoder.cli.textual_ui.widgets.chat_input import ChatTextArea
from decoder.core.agent import Agent
from decoder.core.config import SessionLoggingConfig, DecoderConfig


def default_config() -> DecoderConfig:
    """Default configuration for snapshot testing.
    Remove as much interference as possible from the snapshot comparison, in order to get a clean pixel-to-pixel comparison.
    - Injects a fake backend to prevent (or stub) LLM calls.
    - Disables the welcome banner animation.
    - Forces a value for the displayed workdir
    - Hides the chat input cursor (as the blinking animation is not deterministic).
    """
    return DecoderConfig(
        session_logging=SessionLoggingConfig(enabled=False),
        textual_theme="gruvbox",
        disable_welcome_banner_animation=True,
        displayed_workdir="/test/workdir",
        enable_update_checks=False,
    )


class BaseSnapshotTestApp(DecoderApp):
    CSS_PATH = "../../decoder/cli/textual_ui/app.tcss"

    def __init__(self, config: DecoderConfig | None = None, **kwargs):
        config = config or default_config()

        super().__init__(config=config, **kwargs)

        self.agent = Agent(
            config,
            mode=self._current_agent_mode,
            enable_streaming=self.enable_streaming,
            backend=FakeBackend(),
        )

    async def on_mount(self) -> None:
        await super().on_mount()
        self._hide_chat_input_cursor()

    def _hide_chat_input_cursor(self) -> None:
        text_area = self.query_one(ChatTextArea)
        hidden_cursor_theme = TextAreaTheme(name="hidden_cursor", cursor_style=Style())
        text_area.register_theme(hidden_cursor_theme)
        text_area.theme = "hidden_cursor"
