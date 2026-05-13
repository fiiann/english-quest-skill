---
name: english-shadowing-rpg
description: MMORPG-style English shadowing practice with XP, leveling, daily quests, boss fights, achievements, and error monsters. CEFR A1–C2 auto-progression every 3 levels. Also includes Quiz Mode (grammar) and Vocab Builder (flashcard vocabulary).
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
  - vocab
  - vocab builder
  - vocabulary
  - flashcard
  - word practice
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
  },
  "skill_components": {
    "shadowing":     { "xp": 0, "total_sentences": 0, "perfect_rounds": 0 },
    "quiz":          { "xp": 0, "total_score": 0, "count": 0, "questions_answered": 0 },
    "listening":     { "xp": 0, "total_score": 0, "count": 0 },
    "pronunciation": { "xp": 0, "total_score": 0, "count": 0 },
    "fluency":       { "xp": 0, "total_score": 0, "count": 0 },
    "vocab":         { "xp": 0, "total_score": 0, "count": 0 }
  }
}
```

> ⚠️ **Backward-compat note:** `skill_components` is auto-initialized on first access if missing from an older save file. Do NOT assume it exists — always use `.get("skill_components", {})` or the guard in `award_skill_xp`.

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

### CEFR Difficulty Bands (auto-progression every 3 levels)

| Levels | CEFR | Example |
|---|---|---|
| 1–3 | 🟢 A1 Beginner | "Hello." / "Where are you from?" |
| 4–6 | 🟡 A2 Elementary | "I have been living here for two years." |
| 7–9 | 🟠 B1 Intermediate | "I have never been to Japan before." |
| 10–12 | 🔴 B2 Upper-Intermediate | "I cannot imagine living without good public transport." |
| 13–15 | 🟣 C1 Advanced | "I must confess I have developed an inexplicable fondness..." |
| 16–18 | ⚫ C2 Proficient | "Were it not for his insatiable curiosity, the breakthrough..." |

Sentences are auto-selected to match your **Overall Level** (average of 6 skill components). ±1 band for variety. Each sentence in `SENTENCES` is a 3-tuple: `(sentence, meaning, cefr_level)`.

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

## Vocab Builder — Flashcard Word Mastery

Vocab Builder is a flashcard-based vocabulary learning system. Build your lexicon by reviewing words, tracking mastery levels, and battling the Lexicon Lich!

### Vocab Bank

**File**: `~/.hermes/profiles/elias-strategist/rpg/vocab_bank.json`

Each word card contains:
- `id`, `word`, `definition`, `indonesian`, `cefr`, `part_of_speech`, `example`, `phonetic`, `topic`

**11 topics**: greetings, numbers, time, daily_routine, food, shopping, directions, work, travel, weather, opinions (~100 words total)

### Mastery System

Words have mastery levels 0–3. Rating a card updates its level:

| Rating | Level 0 → | Level 1 → | Level 2 → |
|---|---|---|---|
| Again | 0 (no change) | 0 | 1 |
| Hard | 1 | 0 | 1 |
| Good | 1 | 2 | 2 |
| Easy | 2 | 3 (mastered!) | 3 (mastered!) |

| Mastery | Emoji | Meaning |
|---|---|---|
| 0 | 🆕 | New word |
| 1 | 🔄 | Learning |
| 2 | ✅ | Familiar |
| 3 | ⭐ | Mastered |

### XP Per Rating

| Rating | XP Gained |
|---|---|
| Again | 0 |
| Hard | 5 |
| Good | 10 |
| Easy | 15 |

**Session bonus**: +10 XP (≤4 Good/Easy) or +20 XP (>4 Good/Easy) at session end.

### Vocab Session Commands

- `vocab` / `vocab [topic]` — Start a 5-card session (costs 1⚡)
- `vocab_reveal` — Show the current card's definition
- `vocab_rate [again|hard|good|easy]` — Rate the current card
- `vocab_stats` — Show vocab stats
- `vocab_boss [topic]` — Start vocab boss fight (10 cards, 5⚡)
- `vocab_search <word>` — Search the vocab bank

### Vocab Boss Fight

- 10 vocabulary cards in sequence
- Costs **5⚡** to start
- Each Good/Easy answer deals HP damage to "The Lexicon Lich" (10–20 HP)
- Win: reduce boss HP to 0
- **Rewards**: +300 XP + 50🪙 + Vocab Boss Slayer badge
- Boss HP at end > 0 → still earns XP but no gold

### Vocab Achievements

| Badge | How to Earn |
|---|---|
| 📚 Word Rookie | Review 10 vocabulary cards |
| 📖 Lexicon Apprentice | 50 cards reviewed, 70%+ Good/Easy rate |
| 🗓️ Vocab Daily | Complete vocab sessions 7 days in a row |
| 🎯 Vocab Master | Master 20 words (reach level 3) |
| ⚔️ Vocab Boss Slayer | Defeat a vocab boss |
| 💎 Word Collector | Own 50+ words at level 2+ |

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

## Commands (CLI — session.py)

> ⚠️ The CLI dispatch does NOT have a `start` command. Do NOT use `session.py start`. Use `sentence` to get a sentence, then `compare` after practicing.

```
python3 session.py card              # Show player card (default if no args)
python3 session.py skills            # Show 6-skill breakdown + overall level
python3 session.py sentence          # Get a random greeting sentence
python3 session.py sentence <topic>  # Get sentence from specific topic
python3 session.py compare <target> <spoken> [<topic>]  # Score your attempt
python3 session.py quests            # Show daily quests
python3 session.py shop             # Browse shop
python3 session.py buy <item_key>    # Purchase item
python3 session.py boss_start       # Start boss fight
python3 session.py boss_hit <target> <spoken>  # Process boss hit
python3 session.py quiz              # Start random grammar quiz
python3 session.py quiz <topic>      # Quiz on specific topic
python3 session.py quiz_stats       # Show quiz stats
python3 session.py quiz_boss         # Start quiz boss
python3 session.py quiz_boss <topic> # Quiz boss on topic
```

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

> ⚠️ `session.py start` does NOT exist. The entry point is `sentence` (get a sentence) + `compare` (score it).

```
python3 session.py sentence           # Get greeting sentence
python3 session.py sentence <topic>    # Get sentence by topic
python3 session.py compare "text" "you said"  # Score your attempt
python3 session.py card               # Show player card + skill profile
python3 session.py skills             # Show 5 individual skill levels
```

## Persistence

File: `~/.hermes/profiles/elias-strategist/rpg/shadowing_rpg.json`

All state changes are written immediately to disk after each action.

On load: read state, check for daily resets (if last_practice_date != today, reset stamina + daily quests + check streak).

## Pitfalls

### Voice note transcription — Whisper is now available
Whisper is installed at `/tmp/wf`. Activate and use:
```bash
source /tmp/wf/bin/activate
python3 -c "import whisper; model = whisper.load_model('base'); result = model.transcribe('audio.ogg', language='en')"
```

**Voice-to-transcription workflow:**
1. Find the latest `.ogg` file in `/home/ubuntu/.hermes/profiles/elias-strategist/cache/audio/` (sorted by mtime)
2. Transcribe with `whisper.load_model('base', device='cpu')`
3. Pass the transcribed text to `session.py compare "<target>" "<spoken>" <topic>`

**Whisper limitations:**
- Even `base` model can mishear short phrases: "drink" → "dreamed", "soda" → "so that"
- Always frame Whisper output as "transcribed as" not "what was said"
- Transcription errors ≠ pronunciation errors; use `compare` function's own scoring as truth
- Works best with `.ogg` files from Telegram voice notes

### `session.py start` does not exist
The CLI dispatch has no `start` command. Always use `sentence` to get a sentence, then `compare` to score it.

### Old save files missing `skill_components`
Pre-existing save files (pre-May 2026 skill_components feature) will throw `KeyError` when `award_skill_xp` is called. The function has an auto-init guard internally, but when adding new code that reads `state["skill_components"]` directly, always use `.get("skill_components", {})` fallback.

### `questions_answered` KeyError on quiz answers
If `check_quiz_answer` fails with `KeyError: 'questions_answered'`, the `skill_components.quiz` dict is missing that key (old save or new field added after save was created). Fix: add `if "questions_answered" not in sc["quiz"]: sc["quiz"]["questions_answered"] = 0` before incrementing, and ensure the init schema includes `"questions_answered": 0`.

### `award_skill_xp` — always handle ALL skill IDs
When adding a new `skill_components` entry (e.g. `vocab`), `award_skill_xp()` MUST be updated with a corresponding `elif skill_id == "new_skill":` branch. If not, XP silently falls through and is lost with no error. Always check `get_overall_level()` and `get_skill_profile()` too — they have hardcoded skill lists that must stay in sync. As of May 2026, skills are: shadowing, quiz, listening, pronunciation, fluency, vocab (6 total).

### Whisper transcription accuracy
Whisper (even `base` model) can mishear short phrases, especially:
- Similar-sounding words: "drink" → "dreamed", "soda" → "so that"
- Fast speech or non-native accents
- Background noise or low audio quality
**Always frame Whisper results as "transcribed as" not "what was said"**, and treat transcription errors as audio quality issues, not pronunciation errors. The `compare` function's own scoring is the source of truth for accuracy.

## Dependencies

- `text_to_speech` — play sentences (TTS via edge provider)
- Voice note input (via Telegram) — user sends voice, agent transcribes and calls `session.py compare`
- Local JSON file read/write for persistence via `session.py`

## Azure AI Speech — Pronunciation Assessment (Optional Scoring Backend)

Azure Pronunciation Assessment provides phoneme-level scoring (accuracy, fluency, prosody) as an alternative or complement to local Whisper-based scoring. Particularly valuable for vocab-builder's pronunciation gate and the `pronunciation` skill component.

### Pricing
- **Free tier**: 5 audio hours/month
- **Standard (S0)**: ~$1.00–$1.50 per audio hour
- **Typical shadowing usage** (10–15 min/day ≈ 5–7.5 hrs/month): **free within tier**
- Billed per audio minute of input, not per API call

### API Overview
- **Endpoint**: `https://<region>.api.cognitive.microsoft.com/speech/pxy/pronunciation/assessment/v2`
- **Auth**: Subscription key or Azure AD token (key from `AZURE_SPEECH_KEY` env var)
- **Method**: POST with audio file + reference text + assessment params
- **Response**: JSON with per-word scores, overall score (0–100), accuracy, fluency, completeness

