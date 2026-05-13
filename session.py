#!/usr/bin/env python3
"""
English Shadowing RPG — Interactive Session Manager
Called by the agent to run a single shadowing turn.
Usage: session.py <action> [args...]

Actions:
  start              — Show player card, pick first sentence, return JSON
  sentence <topic>   — Pick a sentence from topic, return JSON
  compare <target> <spoken> <topic> — Process result, update state, return feedback JSON
  boss_start         — Start boss fight
  boss_hit <target> <spoken> — Process boss hit
  shop               — List shop items
  buy <item_key>     — Purchase item
  card               — Show player card
  quests             — Show quest status
"""

import json
import sys
import os
from pathlib import Path

# Ensure home dir for state
STATE_FILE = Path("/home/ubuntu/.hermes/profiles/elias-strategist/rpg/shadowing_rpg.json")
os.chdir("/home/ubuntu/.hermes/profiles/elias-strategist/rpg")
sys.path.insert(0, str(Path(__file__).parent))

from engine import (
    load_state, save_state, init_state, check_daily_reset,
    compare_sentences, process_sentence, get_player_card,
    start_boss_fight, process_boss_hit,
    SENTENCES, UNLOCK_REQUIREMENTS, SHOP_ITEMS, ACHIEVEMENTS,
    xp_for_level, xp_to_next_level, detect_monster_type,
    award_xp,
    QUIZ_BANK,
    check_quiz_answer, get_random_quiz_question,
    start_quiz_boss, process_quiz_boss_hit,
    format_quiz_question,
    SKILL_COMPONENTS, get_skill_profile, get_overall_level,
    calculate_shadowing_scores, award_skill_xp,
    CEFR_EMOJI, CEFR_NAME, filter_sentences_by_level,
    VOCAB_BANK,
    start_vocab_session, reveal_vocab_card, rate_vocab_card,
    get_current_vocab_card, start_vocab_boss, process_vocab_boss_rating,
    search_vocab_bank, check_vocab_daily_reset,
)
import random


def cmd_start():
    state = init_state()
    state = check_daily_reset(state)
    save_state(state)

    card = get_player_card(state)
    unlocked = state["unlocked_skills"]
    greetings = SENTENCES["greetings"][0]
    sp = get_skill_profile(state)
    return {
        "card": card,
        "first_sentence": greetings[0],
        "first_meaning": greetings[1],
        "unlocked_topics": unlocked,
        "stamina": state["player"]["stamina"],
        "can_boss": state["player"]["stamina"] >= 5 and not state["quests"]["weekly_boss"]["defeated"],
        "skill_profile": sp,
    }


def cmd_sentence(topic: str):
    state = load_state()
    if topic not in SENTENCES:
        return {"error": f"Unknown topic: {topic}"}
    if topic not in state["unlocked_skills"]:
        req = UNLOCK_REQUIREMENTS.get(topic, (1, 0))
        return {"error": f"Topic '{topic}' locked! Reach Level {req[0]} and earn {req[1]} XP."}

    sp = state["skill_progress"].get(topic, {"attempted": 0})
    all_sents = SENTENCES[topic]
    player_level = state["player"].get("level", 1)

    # Filter by CEFR level for this player's level FIRST
    filtered = filter_sentences_by_level(all_sents, player_level)
    if not filtered:
        filtered = all_sents  # fallback if no match

    # Build index map: sentence → original index in all_sents
    idx_map = {id(s): all_sents.index(s) for s in filtered}

    # Pick a sentence not yet mastered (prefer unmastered)
    unmastered = [s for s in filtered if idx_map[id(s)] >= sp["attempted"]]
    if not unmastered:
        # Reset progress for this topic
        state["skill_progress"][topic]["attempted"] = 0
        state["skill_progress"][topic]["mastered"] = 0
        state["skill_progress"][topic]["perfect"] = 0
        save_state(state)
        unmastered = filtered

    chosen = random.choice(unmastered)
    sentence = chosen[0]
    meaning = chosen[1]
    cefr = chosen[2] if len(chosen) > 2 else "A1"
    cefr_emoji = CEFR_EMOJI.get(cefr, "🟢")

    return {
        "sentence": sentence,
        "meaning": meaning,
        "topic": topic,
        "cefr": cefr,
        "cefr_emoji": cefr_emoji,
        "cefr_name": CEFR_NAME.get(cefr, "Beginner"),
        "player_level": player_level,
    }


