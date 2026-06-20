#!/usr/bin/env python3
"""Reverseaffinity Photo - Image Editor"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reverseaffinity.photo import run_photo

if __name__ == "__main__":
    run_photo()