### Request Shape (form-data)
```
ReferenceText: "Nice to meet you."
GradingSystem: SixScale|FiveScale|HundredScale
Dimension: Basic|Comprehensive
Scenario: Pronunciationunciation|Read|Aligned|
Audio: <blob>
```

### Response Fields (relevant)
- `pronunciationScore` (0–100)
- `accuracyScore` — phoneme-level
- `fluencyScore` — speaking rate / pauses
- `completenessScore` — full utterance coverage
- `words[].errorType` — omitted/inserted/mispronounced

### When to Use Azure vs Whisper
| Use Case | Tool |
|---|---|
| Real-time feedback during session | Whisper (local, fast) |
| XP gate for pronunciation (vocab-builder) | Azure (structured score, gamifiable) |
| Per-phoneme error detail for feedback | Azure |
| Quick check if Whisper is uncertain | Azure |

### Env Var Needed
```
AZURE_SPEECH_KEY=<subscription-key>
AZURE_SPEECH_REGION=<region, e.g. southeastasia>
```
Region must match where the resource is deployed (e.g. `southeastasia`, `eastus`, `westus2`).

### Quick Test
```bash
curl -X POST "https://<region>.api.cognitive.microsoft.com/speech/pxy/pronunciation/assessment/v2" \
  -H "Ocp-Apim-Subscription-Key: $AZURE_SPEECH_KEY" \
  -F "Audio=@audio.ogg" \
  -F "ReferenceText=Nice to meet you" \
  -F "GradingSystem=FiveScale" \
  -F "Dimension=Basic" \
  -F "Scenario=Pronunciation"
```