def cmd_compare(target: str, spoken: str, topic: str, is_boss: bool = False):
    state = load_state()
    result = compare_sentences(target, spoken)
    acc = result["accuracy"]

    if is_boss:
        boss_result = process_boss_hit(state, target, spoken)
        save_state(state)
        return {
            "is_boss": True,
            "accuracy": acc,
            "damage": boss_result["damage"],
            "boss_hp": boss_result["boss_hp"],
            "boss_max_hp": boss_result["boss_max_hp"],
            "boss_defeated": boss_result["boss_defeated"],
            "boss_name": state["quests"]["weekly_boss"]["boss_name"],
            "xp_gained": boss_result["damage"] // 10 * 3,
            "monsters": result["monsters"],
            "correct": result["correct"],
            "errors": result["errors"],
        }

    session_stats = {"perfect_streak": 0, "session_perfects": 0}
    out = process_sentence(state, target, spoken, topic, session_stats)
    save_state(state)

    # Format errors nicely
    error_lines = []
    for exp, got, etype in out["result"]["errors"]:
        if exp and got:
            error_lines.append(f"  ❌ '{got}' → expected '{exp}' ({etype})")
        elif exp and not got:
            error_lines.append(f"  ❌ Missing: '{exp}'")
        elif got:
            error_lines.append(f"  ❌ Extra: '{got}'")

    monster_lines = []
    for m in out["monsters_defeated"]:
        name, desc = {
            "article_goblin": ("👺 Article Goblin", "a/the confusion"),
            "plural_kraken": ("🐙 Plural Kraken", "missing -s/-es"),
            "phonetic_wraith": ("👻 Phonetic Wraith", "phonetic swap"),
            "vowel_specter": ("🌫️ Vowel Specter", "wrong vowel"),
            "tense_phantom": ("⏰ Tense Phantom", "wrong tense"),
            "wildcard_imp": ("🔥 Wildcard Imp", "wrong word"),
        }.get(m, (m, ""))
        if name:
            monster_lines.append(f"  ⚔️ Defeated: {name} — {desc}")

    new_ach_lines = []
    for ach in out.get("new_achievements", []):
        new_ach_lines.append(f"  🏆 NEW ACHIEVEMENT: {ach['name']} — {ach['desc']}")

    stars = "⭐⭐⭐" if acc == 1.0 else "⭐⭐" if acc >= 0.66 else "⭐"

    feedback = f"""
⚔️ SHADOW RESULT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🗣️ Target: "{target}"
👤 You:    "{spoken}"

{stars} Accuracy: {int(acc*100)}% ({out['correct_count']}/{out['total_words']} words)

"""
    if error_lines:
        feedback += "Errors:\n" + "\n".join(error_lines) + "\n"
    if monster_lines:
        feedback += "\n".join(monster_lines) + "\n"
    if not error_lines:
        feedback += "  ✨ Perfect! No errors!\n"

    feedback += f"""
💰 +{out['xp_gained']} XP  +{out['gold_gained']}🪙

⭐ XP: {state['player']['xp']}/{xp_to_next_level(state['player']['level'])}
⚡ Stamina: {state['player']['stamina']}/{state['player']['max_stamina']}
🔥 Streak: {state['player']['streak']}
"""

    if out["leveled_up"]:
        feedback += f"\n🎉 LEVEL UP! You are now Level {out['new_level']}!\n"

    if out["new_unlocks"]:
        feedback += f"\n🔓 NEW TOPICS UNLOCKED: {', '.join(out['new_unlocks'])}\n"

    if new_ach_lines:
        feedback += "\n" + "\n".join(new_ach_lines) + "\n"

    return {
        "feedback": feedback.strip(),
        "xp_gained": out["xp_gained"],
        "gold_gained": out["gold_gained"],
        "accuracy": acc,
        "leveled_up": out["leveled_up"],
        "new_level": out["new_level"],
        "stamina": state["player"]["stamina"],
        "xp": state["player"]["xp"],
        "xp_needed": xp_to_next_level(state["player"]["level"]),
        "new_achievements": [a["name"] for a in out.get("new_achievements", [])],
        "skill_scores": out.get("skill_scores", {}),
        "skill_xp_awarded": out.get("skill_xp_awarded", {}),
        "overall_level": out.get("overall_level", 1.0),
    }


