# 🎨 Strands Fun Tools

**Creative and interactive tools for Strands AI agents** - Build agents with unique capabilities for Bluetooth, vision, cursor control, screen reading, chess, and more!

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

---

## ✨ Features

- **🔵 Bluetooth Monitoring** - Background device scanning, proximity detection, GATT operations
- **♟️ Chess Engine** - Stockfish integration for playing and analyzing chess
- **📋 Clipboard Management** - Monitor and control system clipboard with history
- **🖱️ Cursor Control** - Mouse automation with PyAutoGUI
- **👁️ Screen Reading** - OCR-based screen monitoring for autonomous control
- **📸 Computer Vision** - YOLO object detection, face recognition, photo capture
- **🎤 Audio Transcription** - Whisper-based continuous audio listening
- **🎨 Display Tools** - Human-like typing, custom spinners, templates
- **🔧 Utilities** - Cryptography, encoding, hashing, JSON/YAML processing
- **📦 Dynamic Packages** - Execute any Python package function at runtime

---

## 📦 Installation

### Basic Installation

```bash
pip install strands-fun-tools
```

This installs core dependencies: `strands-agents`, `pyautogui`, `pyperclip`, `pillow`

### Full Installation (All Features)

```bash
pip install "strands-fun-tools[all]"
```

### Selective Installation

Install only the features you need:

```bash
# Chess
pip install "strands-fun-tools[chess]"

# Vision (YOLO, face recognition, screen reader)
pip install "strands-fun-tools[vision]"

# Bluetooth
pip install "strands-fun-tools[bluetooth]"

# Audio transcription
pip install "strands-fun-tools[audio]"

# Templates & display
pip install "strands-fun-tools[template,display]"

# Utilities (crypto, YAML)
pip install "strands-fun-tools[utility]"
```

---

## 🚀 Quick Start

### Simple Agent Example

```python
from strands import Agent
from strands_fun_tools import clipboard, cursor, screen_reader

agent = Agent(
    tools=[clipboard, cursor, screen_reader],
    system_prompt="You can read screens and control the cursor!"
)

# Agent autonomously reads screen and clicks elements
response = agent("""
1. Read what's on my screen
2. Find the 'Submit' button
3. Click it
""")
```

### Background Monitoring Example

```python
from strands import Agent
from strands_fun_tools import bluetooth, clipboard, yolo_vision

agent = Agent(
    tools=[bluetooth, clipboard, yolo_vision],
    system_prompt="You have background monitoring capabilities!"
)

# Start background monitoring
agent("""
1. Start monitoring Bluetooth devices nearby
2. Start monitoring my clipboard
3. Start YOLO vision to detect objects from camera
4. Tell me when you detect my iPhone nearby or see a person
""")
```

---

## 🛠️ Available Tools

### 📡 Connectivity Tools

#### **bluetooth** - BLE Device Monitoring & Control

```python
# Start background scanning
agent.tool.bluetooth(action="start", scan_interval=5)

# Scan once
agent.tool.bluetooth(action="scan_once", duration=5)

# List discovered devices
agent.tool.bluetooth(action="list_devices")

# Get specific device
agent.tool.bluetooth(action="get_device", address="AA:BB:CC:DD:EE:FF")

# GATT operations
agent.tool.bluetooth(action="list_services", address="AA:BB:CC:DD:EE:FF")
agent.tool.bluetooth(action="read_characteristic", address="...", characteristic_uuid="...")
```

**Features:**
- Background BLE scanning
- Proximity detection (very_close/near/medium/far)
- GATT read/write/subscribe operations
- Device discovery logging
- RSSI-based proximity zones

---

### 🎮 Interactive Tools

#### **chess** - Stockfish Chess Engine

```python
# New game
agent.tool.chess(action="new_game", fen="startpos")

# Get best move
agent.tool.chess(action="get_best_move", depth=15, time=1000)

# Make move
agent.tool.chess(action="make_move", move="e2e4")

# Analyze position
agent.tool.chess(action="analyze", depth=20)
```

**Features:**
- Stockfish 16+ integration
- Position analysis with depth control
- Move validation
- Visual board display
- FEN notation support

---

#### **clipboard** - Clipboard Monitoring & Control

```python
# Start monitoring
agent.tool.clipboard(action="start", check_interval=1)

# Read clipboard
agent.tool.clipboard(action="read")

# Write to clipboard
agent.tool.clipboard(action="write", content="Hello World!")

# Get history
agent.tool.clipboard(action="get_history", limit=10)
```

**Features:**
- Background clipboard monitoring
- Content classification (url, code, email, text, number, file_path)
- Deduplication (only logs changes)
- Timestamped history logging
- Content preview

---

#### **cursor** - Mouse & Keyboard Control

