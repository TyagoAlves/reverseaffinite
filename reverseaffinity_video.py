#!/usr/bin/env python3
"""Reverseaffinity Video - Video Editor"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reverseaffinity.video import run_video

if __name__ == "__main__":
    run_video()