def cmd_boss_start():
    state = init_state()
    state = check_daily_reset(state)
    save_state(state)
    return {"message": start_boss_fight(state)}


def cmd_boss_hit(target: str, spoken: str):
    state = load_state()
    result = process_boss_hit(state, target, spoken)
    save_state(state)

    acc = result["accuracy"]
    stars = "⭐⭐⭐" if acc == 1.0 else "⭐⭐" if acc >= 0.66 else "⭐"

    msg = f"""
⚔️ BOSS HIT!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🗣️ Target: "{target}"
👤 You:    "{spoken}"

{stars} Accuracy: {int(acc*100)}%
💥 Damage dealt: {result['damage']} HP

🏆 {state['quests']['weekly_boss']['boss_name']}
   HP: {result['boss_hp']}/{result['boss_max_hp']}
"""

    if result["boss_defeated"]:
        msg += f"""
🎉 BOSS DEFEATED!!!
+500 XP | +100🪙

You've conquered {state['quests']['weekly_boss']['boss_name']}!
"""

    return {
        "message": msg.strip(),
        "boss_hp": result["boss_hp"],
        "boss_defeated": result["boss_defeated"],
        "xp_gained": result["damage"] // 10 * 3,
    }


def cmd_shop():
    state = load_state()
    gold = state["player"]["gold"]
    purchased = state["shop"]["purchased_titles"] + state["shop"]["purchased_flairs"]
    lines = [f"🛒 SHOP — Your Gold: {gold}🪙\n━━━━━━━━━━━━━━━━━━"]
    for key, item in SHOP_ITEMS.items():
        owned = key in purchased
        cost_str = f"{item['cost']}🪙" if not owned else "OWNED"
        lines.append(f"  {item['name']:30s} {cost_str}")
    return {"message": "\n".join(lines), "gold": gold}


def cmd_buy(item_key: str):
    state = load_state()
    item = SHOP_ITEMS.get(item_key)
    if not item:
        return {"error": f"Unknown item: {item_key}"}

    purchased = state["shop"]["purchased_titles"] + state["shop"]["purchased_flairs"]
    if item_key in purchased:
        return {"error": "You already own this item!"}

    gold = state["player"]["gold"]
    if gold < item["cost"]:
        return {"error": f"Not enough gold! Need {item['cost']}🪙, have {gold}🪙"}

    gold -= item["cost"]
    state["player"]["gold"] = gold

    if item["type"] == "title":
        state["shop"]["purchased_titles"].append(item_key)
        state["shop"]["equipped_title"] = item["name"]
        state["inventory"]["titles"].append(item["name"])
    elif item["type"] == "flair":
        state["shop"]["purchased_flairs"].append(item_key)
        state["shop"]["equipped_flair"] = item["name"]
        state["inventory"]["flairs"].append(item["name"])
    elif item["type"] == "refill":
        state["player"]["stamina"] = min(
            state["player"]["max_stamina"],
            state["player"]["stamina"] + 20
        )

    save_state(state)
    return {
        "message": f"✅ Purchased: {item['name']}!",
        "gold": gold,
        "stamina": state["player"]["stamina"],
    }


def cmd_card():
    state = init_state()
    state = check_daily_reset(state)
    sp = get_skill_profile(state)
    return {"card": get_player_card(state), "skill_profile": sp}


def cmd_skills():
    """Show full skill component breakdown."""
    state = load_state()
    sp = get_skill_profile(state)

    lines = ["📊 SKILL PROFILE\n━━━━━━━━━━━━━━━━━━"]
    for sid in ["shadowing", "quiz", "listening", "pronunciation", "fluency"]:
        info = sp[sid]
        meta = SKILL_COMPONENTS[sid]
        bar = "█" * int(info["xp_in_level"] / max(info["xp_for_next"], 1) * 10) + \
              "░" * (10 - int(info["xp_in_level"] / max(info["xp_for_next"], 1) * 10))
        avg = info.get("avg_score", 0)
        lines.append(f"{meta['icon']} {meta['name']} — Lv.{info['level']} {bar}")
        if avg > 0:
            lines.append(f"   Avg score: {avg}% | Total: {info['total_count']} attempts")
        else:
            lines.append(f"   XP: {info['xp']} | Next: {info['xp_for_next']} XP")

    lines.append(f"\n🏆 Overall Level: ⭐ {sp['_overall']}")
    return {"skills_text": "\n".join(lines), "skill_profile": sp}


