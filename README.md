# Self-AI-Knowledge

Multi-model AI knowledge base and Skill hub.

## Overview

统一包裹并记录三类 AI CLI 交互，自动将交互中的有价值内容沉淀为个人知识库：

- **gemini CLI**
- **codex CLI / GitHub Copilot CLI**  
- **claude / claude code**

## Features

- 🎙️ **Session Recording** - 录制所有 CLI 交互，保持原始上下文
- 🧠 **Knowledge Extraction** - 从会话中提取可信信息、个人思维、技术笔记
- 🛠️ **Skill System** - 基于标准 SKILL.md 的可复用技能
- 🔍 **Full-Text Search** - SQLite FTS5 全文索引
- 🌐 **Web Interface** - 美观的时间线和知识浏览界面

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/Adversit/self-ai-knowledge.git
cd self-ai-knowledge
pip install -e ".[dev]"

# 2. Copy config
cp config.example.toml config.toml
# Edit config.toml with your preferences

# 3. Initialize database
acv init

# 4. Start recording a session
acv run claude --project my-project

# 5. Summarize and promote knowledge
acv summarize --session <session-id>
acv promote --session <session-id> --candidate-index 0 --category tech_notes

# 6. Start web interface
acv web
```

## Project Structure

```
self-ai-knowledge/
├── backend/
│   ├── acv_cli/         # Typer CLI package
│   ├── acv_api/         # FastAPI backend
│   └── services/        # Business logic services
├── web/                 # React + Tailwind frontend
├── data/                # Data storage
│   ├── sessions/        # Session recordings
│   └── knowledge/       # Knowledge items
├── skills/              # Agent Skills
└── docs/                # Documentation
```

## License

MIT
