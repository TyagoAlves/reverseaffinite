```
██████╗ ███████╗██╗   ██╗███████╗██████╗ ███████╗███████╗███████╗██╗███╗   ██╗██╗████████╗███████╗
██╔══██╗██╔════╝██║   ██║██╔════╝██╔══██╗██╔════╝██╔════╝██╔════╝██║████╗  ██║██║╚══██╔══╝██╔════╝
██████╔╝█████╗  ██║   ██║█████╗  ██████╔╝█████╗  ███████╗█████╗  ██║██╔██╗ ██║██║   ██║   █████╗
██╔══██╗██╔══╝  ╚██╗ ██╔╝██╔══╝  ██╔══██╗██╔══╝  ╚════██║██╔══╝  ██║██║╚██╗██║██║   ██║   ██╔══╝
██║  ██║███████╗ ╚████╔╝ ███████╗██║  ██║███████╗███████║██║     ██║██║ ╚████║██║   ██║   ███████╗
╚═╝  ╚═╝╚══════╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝   ╚═╝   ╚══════╝
```

> **The best image editor for Linux — built from scratch.**
> A melhor edição de imagens para Linux — construída do zero.

[![Status](https://img.shields.io/badge/status-active%20development-brightgreen)](#)
[![Python](https://img.shields.io/badge/python-3.8+-blue)](#)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green)](#)
[![License](https://img.shields.io/badge/license-MIT-orange)](#)

---

## Features ✨

- 🎨 **15+ Professional Tools** — Move, Brush, Eraser, Pen (Bezier), Gradient, Shape, Text, Clone Stamp, Healing Brush, Crop, and more
- 🧩 **Layer Stack** with 12 blend modes (Normal, Multiply, Screen, Overlay, etc.), opacity, and visibility controls
- 🎯 **Selection Tools** — Rectangular, Elliptical, Lasso, Magic Wand — with marching ants animation
- 🔍 **Filter Gallery** — Blur, Sharpen, Edge Detect, Pixelate, Posterize, Grayscale, Invert, Sepia
- ⚙️ **Adjustment Layers** — Non-destructive Brightness/Contrast, HSL, Levels
- 🖊️ **Pen/Bezier Tool** — Cubic curves with control handles, like Illustrator/Photoshop
- 🩹 **Healing Brush** — Clone texture with automatic color matching
- 📐 **Rulers, Grid & Snap** — Precision layout tools
- 🔄 **Full Undo/Redo** — 100-level history with interactive History Panel
- 🎨 **Color Panel** — RGB, HSL, and Hex color input
- ⌨️ **Keyboard-First Design** — Every tool has a single-key shortcut (V, M, B, P, E, G...)
- 🧪 **C++ Engine** (in development) — Performance-critical rendering pipeline

---

## Screenshots 📸

> *Screenshots coming soon.*

```
┌──────────────────────────────────────────────────────────────┐
│ [File] [Edit] [Image] [Layer] [Filter] [View]   — □ ×       │
├────────┬─────────────────────────────────────────┬───────────┤
│ ┌────┐ │                                         │ ┌───────┐ │
│ │tools│ │               Canvas                   │ │panels │ │
│ │     │ │                                         │ │       │ │
│ └────┘ │                                         │ └───────┘ │
├────────┴─────────────────────────────────────────┴───────────┤
│ Status: Ready                         X: 500  Y: 300  R:255  │
└──────────────────────────────────────────────────────────────┘
```

---

## Quick Install 🚀

```bash
# Clone the repository
git clone <repo-url>
cd reverseaffinite

# Install dependencies
pip install -r requirements.txt

# Run!
python main.py
```

**Dependencies:**
- Python 3.8+
- PyQt5 ≥ 5.15
- numpy ≥ 1.21
- Pillow ≥ 9.0

---

## Design Philosophy 🧠

**Keyboard-first.** Every tool in reverseaffinite is accessible via a single keystroke. The interface is designed so you never need to take your hands off the keyboard to switch between painting, selecting, zooming, or picking colors.

**Professional layout.** Tool palette on the left (like Photoshop/Affinity), options bar on top, panels on the right. Familiar to anyone coming from professional image editors.

**Non-destructive by design.** Adjustment layers and history snapshots ensure you can always go back. The filter gallery applies changes destructively (for now), but adjustment layers let you tweak parameters indefinitely.

---

## Inspired By 🌟

| Software | What we learned |
|----------|-----------------|
| **Affinity Photo** | Clean UI, layer panel, tool organization |
| **Adobe Photoshop** | Tool behavior, blend modes, keyboard shortcuts |
| **DaVinci Resolve** | Professional workflow, keyboard-first philosophy |

---

## Project Structure 📁

```
reverseaffinite/
├── main.py                  # Application entry point
├── editor/                  # Python engine (rapid prototyping)
│   ├── app_ui.py            # Main window, menus, toolbars
│   ├── canvas.py            # Graphics view, zoom, pan, rendering
│   ├── tools.py             # All 15+ tools and their shortcuts
│   ├── layers.py            # Layer stack, blend modes, compositing
│   ├── filters.py           # Image filters and adjustments
│   ├── history.py           # Undo/redo system with snapshots
│   ├── panels.py            # Color, Layer, History panels
│   └── _colorspace.py       # RGB/HSL/LAB conversions
├── cpp_editor/              # C++ engine (future performance)
├── assets/                  # Icons and resources
├── docs/                    # User documentation (Portuguese/English)
└── plugins/                 # Plugin system (future)
```

---

## Contributing 🤝

See [ROADMAP.md](ROADMAP.md) for the development roadmap and [AGENTS.md](AGENTS.md) for
contribution guidelines and coding standards.

We welcome contributions! Areas we'd love help with:
- C++ rendering engine
- GPU acceleration (OpenGL/CUDA)
- Plugin system
- Additional blend modes
- File format support (PSD, TIFF, RAW)

---

## License 📄

MIT License — see LICENSE file for details.

---

*Built with ❤️ for the Linux creative community.*
