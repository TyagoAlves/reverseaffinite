# reverseaffinite - Roadmap

## Phase 1: Foundation ✅
- [x] Git repo initialized
- [x] Python/PyQt5 GUI skeleton with professional layout
- [x] Tool palette (Photoshop/Affinity-style left sidebar)
- [x] Canvas with zoom/pan
- [x] Basic tools: pencil, brush, eraser, shape, gradient
- [x] Filter gallery (grayscale, blur, sharpen, edge detect, pixelate)
- [x] Layer stack with opacity, visibility, blend mode selection
- [x] Color panel (RGB/HSL/Hex)
- [x] C++ project structure with CMake

## Phase 2: Core Editing (Current)
- [ ] Non-blocking architecture (worker threads for heavy ops)
- [ ] Full layer blending modes (Multiply, Screen, Overlay, etc.)
- [ ] Selection tools: Rect, Ellipse, Lasso, Magic Wand
- [ ] Move tool with drag layers
- [ ] Undo/redo with history panel
- [ ] Rulers, guides, grid system
- [ ] Clone stamp tool

## Phase 3: Professional Tools
- [ ] Pen/Bezier tool with anchor editing
- [ ] Gradient editor
- [ ] Text tool with font management
- [ ] Healing brush / spot heal
- [ ] Dodge/burn/sponge tools
- [ ] Crop tool
- [ ] Adjustment layers (non-destructive)
- [ ] Layer masks
- [ ] Layer groups
- [ ] Blend-if sliders

## Phase 4: Performance + C++ Engine
- [ ] C++ render pipeline with SIMD
- [ ] OpenGL-accelerated canvas
- [ ] 16-bit/channel support
- [ ] CMYK color space
- [ ] Large image support (5GB+)
- [ ] GPU filter acceleration

## Phase 5: Advanced Features
- [ ] Plugin system (Python scripts)
- [ ] PSD/PSB import/export
- [ ] Raw processing (CR3, NEF, ARW)
- [ ] HDR merge
- [ ] Panorama stitching
- [ ] Layer styles (drop shadow, glow, bevel)
- [ ] Smart objects
- [ ] Video layer support

## Long-term Vision
"Best image editor on Linux" - GIMP alternative with professional UX
- Native Linux (Wayland + X11)
- No subscription
- Open core model
- Community plugin ecosystem
