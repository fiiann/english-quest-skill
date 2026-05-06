#!/usr/bin/env python3
"""
English Shadowing RPG — Configuration
Set paths via environment variables or use defaults.
"""

import os
from pathlib import Path

# Base Hermes profile directory
HERMES_BASE = Path(os.environ.get("HERMES_BASE", "/home/ubuntu/.hermes/profiles/elias-strategist"))

# Paths (relative to HERMES_BASE)
SKILLS_DIR = HERMES_BASE / "skills"
RPG_DIR = HERMES_BASE / "rpg"
STATE_FILE = RPG_DIR / "shadowing_rpg.json"

# Skill name (for installation)
SKILL_NAME = "english-quest"

# Sentence bank is embedded in engine.py
# Quiz bank is loaded from quiz_bank.json in the same dir as engine.py
def get_quiz_bank_path():
    return Path(__file__).parent / "quiz_bank.json"