```python
# Get position
agent.tool.cursor(action="position")

# Move cursor
agent.tool.cursor(action="move", x=100, y=100)
agent.tool.cursor(action="smooth_move", x=500, y=500, duration=1.0)

# Click
agent.tool.cursor(action="click", button="left")
agent.tool.cursor(action="double_click")

# Type text
agent.tool.cursor(action="type_text", text="Hello!")

# Keyboard shortcuts
agent.tool.cursor(action="hotkey", keys=["cmd", "c"])  # Copy
```

**Features:**
- Absolute and relative movement
- Smooth animated movement
- Left/right/middle click, drag
- Keyboard input and hotkeys
- Screen size detection

---

### 👁️ Vision Tools

#### **screen_reader** - OCR-Based Screen Monitoring

```python
# Start background monitoring
agent.tool.screen_reader(action="start", interval=2)

# Single capture
agent.tool.screen_reader(action="capture_once")

# Find element by text
agent.tool.screen_reader(action="find_element", search_text="Submit")

# List all detected elements
agent.tool.screen_reader(action="list_elements")
```

**Features:**
- Background OCR scanning with pytesseract
- Text detection with bounding boxes
- Element coordinates for clicking
- Content deduplication
- Timestamped element history

---

#### **yolo_vision** - Object Detection

```python
# Start background detection
agent.tool.yolo_vision(action="start", interval=2, model="yolov8n")

# Single detection
agent.tool.yolo_vision(action="detect_once")

# Get recent detections
agent.tool.yolo_vision(action="get_recent_detections", limit=10)

# Query objects
agent.tool.yolo_vision(action="query_objects", object_class="person")
```

**Features:**
- Background YOLOv8 object detection
- Real-time camera monitoring
- Object counting and tracking
- Confidence scoring
- Timestamped detection logging

---

#### **face_recognition** - AWS Rekognition

```python
# Detect faces in image
agent.tool.face_recognition(
    action="detect_faces",
    image_path="photo.jpg"
)

# Compare faces
agent.tool.face_recognition(
    action="compare_faces",
    source_image="face1.jpg",
    target_image="face2.jpg",
    similarity_threshold=80
)
```

**Features:**
- Face detection with AWS Rekognition
- Face comparison and similarity scoring
- Emotion detection
- Age range estimation
- Gender classification

---

#### **take_photo** - Camera Capture

```python
# Single photo
agent.tool.take_photo(action="capture", save_path="photo.jpg")

# Burst mode
agent.tool.take_photo(
    action="burst",
    count=5,
    interval=1.0,
    save_path="burst"
)

# List available cameras
agent.tool.take_photo(action="list_cameras")
```

**Features:**
- Single and burst capture modes
- Multiple camera support
- Configurable resolution
- Parallel burst capture
- Auto-timestamped filenames

---

### 🎤 Audio Tools

#### **listen** - Whisper Audio Transcription

```python
# Start listening
agent.tool.listen(action="start")

# Get recent transcripts
agent.tool.listen(action="get_transcripts", limit=10)

# Stop listening
agent.tool.listen(action="stop")
```

**Features:**
- Background audio monitoring
- OpenAI Whisper transcription
- Voice activity detection (VAD)
- Timestamped transcription logging
- Configurable language support

---

### 🎨 Display & UI Tools

#### **human_typer** - Human-Like Typing Simulation

```python
agent.tool.human_typer(
    text="Hello World!",
    emotion="excited",        # calm, excited, thoughtful, rushed, nervous
    typo_rate=2,             # 0-10 percentage
    thinking_pauses=True
)
```

**Features:**
- 5 emotion-based typing speeds
- Random typo generation
- Thinking pauses at punctuation
- Backspace corrections
- Variable typing rhythm

---

#### **spinner_generator** - Custom Loading Spinners

```python
agent.tool.spinner_generator(
    spinner_type="dots12",
    text="Loading...",
    color="cyan",
    duration=3
)
```

**Available spinners:** dots, line, pipe, star, moon, clock, arrow, bounce, and 50+ more!

---

#### **template** - Jinja2 Template Rendering

```python
# Create template
agent.tool.template(
    action="create",
    name="report",
    content="# Report for {{ name }}\n\nScore: {{ score }}"
)

# Render template
agent.tool.template(
    action="render",
    name="report",
    data={"name": "User", "score": 95}
)
```

**Features:**
- Jinja2 template engine
- Template creation and storage
- Variable substitution
- File and string rendering

---

### 🔧 Utility Tools

#### **utility** - Cryptography & Encoding

```python
# Encoding
agent.tool.utility(action="base64_encode", text="secret")
agent.tool.utility(action="url_encode", text="hello world")

# Hashing
agent.tool.utility(action="hash", text="password", algorithm="sha256")

# Encryption
agent.tool.utility(action="encrypt", text="secret", key="encryption-key")

# JSON/YAML formatting
agent.tool.utility(action="format_json", text='{"a":1}', indent=2)
```

