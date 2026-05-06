#!/bin/bash
#===============================================
# English Shadowing RPG — Uninstaller
#===============================================
# Usage: bash uninstall.sh [hermes_profile_dir]
#
# This removes the skill and RPG files.
# User progress data (shadowing_rpg.json) is preserved by default.
# Add --delete-data to also remove user progress.
#===============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DELETE_DATA=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --delete-data)
            DELETE_DATA=true
            shift
            ;;
        *)
            HERMES_BASE="$1"
            shift
            ;;
    esac
done

if [ -z "$HERMES_BASE" ]; then
    HERMES_BASE="${HOME}/.hermes/profiles/elias-strategist"
fi

HERMES_BASE="$(realpath -m "$HERMES_BASE")"

echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}  English Shadowing RPG — Uninstaller${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Remove skill
if [ -f "$HERMES_BASE/skills/english-quest.md" ]; then
    rm "$HERMES_BASE/skills/english-quest.md"
    echo -e "${GREEN}✓${NC} Removed skill: $HERMES_BASE/skills/english-quest.md"
fi

# Remove RPG files (keep data)
echo ""
echo -e "${YELLOW}→ Removing RPG files...${NC}"
rm -f "$HERMES_BASE/rpg/engine.py" 2>/dev/null && echo -e "  ${GREEN}✓${NC} Removed engine.py"
rm -f "$HERMES_BASE/rpg/session.py" 2>/dev/null && echo -e "  ${GREEN}✓${NC} Removed session.py"
rm -f "$HERMES_BASE/rpg/quiz_bank.json" 2>/dev/null && echo -e "  ${GREEN}✓${NC} Removed quiz_bank.json"
rm -f "$HERMES_BASE/rpg/config.py" 2>/dev/null && echo -e "  ${GREEN}✓${NC} Removed config.py"

if [ "$DELETE_DATA" = true ]; then
    echo ""
    echo -e "${RED}⚠️  Deleting user progress data...${NC}"
    rm -f "$HERMES_BASE/rpg/shadowing_rpg.json" && echo -e "  ${GREEN}✓${NC} Removed shadowing_rpg.json"
else
    echo ""
    echo -e "${YELLOW}→ User progress preserved (shadowing_rpg.json)${NC}"
    echo -e "  Run with ${YELLOW}--delete-data${NC} to remove it too."
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  ✅ Uninstallation complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
