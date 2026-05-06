---
name: english-quest
description: MMORPG-style English learning RPG with XP, leveling, daily quests, boss fights, grammar quizzes, achievements, and error monsters. CEFR A1-B1.
triggers:
  - shadowing
  - practice speaking
  - english practice
  - english lesson
  - rpg
  - play english
  - start shadowing
  - daily quest
  - boss fight
  - check my stats
  - my profile
  - achievements
  - quiz
  - grammar quiz
  - quiz mode
  - start quiz
---

# English Shadowing RPG — Skill

## Overview
An MMORPG-style English speaking practice system. Practice sentences, earn XP, level up, fight weekly bosses, and unlock achievements. Error types are "monsters" you defeat.

## Architecture
- **Persistence**: `~/.hermes/profiles/elias-strategist/rpg/shadowing_rpg.json`
- **Session type**: Interactive turn-based practice (not cron — runs in chat)
- **No failure punishment** — errors reduce XP but never remove the ability to practice

## Game State Schema

```json
{
  "player": {
    "name": "Fian",
    "level": 1,
    "xp": 0,
    "xp_for_current_level": 0,
    "hp": 100,
    "max_hp": 100,
    "stamina": 20,
    "max_stamina": 20,
    "gold": 0,
    "streak": 0,
    "last_practice_date": "2026-05-05",
    "total_sentences_practiced": 0,
    "total_words_practiced": 0,
    "total_errors": 0,
    "perfect_sessions": 0,
    "created_at": "2026-05-05"
  },
  "unlocked_skills": ["greetings", "numbers", "time", "daily_routine", "food", "shopping", "directions"],
  "skill_progress": {
    "greetings": { "attempted": 5, "mastered": 3, "perfect": 2 },
    "food": { "attempted": 2, "mastered": 1, "perfect": 0 }
  },
  "quests": {
    "daily": {
      "first_steps": false,
      "warm_up": 0,
      "practice_makes_perfect": 0,
      "streak_defender": false,
      "perfect_round": 0,
      "speed_demon": false,
      "last_reset": "2026-05-05"
    },
    "weekly_boss": {
      "defeated": false,
      "attempts": 0,
      "boss_name": "The Article Archon",
      "boss_hp": 100,
      "last_boss_date": "2026-05-05"
    }
  },
  "achievements": [],
  "defeated_monsters": {
    "article_goblin": 0,
    "plural_kraken": 0,
    "phonetic_wraith": 0,
    "vowel_specter": 0,
    "tense_phatom": 0
  },
  "inventory": {
    "titles": ["Beginner"],
    "flairs": []
  },
  "shop": {
    "purchased_titles": [],
    "purchased_flairs": []
  }
}
```

## Level Table

| Level | XP Required | Unlock |
|---|---|---|
| 1 | 0 | Greetings, Numbers, Time |
| 2 | 100 | Daily Routine |
| 3 | 250 | Food |
| 4 | 500 | Shopping, Directions |
| 5 | 900 | Work (B1) |
| 6 | 1500 | Travel (B1) |
| 7 | 2500 | Weather (B1) |
| 8 | 4000 | Opinions (B1) |
| 10 | 7000 | Intermediate Badge |
| 15 | 15000 | Advanced Grammar |
| 20 | 30000 | Idioms |

XP to next level = `level * 100` (exponential)

**Level Down:** If XP drops below current level's threshold AND level > 1, drop one level. No XP floor below 0.

## Error Monsters (Error Types → Monsters)

| Monster | Error Type | Example | XP Reward |
|---|---|---|---|
| 👺 Article Goblin | a/the confusion | "I go to school" (missing "the") | +5 XP |
| 🐙 Plural Krakens | missing -s/-es | "I have three apple" | +5 XP |
| 👻 Phonetic Wraith | phonetic swap | "I wake op at six" | +8 XP |
| 🌫️ Vowel Specter | wrong vowel sound | "ten" → "tin" | +8 XP |
| ⏰ Tense Phantom | wrong verb tense | "I am go to school" | +10 XP |
| 🔥 Wildcard Imp | wrong word entirely | "I am from Jakarta" → "I am in Jakarta" | +10 XP |

**Boss monsters (weekly):**
- "The Article Archon" — 100 HP, requires 80%+ accuracy to defeat
- "The Plural Hydra" — 150 HP
- "The Phonetic Dragon" — 200 HP

## Daily Quests