**Features:**
- Base64, URL, HTML encoding/decoding
- SHA256, MD5, Blake2b hashing
- Fernet encryption/decryption
- UUID generation
- JSON/YAML formatting

---

#### **dynamic_package** - Runtime Package Executor

```python
# Execute any Python function
agent.tool.dynamic_package(
    action="execute",
    package="math",
    function="sqrt",
    args=[16]
)

# List available functions
agent.tool.dynamic_package(
    action="list_functions",
    package="random"
)
```

**Features:**
- Execute any installed package function
- Dynamic function discovery
- Arguments and kwargs support
- Function listing

---

#### **npm** - NPM Package Executor

```python
# Execute npm package
agent.tool.npm(
    action="execute",
    package="cowsay",
    args=["Hello from NPM!"]
)

# Install and execute
agent.tool.npm(
    action="execute",
    package="figlet",
    args=["Cool Text"],
    install=True
)
```

**Features:**
- Execute any npm package
- Auto-installation support
- Arguments passing
- Stdout/stderr capture

---

## 🎯 Complete Example Agent

```python
"""Complete example agent with all fun tools."""

from strands import Agent
from strands_fun_tools import (
    bluetooth,
    chess,
    clipboard,
    cursor,
    screen_reader,
    yolo_vision,
    human_typer,
    spinner_generator,
    template,
    utility,
)

agent = Agent(
    tools=[
        bluetooth,
        chess,
        clipboard,
        cursor,
        screen_reader,
        yolo_vision,
        human_typer,
        spinner_generator,
        template,
        utility,
    ],
    system_prompt="""You are a creative AI agent with unique interactive capabilities.

You can:
- Monitor Bluetooth devices and detect proximity
- Play chess using the Stockfish engine
- Monitor and control the system clipboard
- Control the mouse cursor and automate tasks
- Read the screen using OCR
- Detect objects using YOLO vision
- Type with human-like characteristics
- Display custom loading spinners
- Render Jinja2 templates
- Perform cryptography and encoding operations

Be creative and explore these capabilities!""",
)

if __name__ == "__main__":
    # Example usage
    response = agent(
        """Show me what you can do! Start by:
1. Scanning for Bluetooth devices nearby
2. Getting my clipboard content
3. Detecting what's on my screen
4. Playing a move in chess"""
    )
    print(response)
```

---

## 🔥 Advanced Use Cases

### Autonomous Computer Control

Combine `screen_reader` + `cursor` for autonomous GUI interaction:

```python
from strands import Agent
from strands_fun_tools import screen_reader, cursor

agent = Agent(
    tools=[screen_reader, cursor],
    system_prompt="You can see and control the computer screen."
)

# Agent autonomously finds and clicks UI elements
agent("""
1. Find the 'File' menu on screen
2. Click it
3. Find 'Save' option
4. Click it
""")
```

### Proximity-Based Automation

Use `bluetooth` proximity detection:

```python
from strands import Agent
from strands_fun_tools import bluetooth

agent = Agent(
    tools=[bluetooth],
    system_prompt="Monitor my iPhone proximity and alert when I leave."
)

# Start monitoring
agent("""
Start monitoring my iPhone's Bluetooth signal.
Alert me when the signal drops below -70 dBm (I'm walking away).
""")
```

### Multi-Modal Monitoring

Combine multiple background monitors:

```python
from strands import Agent
from strands_fun_tools import bluetooth, clipboard, yolo_vision, listen

agent = Agent(
    tools=[bluetooth, clipboard, yolo_vision, listen],
    system_prompt="You have multi-modal awareness!"
)

# Start all monitors
agent("""
1. Start Bluetooth monitoring (detect devices)
2. Start clipboard monitoring (track copies)
3. Start YOLO vision (detect objects)
4. Start audio listening (transcribe speech)
5. Report any interesting events
""")
```

---

## 📚 Tool Reference

| Tool | Purpose | Key Actions |
|------|---------|-------------|
| **bluetooth** | BLE device monitoring & GATT | start, scan_once, list_devices, list_services, read_characteristic, subscribe |
| **chess** | Stockfish chess engine | new_game, get_best_move, make_move, analyze |
| **clipboard** | Clipboard management | start, read, write, get_history, clear_history |
| **cursor** | Mouse & keyboard control | move, click, drag, type_text, hotkey |
| **screen_reader** | OCR screen monitoring | start, capture_once, find_element, list_elements |
| **yolo_vision** | Object detection | start, detect_once, query_objects, get_recent_detections |
| **face_recognition** | Face detection (AWS) | detect_faces, compare_faces |
| **take_photo** | Camera capture | capture, burst, list_cameras |
| **listen** | Audio transcription | start, stop, get_transcripts |
| **human_typer** | Human-like typing | type with emotion and typos |
| **spinner_generator** | Loading animations | display custom spinners |
| **template** | Jinja2 templates | create, render, list |
| **utility** | Crypto & encoding | encode, decode, hash, encrypt |
| **dynamic_package** | Python packages | execute, list_functions |
| **npm** | NPM packages | execute (with auto-install) |

