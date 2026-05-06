#!/usr/bin/env python3
"""
English Shadowing RPG — Core Game Engine
Handles: state persistence, XP/leveling, sentence comparison,
monster detection, quest tracking, boss fights, shop, achievements.
"""

import json
import os
import re
import sys
import random
from datetime import datetime, date
from pathlib import Path
from typing import Optional

STATE_FILE = Path("/home/ubuntu/.hermes/profiles/elias-strategist/rpg/shadowing_rpg.json")

# ──────────────────────────────────────────────
#  SENTENCE BANK
# ──────────────────────────────────────────────
SENTENCES = {
    "greetings": [
        ("Hello, my name is Maria.", "Halo, nama saya Maria."),
        ("Nice to meet you.", "Senang berkenalan denganmu."),
        ("How are you today?", "Apa kabar hari ini?"),
        ("I am from Indonesia.", "Saya dari Indonesia."),
        ("I live in Jakarta.", "Saya tinggal di Jakarta."),
        ("I am a student.", "Saya seorang pelajar."),
        ("I am twenty years old.", "Saya berumur dua puluh tahun."),
        ("What is your name?", "Siapa namamu?"),
        ("Where are you from?", "Kamu dari mana?"),
        ("I am pleased to meet you.", "Senang bertemu denganmu."),
    ],
    "numbers": [
        ("There are five apples.", "Ada lima apel."),
        ("It costs ten dollars.", "Harganya sepuluh dolar."),
        ("I have twenty books.", "Saya punya dua puluh buku."),
        ("The price is fifteen euros.", "Harganya lima belas euro."),
        ("Three plus four equals seven.", "Tiga ditambah empat sama dengan tujuh."),
    ],
    "time": [
        ("It is eight o'clock.", "Jam delapan."),
        ("The meeting starts at nine.", "Rapat dimulai jam sembilan."),
        ("Today is Monday, June second.", "Hari ini Senin, tanggal dua Juni."),
        ("I wake up at six thirty.", "Saya bangun jam setengah tujuh."),
        ("Lunch is at twelve fifteen.", "Makan siang jam dua belas limabelas."),
    ],
    "daily_routine": [
        ("I wake up at six o'clock every morning.", "Saya bangun jam enam setiap pagi."),
        ("I eat breakfast before school.", "Saya sarapan sebelum sekolah."),
        ("I go to school by bus.", "Saya pergi ke sekolah naik bus."),
        ("I finish school at three p.m.", "Saya selesai sekolah jam tiga sore."),
        ("I usually have dinner at seven.", "Saya biasanya makan malam jam tujuh."),
        ("I brush my teeth twice a day.", "Saya menyikat gigi dua kali sehari."),
        ("I sleep at ten o'clock every night.", "Saya tidur jam sepuluh setiap malam."),
        ("What time do you usually wake up?", "Jam berapa kamu biasanya bangun?"),
    ],
    "food": [
        ("I like rice and chicken for lunch.", "Saya suka nasi dan ayam untuk makan siang."),
        ("I drink water every day.", "Saya minum air setiap hari."),
        ("Do you want some tea or coffee?", "Kamu mau teh atau kopi?"),
        ("This food is very delicious.", "Makanan ini sangat enak."),
        ("I am hungry. Let's eat something.", "Saya lapar. Mari makan sesuatu."),
        ("My favorite fruit is mango.", "Buah favorit saya mangga."),
        ("I never drink soda.", "Saya tidak pernah minum soda."),
    ],
    "shopping": [
        ("How much is this shirt?", "Berapa harga kaos ini?"),
        ("I would like to buy this dress.", "Saya ingin membeli gaun ini."),
        ("Do you have a smaller size?", "Apakah ada ukuran yang lebih kecil?"),
        ("Can I pay by card?", "Boleh bayar dengan kartu?"),
        ("Where is the fitting room?", "Di mana ruang pas?"),
        ("Is there a sale today?", "Ada diskon hari ini?"),
    ],
    "directions": [
        ("Excuse me, where is the bathroom?", "Permisi, di mana kamar mandi?"),
        ("Turn left at the corner.", "Belok kiri di pojok."),
        ("Go straight for two blocks.", "Jalan lurus dua blok."),
        ("The bank is next to the supermarket.", "Bank di samping supermarket."),
        ("Is it far from here?", "Jauh dari sini?"),
        ("Can you show me on the map?", "Bisa tunjukkan di peta?"),
    ],
    "work": [
        ("I work as a software engineer.", "Saya bekerja sebagai insinyur perangkat lunak."),
        ("I have a meeting at ten a.m.", "Saya ada rapat jam sepuluh pagi."),
        ("I send emails to my clients.", "Saya mengirim email ke klien saya."),
        ("I am responsible for sales.", "Saya bertanggung jawab atas penjualan."),
        ("What do you do for a living?", "Apa pekerjaanmu?"),
    ],
    "travel": [
        ("I am traveling to Tokyo next month.", "Saya akan bepergian ke Tokyo bulan depan."),
        ("I booked a hotel near the airport.", "Saya sudah pesan hotel dekat bandara."),
        ("Do I need a visa for that country?", "Apakah saya butuh visa untuk negara itu?"),
        ("My flight departs at six in the morning.", "Penerbanganku berangkat jam enam pagi."),
        ("I prefer to travel by train.", "Saya lebih suka bepergian dengan kereta."),
    ],
    "weather": [
        ("What is the weather like today?", "Bagaimana cuaca hari ini?"),
        ("It is sunny and warm today.", "Hari ini cerah dan hangat."),
        ("I think it will rain tomorrow.", "Saya pikir besok akan hujan."),
        ("The forecast says it will be cloudy.", "Prakiraan cuaca bilang akan berawan."),
        ("I love the cool weather in the morning.", "Saya suka cuaca sejuk di pagi hari."),
    ],
    "opinions": [
        ("In my opinion, this is a good idea.", "Menurut saya, ini ide yang bagus."),
        ("I agree with what you said.", "Saya setuju dengan yang kamu bilang."),
        ("I disagree because of several reasons.", "Saya tidak setuju karena beberapa alasan."),
        ("What do you think about this?", "Apa pendapatmu tentang ini?"),
        ("I believe learning English is important.", "Saya percaya belajar bahasa Inggris penting."),
    ],
}

UNLOCK_REQUIREMENTS = {
    "greetings": (1, 0),
    "numbers": (1, 0),
    "time": (1, 0),
    "daily_routine": (2, 100),
    "food": (3, 250),
    "shopping": (4, 500),
    "directions": (4, 500),
    "work": (5, 900),
    "travel": (6, 1500),
    "weather": (7, 2500),
    "opinions": (8, 4000),
}

LEVEL_XP = [0, 100, 250, 500, 900, 1500, 2500, 4000, 7000, 12000, 20000, 35000, 60000]

BOSSES = [
    ("The Article Archon", 100),
    ("The Plural Hydra", 150),
    ("The Phonetic Dragon", 200),
    ("The Tense Specter", 250),
]

