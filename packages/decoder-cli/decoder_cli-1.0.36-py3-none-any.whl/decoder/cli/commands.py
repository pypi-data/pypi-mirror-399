from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Command:
    name: str
    handler: str
    description: str
    aliases: list[str] = field(default_factory=list)
    visible: bool = True


class CommandRegistry:
    def __init__(self) -> None:
        self._commands: dict[str, Command] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        self.register(Command("/help", "_show_help", "Show available commands", aliases=["/help", "/?"]))
        self.register(Command("/status", "_show_status", "Show current agent status", aliases=["/status"]))
        self.register(Command("/stats", "_show_stats", "Show usage statistics", aliases=["/stats"]))
        self.register(Command("/config", "_show_config", "Open configuration", aliases=["/config"]))
        self.register(Command("/clear", "_clear_history", "Clear conversation history", aliases=["/clear"]))

    def register(self, command: Command) -> None:
        self._commands[command.name] = command
        # Ensure name is also in aliases for finding
        for alias in command.aliases:
            if alias != command.name:
                # We store only by name in the main dict, but could map aliases if needed.
                # The current find_command logic needs to support aliases.
                pass

    def find_command(self, text: str) -> Command | None:
        if not text.startswith("/"):
            return None

        parts = text.split(" ", 1)
        cmd_name = parts[0]

        # Search by name first
        if cmd := self._commands.get(cmd_name):
            return cmd

        # Search by alias
        for cmd in self._commands.values():
            if cmd_name in cmd.aliases:
                return cmd

        return None

    def get_help_text(self) -> str:
        lines = ["## Available Commands", ""]
        for cmd in sorted(self._commands.values(), key=lambda x: x.name):
            if cmd.visible:
                aliases_str = f" ({', '.join(a for a in cmd.aliases if a != cmd.name)})" if len(cmd.aliases) > 1 else ""
                lines.append(f"- `{cmd.name}`{aliases_str}: {cmd.description}")
        return "\n".join(lines)

    @property
    def commands(self) -> dict[str, Command]:
        return self._commands