## Sending Telegram Messages via Bot API (curl)

When Hermes gateway is **not** running (script/cron context), send Telegram messages directly via the Bot API — **not** through the gateway.

```bash
# Credentials are in the profile's .env, NOT config.yaml
source ~/.hermes/profiles/elias-strategist/.env

curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d "chat_id=${TELEGRAM_HOME_CHANNEL}" \
  -d "text=<message>" \
  -d "parse_mode=HTML"
```

- `TELEGRAM_BOT_TOKEN` — bot token (e.g. `bot876069...Nm_Q`)
- `TELEGRAM_HOME_CHANNEL` — Fian's user ID (`7978577957`)
- Both vars live in `~/.hermes/profiles/elias-strategist/.env`

> 📁 **Escalator reference**: See `references/escalator-reminder.md` for the `reminder_escalator.py` script, Telegram curl delivery pattern, and credential locations.

## Cron Job Pitfall — Empty Model Env Var

**Symptom**: Cron job fails with `unknown model '' (2013)` — empty model name passed to API.

**Cause**: The `model` environment variable is set to empty string in the shell environment. Cron jobs inherit it and pass an empty model name.

**Fix**: Always explicitly set `model` and `provider` on every cron job at creation time:
```
model: MiniMax-Text-01
provider: minimax
```
Never rely on inherited env vars for model selection in scheduled jobs.



## Setup Notes

- First launch: state initialized with defaults (name: Fian, level 1, 20 stamina)
- Name: pulled from user memory (Fian) — can be updated via config
- Timezone: from `config.yaml` or local system
- Daily reset: midnight local time
- Weekly boss reset: every Sunday midnight