MONSTER_MAP = {
    "article_goblin": ("Article Goblin", "a/the word confusion"),
    "plural_kraken": ("Plural Krakens", "missing -s/-es"),
    "phonetic_wraith": ("Phonetic Wraith", "phonetic word swap"),
    "vowel_specter": ("Vowel Specter", "wrong vowel sound"),
    "tense_phantom": ("Tense Phantom", "wrong verb tense"),
    "wildcard_imp": ("Wildcard Imp", "completely wrong word"),
}

SHOP_ITEMS = {
    "title_word_apprentice": {"type": "title", "name": "Word Apprentice", "cost": 50},
    "title_shadow_warrior": {"type": "title", "name": "Shadow Warrior", "cost": 150},
    "title_word_sage": {"type": "title", "name": "Word Sage", "cost": 500},
    "title_grammar_knight": {"type": "title", "name": "Grammar Knight", "cost": 1000},
    "flair_sword": {"type": "flair", "name": "⚔️", "cost": 100},
    "flair_fire": {"type": "flair", "name": "🔥", "cost": 100},
    "flair_dragon": {"type": "flair", "name": "🐉", "cost": 300},
    "flair_crown": {"type": "flair", "name": "👑", "cost": 1000},
    "stamina_refill": {"type": "refill", "name": "Stamina Refill (+20⚡)", "cost": 200},
}

ACHIEVEMENTS = {
    "day_1": {"name": "Day 1", "desc": "Complete first sentence", "id": "day_1"},
    "streak_7": {"name": "7-Day Streak", "desc": "Practice 7 days in a row", "id": "streak_7"},
    "streak_30": {"name": "30-Day Streak", "desc": "Practice 30 days in a row", "id": "streak_30"},
    "perfect_10": {"name": "Perfect 10", "desc": "10 perfect sentences in one session", "id": "perfect_10"},
    "grammar_grinder": {"name": "Grammar Grinder", "desc": "100 sentences completed", "id": "grammar_grinder"},
    "shadow_master": {"name": "Shadow Master", "desc": "500 sentences, 90%+ accuracy", "id": "shadow_master"},
    "monster_hunter": {"name": "Monster Hunter", "desc": "Defeat 50 monsters total", "id": "monster_hunter"},
    "streak_hero": {"name": "Streak Hero", "desc": "Defend streak 7 times", "id": "streak_hero"},
    "no_mistakes": {"name": "No Mistakes", "desc": "Complete 20 sentences with zero errors", "id": "no_mistakes"},
    "level_10": {"name": "Level 10", "desc": "Reach level 10", "id": "level_10"},
    "level_20": {"name": "Level 20", "desc": "Reach level 20", "id": "level_20"},
    "boss_slayer": {"name": "Boss Slayer", "desc": "Defeat a weekly boss", "id": "boss_slayer"},
    "first_boss": {"name": "First Boss", "desc": "Attempt your first boss fight", "id": "first_boss"},
    "streak_broken": {"name": "Honest Effort", "desc": "Miss a day — but you came back!", "id": "streak_broken"},
    # Quiz achievements
    "quiz_rookie": {"name": "Quiz Rookie", "desc": "Complete 10 quiz questions", "id": "quiz_rookie"},
    "grammar_apprentice": {"name": "Grammar Apprentice", "desc": "50 quiz questions, 80%+ accuracy", "id": "grammar_apprentice"},
    "quiz_perfect_10": {"name": "Perfect 10", "desc": "10 quiz answers in a row correct", "id": "quiz_perfect_10"},
    "quiz_boss_slayer": {"name": "Quiz Boss Slayer", "desc": "Defeat a quiz boss", "id": "quiz_boss_slayer"},
}

# ──────────────────────────────────────────────
#  SKILL COMPONENTS
# ──────────────────────────────────────────────

# Skill component IDs
SKILL_COMPONENTS = {
    "shadowing":       {"name": "Shadowing",       "icon": "🗣️",  "desc": "Voice shadowing practice"},
    "quiz":            {"name": "Quiz",            "icon": "📝",  "desc": "Grammar quiz mastery"},
    "listening":       {"name": "Listening",       "icon": "🎧",  "desc": "Comprehension skill"},
    "pronunciation":   {"name": "Pronunciation",   "icon": "🗽",  "desc": "Sound accuracy"},
    "fluency":         {"name": "Fluency",         "icon": "⚡",  "desc": "Speed & smoothness"},
}

# XP thresholds per skill level (1-10)
# Level 1 = 0 XP, Level 10 = 5000 XP (exponential)
SKILL_LEVEL_XP = [0, 50, 120, 220, 350, 520, 750, 1050, 1450, 2000, 5000]

def skill_level_from_xp(xp: int) -> int:
    """Convert XP to skill level (1-10)."""
    level = 1
    for i, threshold in enumerate(SKILL_LEVEL_XP):
        if xp >= threshold:
            level = i + 1
    return min(level, 10)

def skill_xp_to_next(xp: int) -> tuple[int, int]:
    """Returns (current_level, xp_in_current_level, xp_for_next_level)."""
    level = skill_level_from_xp(xp)
    current_threshold = SKILL_LEVEL_XP[level - 1] if level > 1 else 0
    next_threshold = SKILL_LEVEL_XP[min(level, len(SKILL_LEVEL_XP) - 1)]
    xp_in_level = xp - current_threshold
    xp_for_next = next_threshold - current_threshold
    return level, xp_in_level, xp_for_next

# XP awards per activity
SKILL_XP_AWARD = {
    "shadowing":     {"perfect": 15, "good": 8, "try_again": 3},   # per sentence
    "quiz":          {"correct": 10, "streak_bonus": 5},             # per question
    "listening":     {"weight": 0.30},  # weight in overall shadowing score
    "pronunciation":  {"weight": 0.40},  # weight in overall shadowing score
    "fluency":       {"weight": 0.30},  # weight in overall shadowing score
}

# ──────────────────────────────────────────────
#  SKILL COMPONENT CALCULATIONS
# ──────────────────────────────────────────────

def calculate_shadowing_scores(target: str, spoken: str) -> dict:
    """
    Calculate listening, pronunciation, and fluency scores from shadowing attempt.
    Returns dict with 0-100 scores for each component.
    """
    target_words = get_words(target)
    spoken_words = get_words(spoken)

    # ── LISTENING SCORE ──
    # How well did user understand? Measured by word match accuracy.
    # Also penalize extra/missing words (misunderstanding).
    if len(target_words) == 0:
        listening = 100
    else:
        correct = sum(1 for w in spoken_words if w in target_words)
        # Penalize if user added or skipped words
        missed = len(target_words) - sum(1 for w in target_words if w in spoken_words)
        extra = max(0, len(spoken_words) - correct)
        listening = max(0, (correct / len(target_words)) * 100) - (missed * 5) - (extra * 3)
        listening = max(0, min(100, listening))

    # ── PRONUNCIATION SCORE ──
    # Word-level accuracy (ignores word order, just match/mismatch).
    if len(target_words) == 0:
        pronunciation = 100
    else:
        correct = sum(1 for w in spoken_words if w in target_words)
        wrong_word = len(spoken_words) - correct
        # Also penalize missing words as pronunciation issue
        missing = len(target_words) - correct
        pronunciation = max(0, (correct / len(target_words)) * 100)
        pronunciation = max(0, min(100, pronunciation))

    # ── FLUENCY SCORE ──
    # Based on accuracy (close enough = more fluent attempt).
    # Also give small boost for longer spoken attempts.
    if len(spoken_words) == 0:
        fluency = 0
    else:
        # Base on overall accuracy
        base_fluency = (len([w for w in spoken_words if w in target_words]) /
                        max(len(target_words), len(spoken_words))) * 100
        # Length bonus (longer, correct sentences = more fluent)
        length_ratio = min(len(spoken_words) / max(len(target_words), 1), 1.5)
        fluency = min(100, base_fluency * length_ratio)

    return {
        "listening": round(listening, 1),
        "pronunciation": round(pronunciation, 1),
        "fluency": round(fluency, 1),
    }


