---
description: Repository Information Overview
alwaysApply: true
---

# Avilon Information

## Summary
Avilon is a Game Library Manager application built with Python. It provides a graphical interface for managing a collection of games with features like splash screens, game image management, and map integration. The application is designed to be compiled into a standalone Windows executable.

## Structure
- **Root Directory**: Contains main Python scripts, configuration files, and build scripts
- **build/**: Contains PyInstaller build artifacts
- **dist/**: Contains the compiled executable
- **game_images/**: Stores game images uploaded by users
- **test_images/**: Contains test images for validation testing

## Language & Runtime
**Language**: Python
**Version**: Python 3 (compatible with 3.13)
**Build System**: PyInstaller
**Package Manager**: pip

## Dependencies
**Main Dependencies**:
- Pillow >= 9.0.0 (Image processing)
- pywebview >= 4.0.0 (Web content integration)
- tkinter (GUI framework, built into Python)

## Build & Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Build executable
python -m PyInstaller Avilon.spec --clean --noconfirm

# Alternative build using batch file
build_avilon.bat
```

## Configuration
**Main Configuration Files**:
- `avilon_config.json`: Stores user preferences (language, theme, startup settings)
- `avilon_games.json`: Stores game library data
- `Avilon.spec`: PyInstaller configuration for building the executable

## Main Files
**Entry Point**: `Avilon_clean.py`
**Resources**:
- `logo.ico`: Application icon used in the GUI and executable
- `game_images/`: Directory for storing game images

## Testing
**Test Files**: `test_validations.py`
**Test Resources**: `test_images/` directory
**Run Command**:
```bash
python test_validations.py
```

## Features
- Splash screen with animations
- Game library management
- Image handling for games and maps
- Theme customization
- Map integration
- Standalone executable distribution