| Quest | XP | Condition |
|---|---|---|
| 🐣 First Steps | 50 | Complete 1 sentence |
| 🔥 Warm Up | 100 | Complete 5 sentences |
| ⚔️ Practice Makes Perfect | 200 | Complete 10 sentences |
| 🛡️ Streak Defender | 300 | Practice on a streak day |
| ✨ Perfect Round | 150 | Get 5⭐ in a row |
| ⚡ Speed Demon | 100 | 10 sentences in <5 minutes |
| 🎯 No Mistakes | 250 | 20 sentences, 0 errors |

Quests reset at midnight local time each day.

## XP Awards Per Action

| Action | XP |
|---|---|
| Perfect sentence (⭐⭐⭐) | +20 XP |
| Good sentence (1 error, ⭐⭐) | +10 XP |
| Try again (2 errors, ⭐) | +5 XP |
| Defeat a monster (per error type) | +5–10 XP |
| Complete daily quest | +50–300 XP |
| Boss defeated (weekly) | +500 XP |
| Gold earned (sentences only) | +2 per sentence |

## Boss Fight (Weekly)

- Trigger: "boss fight" or "weekly boss" or "boss"
- 10 sentences in sequence, 90s each
- Boss HP starts at 100
- Each sentence: boss loses HP equal to accuracy% (100% = -100 HP)
- Win condition: boss HP reaches 0 (≥80% overall accuracy)
- If HP > 0 after 10 sentences → boss escapes, but you still get XP
- **Non-stressful framing:** Even if you "lose", you still earn XP and get encouragement
- Boss refreshes every Sunday midnight

## Quiz Mode (Grammar Practice — Text Only)

Quiz Mode is a **text-only grammar practice** system. No voice recording needed — perfect for quiet environments or midnight practice. Tests your knowledge of articles, plurals, verb tenses, prepositions, and sentence structure.

### How Quiz Works
- Type `quiz` to get a random grammar question
- Type `quiz [topic]` for a specific topic (e.g., `quiz greetings`)
- Answer by **letter** (A, B, C, D) or **type the full answer text**
- Costs **1⚡** per question
- **+10–15 XP** and **+2🪙** per correct answer
- **Streak bonus:** Every 5 correct in a row → **+50 XP bonus**
- Wrong answer: No XP loss, streak resets

### Quiz Topics Available
| Topic | CEFR | Grammar Focus |
|---|---|---|
| greetings | A1 | articles, subject pronouns, questions |
| numbers | A1 | plurals, there is/are, quantities |
| time | A1 | prepositions (at/on/in), ordinals |
| daily_routine | A1–A2 | phrasal verbs, frequency, word order |
| food | A1–A2 | some/any, uncountable nouns, adjectives |
| shopping | A1 | this/that, how much, can/could |
| directions | A1 | imperatives, prepositions of place |
| work | B1 | verb tenses, job vocabulary |
| travel | B1 | future tense (going to), transport |
| weather | B1 | predictions, present continuous |
| opinions | B1 | sequencers, because/so, opinion verbs |

### Question Types
| Type | Example | How to Answer |
|---|---|---|
| `fill_blank` | `___ name is Maria.` | Type the missing word |
| `multiple_choice` | `Where ___ you from?` | A, B, C, or D |
| `correct_sentence` | `Find the error` | Pick ✓ Correct or the error |
| `word_order` | `Arrange: name / my / Maria / is` | Type the correct sentence |

### Quiz Boss Fight
- Type `quiz boss` or `quiz boss [topic]`
- **10 questions** in sequence, costs **5⚡**
- Boss HP starts at **100**
- Each correct answer deals **10 HP damage**
- Win: reduce boss HP to 0 (≥80% accuracy)
- **Boss rewards:** +300 XP + 50🪙
- Even if boss escapes → you still earn XP!

### Quiz Boss Types
| Boss | HP | Theme |
|---|---|---|
| The Article Archon | 100 | Articles & pronouns |
| The Plural Hydra | 100 | Plurals & quantities |
| The Phonetic Dragon | 100 | Word sounds & spelling |
| The Tense Specter | 100 | Verb tenses |
| The Vocab Vampire | 100 | Word choice & meaning |

### Quiz Commands
- `quiz` / `quiz [topic]` — Start a quick quiz
- `quiz boss` / `quiz boss [topic]` — Start quiz boss fight
- `quiz stats` — Show quiz-specific stats

### Quiz Achievements
| Badge | How to Earn |
|---|---|
| 📝 Quiz Rookie | Complete 10 quiz questions |
| 🧠 Grammar Apprentice | 50 quiz questions, 80%+ accuracy |
| 🎯 Perfect 10 | 10 quiz answers in a row correct |
| 🏆 Quiz Boss Slayer | Defeat a quiz boss |

