# reverseaffinite - Agent Guide

## Architecture
- **Python prototype** (`editor/`): Rapid iteration, UI layout, tool prototyping
- **C++ engine** (`cpp_editor/`): Performance-critical rendering, pixel ops, final product
- The Python version serves as design prototype; C++ version is the production target

## Branch Strategy
- `main`: Stable, reviewed code only
- `feature/*`: Individual features (e.g., `feature/layer-blending`, `feature/pen-tool`)

## Agent Types

### Agent: Feature Implementation
- Implements one specific feature per task
- Must update both Python and C++ versions in parallel
- Adds unit tests where applicable
- Outputs: source code changes + brief summary

### Agent: Bug Fix
- Reproduces issue first
- Fixes in both Python and C++
- Verifies fix works

### Agent: Performance
- Profiles hot paths
- Optimizes pixel operations
- Uses numpy/SIMD where possible

## Coding Standards
- No comments in code (self-documenting names)
- Qt5/PyQt5 for UI, numpy for pixel ops
- C++17 standard
- 4-space indentation (Python), 4-space (C++)
- CamelCase for classes, snake_case for functions/variables

## Tool Reference
- Each tool has: `shortcut` (single key), `name`, `press/move/release` handlers
- Tool state lives in the tool instance, not the canvas
- Canvas delegates all interaction to active tool

## Current Tools (by shortcut)
V=Move, M=Select, L=Lasso, W=Magic Wand, B=Brush, P=Pencil
E=Eraser, G=Gradient, U=Shape, S=Clone Stamp, H=Hand, Z=Zoom
I=Color Picker, K=Flood Fill