def cmd_quests():
    state = load_state()
    q = state["quests"]["daily"]
    boss = state["quests"]["weekly_boss"]

    lines = ["📋 DAILY QUESTS\n━━━━━━━━━━━━━━━━━━"]
    for name, done in [
        ("🐣 First Steps (1 sentence)", q["first_steps"]),
        (f"🔥 Warm Up (5 sentences) — {q['warm_up']}/5", q["warm_up"] >= 5),
        (f"⚔️ Practice Makes Perfect (10) — {q['practice_makes_perfect']}/10", q["practice_makes_perfect"] >= 10),
        (f"🛡️ Streak Defender (practice on streak day)", q["streak_defender"]),
        (f"✨ Perfect Round (5⭐ in a row) — {q['perfect_round']}/5", q["perfect_round"] >= 5),
    ]:
        status = "✅" if done else "☐"
        lines.append(f"  {status} {name}")

    lines.append(f"\n🏆 WEEKLY BOSS: {boss['boss_name']}")
    if boss["defeated"]:
        lines.append("  ✅ DEFEATED this week!")
    else:
        lines.append(f"  ☑️ HP: {boss['boss_hp']}/{boss['boss_max_hp']} — 'boss fight' to challenge!")

    return {"message": "\n".join(lines)}


# ──────────────────────────────────────────────
#  QUIZ COMMANDS
# ──────────────────────────────────────────────

def cmd_quiz(topic: str = None):
    """Start a quick quiz (1 question)."""
    state = init_state()
    state = check_daily_reset(state)
    save_state(state)

    player = state["player"]
    if player["stamina"] < 1:
        return {"error": "⚡ Not enough stamina! You need at least 1⚡ to do a quiz."}

    if topic and topic not in QUIZ_BANK:
        return {"error": f"Unknown topic: {topic}. Topics: {', '.join(QUIZ_BANK.keys())}"}

    q = get_random_quiz_question(state, topic)
    if not q:
        return {"error": "No questions available right now. Try again later!"}

    # Save current question for answer checking
    state["quiz_state"]["_current_question"] = q["id"]
    save_state(state)

    return {
        "question": q,
        "question_formatted": format_quiz_question(q),
        "stamina": player["stamina"],
        "unlocked_topics": list(QUIZ_BANK.keys()),
    }


def cmd_quiz_answer(question_id: str, user_answer: str):
    """Check an answer to the current quiz question."""
    state = load_state()
    result = check_quiz_answer(state, question_id, user_answer)
    result["skill_profile"] = get_skill_profile(state)
    return result


def cmd_quiz_boss(topic: str = None):
    """Start a quiz boss fight (10 questions, costs 5 stamina)."""
    state = init_state()
    state = check_daily_reset(state)
    save_state(state)

    if topic and topic not in QUIZ_BANK:
        return {"error": f"Unknown topic: {topic}. Topics: {', '.join(QUIZ_BANK.keys())}"}

    result = start_quiz_boss(state, topic)
    return result


def cmd_quiz_boss_hit(question_id: str, user_answer: str):
    """Answer a quiz boss question."""
    state = load_state()
    return process_quiz_boss_hit(state, question_id, user_answer)


def cmd_quiz_stats():
    """Show quiz-specific stats."""
    state = load_state()
    qs = state.get("quiz_state", {})
    player = state["player"]

    total_q = qs.get("questions_answered", 0)
    correct = qs.get("correct_answers", 0)
    streak = qs.get("quiz_streak", 0)
    bosses_def = qs.get("quiz_bosses_defeated", 0)
    bosses_att = qs.get("quiz_boss_attempts", 0)

    accuracy = f"{int(correct / total_q * 100)}%" if total_q > 0 else "—"

    lines = [
        "📊 QUIZ STATS",
        "━" * 32,
        f"  Questions answered: {total_q}",
        f"  Correct answers:   {correct}",
        f"  Accuracy:          {accuracy}",
        f"  Current streak:    {streak}",
        f"  Quiz bosses:      {bosses_def} defeated / {bosses_att} attempts",
        "",
        f"⚡ Stamina: {player['stamina']}/{player['max_stamina']}",
    ]

    return {"message": "\n".join(lines), "stats": {
        "total_q": total_q,
        "correct": correct,
        "accuracy": accuracy,
        "streak": streak,
        "bosses_defeated": bosses_def,
        "bosses_attempts": bosses_att,
    }}


