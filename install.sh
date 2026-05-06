#!/bin/bash
#===============================================
# English Shadowing RPG — One-Click Installer
#===============================================
# Usage: bash install.sh [hermes_profile_dir]
#
# Default profile dir: ~/.hermes/profiles/elias-strategist
# Example: bash install.sh ~/.hermes/profiles/my-profile
#===============================================

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory (resolve symlinks)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Determine Hermes base directory
if [ -n "$1" ]; then
    HERMES_BASE="$1"
else
    HERMES_BASE="${HOME}/.hermes/profiles/elias-strategist"
fi

HERMES_BASE="$(realpath -m "$HERMES_BASE")"

echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}  English Shadowing RPG — Installer${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "Hermes profile: ${GREEN}$HERMES_BASE${NC}"

# Check Hermes directory exists
if [ ! -d "$HERMES_BASE" ]; then
    echo -e "${RED}✗ Error: Hermes profile directory not found!${NC}"
    echo -e "  $HERMES_BASE"
    echo ""
    echo -e "${YELLOW}Please run the Hermes agent first to create your profile.${NC}"
    exit 1
fi

SKILLS_DIR="$HERMES_BASE/skills"
RPG_DIR="$HERMES_BASE/rpg"

# Create directories
echo ""
echo -e "${YELLOW}→ Creating directories...${NC}"
mkdir -p "$SKILLS_DIR"
mkdir -p "$RPG_DIR"

# Install skill
echo ""
echo -e "${YELLOW}→ Installing skill...${NC}"
cp "$SCRIPT_DIR/SKILL.md" "$SKILLS_DIR/english-quest.md"
echo -e "  ${GREEN}✓${NC} Copied SKILL.md → $SKILLS_DIR/english-quest.md"

# Install RPG files
echo ""
echo -e "${YELLOW}→ Installing RPG engine...${NC}"
cp "$SCRIPT_DIR/src/"*.py "$RPG_DIR/"
cp "$SCRIPT_DIR/src/"*.json "$RPG_DIR/" 2>/dev/null || true
echo -e "  ${GREEN}✓${NC} Copied engine files → $RPG_DIR/"

# Initialize state file if not exists
if [ ! -f "$RPG_DIR/shadowing_rpg.json" ]; then
    echo ""
    echo -e "${YELLOW}→ Initializing player state...${NC}"
    cat > "$RPG_DIR/shadowing_rpg.json" << 'EOF'
{
  "player": {
    "name": "Adventurer",
    "level": 1,
    "xp": 0,
    "xp_for_current_level": 0,
    "hp": 100,
    "max_hp": 100,
    "stamina": 20,
    "max_stamina": 20,
    "gold": 0,
    "streak": 0,
    "last_practice_date": "",
    "total_sentences_practiced": 0,
    "total_words_practiced": 0,
    "total_errors": 0,
    "perfect_sessions": 0,
    "created_at": ""
  },
  "unlocked_skills": ["greetings", "numbers", "time"],
  "skill_progress": {},
  "quests": {
    "daily": {
      "first_steps": false,
      "warm_up": 0,
      "practice_makes_perfect": 0,
      "streak_defender": false,
      "perfect_round": 0,
      "speed_demon": false,
      "last_reset": ""
    },
    "weekly_boss": {
      "defeated": false,
      "attempts": 0,
      "boss_name": "The Article Archon",
      "boss_hp": 100,
      "last_boss_date": ""
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
EOF
    echo -e "  ${GREEN}✓${NC} Created shadowing_rpg.json"
else
    echo -e "  ${YELLOW}→${NC} shadowing_rpg.json already exists, skipping"
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  ✅ Installation complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "To start practicing, say: ${YELLOW}shadowing${NC} or ${YELLOW}start rpg${NC}"
echo ""
echo -e "Available commands:"
echo -e "  • ${YELLOW}shadowing${NC} / ${YELLOW}start rpg${NC} — Begin session"
echo -e "  • ${YELLOW}boss${NC} — Weekly boss fight"
echo -e "  • ${YELLOW}stats${NC} / ${YELLOW}profile${NC} — View your card"
echo -e "  • ${YELLOW}quests${NC} — Daily quests"
echo -e "  • ${YELLOW}shop${NC} — Browse rewards"
echo -e "  • ${YELLOW}quiz${NC} — Grammar quiz"
echo ""
