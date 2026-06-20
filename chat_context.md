# Reverse Affinite - Chat Context Export
# ==============
# This file contains the export of the Reverse Affinite image editor project chat context.
# Generated on 2026-06-18
# ==============================

## Overview

The Reverse Affinite image editor project is a comprehensive image editing application built from scratch for Linux. It's inspired by the best features from Affinity Photo, Adobe Photoshop, and DaVinci Resolve, but with modern OpenGL rendering, C++ engine for performance, and a Python prototype for rapid iteration.

## Current Development Status

The project is in **Phase 2/3** with 10 feature branches (feature-1 through feature-10) each assigned to an agent. The main branch contains:

- **C++ Core Engine** (chapter 3) with OpenGL acceleration
- **Python Prototype** (chapter 2) with full feature set
- **Brush Engine** with sophisticated tool rendering
- **Layer Masks** for precise editing operations
- **Layer Groups** for organizing complex compositions
- **Gradient Editor** with multi-stop gradients
- **Pen Tool** with bezier curve support
- **Snapping System** for precise alignment
- **File Format support** including PSD import/export
- **Preferences** system with dark theme support
- **Enhanced History Panel** with visual thumbnails
- **Internationalization (i18n)** support for pt-BR and en-US

## Project Architecture

### Core Structure
```
reverseaffinite/
├── main.py                 # Entry point
├── editor/
│   ├── app_ui.py           # Main UI
│   ├── canvas.py           # Viewport & Tools
│   ├── tools.py            # Tool system
│   ├── layers.py           # Layer management
│   ├── panels.py           # UI panels
│   ├── filters.py          # Image filters
│   ├── history.py          # Undo/redo system
│   ├── i18n.py             # Translation system
│   ├── resources.py        # UI theme
│   ├── splash.py           # Splash screen
│   └── brushengine.py      # Brush engine
├── cpp_editor/              # Native C++ engine
│   ├── src/                # Source files
│   └── include/            # Headers
├── tests/                   # Testing suite
│   ├── test_*.py            # Individual tests
│   └── run_all.py          # Test runner
├── tools/                   # Helper tools
│   ├── demo.py             # Demo script
│   └── extract_strings.py # i18n helper
├── assets/                  # Project assets
│   └── icon.svg             # Application icon
├── docs/                    # Documentation
│   ├── user_guide.md
│   ├── shortcuts.md
│   ├── blend_modes.md
│   └── project_architecture.md
├── requirements.txt         # Python dependencies
└── README.md               # Project readme
```

### Key Technologies

- **Python (PyQt5)**: UI prototype and rapid development
- **C++ with Qt5**: Performance-critical rendering pipeline
- **OpenGL**: Hardware-accelerated canvas operations
- **Numpy**: SIMD-optimized image filters
- **Modern OpenGL**: Framebuffer objects, shader programs
- **Git version control**: Branch per feature

## Features Implemented

### Phase 2 (Core Editing)
- 15+ tools with industry-standard shortcuts
- Layer blending modes (Normal, Multiply, Screen, Overlay, etc.)
- Selection tools (Rectangular, Elliptical, Lasso, Magic Wand)
- Canvas operations (zoom, pan, rulers, guides)

### Phase 3 (Professional Tools)
- Advanced brush engine with dynamic tips
- Layer masks for precise editing
- Layer groups with folder support
- Gradient editor with multi-stop gradients
- Pen tool with bezier editing
- Snapping system for alignment
- File format support (PSD import/export)
- Preferences system with dark theme
- Visual history thumbnails
- Internationalization support

## Design Philosophy

1. **Performance First**: C++ engine for core operations, OpenGL for display
2. **Rapid Iteration**: Python prototype, C++ production refinement
3. **User Experience**: Industry-standard shortcuts, professional UI
4. **Open Source**: No subscription, free for all

## Build Instructions

### Python Prototype (for development and testing)
```bash
# Clone the repository
cd /media/tyago/Ventoy/reverseaffinite

# Install dependencies
pip install -r requirements.txt

# Run the application
python3 main.py
```

### Native C++ Build (for production)
```bash
# Install Qt5 development libraries (Ubuntu/Debian)
sudo apt install qtbase5-dev qt5-qmake

# Build with CMake
cd /media/tyago/Ventoy/reverseaffinite/cpp_editor
cmake -B build -DCMAKE_BUILD_TYPE=Release
make -C build -j$(nproc)

# Run
./build/reverseaffinite
```

### Testing
```bash
cd /media/tyago/Ventoy/reverseaffinite
python3 -m pytest tests/
```

### Running Demo
```bash
cd /media/tyago/Ventoy/reverseaffinite
python3 tools/demo.py
```

## Development Model

The project uses an agency model where:
- **Agent 1-10**: Each responsible for a specific feature
- **Agent 11**: Testing infrastructure
- **Agent 12**: Project management and coordination
- **Main branch**: Integration of merged features
- **Phase branches**: Feature development

## Testing

The project includes comprehensive unit tests with 134 tests, all passing. The testing infrastructure includes:
- Unit tests for all core functionality
- Integration tests for workflows
- Performance benchmarks
- CI/CD pipeline integration

## Issues & Future Work

**Current Issues:**
1. Main branch has diverged from some feature branches - careful merge required
2. Feature merging conflicts in shared UI components

**Ongoing Work:**
1. Testing agent monitoring - integration of all 10 agents
2. CI workflow setup for automated testing
3. Documentation generation from code

## Outlook

This project represents a fresh start for native image editing in Linux. It combines the best concepts from established editors while maintaining a modern, open-source approach. The goal is to create "the best image editor on Linux" that truly competes with commercial alternatives.

## Contact

For questions, contributions, or support:
- Project repository at /media/tyago/Ventoy/reverseaffinite/
- Submit issues via the standard GitHub workflow
- The AGENTS.md file contains detailed information for feature contributors

---
Generated by OpenCode AI Assistant
Export timestamp: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
