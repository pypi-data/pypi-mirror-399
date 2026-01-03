# MiMo CLI 🤖

Your terminal AI assistant with tools to edit files and run commands.

## ⚡ Quick Setup

**Config file:** `~/.mimo/config.toml`

Just run `mimo` - it will automatically create the config file if it doesn't exist.

## 🔧 Configuration

### Config File (`~/.mimo/config.toml`)
```toml
[llm]
model = "openai/gpt-4o-mini"
# api_base = "https://api.example.com/v1"
# api_key = "your-key-here"

[permissions]
auto_accept_editor = false  # Auto-accept file edits in current directory
```

### Environment Variables
```bash
export MIMO_MODEL="openai/gpt-4o-mini"
export MIMO_API_BASE="https://api.example.com/v1"
export MIMO_API_KEY="your-key-here"
```

### CLI Arguments
```bash
mimo --model openai/gpt-4
mimo --api-base https://custom-api.com/v1
```

## 🚀 Usage
```bash
mimo                    # Start chatting (creates config if missing)
mimo --model gpt-4      # Use specific model
```

---
*Created by MiMo* 🎯
