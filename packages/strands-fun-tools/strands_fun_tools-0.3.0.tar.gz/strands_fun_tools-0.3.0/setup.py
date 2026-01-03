"""Setup configuration for strands-fun-tools."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = (
    readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""
)

setup(
    name="strands-fun-tools",
    version="0.1.1",
    description="Creative and utility tools for Strands AI agents - interactive experiences",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Cagatay Cali",
    author_email="cagataycali@icloud.com",
    url="https://github.com/cagataycali/strands-fun-tools",
    license="Apache-2.0",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.10",
    install_requires=[
        "strands-agents",
        "pyautogui",
        "pyperclip",
        "pillow",
    ],
    extras_require={
        # Note: 'audio' excluded from 'all' due to Python 3.14 compatibility
        # (numba/openai-whisper require Python 3.10-3.13)
        "all": [
            "stockfish",
            "rich",
            "opencv-python",
            "boto3",
            "halo",
            "colorama",
            "jinja2",
            "pyyaml",
            "cryptography",
            "pytesseract",
            "bleak",
            "prompt_toolkit",
        ],
        "chess": ["stockfish", "rich"],
        "vision": ["opencv-python", "ultralytics", "pytesseract", "pillow"],
        "bluetooth": ["bleak"],
        "audio": ["openai-whisper", "sounddevice", "webrtcvad"],
        "display": ["rich", "halo", "colorama"],
        "template": ["jinja2", "rich"],
        "utility": ["pyyaml", "cryptography"],
        "face": ["opencv-python", "boto3"],
        "dialog": ["prompt_toolkit"],
        "dev": [
            "mypy>=1.8.0",
            "black>=24.0.0",
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia",
        "Topic :: Games/Entertainment",
    ],
    keywords="strands ai agents tools bluetooth chess clipboard cursor vision audio fun creative",
    project_urls={
        "Bug Reports": "https://github.com/cagataycali/strands-fun-tools/issues",
        "Source": "https://github.com/cagataycali/strands-fun-tools",
    },
)
