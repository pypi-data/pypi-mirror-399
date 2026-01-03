"""Usage statistics tracking for Decoder CLI.

Tracks per-model usage, token consumption, and lines of code written.
Statistics are persisted to ~/.decoder/usage_stats.json.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from decoder.core.paths.global_paths import DECODER_HOME


def _get_stats_file() -> Path:
    return DECODER_HOME.path / "usage_stats.json"


@dataclass
class ModelUsage:
    """Usage statistics for a single model."""
    requests: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens

    def to_dict(self) -> dict[str, int]:
        return {
            "requests": self.requests,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModelUsage:
        return cls(
            requests=data.get("requests", 0),
            prompt_tokens=data.get("prompt_tokens", 0),
            completion_tokens=data.get("completion_tokens", 0),
        )


@dataclass
class DailyStats:
    """Statistics for a single day."""
    date: str
    models: dict[str, ModelUsage] = field(default_factory=dict)
    lines_written: int = 0
    files_created: int = 0
    files_modified: int = 0

    @property
    def total_tokens(self) -> int:
        return sum(m.total_tokens for m in self.models.values())

    @property
    def total_requests(self) -> int:
        return sum(m.requests for m in self.models.values())

    def to_dict(self) -> dict[str, Any]:
        return {
            "date": self.date,
            "models": {k: v.to_dict() for k, v in self.models.items()},
            "lines_written": self.lines_written,
            "files_created": self.files_created,
            "files_modified": self.files_modified,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DailyStats:
        models = {
            k: ModelUsage.from_dict(v)
            for k, v in data.get("models", {}).items()
        }
        return cls(
            date=data.get("date", ""),
            models=models,
            lines_written=data.get("lines_written", 0),
            files_created=data.get("files_created", 0),
            files_modified=data.get("files_modified", 0),
        )


@dataclass
class UsageStats:
    """All-time usage statistics."""
    daily: dict[str, DailyStats] = field(default_factory=dict)

    @property
    def all_time_tokens(self) -> int:
        return sum(d.total_tokens for d in self.daily.values())

    @property
    def all_time_requests(self) -> int:
        return sum(d.total_requests for d in self.daily.values())

    @property
    def all_time_lines_written(self) -> int:
        return sum(d.lines_written for d in self.daily.values())

    @property
    def all_time_files_created(self) -> int:
        return sum(d.files_created for d in self.daily.values())

    @property
    def all_time_files_modified(self) -> int:
        return sum(d.files_modified for d in self.daily.values())

    def get_model_stats(self) -> dict[str, ModelUsage]:
        """Aggregate stats per model across all days."""
        result: dict[str, ModelUsage] = {}
        for daily in self.daily.values():
            for model_name, usage in daily.models.items():
                if model_name not in result:
                    result[model_name] = ModelUsage()
                result[model_name].requests += usage.requests
                result[model_name].prompt_tokens += usage.prompt_tokens
                result[model_name].completion_tokens += usage.completion_tokens
        return result

    def to_dict(self) -> dict[str, Any]:
        return {
            "daily": {k: v.to_dict() for k, v in self.daily.items()},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UsageStats:
        daily = {
            k: DailyStats.from_dict(v)
            for k, v in data.get("daily", {}).items()
        }
        return cls(daily=daily)


class UsageStatsManager:
    """Manager for loading, updating, and saving usage statistics."""

    _instance: UsageStatsManager | None = None
    _stats: UsageStats | None = None

    def __new__(cls) -> UsageStatsManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def stats(self) -> UsageStats:
        if self._stats is None:
            self._stats = self._load()
        return self._stats

    def _load(self) -> UsageStats:
        """Load statistics from file."""
        stats_file = _get_stats_file()
        if not stats_file.exists():
            return UsageStats()

        try:
            data = json.loads(stats_file.read_text(encoding="utf-8"))
            return UsageStats.from_dict(data)
        except (json.JSONDecodeError, ValueError, KeyError):
            return UsageStats()

    def save(self) -> None:
        """Save statistics to file."""
        if self._stats is None:
            return

        stats_file = _get_stats_file()
        stats_file.parent.mkdir(parents=True, exist_ok=True)
        stats_file.write_text(
            json.dumps(self.stats.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _get_today_key(self) -> str:
        return datetime.now().strftime("%Y-%m-%d")

    def _ensure_today(self) -> DailyStats:
        today_key = self._get_today_key()
        if today_key not in self.stats.daily:
            self.stats.daily[today_key] = DailyStats(date=today_key)
        return self.stats.daily[today_key]

    def record_request(
        self, model_name: str, prompt_tokens: int, completion_tokens: int
    ) -> None:
        """Record a request to a model."""
        today = self._ensure_today()

        if model_name not in today.models:
            today.models[model_name] = ModelUsage()

        today.models[model_name].requests += 1
        today.models[model_name].prompt_tokens += prompt_tokens
        today.models[model_name].completion_tokens += completion_tokens

        self.save()

    def record_lines_written(self, count: int, is_new_file: bool = False) -> None:
        """Record lines of code written by AI."""
        today = self._ensure_today()
        today.lines_written += count

        if is_new_file:
            today.files_created += 1
        else:
            today.files_modified += 1

        self.save()

    def get_today_stats(self) -> DailyStats:
        """Get statistics for today."""
        today_key = self._get_today_key()
        return self.stats.daily.get(today_key, DailyStats(date=today_key))

    def get_all_time_stats(self) -> UsageStats:
        """Get all-time statistics."""
        return self.stats

    def format_stats_report(self) -> str:
        """Format a human-readable statistics report."""
        today = self.get_today_stats()
        all_time = self.get_all_time_stats()
        model_stats = all_time.get_model_stats()

        lines = [
            "## 📊 Статистика использования",
            "",
            "### Сегодня",
            f"- **Запросов**: {today.total_requests:,}",
            f"- **Токенов**: {today.total_tokens:,}",
            f"- **Строк кода написано**: {today.lines_written:,}",
            f"- **Файлов создано**: {today.files_created:,}",
            f"- **Файлов изменено**: {today.files_modified:,}",
            "",
            "### За всё время",
            f"- **Запросов**: {all_time.all_time_requests:,}",
            f"- **Токенов**: {all_time.all_time_tokens:,}",
            f"- **Строк кода написано**: {all_time.all_time_lines_written:,}",
            f"- **Файлов создано**: {all_time.all_time_files_created:,}",
            f"- **Файлов изменено**: {all_time.all_time_files_modified:,}",
            "",
        ]

        if model_stats:
            lines.append("### По моделям")
            # Sort by total tokens (most used first)
            sorted_models = sorted(
                model_stats.items(),
                key=lambda x: x[1].total_tokens,
                reverse=True,
            )
            for model_name, usage in sorted_models:
                lines.append(
                    f"- **{model_name}**: {usage.requests:,} запросов, "
                    f"{usage.total_tokens:,} токенов"
                )

        return "\n".join(lines)


# Global instance
usage_stats_manager = UsageStatsManager()