## Session Flow

```
1. User says "shadowing" / "start rpg" / "practice"
2. Load player state from JSON
3. Check: is stamina > 0? Is it a new day (reset quests/stamina)?
4. Show: Player card (level, XP, streak, HP, stamina)
5. Show: Daily quests progress
6. Pick sentence from unlocked skills (or let user choose topic)
7. Play TTS + show text
8. Wait for voice note
9. Transcribe + compare + identify monster
10. Award XP + gold + defeat monster
11. Check daily quest progress
12. Check level up
13. Repeat or end session
```

## Commands During RPG

- `shadowing` / `start` / `practice` — begin a session
- `boss` / `boss fight` — start weekly boss fight
- `stats` / `profile` / `me` — show player card
- `quests` / `daily` — show quest progress
- `achievements` / `badges` — show earned achievements
- `shop` — browse rewards
- `buy [item]` — purchase a shop item
- `topic [name]` — switch sentence topic
- `stop` / `quit` — end session (stamina resets next day anyway)
- `reset` — manually reset daily quests (admin/debug)

## Feedback Format

```
⚔️ Shadowing Quest!
━━━━━━━━━━━━━━━━━━
🎮 ShadowPlayer | Lvl 3
⭐ 450/500 XP    🔥 Streak: 5
❤️ 100/100      ⚡ 18/20 Stamina
🗡️ Gold: 85

📋 Topic: Greetings
━━━━━━━━━━━━━━━━━━
🗣️ "Nice to meet you."
   (Senang berkenalan)

🎤 Your turn! Send a voice note.

──────────────────────────────
After attempt:
⚔️ Combat Result!
━━━━━━━━━━━━━━━━━━
🗣️ Target:  "Nice to meet you."
👤 You said: "Nice to meet you."
✅ Words correct: 3/3 (100%)
⚔️ No monsters defeated this round!

💥 PERFECT ROUND! ✨
+20 XP | +2 Gold
```

## Sentence Bank — Organized by Skill Tree

### A1 — Beginner (Unlocked at Start)
**Greetings & Introductions:**
- "Hello, my name is Maria."
- "Nice to meet you."
- "How are you today?"
- "I am from Indonesia."
- "I live in Jakarta."
- "I am a student."
- "I am twenty years old."
- "What is your name?"
- "Where are you from?"
- "I am pleased to meet you."

**Numbers:**
- "There are five apples."
- "It costs ten dollars."
- "I have twenty books."
- "The price is fifteen euros."
- "Three plus four equals seven."

**Time:**
- "It is eight o'clock."
- "The meeting starts at nine."
- "Today is Monday, June second."
- "I wake up at six thirty."
- "Lunch is at twelve fifteen."

### A2 — Elementary (Unlocked at Level 2)
**Daily Routine:**
- "I wake up at six o'clock every morning."
- "I eat breakfast before school."
- "I go to school by bus."
- "I finish school at three p.m."
- "I usually have dinner at seven."
- "I brush my teeth twice a day."
- "I sleep at ten o'clock every night."
- "What time do you usually wake up?"

**Food & Drinks:**
- "I like rice and chicken for lunch."
- "I drink water every day."
- "Do you want some tea or coffee?"
- "This food is very delicious."
- "I am hungry. Let's eat something."
- "My favorite fruit is mango."
- "I never drink soda."

**Shopping:**
- "How much is this shirt?"
- "I would like to buy this dress."
- "Do you have a smaller size?"
- "Can I pay by card?"
- "Where is the fitting room?"
- "Is there a sale today?"

**Directions:**
- "Excuse me, where is the bathroom?"
- "Turn left at the corner."
- "Go straight for two blocks."
- "The bank is next to the supermarket."
- "Is it far from here?"
- "Can you show me on the map?"

### B1 — Intermediate (Unlocked at Level 5)
**Work:**
- "I work as a software engineer."
- "I have a meeting at ten a.m."
- "I send emails to my clients."
- "I am responsible for sales."
- "What do you do for a living?"

**Travel:**
- "I am traveling to Tokyo next month."
- "I booked a hotel near the airport."
- "Do I need a visa for that country?"
- "My flight departs at six in the morning."
- "I prefer to travel by train."

**Weather:**
- "What is the weather like today?"
- "It is sunny and warm today."
- "I think it will rain tomorrow."
- "The forecast says it will be cloudy."
- "I love the cool weather in the morning."

