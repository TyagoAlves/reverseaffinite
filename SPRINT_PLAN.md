# Sprint 3 Plan

**Planned:** 2026-06-18 to 2026-06-25
**Project:** reverseaffinite Photo Editor

---

## What Was Accomplished

### Sprint 2 (Current — commit 9590cbf)
- ✅ C++ engine scaffolding with SIMD pixel ops, OpenGL canvas
- ✅ Blend modes: Normal, Multiply, Screen, Overlay, Darken, Lighten, Color Dodge, Color Burn, Hard Light, Soft Light, Difference, Exclusion
- ✅ Selection tools: Rect, Ellipse, Lasso, Magic Wand with marching ants
- ✅ Layer stack with add/remove/duplicate/move/flatten/merge_visible
- ✅ Adjustment layers: Brightness/Contrast, HSL, Levels
- ✅ Tool system: 19 tools with keyboard shortcuts
- ✅ Filters: grayscale, invert, brightness, contrast, levels, hue_saturation, color_balance, curves, gaussian_blur, sharpen, edge_detect, pixelate, posterize, sepia, heal_patch, noise_reduce
- ✅ Undo/Redo (100-level)
- ✅ Color panel (RGB/HSL/Hex)
- ✅ Rulers, grid display
- ✅ Dark theme
- ✅ Splash screen
- ✅ 136 unit tests (134 passing)
- ✅ Documentation (architecture, user guide, shortcuts, blend modes)
- ✅ Brush engine core (CircleTip, SquareTip, TextureTip, stroke rendering)
- ✅ Guide system (horizontal/vertical, save/load)
- ✅ Snapping engine (grid, guides, bounds, layers)
- ✅ Path system (bezier anchors/handles/segments)
- ✅ Gradient editor (linear/radial, stop editing)
- ✅ i18n framework with `_()` shorthand, 3 locales (EN/ES/PT-BR), ~270 strings
- ✅ History panel with thumbnails
- ✅ Preferences dialog structure
- ✅ File format export options

---

## What's Remaining

### Must-Have for v0.2
| Priority | Feature | Status | Effort | Dependencies |
|----------|---------|--------|--------|-------------|
| P0 | **Merge all branches to main** | Blocked | 2 days | Conflict resolution in 5 files |
| P0 | **Layer masks** | Not started | 3 days | Layer system |
| P0 | **Layer groups** | Not started | 2 days | Layer stack |
| P1 | **Pen tool curve editing** | Partially done | 2 days | Path system working |
| P1 | **Brush preset system** | Partially done | 1 day | Brush engine (can split) |
| P1 | **Preferences dialog** | Partially done | 2 days | i18n integration |
| P1 | **Fix 2 failing tests** | Ready | 0.5 day | Test expectations |
| P2 | **C++ engine integration** | Started | 5 days | Python prototype stable |

### Nice-to-Have
| Feature | Status | Effort |
|---------|--------|--------|
| Texture brush presets | Not started | 1 day |
| RTL language support (Arabic, Hebrew) | Not started | 1 day |
| Keyboard shortcut customization | Not started | 1 day |
| Plugin system | Not started | 5 days |

---

## Task Splitting Recommendations

Some feature branches are too broad and should be split for parallel development:

### feature-brush-engine → Split into:
1. **feature-brush-presets** — JSON preset load/save, preset list UI
2. **feature-brush-texture** — TextureTip with image-based brush textures
3. **feature-brush-dynamics** — Size/opacity/flow jitter and pressure sensitivity

### feature-preferences → Split into:
1. **feature-prefs-dialog** — Preferences dialog UI
2. **feature-prefs-shortcuts** — Custom keyboard shortcut mapping
3. **feature-prefs-performance** — Memory/performance settings

### feature-i18n → Split into:
1. **feature-i18n-framework** — Core translation engine (already done)
2. **feature-i18n-locales** — Community translation files
3. **feature-i18n-rtl** — RTL and bidirectional text support

---

## Merge Strategy

### Safe to merge now (no conflicts with each other):
1. `feature-snapping` — `snapping.py` is new file, no conflicts
2. `feature-brush-engine` — `brushengine.py` is new file, no conflicts
3. `feature-pen-edit` — `path.py` is new file, no conflicts
4. `feature-i18n` — `i18n.py` + `locale/` are new, no conflicts
5. `feature-gradient-editor` — `gradient.py`, `gradient_editor.py` are new, no conflicts

### Requires careful merge (have conflicts with each other):
1. `feature-history-thumbs` — conflicts with feature-preferences on panels.py, history.py, canvas.py, app_ui.py
2. `feature-file-formats` — conflicts with feature-preferences on tools.py, canvas.py, app_ui.py
3. `feature-preferences` — conflicts with ALL branches (it has accumulated all work)

### Recommended merge order:
1. First merge new-file-only branches (snapping, brush-engine, pen-edit, gradient-editor, i18n)
2. Then merge feature-history-thumbs
3. Then merge feature-file-formats
4. Finally merge feature-preferences as the integration branch
5. Resolve conflicts sequentially

---

## Priority Order for Remaining Work

```
Sprint 3a (Days 1-2): Merge & Stabilize
  └─ Merge 5 safe feature branches → main
  └─ Fix 2 failing tests
  └─ Resolve conflicts in feature-history-thumbs, feature-file-formats, feature-preferences
  └─ Commit and push integrated main

Sprint 3b (Days 3-4): Layer Features
  └─ Implement feature-layer-masks (P0)
  └─ Implement feature-layer-groups (P0)
  └─ Wire masks and groups into UI

Sprint 3c (Days 5-7): Polish & Extend
  └─ Pen tool curve editing (P1)
  └─ Brush presets (P1)
  └─ Preferences dialog (P1)
  └─ Split tasks and assign to agents
```

---

## Estimated Timeline

| Milestone | Date | Deliverable |
|-----------|------|-------------|
| All branches merged | 2026-06-20 | Integrated main branch |
| Layer masks + groups | 2026-06-22 | feature-layer-masks, feature-layer-groups on main |
| Pen editing + presets | 2026-06-24 | Working pen curve editing, brush presets |
| Preferences + test fix | 2026-06-25 | Preferences dialog, 136/136 tests passing |
| Sprint 3 complete | 2026-06-25 | v0.2 release candidate |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Merge conflicts in 5+ files | High | High | Merge incrementally; resolve conflicts one branch at a time |
| Working tree changes lost | Medium | Critical | Commit or stash all working changes before branch switching |
| Feature-layer-masks incomplete | Medium | High | Start immediately after merge; reuse existing layer infrastructure |
| C++ engine integration stalled | Low | Medium | Python prototype is sufficient for v0.2; defer C++ to Sprint 4 |