---

## 📋 Background Monitoring Tools

Several tools support **background monitoring mode**:

| Tool | Monitors | Interval | Logs To |
|------|----------|----------|---------|
| **bluetooth** | BLE devices | 2-60s | `.bluetooth_monitor/devices.jsonl` |
| **clipboard** | Clipboard content | 0.5-5s | `.clipboard_monitor/clipboard.jsonl` |
| **screen_reader** | Screen OCR | 1-10s | `.screen_monitor/elements.jsonl` |
| **yolo_vision** | Camera objects | 1-10s | `.yolo_detections/detections.jsonl` |
| **listen** | Audio speech | Continuous | `.audio_transcripts/transcripts.jsonl` |

**Pattern:**
```python
# Start monitoring
tool(action="start", interval=2)

# Query recent events
tool(action="get_history", limit=10)

# Stop monitoring
tool(action="stop")
```

---

## 🧪 Testing Tools

```python
from strands import Agent
from strands_fun_tools import chess, utility, template

agent = Agent(tools=[chess, utility, template])

# Test chess
agent("Start a new chess game and suggest the best opening move")

# Test utility
agent("Encode 'secret message' in base64 and then hash it with SHA256")

# Test template
agent("Create a template for a greeting card and render it with name='Alice'")
```

---

## 🔐 Security & Privacy

**Tools that access hardware:**
- `take_photo`, `yolo_vision`, `listen` - **Camera/microphone access**
- `bluetooth` - **Network scanning**
- `cursor`, `screen_reader` - **Screen access and control**

**Best practices:**
- Run agents in trusted environments only
- Review agent system prompts carefully
- Monitor background logging directories
- Clear history logs periodically
- Use firewall rules for network tools

---

## 🐛 Troubleshooting

### **Bluetooth not finding devices**
- Ensure Bluetooth is enabled
- Run with sudo on Linux: `sudo python agent.py`
- Grant Bluetooth permissions on macOS

### **YOLO not detecting objects**
- First run downloads YOLOv8 model (~6MB)
- Ensure camera permissions granted
- Check camera index (default: 0)

### **Screen reader finding no text**
- Install Tesseract: `brew install tesseract` (macOS)
- Ensure pytesseract can find tesseract binary
- Try higher resolution screenshots

### **Cursor control not working in container**
- PyAutoGUI requires GUI environment
- Not available in Docker containers
- Run on host machine with display

---

## 📖 Dependencies

**Core:**
- `strands-agents` - Strands AI framework
- `pyautogui` - Cursor control
- `pyperclip` - Clipboard access
- `pillow` - Image processing

**Optional (by feature):**
- **Chess:** `stockfish`, `rich`
- **Vision:** `opencv-python`, `ultralytics`, `pytesseract`
- **Bluetooth:** `bleak`
- **Audio:** `openai-whisper`, `sounddevice`, `webrtcvad`
- **Display:** `rich`, `halo`, `colorama`
- **Templates:** `jinja2`
- **Utilities:** `pyyaml`, `cryptography`, `boto3`
- **Dialog:** `prompt_toolkit`

---

## 🤝 Contributing

Issues and PRs welcome at [github.com/cagataycali/strands-fun-tools](https://github.com/cagataycali/strands-fun-tools)

**Development setup:**
```bash
git clone https://github.com/cagataycali/strands-fun-tools.git
cd strands-fun-tools
pip install -e ".[all,dev]"
```

---

## 📜 License

Apache-2.0 License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Built with:
- [Strands Agents](https://github.com/strands-agents/sdk-python) - AI agent framework
- [Stockfish](https://stockfishchess.org/) - Chess engine
- [YOLOv8](https://github.com/ultralytics/ultralytics) - Object detection
- [Whisper](https://github.com/openai/whisper) - Audio transcription
- [Bleak](https://github.com/hbldh/bleak) - Bluetooth Low Energy
- [PyAutoGUI](https://github.com/asweigart/pyautogui) - GUI automation
- [Pytesseract](https://github.com/madmaze/pytesseract) - OCR

---

<div align="center">
  <p><strong>🎨 Make your AI agents fun and interactive! 🚀</strong></p>
  <p>Built with ❤️ for the Strands community</p>
</div>
