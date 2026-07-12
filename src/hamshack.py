#!/usr/bin/env python3

"""
Compatibility launcher for HamRadio-Pi Ultimate.

Existing users may continue running:

    python src/hamshack.py

The main application entry point is now src/app.py.
"""

from app import main


if __name__ == "__main__":
    main()
