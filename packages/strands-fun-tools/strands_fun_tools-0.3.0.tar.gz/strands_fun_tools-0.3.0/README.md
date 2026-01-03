# 🎨 Strands Fun Tools

Creative and utility tools for Strands AI agents - Bluetooth, vision, cursor control, audio, and more!

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## 📦 Installation

```bash
# Base installation (human_typer only)
pip install strands-fun-tools

# With specific features
pip install "strands-fun-tools[cursor,clipboard,vision]"

# Everything
pip install "strands-fun-tools[all]"
```

## 🛠️ Available Tools

### 🎮 Interaction
- **human_typer** - Human-like typing with emotions and typos
- **cursor** - Mouse & keyboard automation (pyautogui)
- **clipboard** - Clipboard monitoring & history
- **dialog** - Interactive terminal prompts

### 👁️ Vision
- **screen_reader** - OCR-based screen monitoring
- **yolo_vision** - Real-time object detection (YOLOv8)
- **face_recognition** - Face detection via AWS Rekognition
- **take_photo** - Camera capture & burst mode

### 🎤 Audio
- **listen** - Background audio transcription (Whisper)

### 📡 Connectivity
- **bluetooth** - BLE device monitoring & GATT operations

### ♟️ Games
- **chess** - Stockfish chess engine integration

### 🎨 Display
- **spinner_generator** - Custom loading animations
- **template** - Jinja2 template rendering
- **asciimatics_ui** - Terminal UI framework

### 🔧 Utilities
- **utility** - Crypto, encoding, hashing, JSON/YAML
- **dynamic_package** - Execute any Python package function
- **npm** - Run npm packages from Python

## 🚀 Quick Start

```python
from strands import Agent
from strands_fun_tools import human_typer, cursor, clipboard

agent = Agent(
    tools=[human_typer, cursor, clipboard],
    system_prompt="You can type like a human and control the cursor!"
)

agent("Type 'Hello World!' with excited emotion and then copy it to clipboard")
```

## 📋 Tool Reference

| Tool | Install Extra | Key Actions |
|------|---------------|-------------|
| **human_typer** | *(base)* | Type with emotions: calm, excited, thoughtful, rushed, nervous |
| **cursor** | `[cursor]` | move, click, drag, type_text, hotkey |
| **clipboard** | `[clipboard]` | start, read, write, get_history |
| **screen_reader** | `[vision]` | start, capture_once, find_element |
| **yolo_vision** | `[vision]` | start, detect_once, query_objects |
| **face_recognition** | `[face]` | detect_faces, compare_faces |
| **take_photo** | `[vision]` | capture, burst, list_cameras |
| **listen** | `[audio]` | start, stop, get_transcripts |
| **bluetooth** | `[bluetooth]` | start, scan_once, list_devices, read_characteristic |
| **chess** | `[chess]` | new_game, get_best_move, make_move, analyze |
| **spinner_generator** | `[display]` | Display 50+ spinner types |
| **template** | `[template]` | create, render Jinja2 templates |
| **utility** | `[utility]` | encode, decode, hash, encrypt |
| **dynamic_package** | *(base)* | execute any Python function |
| **npm** | *(base)* | execute npm packages |
| **dialog** | `[dialog]` | Interactive terminal prompts |
| **asciimatics_ui** | `[ui]` | Terminal UI framework |

## 🎯 Examples

### Background Monitoring
```python
from strands import Agent
from strands_fun_tools import bluetooth, clipboard, yolo_vision

agent = Agent(tools=[bluetooth, clipboard, yolo_vision])

agent("""
Start monitoring:
1. Bluetooth devices nearby
2. Clipboard content changes  
3. Objects visible on camera
""")
```

### Autonomous Screen Control
```python
from strands import Agent
from strands_fun_tools import screen_reader, cursor

agent = Agent(tools=[screen_reader, cursor])

agent("""
1. Find the 'Submit' button on screen
2. Click it
""")
```

### Human-Like Typing
```python
agent.tool.human_typer(
    text="Hello World!",
    emotion="excited",      # calm, excited, thoughtful, rushed, nervous
    typo_rate=2,           # 0-10 percentage
    thinking_pauses=True   # Pause at punctuation
)
```

## 📚 Documentation

Full documentation at [github.com/cagataycali/strands-fun-tools](https://github.com/cagataycali/strands-fun-tools)

## 🤝 Contributing

Issues and PRs welcome!

```bash
git clone https://github.com/cagataycali/strands-fun-tools.git
cd strands-fun-tools
pip install -e ".[all,dev]"
```

## 📄 License

Apache-2.0 - see [LICENSE](LICENSE)

---

<div align="center">
Built with ❤️ for the Strands community
</div>
