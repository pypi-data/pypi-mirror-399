from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Command:
    name: str
    handler: str
    description: str
    visible: bool = True


class CommandRegistry:
    def __init__(self) -> None:
        self._commands: dict[str, Command] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        self.register(Command("/help", "_show_help", "Show available commands"))
        self.register(Command("/status", "_show_status", "Show current agent status"))
        self.register(Command("/stats", "_show_stats", "Show usage statistics"))
        self.register(Command("/config", "_show_config", "Open configuration"))
        self.register(Command("/clear", "_clear_history", "Clear conversation history"))

    def register(self, command: Command) -> None:
        self._commands[command.name] = command

    def find_command(self, text: str) -> Command | None:
        if not text.startswith("/"):
            return None

        # Exact match first
        parts = text.split(" ", 1)
        cmd_name = parts[0]

        return self._commands.get(cmd_name)

    def get_help_text(self) -> str:
        lines = ["## Available Commands", ""]
        for cmd in sorted(self._commands.values(), key=lambda x: x.name):
            if cmd.visible:
                lines.append(f"- `{cmd.name}`: {cmd.description}")
        return "\n".join(lines)

    @property
    def commands(self) -> list[Command]:
        return list(self._commands.values())
