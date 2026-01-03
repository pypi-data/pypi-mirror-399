# MacAgent Core

> **Free, open-source AI orchestration for macOS**

MacAgent Core is a local-first, privacy-respecting AI assistant with mathematical audit integrity. Every action is cryptographically signed and tamper-evident.

## Features

- 🧠 **Local-First AI** - Uses Ollama locally. Your data never leaves your Mac.
- 📊 **HMAC-SHA256 Audit Trail** - Cryptographically signed action logs
- 🎙️ **Voice Control** - Siri integration with 21 natural commands
- 🛡️ **5-Tier Safety** - Risk-assessed actions from auto-allow to voice verification

## Installation

```bash
# Via pip (recommended)
pip install macagent-core

# Via Homebrew tap
brew tap midnightnow/tools && brew install macagent
```

## Quick Start

```bash
# Check status
macagent status

# Run with local LLM
macagent

# Voice command via Siri
macagent siri "open Documents in Finder"
```

## Requirements

- macOS 12 (Monterey) or later
- Apple Silicon (M1/M2/M3/M4)
- Optional: Ollama for local LLM

## License

MIT License - See [LICENSE](LICENSE) for details.

## Pro/Max/Ultra

For advanced features like Tinhat EMF scanning, WiFi/Bluetooth imaging, OS4AI engine, and fleet management, see [macagent.pro](https://macagent.pro).
