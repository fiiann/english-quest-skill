# 🎮 English Quest

> An MMORPG-style English learning system powered by AI. Practice sentences, earn XP, level up, fight weekly bosses, do grammar quizzes, and unlock achievements. CEFR A1–B1.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Features

- **🎙️ Voice Shadowing** — Practice speaking with real sentences, get instant feedback
- **⚔️ Error Monsters** — Each mistake is a "monster" you defeat
- **📊 XP & Leveling** — Progress from Level 1 to Level 20+
- **🏆 Weekly Boss Fights** — Take on challenging bosses every Sunday
- **📝 Grammar Quiz Mode** — Text-based grammar practice (no mic needed)
- **🛒 Shop System** — Buy titles and flairs with gold you earn
- **🔥 Daily Quests** — Keep your streak alive with daily goals
- **📜 11 Topics** — Greetings, Numbers, Time, Daily Routine, Food, Shopping, Directions, Work, Travel, Weather, Opinions

## 🚀 Quick Install

```bash
# One-line install (default profile)
bash -c "$(curl -sL https://raw.githubusercontent.com/fiiann/english-quest-skill/main/install.sh)"

# Or clone and install manually
git clone https://github.com/fiiann/english-quest-skill.git
cd english-quest-skill
bash install.sh
```

That's it! Restart your Hermes agent and say `shadowing` or `start rpg` to begin.

## 📋 Requirements

- **Hermes Agent** — This skill runs inside the [Hermes personal AI agent](https://github.com/your-hermes-repo)
- **Python 3.11+** — Built-in on most systems
- **Internet** — For voice transcription and TTS

## 🎯 How to Play

### Starting a Session
```
shadowing    # or "start rpg", "practice"
```

### Commands
| Command | Description |
|---------|-------------|
| `shadowing` / `start rpg` | Begin a practice session |
| `boss` | Start weekly boss fight |
| `stats` / `profile` | View your player card |
| `quests` / `daily` | See daily quest progress |
| `shop` | Browse reward shop |
| `quiz` | Start grammar quiz |
| `topic [name]` | Switch topic (e.g., `topic food`) |
| `stop` | End session |

## 🎮 Game Mechanics

### XP & Leveling
| Level | XP Required | Unlocks |
|-------|-------------|---------|
| 1 | 0 | Greetings, Numbers, Time |
| 2 | 100 | Daily Routine |
| 3 | 250 | Food |
| 4 | 500 | Shopping, Directions |
| 5 | 900 | Work (B1) |
| 6 | 1500 | Travel (B1) |
| 7 | 2500 | Weather (B1) |
| 8 | 4000 | Opinions (B1) |

### Error Monsters
| Monster | Error Type | Example |
|---------|-----------|---------|
| 👺 Article Goblin | a/the confusion | "I go to school" |
| 🐙 Plural Kraken | missing -s/-es | "I have three apple" |
| 👻 Phonetic Wraith | phonetic swap | "I wake op at six" |
| 🌫️ Vowel Specter | wrong vowel | "ten" → "tin" |
| ⏰ Tense Phantom | wrong verb tense | "I am go to school" |

### Boss Fights (Weekly)
- **The Article Archon** — 100 HP, requires 80%+ accuracy
- **The Plural Hydra** — 150 HP
- **The Phonetic Dragon** — 200 HP

Boss refreshes every **Sunday at midnight**.

## 🏠 For Developers

### Repository Structure
```
english-quest-skill/
├── SKILL.md          # Hermes skill definition
├── install.sh        # One-click installer
├── uninstall.sh      # Clean uninstaller
├── src/
│   ├── engine.py     # Core game logic
│   ├── session.py    # CLI session manager
│   ├── quiz_bank.json # Quiz question bank
│   └── config.py    # Path configuration
└── README.md
```

### Customizing the Sentence Bank
Edit `src/engine.py` and look for `SENTENCES` dict to add/modify sentences:
```python
SENTENCES = {
    "greetings": [
        ("Hello, my name is Maria.", "Halo, nama saya Maria."),
        ("Nice to meet you.", "Senang berkenalan denganmu."),
        # Add more...
    ],
}
```

### Adding Quiz Questions
Edit `src/quiz_bank.json` to add grammar quiz questions.

## 📄 License

MIT License — free to use, modify, and distribute.

## 🙏 Credits

Built with ❤️ for language learners everywhere.

---

**Made with Hermes Agent** — Your personal AI agent that runs skills like this one.