def award_skill_xp(state: dict, skill_id: str, base_xp: int,
                   listening: float = None, pronunciation: float = None,
                   fluency: float = None) -> dict:
    """
    Award XP to a skill component and update its tracking stats.
    For shadowing: also update listening/pronunciation/fluency sub-scores.
    Returns dict of XP awarded per skill.
    """
    sc = state["skill_components"]

    xp_awarded = {}

    if skill_id == "shadowing":
        sc["shadowing"]["total_sentences"] += 1
        if base_xp >= 15:  # perfect
            sc["shadowing"]["perfect_rounds"] += 1
        xp = base_xp
        sc["shadowing"]["xp"] += xp
        xp_awarded["shadowing"] = xp

        # Sub-scores from shadowing
        if listening is not None:
            sc["listening"]["total_score"] += listening
            sc["listening"]["count"] += 1
            listening_xp = int(listening * 0.10)  # 10% of score as XP
            sc["listening"]["xp"] += listening_xp
            xp_awarded["listening"] = listening_xp

        if pronunciation is not None:
            sc["pronunciation"]["total_score"] += pronunciation
            sc["pronunciation"]["count"] += 1
            pronunciation_xp = int(pronunciation * 0.10)
            sc["pronunciation"]["xp"] += pronunciation_xp
            xp_awarded["pronunciation"] = pronunciation_xp

        if fluency is not None:
            sc["fluency"]["total_score"] += fluency
            sc["fluency"]["count"] += 1
            fluency_xp = int(fluency * 0.10)
            sc["fluency"]["xp"] += fluency_xp
            xp_awarded["fluency"] = fluency_xp

    elif skill_id == "quiz":
        sc["quiz"]["questions_answered"] += 1
        xp = base_xp
        sc["quiz"]["xp"] += xp
        xp_awarded["quiz"] = xp

    return xp_awarded


def get_skill_level(state: dict, skill_id: str) -> int:
    """Get current level (1-10) for a skill component."""
    xp = state.get("skill_components", {}).get(skill_id, {}).get("xp", 0)
    return skill_level_from_xp(xp)


def get_overall_level(state: dict) -> float:
    """Get overall level as average of all 5 skill levels (can be fractional)."""
    skills = ["shadowing", "quiz", "listening", "pronunciation", "fluency"]
    levels = [get_skill_level(state, s) for s in skills]
    return sum(levels) / len(levels)


def get_skill_profile(state: dict) -> dict:
    """Return full skill profile for display."""
    skills = ["shadowing", "quiz", "listening", "pronunciation", "fluency"]
    profile = {}
    for sid in skills:
        sc = state.get("skill_components", {}).get(sid, {"xp": 0, "total_score": 0, "count": 0})
        level, xp_in, xp_next = skill_xp_to_next(sc.get("xp", 0))
        avg_score = (sc.get("total_score", 0) / max(sc.get("count", 1), 1)
                     if sc.get("count", 0) > 0 else 0)
        profile[sid] = {
            "level": level,
            "xp": sc.get("xp", 0),
            "xp_in_level": xp_in,
            "xp_for_next": xp_next,
            "avg_score": round(avg_score, 1),
            "total_count": sc.get("count", 0),
        }
    profile["_overall"] = round(get_overall_level(state), 1)
    return profile


# ──────────────────────────────────────────────
#  QUIZ BANK
# ──────────────────────────────────────────────

QUIZ_BANK_FILE = Path("/home/ubuntu/.hermes/profiles/elias-strategist/rpg/quiz_bank.json")

def load_quiz_bank() -> dict:
    if QUIZ_BANK_FILE.exists():
        with open(QUIZ_BANK_FILE) as f:
            return json.load(f)
    return {}

QUIZ_BANK = load_quiz_bank()


# ──────────────────────────────────────────────
#  STATE MANAGEMENT
# ──────────────────────────────────────────────

def load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return None


