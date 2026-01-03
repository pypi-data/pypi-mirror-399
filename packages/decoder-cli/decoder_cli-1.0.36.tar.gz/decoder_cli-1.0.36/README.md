# Decoder

[![PyPI Version](https://img.shields.io/pypi/v/decoder)](https://pypi.org/project/decoder)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/release/python-3120/)
[![License](https://img.shields.io/github/license/qynon/decoder)](https://github.com/qynon/decoder/blob/main/LICENSE)
[![Telegram](https://img.shields.io/badge/Telegram-Join-blue?logo=telegram)](https://t.me/qynon)


**A CLI coding assistant by [qynon](https://t.me/qynon).**

Decoder is a command-line coding assistant powered by various AI models. It provides a conversational interface to your codebase, allowing you to use natural language to explore, modify, and interact with your projects through a powerful set of tools.

> [!WARNING]
> Decoder works on Windows, but we officially support and target UNIX environments.

### Installation

**Using uv (Recommended)**

```bash
uv tool install decoder
```

**Using pip**

```bash
pip install decoder
```

## Features

- **Animated Splash Screen**: A beautiful typing animation and interactive welcome screen.
- **Interactive Chat**: A conversational AI agent that understands your requests and breaks down complex tasks.
- **Powerful Toolset**: A suite of tools for file manipulation, code searching, version control, and command execution.
  - Read, write, and patch files (`read_file`, `write_file`, `search_replace`).
  - Execute shell commands in a stateful terminal (`bash`).
  - Recursively search code with `grep`.
  - Manage a `todo` list to track progress.
- **Project-Aware Context**: Automatically scans project structure and Git status.
- **Highly Configurable**: Customize models, providers, and themes via `config.toml`.
- **Safety First**: Tool execution approval for all destructive actions.

## Quick Start

1. Navigate to your project's root:
   ```bash
   cd /path/to/your/project
   ```

2. Run Decoder:
   ```bash
   decoder
   ```

3. Follow the onboarding to set up your API keys.

## Configuration

Decoder is configured via `config.toml` (located in `~/.decoder/config.toml`).

### API Keys
Set your keys in `~/.decoder/.env`:
```bash
ONLYSQ_API_KEY=your_key
```

## License

Copyright 2025 qynon

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the [LICENSE](LICENSE) file for the full license text.