# ──────────────────────────────────────────────
#  VOCAB COMMANDS
# ──────────────────────────────────────────────

def cmd_vocab_start(topic: str = None):
    """Start a new vocab session (10 cards, costs 1 stamina)."""
    state = init_state()
    state = check_daily_reset(state)
    state = check_vocab_daily_reset(state)
    save_state(state)

    result = start_vocab_session(state, topic)
    return result


def cmd_vocab():
    """Get the current vocab card (without revealing)."""
    state = load_state()
    vs = state.get("vocab_state", {})
    session = vs.get("active_vocab_session")

    if not session:
        return {"error": "No active vocab session. Start one with 'vocab_start' or 'vocab'."}

    card = get_current_vocab_card(state)
    if not card:
        return {"error": "Session ended. Start a new one with 'vocab'."}

    mastery_emoji = ["🆕", "🔄", "✅", "⭐"][card.get("_mastery_level", 0)]

    # Show just the word (like a flashcard face)
    msg = f"""📚 VOCAB CARD
━━━━━━━━━━━━━━━━━━
{mastery_emoji} {card['word']} ({card.get('part_of_speech', '')})
CEFR: {card.get('cefr', 'A1')}

💡 Type 'vocab_reveal' to see the definition!"""

    return {
        "feedback": msg,
        "card": card,
        "card_number": session["current_index"] + 1,
        "total_cards": len(session["cards"]),
    }


def cmd_vocab_reveal():
    """Reveal the current card's definition."""
    state = load_state()
    state = check_vocab_daily_reset(state)
    result = reveal_vocab_card(state)
    return result


def cmd_vocab_rate(rating: str):
    """Rate the current card: again, hard, good, easy."""
    state = load_state()
    vs = state.get("vocab_state", {})
    session = vs.get("active_vocab_session")

    if not session:
        return {"error": "No active vocab session. Start one with 'vocab'."}

    # Get current card id
    if session["current_index"] >= len(session["cards"]):
        return {"error": "Session ended. Start a new one with 'vocab'."}

    card_id = session["cards"][session["current_index"]]

    if session.get("is_boss"):
        result = process_vocab_boss_rating(state, card_id, rating)
        result["stamina"] = state["player"]["stamina"]
        result["xp"] = state["player"]["xp"]
        return result
    else:
        result = rate_vocab_card(state, card_id, rating)
        result["stamina"] = state["player"]["stamina"]
        result["xp"] = state["player"]["xp"]
        return result


def cmd_vocab_stats():
    """Show vocab-specific stats."""
    state = load_state()
    vs = state.get("vocab_state", {})
    mastery = vs.get("word_mastery", {})
    player = state["player"]

    cards_reviewed = vs.get("cards_reviewed", 0)
    correct = vs.get("correct_recalls", 0)
    streak = vs.get("vocab_streak", 0)
    sessions = vs.get("vocab_sessions", 0)
    mastered = sum(1 for w in mastery.values() if w.get("level", 0) >= 3)
    learning = sum(1 for w in mastery.values() if w.get("level", 0) in (1, 2))
    new_words = sum(1 for w in mastery.values() if w.get("level", 0) == 0)

    accuracy = f"{int(correct / cards_reviewed * 100)}%" if cards_reviewed > 0 else "—"

    lines = [
        "📚 VOCAB STATS",
        "━" * 32,
        f"  Sessions completed: {sessions}",
        f"  Cards reviewed:    {cards_reviewed}",
        f"  Correct recalls:   {correct}",
        f"  Accuracy:          {accuracy}",
        f"  Current streak:    {streak} days",
        "",
        f"  📖 Mastered (⭐):  {mastered}",
        f"  🔄 Learning:       {learning}",
        f"  🆕 New words:      {new_words}",
        "",
        f"⚡ Stamina: {player['stamina']}/{player['max_stamina']}",
    ]

    return {"message": "\n".join(lines), "stats": {
        "sessions": sessions,
        "cards_reviewed": cards_reviewed,
        "correct": correct,
        "accuracy": accuracy,
        "streak": streak,
        "mastered": mastered,
        "learning": learning,
        "new_words": new_words,
    }}