def save_state(state: dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def init_state(name: str = "Fian") -> dict:
    state = load_state()
    if state is None:
        today = date.today().isoformat()
        state = {
            "player": {
                "name": name,
                "level": 1,
                "xp": 0,
                "hp": 100,
                "max_hp": 100,
                "stamina": 20,
                "max_stamina": 20,
                "gold": 0,
                "streak": 0,
                "last_practice_date": None,
                "total_sentences_practiced": 0,
                "total_words_practiced": 0,
                "total_errors": 0,
                "perfect_sessions": 0,
                "created_at": today,
            },
            "unlocked_skills": ["greetings", "numbers", "time"],
            "skill_progress": {k: {"attempted": 0, "mastered": 0, "perfect": 0}
                               for k in SENTENCES.keys()},
            "quests": {
                "daily": {
                    "first_steps": False,
                    "warm_up": 0,
                    "practice_makes_perfect": 0,
                    "streak_defender": False,
                    "perfect_round": 0,
                    "speed_demon": False,
                    "last_reset": today,
                },
                "weekly_boss": {
                    "defeated": False,
                    "attempts": 0,
                    "boss_name": "The Article Archon",
                    "boss_max_hp": 100,
                    "boss_hp": 100,
                    "last_boss_date": None,
                },
            },
            "achievements": [],
            "defeated_monsters": {k: 0 for k in
                                  ["article_goblin", "plural_kraken", "phonetic_wraith",
                                   "vowel_specter", "tense_phantom", "wildcard_imp"]},
            "inventory": {"titles": ["Beginner"], "flairs": []},
            "shop": {
                "purchased_titles": [],
                "purchased_flairs": [],
                "equipped_title": None,
                "equipped_flair": None,
            },
            "quiz_state": {
                "questions_answered": 0,
                "correct_answers": 0,
                "quiz_bosses_defeated": 0,
                "quiz_boss_attempts": 0,
                "quiz_streak": 0,
                "last_quiz_date": None,
                "quiz_questions_seen": [],
                "active_quiz_boss": None,
            },
            "skill_components": {
                "shadowing":     {"xp": 0, "total_sentences": 0, "perfect_rounds": 0},
                "quiz":          {"xp": 0, "questions_answered": 0, "correct_answers": 0, "perfect_streaks": 0},
                "listening":     {"xp": 0, "total_score": 0, "count": 0},
                "pronunciation": {"xp": 0, "total_score": 0, "count": 0},
                "fluency":       {"xp": 0, "total_score": 0, "count": 0},
            },
        }
        save_state(state)
    return state


def check_daily_reset(state: dict) -> dict:
    today = date.today().isoformat()
    last = state["player"]["last_practice_date"]

    # Ensure quiz_state exists (for saves made before quiz was added)
    if "quiz_state" not in state:
        state["quiz_state"] = {
            "questions_answered": 0,
            "correct_answers": 0,
            "quiz_bosses_defeated": 0,
            "quiz_boss_attempts": 0,
            "quiz_streak": 0,
            "last_quiz_date": None,
            "quiz_questions_seen": [],
            "active_quiz_boss": None,
        }

    # Ensure skill_components exists (for saves made before skill system)
    if "skill_components" not in state:
        state["skill_components"] = {
            "shadowing":     {"xp": 0, "total_sentences": 0, "perfect_rounds": 0},
            "quiz":          {"xp": 0, "questions_answered": 0, "correct_answers": 0, "perfect_streaks": 0},
            "listening":     {"xp": 0, "total_score": 0, "count": 0},
            "pronunciation": {"xp": 0, "total_score": 0, "count": 0},
            "fluency":       {"xp": 0, "total_score": 0, "count": 0},
        }

    if last != today:
        # Reset stamina
        state["player"]["stamina"] = state["player"]["max_stamina"]

        # Check streak
        if last is not None:
            yesterday = (date.fromisoformat(last) + __import__("datetime").timedelta(days=1)).isoformat()
            if last != yesterday:
                # Streak broken
                if state["player"]["streak"] > 0:
                    unlock_achievement(state, "streak_broken")
                state["player"]["streak"] = 0

        # Reset daily quests
        state["quests"]["daily"] = {
            "first_steps": False,
            "warm_up": 0,
            "practice_makes_perfect": 0,
            "streak_defender": False,
            "perfect_round": 0,
            "speed_demon": False,
            "last_reset": today,
        }

        # Reset quiz daily streak
        state["quiz_state"]["quiz_streak"] = 0
        state["quiz_state"]["last_quiz_date"] = today

        # Check weekly boss reset (every Sunday — reset if last_boss_date is from last week)
        last_boss = state["quests"]["weekly_boss"].get("last_boss_date")
        if last_boss:
            lb = date.fromisoformat(last_boss)
            today_d = date.fromisoformat(today)
            # Simple: if it's a new week (iso weekday == 7 == Sunday), reset boss
            if today_d.weekday() == 6:  # Sunday
                if last_boss[:4] != today[:4] or last_boss[5:7] != today[5:7]:
                    # New week — new boss
                    idx = (today_d.isocalendar()[1]) % len(BOSSES)
                    boss_name, boss_hp = BOSSES[idx]
                    state["quests"]["weekly_boss"] = {
                        "defeated": False,
                        "attempts": 0,
                        "boss_name": boss_name,
                        "boss_max_hp": boss_hp,
                        "boss_hp": boss_hp,
                        "last_boss_date": today,
                    }

    return state


def xp_for_level(level: int) -> int:
    if level <= 1:
        return 0
    return LEVEL_XP[min(level - 1, len(LEVEL_XP) - 1)]


def xp_to_next_level(level: int) -> int:
    return level * 100


def award_xp(state: dict, amount: int, silent: bool = False) -> tuple[int, bool]:
    """Award XP, handle leveling. Returns (xp_awarded, leveled_up)."""
    player = state["player"]
    old_level = player["level"]
    player["xp"] += amount
    if player["xp"] < 0:
        player["xp"] = 0

    # Check level down
    while player["level"] > 1 and player["xp"] < xp_for_level(player["level"]):
        player["level"] -= 1

    # Check level up
    leveled_up = False
    while player["xp"] >= xp_to_next_level(player["level"]):
        player["level"] += 1
        leveled_up = True

    # Check skill unlocks
    new_unlocks = []
    for skill, (req_level, req_xp) in UNLOCK_REQUIREMENTS.items():
        if skill not in state["unlocked_skills"]:
            if player["level"] >= req_level and player["xp"] >= req_xp:
                state["unlocked_skills"].append(skill)
                new_unlocks.append(skill)

    return leveled_up, new_unlocks


# ──────────────────────────────────────────────
#  SENTENCE COMPARISON & MONSTER DETECTION
# ──────────────────────────────────────────────

def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s']", "", text)
    return text


def get_words(text: str) -> list:
    return normalize_text(text).split()


def compare_sentences(target: str, spoken: str) -> dict:
    """
    Returns dict with:
      - correct: list of correct words
      - errors: list of (expected, got, error_type)
      - accuracy: float 0-1
      - monsters: list of monster IDs defeated
    """
    target_words = get_words(target)
    spoken_words = get_words(spoken)

    correct = []
    errors = []
    monsters = []

    # Simple word-by-word alignment
    i, j = 0, 0
    while i < len(target_words) or j < len(spoken_words):
        if i >= len(target_words):
            # Extra words in spoken
            errors.append((None, spoken_words[j], "extra_word"))
            monsters.append("wildcard_imp")
            j += 1
        elif j >= len(spoken_words):
            # Missing words
            errors.append((target_words[i], None, "missing_word"))
            monsters.append("article_goblin")  # approximate
            i += 1
        elif target_words[i] == spoken_words[j]:
            correct.append(target_words[i])
            i += 1
            j += 1
        else:
            # Check for article errors
            t_w = target_words[i]
            s_w = spoken_words[j]
            if t_w in ("a", "the") and s_w in ("a", "the"):
                if t_w != s_w:
                    errors.append((t_w, s_w, "article_error"))
                    monsters.append("article_goblin")
                    correct.append(t_w)
                    i += 1
                    j += 1
                    continue
            # Check for plural
            if t_w.rstrip("s") == s_w.rstrip("s") and len(t_w) > 2 and t_w[-1] == "s":
                errors.append((t_w, s_w, "plural_error"))
                monsters.append("plural_kraken")
                correct.append(t_w)
                i += 1
                j += 1
                continue
            # Phonetic swap (very short, similar)
            if len(t_w) <= 3 and len(s_w) <= 3 and sorted(t_w) == sorted(s_w):
                errors.append((t_w, s_w, "phonetic_swap"))
                monsters.append("phonetic_wraith")
                correct.append(t_w)
                i += 1
                j += 1
                continue
            # Wrong word
            errors.append((t_w, s_w, "wrong_word"))
            monsters.append("wildcard_imp")
            correct.append(t_w)
            i += 1
            j += 1

    # Also check for phonetic similarity (Levenshtein-ish)
    # If accuracy looks too low, flag phonetic errors
    total = len(target_words)
    acc = len(correct) / total if total > 0 else 0

    return {
        "correct": correct,
        "errors": errors,
        "accuracy": acc,
        "monsters": monsters,
        "correct_count": len(correct),
        "total_words": total,
        "error_count": len(errors),
    }


def detect_monster_type(errors: list) -> Optional[str]:
    """Determine dominant monster type from errors."""
    if not errors:
        return None
    types = [e[2] for e in errors]
    # Priority mapping
    if "article_error" in types:
        return "article_goblin"
    if "plural_error" in types:
        return "plural_kraken"
    if "phonetic_swap" in types:
        return "phonetic_wraith"
    if "wrong_word" in types:
        return "wildcard_imp"
    return "wildcard_imp"


# ──────────────────────────────────────────────
#  ACHIEVEMENTS
# ──────────────────────────────────────────────

def unlock_achievement(state: dict, ach_id: str) -> Optional[dict]:
    if ach_id in state["achievements"]:
        return None
    ach = ACHIEVEMENTS.get(ach_id)
    if ach:
        state["achievements"].append(ach_id)
        save_state(state)
        return ach
    return None


def check_achievements(state: dict) -> list:
    player = state["player"]
    newly = []
    total = player["total_sentences_practiced"]

    if total >= 1:
        n = unlock_achievement(state, "day_1")
        if n:
            newly.append(n)
    if player["streak"] >= 7:
        n = unlock_achievement(state, "streak_7")
        if n:
            newly.append(n)
    if player["streak"] >= 30:
        n = unlock_achievement(state, "streak_30")
        if n:
            newly.append(n)
    if total >= 100:
        n = unlock_achievement(state, "grammar_grinder")
        if n:
            newly.append(n)
    if total >= 500 and player["total_errors"] / max(player["total_words_practiced"], 1) < 0.1:
        n = unlock_achievement(state, "shadow_master")
        if n:
            newly.append(n)

    total_monsters = sum(state["defeated_monsters"].values())
    if total_monsters >= 50:
        n = unlock_achievement(state, "monster_hunter")
        if n:
            newly.append(n)

    if player["level"] >= 10:
        n = unlock_achievement(state, "level_10")
        if n:
            newly.append(n)
    if player["level"] >= 20:
        n = unlock_achievement(state, "level_20")
        if n:
            newly.append(n)

    if state["quests"]["weekly_boss"]["defeated"]:
        n = unlock_achievement(state, "boss_slayer")
        if n:
            newly.append(n)
    if state["quests"]["weekly_boss"]["attempts"] >= 1:
        n = unlock_achievement(state, "first_boss")
        if n:
            newly.append(n)

    return newly


# ──────────────────────────────────────────────
#  DAILY QUESTS
# ──────────────────────────────────────────────

def update_quests(state: dict, sentence_result: dict, perfect_streak: int = 0):
    dq = state["quests"]["daily"]
    player = state["player"]

    dq["first_steps"] = True
    dq["warm_up"] += 1
    dq["practice_makes_perfect"] += 1

    if perfect_streak >= 5:
        dq["perfect_round"] = perfect_streak

    # Streak defender
    if state["player"]["streak"] > 0:
        dq["streak_defender"] = True

    # Speed demon: mark for now, checked on session end with timer


# ──────────────────────────────────────────────
#  BOSS FIGHT
# ──────────────────────────────────────────────

def start_boss_fight(state: dict) -> str:
    player = state["player"]
    if player["stamina"] < 5:
        return "⚡ Not enough stamina! You need at least 5⚡ to start a boss fight."

    today = date.today().isoformat()
    boss = state["quests"]["weekly_boss"]

    # Check if already defeated this week
    if boss["defeated"]:
        return f"🏆 You've already defeated {boss['boss_name']} this week! Next boss comes Sunday."

    boss["attempts"] += 1
    boss["last_boss_date"] = today
    player["stamina"] -= 5  # Boss fight costs 5 stamina

    idx = (date.fromisoformat(today).isocalendar()[1]) % len(BOSSES)
    boss_name, boss_hp = BOSSES[idx]
    boss["boss_name"] = boss_name
    boss["boss_max_hp"] = boss_hp
    boss["boss_hp"] = boss_hp

    save_state(state)
    return f"⚔️ BOSS FIGHT: {boss_name}! HP: {boss_hp}\n\n5 sentences to deal maximum damage! Cost: 5⚡\n\nSay 'ready' to begin!"


def process_boss_hit(state: dict, target: str, spoken: str) -> dict:
    boss = state["quests"]["weekly_boss"]
    result = compare_sentences(target, spoken)
    acc = result["accuracy"]
    damage = int(acc * 100)
    boss["boss_hp"] = max(0, boss["boss_hp"] - damage)

    if boss["boss_hp"] <= 0 and not boss["defeated"]:
        boss["defeated"] = True
        boss["boss_hp"] = 0
        award_xp(state, 500)
        state["player"]["gold"] += 100
        unlock_achievement(state, "boss_slayer")

    save_state(state)
    return {
        "accuracy": acc,
        "damage": damage,
        "boss_hp": boss["boss_hp"],
        "boss_max_hp": boss["boss_max_hp"],
        "boss_defeated": boss["defeated"],
        "result": result,
    }


# ──────────────────────────────────────────────
#  MAIN SESSION LOGIC
# ──────────────────────────────────────────────

def process_sentence(state: dict, target: str, spoken: str,
                     topic: str, session_stats: dict) -> dict:
    player = state["player"]
    result = compare_sentences(target, spoken)
    acc = result["accuracy"]
    correct_count = result["correct_count"]
    total_words = result["total_words"]

    # Update player stats
    player["total_sentences_practiced"] += 1
    player["total_words_practiced"] += total_words
    player["total_errors"] += result["error_count"]
    player["last_practice_date"] = date.today().isoformat()

    # Update streak
    if player["streak"] == 0:
        player["streak"] = 1
    else:
        last = player.get("last_practice_date")
        if last:
            yesterday = (date.today() - __import__("datetime").timedelta(days=1)).isoformat()
            if last == yesterday:
                player["streak"] += 1
            elif last == date.today().isoformat():
                pass  # same day
            else:
                player["streak"] = 1

    # Update skill progress
    sp = state["skill_progress"].get(topic, {"attempted": 0, "mastered": 0, "perfect": 0})
    sp["attempted"] += 1
    if acc >= 0.9:
        sp["mastered"] += 1
    if acc == 1.0:
        sp["perfect"] += 1

    # Stamina
    player["stamina"] = max(0, player["stamina"] - 1)

    # XP and gold
    monsters = result["monsters"]
    xp_gained = 0
    gold_gained = 0

    if acc == 1.0:
        xp_gained = 20
        gold_gained = 2
        session_stats["perfect_streak"] += 1
        session_stats["session_perfects"] += 1
    elif acc >= 0.66:
        xp_gained = 10
        gold_gained = 1
        session_stats["perfect_streak"] = 0
    else:
        xp_gained = 5
        gold_gained = 0
        session_stats["perfect_streak"] = 0

    # Monster defeats
    for m in monsters:
        state["defeated_monsters"][m] += 1

    # XP for monster defeats
    xp_gained += len(monsters) * 3

    old_level = player["level"]
    leveled_up, new_unlocks = award_xp(state, xp_gained)
    player["gold"] += gold_gained

    # Award skill component XP
    skill_scores = calculate_shadowing_scores(target, spoken)
    skill_xp_map = {15: 15, 10: 8, 5: 3}  # perfect, good, try_again
    base_skill_xp = skill_xp_map.get(xp_gained, 3)
    skill_xp_awarded = award_skill_xp(
        state, "shadowing", base_skill_xp,
        listening=skill_scores["listening"],
        pronunciation=skill_scores["pronunciation"],
        fluency=skill_scores["fluency"],
    )

    # Daily quests
    update_quests(state, result, session_stats["perfect_streak"])

    # Achievements
    new_achievements = check_achievements(state)

    save_state(state)

    return {
        "xp_gained": xp_gained,
        "gold_gained": gold_gained,
        "leveled_up": leveled_up,
        "old_level": old_level,
        "new_level": player["level"],
        "new_unlocks": new_unlocks,
        "accuracy": acc,
        "correct_count": correct_count,
        "total_words": total_words,
        "monsters_defeated": monsters,
        "result": result,
        "new_achievements": new_achievements,
        "skill_scores": skill_scores,
        "skill_xp_awarded": skill_xp_awarded,
        "overall_level": get_overall_level(state),
        "boss": None,
    }


def get_player_card(state: dict) -> str:
    p = state["player"]
    q = state["quests"]["daily"]
    flair = state["shop"].get("equipped_flair") or ""
    title = state["shop"].get("equipped_title")
    title_str = f' "{title}"' if title else ""

    xp_needed = xp_to_next_level(p["level"])
    xp_current = p["xp"] - xp_for_level(p["level"])
    xp_bar = "█" * int(xp_current / xp_needed * 10) + "░" * (10 - int(xp_current / xp_needed * 10))

    # Skill components
    sp = get_skill_profile(state)
    overall = sp["_overall"]

    skill_lines = []
    for sid in ["shadowing", "quiz", "listening", "pronunciation", "fluency"]:
        info = sp[sid]
        meta = SKILL_COMPONENTS[sid]
        icon = meta["icon"]
        bar = "█" * int(info["xp_in_level"] / max(info["xp_for_next"], 1) * 8) + \
              "░" * (8 - int(info["xp_in_level"] / max(info["xp_for_next"], 1) * 8))
        skill_lines.append(
            f"  {icon} {meta['name']:<14} Lv.{info['level']} {bar}"
        )
    skill_lines.append(
        f"  ──────────────────────────────────"
    )
    skill_lines.append(
        f"  🏆 Overall Level: ⭐ {overall}"
    )

    # Daily quest status
    quest_lines = []
    if q["first_steps"]:
        quest_lines.append("  🐣 First Steps ✅")
    else:
        quest_lines.append("  🐣 First Steps — Complete 1 sentence")

    if q["warm_up"] >= 5:
        quest_lines.append("  🔥 Warm Up ✅")
    else:
        quest_lines.append(f"  🔥 Warm Up — {q['warm_up']}/5 sentences")

    if q["practice_makes_perfect"] >= 10:
        quest_lines.append("  ⚔️ Practice Makes Perfect ✅")
    else:
        quest_lines.append(f"  ⚔️ Practice Makes Perfect — {q['practice_makes_perfect']}/10")

    # Weekly boss
    boss = state["quests"]["weekly_boss"]
    if boss["defeated"]:
        quest_lines.append(f"  🏆 Weekly Boss: {boss['boss_name']} ✅ DEFEATED")
    else:
        quest_lines.append(f"  🏆 Weekly Boss: {boss['boss_name']} ({boss['boss_hp']}/{boss['boss_max_hp']} HP)")

    total_monsters = sum(state["defeated_monsters"].values())

    card = f"""
🎮 SHADOW PLAYER CARD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{flair} {p['name']} | Lv.{p['level']}{title_str}
⭐ {p['xp']}/{xp_needed} XP  {xp_bar}
🔥 Streak: {p['streak']} days
❤️ {p['hp']}/{p['max_hp']} HP   ⚡ {p['stamina']}/{p['max_stamina']} Stamina
🪙 Gold: {p['gold']}

📊 Skills
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""" + "\n".join(skill_lines) + f"""

📋 Daily Quests
""" + "\n".join(quest_lines)

    if state["achievements"]:
        ach_names = [ACHIEVEMENTS[a]["name"] for a in state["achievements"][-3:]]
        card += f"\n\n🏅 Recent: {', '.join(ach_names)}"

    return card


# ──────────────────────────────────────────────
#  QUIZ ENGINE
# ──────────────────────────────────────────────

def init_quiz_state() -> dict:
    return {
        "questions_answered": 0,
        "correct_answers": 0,
        "quiz_bosses_defeated": 0,
        "quiz_boss_attempts": 0,
        "quiz_streak": 0,
        "last_quiz_date": None,
        "quiz_questions_seen": [],
        "active_quiz_boss": None,
    }


def check_quiz_daily_reset(state: dict) -> dict:
    """Reset daily quiz streaks if it's a new day."""
    today = date.today().isoformat()
    qs = state.get("quiz_state", {})
    last = qs.get("last_quiz_date")

    if last != today:
        qs["quiz_streak"] = 0
        qs["last_quiz_date"] = today
        state["quiz_state"] = qs
    return state


def get_random_quiz_question(state: dict, topic: str = None) -> Optional[dict]:
    """Pick a random quiz question not yet seen today, or from specific topic."""
    qs = state.get("quiz_state", {})
    seen = qs.get("quiz_questions_seen", [])

    # Build eligible pool
    if topic and topic in QUIZ_BANK:
        pool = [q for q in QUIZ_BANK[topic] if q["id"] not in seen]
    else:
        pool = []
        for t_questions in QUIZ_BANK.values():
            pool.extend([q for q in t_questions if q["id"] not in seen])

    if not pool:
        # Reset seen questions for the day
        qs["quiz_questions_seen"] = []
        pool = []
        for t_questions in QUIZ_BANK.values():
            pool.extend(t_questions)

    if not pool:
        return None

    return random.choice(pool)


def format_quiz_question(q: dict) -> str:
    """Format a quiz question for display (no answer hint)."""
    question = q["question"]
    options = q["options"]
    cefr = q.get("cefr", "A1")
    xp_r = q.get("xp_reward", 10)

    lines = [
        f"📝 GRAMMAR QUIZ  [CEFR {cefr}]",
        "━" * 32,
        f"\n{question}\n",
    ]

    for i, opt in enumerate(options):
        lines.append(f"  {chr(65+i)}) {opt}")

    lines.append(f"\n⚡ -1 stamina  |  +{xp_r} XP per correct answer")
    return "\n".join(lines)


def check_quiz_answer(state: dict, question_id: str, user_answer: str) -> dict:
    """
    Check user's answer to a quiz question.
    user_answer: the option letter (A, B, C, D) or the answer text.
    Returns feedback dict.
    """
    player = state["player"]
    qs = state["quiz_state"]

    # Find the question
    question = None
    for topic, questions in QUIZ_BANK.items():
        for q in questions:
            if q["id"] == question_id:
                question = q
                question["_topic"] = topic
                break
        if question:
            break

    if not question:
        return {"error": "Question not found", "question_id": question_id}

    correct_answer = question["answer"]
    options = question["options"]

    # Normalize answer: user can answer by letter (A/B/C/D) or text
    user_answer_clean = user_answer.strip()
    user_answer_upper = user_answer_clean.upper()

    # Check: is it a letter?
    if len(user_answer_upper) == 1 and user_answer_upper in "ABCD":
        letter_idx = ord(user_answer_upper) - ord("A")
        if letter_idx < len(options):
            selected_answer = options[letter_idx]
        else:
            selected_answer = user_answer_clean
    else:
        # Try to match by text (case-insensitive)
        selected_answer = user_answer_clean
        matched = False
        for opt in options:
            if opt.lower().strip() == user_answer_clean.lower().strip():
                selected_answer = opt
                matched = True
                break
        if not matched:
            # Fuzzy match: partial
            for opt in options:
                if user_answer_clean.lower() in opt.lower() or opt.lower() in user_answer_clean.lower():
                    selected_answer = opt
                    matched = True
                    break

    is_correct = False
    # Check exact match first
    if selected_answer == correct_answer:
        is_correct = True
    # Also check if the letter matches
    if not is_correct and len(user_answer_upper) == 1:
        letter_idx = ord(user_answer_upper) - ord("A")
        if letter_idx < len(options) and options[letter_idx] == correct_answer:
            is_correct = True

    # Stamina cost
    if player["stamina"] < 1:
        return {"error": "⚡ Not enough stamina!", "stamina": player["stamina"]}

    player["stamina"] -= 1
    player["last_practice_date"] = date.today().isoformat()
    qs["questions_answered"] += 1

    # Mark question as seen
    if question_id not in qs["quiz_questions_seen"]:
        qs["quiz_questions_seen"].append(question_id)

    xp_gained = 0
    gold_gained = 0
    monsters_defeated = []
    monster_id = question.get("monster", "article_goblin")
    explanation = question.get("explanation", "")

    if is_correct:
        qs["correct_answers"] += 1
        qs["quiz_streak"] += 1
        xp_gained = question.get("xp_reward", 10)
        gold_gained = 2

        # Streak bonus: 5 in a row = +50 XP bonus
        if qs["quiz_streak"] > 0 and qs["quiz_streak"] % 5 == 0:
            xp_gained += 50

        # Defeat monster
        monsters_defeated = [monster_id]
        state["defeated_monsters"][monster_id] = state["defeated_monsters"].get(monster_id, 0) + 1
    else:
        qs["quiz_streak"] = 0  # Reset streak on wrong answer

    # Award XP
    leveled_up, new_unlocks = award_xp(state, xp_gained)
    player["gold"] += gold_gained

    # Award quiz skill component XP
    quiz_xp_awarded = award_skill_xp(state, "quiz", xp_gained)

    # Check quiz achievements
    new_achievements = []
    total_q = qs["questions_answered"]
    if total_q >= 10:
        n = unlock_achievement(state, "quiz_rookie")
        if n:
            new_achievements.append(n)
    if total_q >= 50 and qs["correct_answers"] / total_q >= 0.8:
        n = unlock_achievement(state, "grammar_apprentice")
        if n:
            new_achievements.append(n)
    if qs["quiz_streak"] >= 10:
        n = unlock_achievement(state, "quiz_perfect_10")
        if n:
            new_achievements.append(n)

    # Update last quiz date
    qs["last_quiz_date"] = date.today().isoformat()

    save_state(state)

    # Build feedback
    if is_correct:
        stars = "⭐" * min(qs["quiz_streak"], 5)
        feedback = f"""
✅ CORRECT! {stars}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 Question: {question['question']}
✏️ Your answer: {selected_answer}

💡 {explanation}

+{xp_gained} XP  +{gold_gained}🪙
🏅 Streak: {qs['quiz_streak']}
⚡ Stamina: {player['stamina']}/{player['max_stamina']}
"""
    else:
        feedback = f"""
❌ WRONG
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 Question: {question['question']}
✏️ Your answer: {selected_answer}
✅ Correct: {correct_answer}

💡 {explanation}

No XP lost — try again!
🏅 Streak: 0
⚡ Stamina: {player['stamina']}/{player['max_stamina']}
"""

    return {
        "is_correct": is_correct,
        "feedback": feedback.strip(),
        "xp_gained": xp_gained,
        "gold_gained": gold_gained,
        "correct_answer": correct_answer,
        "selected_answer": selected_answer,
        "monsters_defeated": monsters_defeated,
        "streak": qs["quiz_streak"],
        "stamina": player["stamina"],
        "leveled_up": leveled_up,
        "new_unlocks": new_unlocks,
        "new_achievements": new_achievements,
        "question": question,
        "quiz_xp_awarded": quiz_xp_awarded.get("quiz", 0),
        "overall_level": get_overall_level(state),
    }


def start_quiz_boss(state: dict, topic: str = None) -> dict:
    """Start a quiz boss fight — 10 questions, boss HP system."""
    player = state["player"]
    qs = state["quiz_state"]

    if player["stamina"] < 5:
        return {"error": "⚡ Not enough stamina! Need 5⚡ for quiz boss."}

    if qs.get("active_quiz_boss"):
        return {
            "error": f"⚔️ You already have an active quiz boss! Complete it first."
        }

    player["stamina"] -= 5

    # Pick 10 random questions
    seen = qs.get("quiz_questions_seen", [])
    all_qs = []
    for t_questions in QUIZ_BANK.values():
        if topic is None or topic == t_questions[0].get("topic"):
            all_qs.extend([q for q in t_questions if q["id"] not in seen])

    if len(all_qs) < 10:
        # Reset seen pool
        all_qs = []
        for t_questions in QUIZ_BANK.values():
            all_qs.extend(t_questions)

    random.shuffle(all_qs)
    boss_questions = all_qs[:10]

    # Boss HP based on topic
    boss_names = [
        "The Article Archon",
        "The Plural Hydra",
        "The Phonetic Dragon",
        "The Tense Specter",
        "The Vocab Vampire",
    ]
    boss_name = boss_names[qs["quiz_bosses_defeated"] % len(boss_names)]
    boss_max_hp = 100

    qs["active_quiz_boss"] = {
        "name": boss_name,
        "boss_max_hp": boss_max_hp,
        "boss_hp": boss_max_hp,
        "questions": [q["id"] for q in boss_questions],
        "current_q_index": 0,
        "correct_count": 0,
        "total_questions": 10,
    }
    qs["quiz_boss_attempts"] += 1

    save_state(state)

    first_q = boss_questions[0]
    first_q["_topic"] = None
    for t, qs_list in QUIZ_BANK.items():
        if first_q["id"] in [q["id"] for q in qs_list]:
            first_q["_topic"] = t
            break

    return {
        "boss_name": boss_name,
        "boss_hp": boss_max_hp,
        "boss_max_hp": boss_max_hp,
        "boss_message": f"""
⚔️ QUIZ BOSS FIGHT: {boss_name}!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏥 Boss HP: {boss_max_hp}/{boss_max_hp}
📝 10 questions to defeat the boss!
⚡ Cost: 5 stamina (paid)

Boss damage = your accuracy × 10 HP per question
Win: reduce boss HP to 0 (≥80% overall accuracy)
Even if you 'lose' — you still earn XP!

""",
        "current_question": first_q,
        "question_number": 1,
        "total_questions": 10,
    }


def process_quiz_boss_hit(state: dict, question_id: str, user_answer: str) -> dict:
    """Process one answer in a quiz boss fight."""
    player = state["player"]
    qs = state["quiz_state"]
    boss = qs.get("active_quiz_boss")

    if not boss:
        return {"error": "No active quiz boss. Start one with 'quiz boss'."}

    if question_id != boss["questions"][boss["current_q_index"]]:
        return {"error": "Wrong question order! Answer the current question first."}

    # Find question data
    question = None
    for t, t_questions in QUIZ_BANK.items():
        for q in t_questions:
            if q["id"] == question_id:
                question = dict(q)
                question["_topic"] = t
                break
        if question:
            break

    if not question:
        return {"error": "Question not found"}

    correct_answer = question["answer"]
    options = question["options"]
    user_answer_upper = user_answer.strip().upper()

    # Resolve answer
    if len(user_answer_upper) == 1 and user_answer_upper in "ABCD":
        letter_idx = ord(user_answer_upper) - ord("A")
        selected = options[letter_idx] if letter_idx < len(options) else user_answer
    else:
        selected = user_answer.strip()
        for opt in options:
            if opt.lower().strip() == selected.lower():
                selected = opt
                break

    is_correct = selected == correct_answer

    # Stamina cost already paid at boss start
    qs["questions_answered"] += 1
    if question_id not in qs["quiz_questions_seen"]:
        qs["quiz_questions_seen"].append(question_id)

    xp_gained = 0
    gold_gained = 0
    damage = 0
    monster_id = question.get("monster", "article_goblin")

    if is_correct:
        boss["correct_count"] += 1
        qs["correct_answers"] += 1
        qs["quiz_streak"] += 1
        xp_gained = question.get("xp_reward", 10) + 5  # Boss bonus XP
        gold_gained = 3
        damage = 10  # 10 HP per correct answer

        # Streak bonus
        if qs["quiz_streak"] % 5 == 0:
            xp_gained += 50

        state["defeated_monsters"][monster_id] = state["defeated_monsters"].get(monster_id, 0) + 1
    else:
        qs["quiz_streak"] = 0
        damage = 0

    boss["boss_hp"] = max(0, boss["boss_hp"] - damage)
    boss["current_q_index"] += 1

    # XP and gold
    award_xp(state, xp_gained)
    player["gold"] += gold_gained

    # Check boss defeated
    boss_defeated = boss["boss_hp"] <= 0
    boss_complete = boss["current_q_index"] >= boss["total_questions"]

    if boss_defeated:
        boss["boss_hp"] = 0
        award_xp(state, 300)
        player["gold"] += 50
        qs["quiz_bosses_defeated"] += 1
        unlock_achievement(state, "quiz_boss_slayer")

    if boss_complete and not boss_defeated:
        # Boss survived but got damaged
        pass

    # Get next question if any
    next_question = None
    if boss["current_q_index"] < boss["total_questions"] and not boss_defeated:
        next_q_id = boss["questions"][boss["current_q_index"]]
        for t, t_questions in QUIZ_BANK.items():
            for q in t_questions:
                if q["id"] == next_q_id:
                    next_question = dict(q)
                    next_question["_topic"] = t
                    break
            if next_question:
                break

    save_state(state)

    # Build feedback
    explanation = question.get("explanation", "")
    if is_correct:
        feedback = f"""
{'✅ CORRECT!'} 💥 -{damage} HP to {boss['name']}!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 {question['question']}
✏️ Your answer: {selected}
🏅 Streak: {qs['quiz_streak']}
+{xp_gained} XP | +{gold_gained}🪙
"""
    else:
        feedback = f"""
❌ WRONG! {boss['name']} takes no damage!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 {question['question']}
✏️ Your answer: {selected}
✅ Correct: {correct_answer}
💡 {explanation}
🏅 Streak: 0
"""

    result = {
        "feedback": feedback.strip(),
        "is_correct": is_correct,
        "damage": damage,
        "boss_hp": boss["boss_hp"],
        "boss_max_hp": boss["boss_max_hp"],
        "boss_name": boss["name"],
        "boss_defeated": boss_defeated,
        "boss_complete": boss_complete,
        "question_number": boss["current_q_index"],
        "correct_count": boss["correct_count"],
        "xp_gained": xp_gained,
        "gold_gained": gold_gained,
        "stamina": player["stamina"],
        "next_question": next_question,
        "next_question_number": boss["current_q_index"] + 1 if next_question else None,
    }

    if boss_defeated:
        result["victory_message"] = f"""
🎉 QUIZ BOSS DEFEATED!!!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚔️ {boss['name']} has been vanquished!

📊 Boss Fight Stats:
  ✅ Correct: {boss['correct_count']}/{boss['total_questions']}
  💥 Damage dealt: {boss['boss_max_hp']}

🏆 Rewards:
  +300 XP | +50🪙
  ⚔️ Quiz Boss Slayer badge earned!

You're a Grammar Warrior!
"""

    if boss_complete and not boss_defeated:
        accuracy = int(boss["correct_count"] / boss["total_questions"] * 100)
        result["survival_message"] = f"""
🏳️ Boss Escaped!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{boss['name']} survived with {boss['boss_hp']}/{boss['boss_max_hp']} HP.

📊 Accuracy: {accuracy}%
✅ Correct: {boss['correct_count']}/10

You still earned XP! Keep practicing!
"""

    # Clear boss if complete
    if boss_defeated or boss_complete:
        qs["active_quiz_boss"] = None

    save_state(state)
    return result


# ──────────────────────────────────────────────
#  MAIN ENTRY
# ──────────────────────────────────────────────

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"

    if cmd == "status":
        state = init_state()
        state = check_daily_reset(state)
        print(get_player_card(state))

    elif cmd == "card":
        state = init_state()
        state = check_daily_reset(state)
        print(get_player_card(state))

    elif cmd == "boss":
        state = init_state()
        state = check_daily_reset(state)
        print(start_boss_fight(state))

    elif cmd == "shop":
        lines = ["🛒 SHOP\n━━━━━━━━━━━━━━━━━━"]
        for key, item in SHOP_ITEMS.items():
            lines.append(f"  {item['name']} — {item['cost']}🪙")
        print("\n".join(lines))

    elif cmd == "achievements":
        state = init_state()
        lines = ["🏆 ACHIEVEMENTS\n━━━━━━━━━━━━━━━━━━"]
        for ach_id in state["achievements"]:
            ach = ACHIEVEMENTS[ach_id]
            lines.append(f"  ✅ {ach['name']} — {ach['desc']}")
        print("\n".join(lines))

    elif cmd == "sentences":
        topic = sys.argv[2] if len(sys.argv) > 2 else None
        if topic and topic in SENTENCES:
            for i, (s, m) in enumerate(SENTENCES[topic]):
                print(f"  {i+1}. {s}")
        else:
            for t, sents in SENTENCES.items():
                print(f"\n[{t.upper()}]")
                for s, m in sents:
                    print(f"  {s}")

    else:
        print(f"Unknown command: {cmd}")
        print("Commands: status, card, boss, shop, achievements, sentences [topic]")