**Opinions:**
- "In my opinion, this is a good idea."
- "I agree with what you said."
- "I disagree because of several reasons."
- "What do you think about this?"
- "I believe learning English is important."

## Shop Items

| Item | Cost | Effect |
|---|---|---|
| Title: "Word Apprentice" | 50 Gold | Badge displayed on profile |
| Title: "Shadow Warrior" | 150 Gold | Badge displayed on profile |
| Title: "Word Sage" | 500 Gold | Badge displayed on profile |
| Flair: ⚔️ | 100 Gold | Equip on profile |
| Flair: 🔥 | 100 Gold | Equip on profile |
| Flair: 🐉 | 300 Gold | Equip on profile |
| Flair: 👑 | 1000 Gold | Equip on profile |
| Stamina Refill | 200 Gold | Restore 20 stamina immediately |

## Achievements

| Badge | How to Earn |
|---|---|
| 🐣 Day 1 | Complete first sentence |
| 🔥 7-Day Streak | Practice 7 days in a row |
| 🔥 30-Day Streak | Practice 30 days in a row |
| ⭐ Perfect 10 | 10 perfect sentences in one session |
| 📗 Grammar Grinder | 100 sentences completed |
| 🗣️ Shadow Master | 500 sentences, 90%+ accuracy |
| 👺 Monster Hunter | Defeat 50 monsters total |
| 🛡️ Streak Hero | Defend streak 7 times |
| 🎯 No Mistakes | Complete 20 sentences with zero errors |
| 👑 Level 10 | Reach level 10 |
| 👑 Level 20 | Reach level 20 |
| 🏆 Boss Slayer | Defeat a weekly boss |
| 💀 Streak Broken | Miss a day (honest badge) |
| ⚔️ First Boss | Attempt your first boss fight |

## Commands During RPG

All commands work in Telegram chat. State is persisted automatically.

### Starting
- `shadowing` / `start rpg` / `practice` → Start session, show card + pick sentence
- `boss` / `boss fight` → Start weekly boss fight (costs 5⚡)
- `stats` / `profile` / `me` → Show player card
- `quests` / `daily` → Show quest progress
- `shop` → Browse rewards
- `buy [item]` → Purchase item (e.g., `buy title_shadow_warrior`)
- `achievements` / `badges` → Show earned achievements
- `topic [name]` → Switch sentence topic (greetings, numbers, time, daily_routine, food, shopping, directions, work, travel, weather, opinions)
- `stop` / `quit` → End session

### Quiz Mode
- `quiz` → Start random grammar quiz
- `quiz [topic]` → Quiz on specific topic
- `quiz boss` → Start quiz boss fight (10 questions, 5⚡)
- `quiz boss [topic]` → Quiz boss on specific topic
- `quiz stats` → Show quiz stats

### During Session
After each voice note, the system automatically:
1. Transcribes your speech
2. Compares with target
3. Awards XP + Gold
4. Defeats error monsters
5. Updates daily quests
6. Checks level ups
7. Returns feedback

### Commands During Boss Fight
- `ready` → Begin boss fight sequence
- `hit [your transcript]` → Process boss hit (done automatically after voice note)
- `skip boss` → Exit boss fight

## Session Script Usage

The RPG engine is at: `~/.hermes/profiles/elias-strategist/rpg/session.py`

```
python3 session.py start              # Start session
python3 session.py card              # Show player card
python3 session.py quests             # Show daily quests
python3 session.py shop              # Browse shop
python3 session.py buy <item_key>    # Purchase item
python3 session.py boss_start         # Start boss fight
python3 session.py boss_hit <target> <spoken>  # Process boss hit
python3 session.py sentence <topic>   # Get random sentence
python3 session.py compare <target> <spoken> <topic>  # Process sentence
```

## Persistence

File: `~/.hermes/profiles/elias-strategist/rpg/shadowing_rpg.json`

All state changes are written immediately to disk after each action.

On load: read state, check for daily resets (if last_practice_date != today, reset stamina + daily quests + check streak).

## Dependencies

- `text_to_speech` — play sentences (TTS via edge provider)
- Voice note input (via Telegram) — user sends voice, agent transcribes and calls `session.py compare`
- Local JSON file read/write for persistence via `session.py`

## Setup Notes

- First launch: state initialized with defaults (name: Fian, level 1, 20 stamina)
- Name: pulled from user memory (Fian) — can be updated via config
- Timezone: from `config.yaml` or local system
- Daily reset: midnight local time
- Weekly boss reset: every Sunday midnight
