#!/usr/bin/env python3
"""
Extract translatable strings from editor/ source files.
Scans for _("...") calls and reports untranslated strings.
"""

import ast
import json
import os
import sys
from pathlib import Path


EDITOR_DIR = Path(__file__).resolve().parent.parent / "editor"
LOCALE_DIR = Path(__file__).resolve().parent.parent / "locale"


def extract_strings_from_file(filepath):
    """Parse a .py file and return all string literals passed to _()."""
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=str(filepath))
        except SyntaxError as e:
            print(f"  [SKIP] {filepath}: {e}", file=sys.stderr)
            return set()

    strings = set()

    class _CallVisitor(ast.NodeVisitor):
        def visit_Call(self, node):
            if (
                isinstance(node.func, ast.Name)
                and node.func.id == "_"
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            ):
                strings.add(node.args[0].value)
            self.generic_visit(node)

    _CallVisitor().visit(tree)
    return strings


def load_locale(lang_code):
    path = LOCALE_DIR / f"{lang_code}.json"
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    merged = {}
    for module_strings in data.values():
        merged.update(module_strings)
    return merged


def main():
    all_strings = set()

    print("Scanning editor/ for _() calls...")
    for root, _dirs, files in os.walk(EDITOR_DIR):
        for fn in files:
            if fn.endswith(".py"):
                path = os.path.join(root, fn)
                rel = os.path.relpath(path, EDITOR_DIR.parent)
                strings = extract_strings_from_file(path)
                if strings:
                    print(f"  {rel}: {len(strings)} strings")
                all_strings.update(strings)

    print(f"\nTotal unique strings found: {len(all_strings)}")

    # Check existing locale files
    langs_found = 0
    for fn in sorted(os.listdir(LOCALE_DIR)):
        if not fn.endswith(".json"):
            continue
        code = fn[:-5]
        translations = load_locale(code)
        untranslated = all_strings - set(translations.keys())
        extra_keys = set(translations.keys()) - all_strings

        print(f"\n--- {code} ---")
        print(f"  Total keys: {len(translations)}")
        print(f"  Translatable strings match: {len(all_strings)}")

        found = sum(1 for s in all_strings if s in translations)
        print(f"  Translated: {found}/{len(all_strings)}")

        if untranslated:
            print(f"  Untranslated ({len(untranslated)}):")
            for s in sorted(untranslated):
                print(f"    - {s}")
        if extra_keys:
            print(f"  Extra keys not in code ({len(extra_keys)}):")
            for s in sorted(extra_keys):
                print(f"    - {s}")
        langs_found += 1

    if langs_found == 0:
        print("\nNo locale files found. Run this script after creating locale JSONs.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