def cmd_vocab_boss(topic: str = None):
    """Start a vocab boss fight (10 cards, costs 5 stamina)."""
    state = init_state()
    state = check_daily_reset(state)
    state = check_vocab_daily_reset(state)
    save_state(state)

    result = start_vocab_boss(state, topic)
    return result


def cmd_vocab_search(query: str):
    """Search the vocab bank for a word."""
    if not query.strip():
        return {"error": "Usage: vocab_search <word>"}

    results = search_vocab_bank(query)
    if not results:
        return {"error": f"No words found matching '{query}'."}

    lines = [f"🔍 VOCAB SEARCH: '{query}'\n{'━' * 32}"]
    for card in results[:10]:
        mastery_emoji = ["🆕", "🔄", "✅", "⭐"][card.get("_mastery_level", 0)]
        lines.append(f"{mastery_emoji} {card['word']} — {card.get('definition', '')}")
        lines.append(f"   🇮🇩 {card.get('indonesian', '')}  |  [{card.get('cefr', 'A1')}]")
        lines.append("")

    return {"message": "\n".join(lines), "results": results[:10]}


# ──────────────────────────────────────────────
#  MAIN DISPATCH
# ──────────────────────────────────────────────

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "card"
    args = sys.argv[2:]

    out = None
    if cmd == "start":
        out = cmd_start()
    elif cmd == "sentence":
        out = cmd_sentence(args[0] if args else "greetings")
    elif cmd == "compare":
        out = cmd_compare(args[0], args[1], args[2] if len(args) > 2 else "greetings")
    elif cmd == "boss_start":
        out = cmd_boss_start()
    elif cmd == "boss_hit":
        out = cmd_boss_hit(args[0], args[1])
    elif cmd == "shop":
        out = cmd_shop()
    elif cmd == "buy":
        out = cmd_buy(args[0] if args else "")
    elif cmd == "card":
        out = cmd_card()
    elif cmd == "quests":
        out = cmd_quests()
    elif cmd == "quiz":
        # quiz [topic]
        topic = args[0] if args else None
        out = cmd_quiz(topic)
    elif cmd == "quiz_answer":
        # quiz_answer <question_id> <user_answer>
        if len(args) < 2:
            out = {"error": "Usage: quiz_answer <question_id> <answer>"}
        else:
            out = cmd_quiz_answer(args[0], args[1])
    elif cmd == "quiz_boss":
        # quiz_boss [topic]
        topic = args[0] if args else None
        out = cmd_quiz_boss(topic)
    elif cmd == "quiz_boss_hit":
        # quiz_boss_hit <question_id> <user_answer>
        if len(args) < 2:
            out = {"error": "Usage: quiz_boss_hit <question_id> <answer>"}
        else:
            out = cmd_quiz_boss_hit(args[0], args[1])
    elif cmd == "quiz_stats":
        out = cmd_quiz_stats()
    elif cmd == "vocab":
        # vocab or vocab [topic]
        topic = args[0] if args else None
        out = cmd_vocab_start(topic) if not args else cmd_vocab()
    elif cmd == "vocab_start":
        topic = args[0] if args else None
        out = cmd_vocab_start(topic)
    elif cmd == "vocab_reveal":
        out = cmd_vocab_reveal()
    elif cmd == "vocab_rate":
        if not args:
            out = {"error": "Usage: vocab_rate <again|hard|good|easy>"}
        else:
            out = cmd_vocab_rate(args[0])
    elif cmd == "vocab_stats":
        out = cmd_vocab_stats()
    elif cmd == "vocab_boss":
        topic = args[0] if args else None
        out = cmd_vocab_boss(topic)
    elif cmd == "vocab_search":
        if not args:
            out = {"error": "Usage: vocab_search <word>"}
        else:
            out = cmd_vocab_search(" ".join(args))
    elif cmd == "skills":
        out = cmd_skills()
    else:
        out = {"error": f"Unknown command: {cmd}"}

    print(json.dumps(out, indent=2, ensure_ascii=False))
