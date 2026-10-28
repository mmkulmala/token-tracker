# 🪙 Token Tracker for Claude Code

This is a Python-based graphical user interface (GUI) tool designed to scan and estimate the total token count of your game project files when interacting with Anthropic's Claude models. It helps you easily analyze your codebase and predict which Claude subscription plan (Tier) you will need for your future coding workflows.

## ✨ Features

- **Folder Scanning**: Select your game project's root directory directly from the graphical user interface.
- **Automatic Language Detection**: Instantly identifies and categorizes your files based on their extensions (e.g., Python, Godot GDScript, C# for Unity/Unreal, etc.).
- **File & Token Breakdown**: Displays file names, detected languages, sizes (KB), and token estimates in a clean, scrollable table.
- **Smart Filtering**: Automatically ignores heavy repository or environment folders (such as `.git`, `node_modules`, `venv`, `__pycache__`) so they won't distort your game's true context size.
- **Dynamic Tier Recommendation**: Calculates your estimated daily token volume based on your custom prompt iterations, advising whether you fit into the **Free ($0/mo)**, **Pro ($20/mo)**, **Max 5x ($100/mo)**, or **Max 20x ($200/mo)** tiers.

## 📦 Installation
Install as an application (creates a `token-tracker` command):

```bash
uv tool install .
```

Then run:

```bash
token-tracker
```

For development, run directly:

```bash
uv run token_tracker.py
```

Since this project uses the modern `uv` package manager, installation and execution are extremely fast and straightforward.

### 1. Ensure System Dependencies (Linux)
The interface uses Python's built-in `tkinter` library. On some Linux distributions (such as Ubuntu/Debian), it must be installed at the system level. Run this command if needed:
```bash
sudo apt update && sudo apt install python3-tk
```

### 2. Running the Application
Navigate to your project directory and run the application using the following command:
```bash
uv run token_tracker.py
```

## ⚙️ Project Settings (`pyproject.toml`)
The project is configured as an installable package:

```toml
[project]
name = "token-tracker"
version = "0.1.0"
description = "Token tracker"
readme = "README.md"
requires-python = ">=3.11"
dependencies = []

[project.scripts]
token-tracker = "token_tracker:main"

[tool.uv]
package = true
```

## 📝 Supported Languages & Formats
The tool automatically detects and estimates tokens for common game development files, including:
- **Python** (`.py`)
- **Godot GDScript** (`.gd`)
- **C# / C++ / C** (`.cs`, `.cpp`, `.hpp`, `.h`, `.c`)
- **JavaScript / TypeScript** (`.js`, `.ts`)
- **Web files** (`.html`, `.css`)
- **Configurations & Docs** (`.json`, `.yaml`, `.toml`, `.xml`, `.md`)

## 📏 Estimation Limits
Tier recommendation thresholds used by the app:
- **FREE Tier**: total context <= 60,000 tokens and daily volume <= 200,000 tokens
- **PRO Tier**: daily volume > 200,000 tokens
- **MAX 5x**: total context > 60,000 tokens or daily volume > 1,500,000 tokens
- **MAX 20x**: total context > 150,000 tokens or daily volume > 5,000,000 tokens

Token estimate uses ~4 characters per token. Sliders for daily iterations and estimated output per prompt affect daily volume and can move the recommendation up or down.
