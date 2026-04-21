#!/usr/bin/env bash
# ESF Companion Installer
# Installs the ESF Companion into your current directory.
#
# Usage (run from your project directory):
#   curl -fsSL https://raw.githubusercontent.com/nmadrid27/esf-companion/main/install.sh | bash
#
# Options:
#   --sample       Install pre-filled BUILD-level test data (Alex Rivera)
#   --force        Skip all interactive prompts (for scripted installs).
#                  Ambient mode is ON by default under --force; pair with
#                  --no-ambient to install in manual mode.
#   --no-ambient   Install without the always-on ambient CLAUDE.md block.
#                  Use /esf-project manually when you want ESF active.
#   --platform     Set platform without prompting
#                  Values: claude, conversation, chatgpt, gemini, codex, cowork
#   --source       Install from a local directory instead of the GitHub CDN.
#                  Pass an absolute path to a checkout of this repo. Used by
#                  the smoke test for pre-merge validation of local content.
#
# Examples:
#   curl -fsSL ... | bash -s -- --force --platform claude
#   curl -fsSL ... | bash -s -- --force --no-ambient --platform claude
#   curl -fsSL ... | bash -s -- --force --platform chatgpt
#   curl -fsSL ... | bash -s -- --force --platform gemini
#   curl -fsSL ... | bash -s -- --force --platform codex
#   curl -fsSL ... | bash -s -- --sample

set -e

SAMPLE=false
FORCE=false
AMBIENT=true
PLATFORM_FLAG=""
PLATFORM_NEXT=false
SOURCE_DIR=""
SOURCE_NEXT=false
for arg in "$@"; do
  if [ "$PLATFORM_NEXT" = true ]; then
    PLATFORM_FLAG="$arg"
    PLATFORM_NEXT=false
  elif [ "$SOURCE_NEXT" = true ]; then
    SOURCE_DIR="$arg"
    SOURCE_NEXT=false
  elif [ "$arg" = "--sample" ]; then
    SAMPLE=true
  elif [ "$arg" = "--force" ]; then
    FORCE=true
  elif [ "$arg" = "--no-ambient" ]; then
    AMBIENT=false
  elif [[ "$arg" == --platform=* ]]; then
    PLATFORM_FLAG="${arg#--platform=}"
  elif [ "$arg" = "--platform" ]; then
    PLATFORM_NEXT=true
  elif [[ "$arg" == --source=* ]]; then
    SOURCE_DIR="${arg#--source=}"
  elif [ "$arg" = "--source" ]; then
    SOURCE_NEXT=true
  fi
done

if [ -n "$SOURCE_DIR" ]; then
  if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: --source path does not exist: $SOURCE_DIR" >&2
    exit 1
  fi
  # curl supports file:// natively; reuse every existing fetch call unchanged.
  TOOLKIT_BASE="file://$(cd "$SOURCE_DIR" && pwd)"
else
  TOOLKIT_BASE="https://raw.githubusercontent.com/nmadrid27/esf-companion/main"
fi
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Download a file only if it does not already exist (preserves user customizations)
fetch_if_missing() {
  local url="$1"
  local dest="$2"
  if [ ! -f "$dest" ]; then
    curl -fsSL "$url" -o "$dest"
  fi
}

echo ""
echo -e "${CYAN}ESF Companion - Installer${NC}"
echo "──────────────────────────────────────"

# Warn if already installed
if [ -d ".claude/agents" ] && [ -f ".claude/agents/esf-companion.md" ]; then
  if [ "$FORCE" = true ]; then
    echo -e "${YELLOW}Force mode: skipping prompts. Existing customized files will be preserved.${NC}"
  else
    echo -e "${YELLOW}Warning: ESF Companion appears to already be installed.${NC}"
    read -r -p "Overwrite with the latest version? (y/N): " confirm </dev/tty
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
      echo "Installation cancelled."
      exit 0
    fi
  fi
fi

# Determine install directory
if [ "$FORCE" != true ]; then
  echo ""
  # Detect whether the current directory has substantive content
  # (anything beyond .git, .gitignore, or a lone .DS_Store)
  CURRENT_HAS_FILES=false
  if [ -n "$(ls -A 2>/dev/null | grep -vE '^(\.git|\.gitignore|\.DS_Store)$')" ]; then
    CURRENT_HAS_FILES=true
  fi

  if [ "$CURRENT_HAS_FILES" = true ]; then
    echo "Your current folder already has files:"
    echo "  $(pwd)"
    echo ""
    echo "  1) Install here (add ESF files alongside existing work)"
    echo "  2) Create a new folder"
    echo ""
    read -r -p "Choose [1/2]: " DIR_CHOICE </dev/tty
    [ -z "$DIR_CHOICE" ] && DIR_CHOICE="1"
  else
    echo "Where should ESF Companion be installed?"
    echo ""
    echo "  1) Current folder: $(pwd)"
    echo "  2) Create a new folder  [default: esf-companion]"
    echo ""
    read -r -p "Choose [1/2] (default: 2): " DIR_CHOICE </dev/tty
    [ -z "$DIR_CHOICE" ] && DIR_CHOICE="2"
  fi

  if [ "$DIR_CHOICE" = "2" ]; then
    echo ""
    read -r -p "Folder name [esf-companion]: " NEW_FOLDER </dev/tty
    [ -z "$NEW_FOLDER" ] && NEW_FOLDER="esf-companion"
    # Sanitize: lowercase, hyphens, alphanumeric only
    NEW_FOLDER=$(echo "$NEW_FOLDER" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-')
    if [ -z "$NEW_FOLDER" ]; then
      NEW_FOLDER="esf-companion"
    fi
    if [ -d "$NEW_FOLDER" ] && [ -n "$(ls -A "$NEW_FOLDER" 2>/dev/null)" ]; then
      echo -e "${YELLOW}Warning: '$NEW_FOLDER' already exists and is not empty.${NC}"
      read -r -p "Install into it anyway? (y/N): " CONFIRM_DIR </dev/tty
      if [[ ! "$CONFIRM_DIR" =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
      fi
    fi
    mkdir -p "$NEW_FOLDER"
    cd "$NEW_FOLDER"
    echo -e "  ${GREEN}Installing into: $(pwd)${NC}"
  else
    echo -e "  ${GREEN}Installing into current folder: $(pwd)${NC}"
  fi
fi

# Check for git repo
if [ ! -d ".git" ]; then
  if [ "$FORCE" = true ]; then
    echo -e "${YELLOW}Force mode: installing without git repo.${NC}"
  else
    echo -e "${YELLOW}Warning: This directory is not a git repository.${NC}"
    echo "The Companion works best inside a git repo (your project directory)."
    echo ""
    echo "Options:"
    echo "  1) Run the setup script (creates a repo for you)"
    echo "  2) Install here anyway (no git)"
    echo "  3) Cancel"
    read -r -p "Choose [1/2/3]: " GIT_CHOICE </dev/tty
    case "$GIT_CHOICE" in
      1)
        SETUP_URL="https://raw.githubusercontent.com/nmadrid27/esf-companion/main/setup-repo.sh"
        echo "Downloading setup script..."
        curl -fsSL "$SETUP_URL" -o /tmp/esf-setup-repo.sh
        echo "Running setup script..."
        bash /tmp/esf-setup-repo.sh </dev/tty
        rm -f /tmp/esf-setup-repo.sh
        exit $?
        ;;
      2)
        echo "Continuing without git..."
        ;;
      *)
        echo "Installation cancelled."
        exit 0
        ;;
    esac
  fi
fi

# Determine platform
PLATFORM="claude"
if [ -n "$PLATFORM_FLAG" ]; then
  case "$PLATFORM_FLAG" in
    claude|conversation|chatgpt|gemini|codex|cowork)
      PLATFORM="$PLATFORM_FLAG"
      echo "Platform: $PLATFORM (set via --platform flag)"
      ;;
    *)
      echo -e "${RED}Error: --platform must be one of: claude, conversation, chatgpt, gemini, codex, cowork. Got: '$PLATFORM_FLAG'${NC}"
      exit 1
      ;;
  esac
elif [ "$FORCE" != true ]; then
  echo ""
  echo "What AI tool will you use with ESF Companion?"
  echo ""
  echo "  1) Claude Code (full experience: agent, skills, drift detection)"
  echo "  2) Claude.ai (conversation or Projects)"
  echo "  3) ChatGPT"
  echo "  4) Gemini"
  echo "  5) Codex CLI"
  echo "  6) Cowork (Claude desktop app)"
  echo "  7) Not sure yet"
  echo ""
  read -r -p "Choose [1-7]: " PLATFORM_CHOICE </dev/tty
  case "$PLATFORM_CHOICE" in
    2)
      PLATFORM="conversation"
      ;;
    3)
      PLATFORM="chatgpt"
      ;;
    4)
      PLATFORM="gemini"
      ;;
    5)
      PLATFORM="codex"
      ;;
    6)
      PLATFORM="cowork"
      ;;
    7)
      PLATFORM="conversation"
      ;;
    *)
      PLATFORM="claude"
      ;;
  esac
fi

echo "Installing..."

# Cowork: download the .plugin file — no project-directory install needed
if [ "$PLATFORM" = "cowork" ]; then
  PLUGIN_URL="https://github.com/nmadrid27/esf-companion/releases/latest/download/esf-companion.plugin"
  PLUGIN_DEST="esf-companion.plugin"

  echo "  Downloading ESF Companion plugin for Cowork..."
  if curl -fsSL "$PLUGIN_URL" -o "$PLUGIN_DEST"; then
    echo ""
    echo -e "${GREEN}ESF Companion plugin downloaded.${NC}"
    echo -e "${YELLOW}Note: the plugin is versioned and released separately from this installer."
    echo -e "If the plugin feels out of date, check for a newer release at:${NC}"
    echo "  https://github.com/nmadrid27/esf-companion/releases"
    echo ""
    echo "──────────────────────────────────────"
    echo -e "${CYAN}Next steps:${NC}"
    echo ""
    echo "  1. Open Cowork (Claude desktop app)."
    echo ""
    echo "  2. Open the plugin file:"
    echo "     $(pwd)/$PLUGIN_DEST"
    echo ""
    echo "  3. Cowork will show a plugin preview. Click 'Install' to accept."
    echo ""
    echo "  4. Open the folder where you want to work (your project folder)."
    echo ""
    echo "  5. Run /esf-start to initialize your workspace."
    echo ""
    echo "  The plugin reads companion-state.md from your selected folder"
    echo "  and carries state across sessions."
    echo ""
    echo "──────────────────────────────────────"
    echo -e "${CYAN}Want ESF to activate automatically every session?${NC}"
    echo ""
    echo "  Set up a Claude.ai Project:"
    echo ""
    echo "  1. Go to claude.ai and create a new Project."
    echo ""
    echo "  2. In Project Settings, paste the contents of:"
    echo "     prompts/esf-companion.md"
    echo "     into the system prompt field."
    echo ""
    echo "  3. Upload companion-state.md as a Project knowledge file."
    echo ""
    echo "  ESF will activate automatically at the start of every conversation"
    echo "  in that Project, with your identity and context already loaded."
    echo "──────────────────────────────────────"
    echo ""
  else
    echo ""
    echo -e "${RED}Plugin download failed.${NC}"
    echo ""
    echo "The plugin is released separately from the installer and may not"
    echo "be published yet, or you may be offline."
    echo ""
    echo "Download it manually when available:"
    echo "  https://github.com/nmadrid27/esf-companion/releases"
    echo ""
    echo "In the meantime, you can use the conversation platform path instead:"
    echo "  Re-run and choose option 2 (Claude.ai) for a full-featured experience"
    echo "  without installing a plugin."
    echo ""
  fi
  exit 0
fi

# Conversation-mode platforms: claude.ai, chatgpt, gemini, codex, or generic conversation
if [ "$PLATFORM" != "claude" ]; then
  # Warn if --sample was passed (sample data requires Claude Code)
  if [ "$SAMPLE" = true ]; then
    echo -e "${YELLOW}Note: --sample requires Claude Code. Sample data not installed for this platform.${NC}"
  fi

  # Base lightweight install (shared by all non-Claude-Code platforms)
  mkdir -p prompts
  mkdir -p templates

  echo "  Fetching companion prompts..."
  fetch_if_missing "$TOOLKIT_BASE/prompts/companion.md" prompts/companion.md
  fetch_if_missing "$TOOLKIT_BASE/prompts/esf-companion.md" prompts/esf-companion.md
  fetch_if_missing "$TOOLKIT_BASE/prompts/project-workflow.md" prompts/project-workflow.md
  fetch_if_missing "$TOOLKIT_BASE/prompts/quick-start.md" prompts/quick-start.md
  fetch_if_missing "$TOOLKIT_BASE/prompts/README.md" prompts/README.md

  echo "  Fetching templates..."
  fetch_if_missing "$TOOLKIT_BASE/templates/position-statement-template.md" templates/position-statement-template.md
  fetch_if_missing "$TOOLKIT_BASE/templates/position-statement.md" templates/position-statement.md
  fetch_if_missing "$TOOLKIT_BASE/templates/record-of-resistance-template.md" templates/record-of-resistance-template.md
  fetch_if_missing "$TOOLKIT_BASE/templates/record-of-resistance.md" templates/record-of-resistance.md
  fetch_if_missing "$TOOLKIT_BASE/templates/ai-use-log-template.md" templates/ai-use-log-template.md
  fetch_if_missing "$TOOLKIT_BASE/templates/ai-use-log.md" templates/ai-use-log.md
  fetch_if_missing "$TOOLKIT_BASE/templates/companion-state-template.md" templates/companion-state-template.md
  fetch_if_missing "$TOOLKIT_BASE/templates/companion-notes-template.md" templates/companion-notes-template.md
  fetch_if_missing "$TOOLKIT_BASE/templates/five-questions-checklist.md" templates/five-questions-checklist.md
  fetch_if_missing "$TOOLKIT_BASE/templates/disclosure-statement.md" templates/disclosure-statement.md
  fetch_if_missing "$TOOLKIT_BASE/templates/session-log-template.md" templates/session-log-template.md
  fetch_if_missing "$TOOLKIT_BASE/templates/reflection-template.md" templates/reflection-template.md
  fetch_if_missing "$TOOLKIT_BASE/templates/project-plan.md" templates/project-plan.md
  fetch_if_missing "$TOOLKIT_BASE/templates/project-scope-template.md" templates/project-scope-template.md
  fetch_if_missing "$TOOLKIT_BASE/templates/evolution-log-template.md" templates/evolution-log-template.md

  if [ ! -f "WORKFLOW.md" ]; then
    curl -fsSL "$TOOLKIT_BASE/WORKFLOW.md" -o WORKFLOW.md
  fi
  fetch_if_missing "$TOOLKIT_BASE/START_HERE.md" START_HERE.md

  # Platform-specific config file
  case "$PLATFORM" in
    chatgpt)
      echo "  Fetching ChatGPT custom instructions..."
      fetch_if_missing "$TOOLKIT_BASE/chatgpt-instructions.md" chatgpt-instructions.md
      ;;
    gemini)
      echo "  Fetching Gemini system prompt..."
      fetch_if_missing "$TOOLKIT_BASE/GEMINI.md" GEMINI.md
      ;;
    codex)
      echo "  Fetching Codex CLI agent config..."
      mkdir -p .codex
      fetch_if_missing "$TOOLKIT_BASE/.codex/AGENTS.md" .codex/AGENTS.md
      ;;
  esac

  # Auto-commit if in a git repo
  if [ -d ".git" ]; then
    git add prompts/ templates/ WORKFLOW.md START_HERE.md 2>/dev/null
    [ -f .gitignore ] && git add .gitignore 2>/dev/null
    [ -f chatgpt-instructions.md ] && git add chatgpt-instructions.md 2>/dev/null
    [ -f GEMINI.md ] && git add GEMINI.md 2>/dev/null
    [ -d .codex ] && git add .codex/ 2>/dev/null
    git commit -m "Install ESF Companion ($PLATFORM)" --quiet 2>/dev/null && \
      echo -e "  ${GREEN}Companion files committed to git.${NC}" || true
  fi

  echo ""
  echo -e "${GREEN}ESF Companion installed.${NC}"
  echo ""
  echo "──────────────────────────────────────"
  echo -e "${CYAN}Next steps:${NC}"
  echo ""

  case "$PLATFORM" in
    chatgpt)
      echo "  1. Open chatgpt-instructions.md."
      echo "     Copy Section 1 into ChatGPT Settings > Personalization >"
      echo "     Custom Instructions > 'What to know about you'."
      echo "     Copy Section 2 into 'How to respond'."
      echo ""
      echo "  2. (Optional) Use ChatGPT Projects for persistent context:"
      echo "     Create a project and upload companion-state.md as a project file."
      echo "     Context loads automatically each session."
      echo ""
      echo "  3. Start a conversation and paste your Position Statement to begin."
      echo "     The Companion will guide you through the ESF workflow."
      ;;
    gemini)
      echo "  1. Open GEMINI.md."
      echo "     Paste everything below the '---' line as your first message"
      echo "     in a new Gemini conversation."
      echo ""
      echo "  2. After the system prompt, say what you are working on."
      echo "     The Companion will check for your Position Statement and guide"
      echo "     you through the ESF workflow."
      echo ""
      echo "  3. At session end, ask the Companion to generate a PROJECT.md block."
      echo "     Save it and paste it at the start of your next conversation."
      ;;
    codex)
      echo "  1. .codex/AGENTS.md is now in your project directory."
      echo "     Codex CLI reads it automatically when you open a session."
      echo ""
      echo "  2. Run onboarding in your first session:"
      echo "     Tell the Companion: 'Run ESF onboarding. Here are my details: [your context]'"
      echo ""
      echo "  3. The Companion will create projects/_esf/companion-state.md"
      echo "     and guide you through the ESF workflow from there."
      ;;
    *)
      # Claude.ai or generic conversation
      echo "  1. Open prompts/quick-start.md, fill in the four fields at the top,"
      echo "     and paste the whole document as your first message."
      echo ""
      echo "  Or set up custom instructions for your tool:"
      echo "     Claude.ai:  Settings > Custom Instructions (or use a Project)"
      echo "     ChatGPT:    Settings > Personalization > Custom Instructions"
      echo "     Gemini:     Paste GEMINI.md at the start of your conversation"
      echo ""
      echo "  Claude.ai Projects (recommended for returning users):"
      echo "     Create a project, upload companion-state.md and your brief"
      echo "     as knowledge files, set prompts/esf-companion.md as the"
      echo "     system prompt. Context loads automatically every session."
      ;;
  esac

  echo ""
  echo "  Templates are in the templates/ folder."
  echo "  The visual process diagram is in WORKFLOW.md."
  echo ""
  echo "  For a quick overview, read START_HERE.md"
  echo ""
  echo "  Want the full Claude Code experience later? Re-run and choose option 1."
  echo "──────────────────────────────────────"
  echo ""
  exit 0
fi

# Full Claude Code install

# Ambient mode prompt
if [ "$FORCE" != true ]; then
  echo ""
  echo "──────────────────────────────────────"
  echo -e "${CYAN}How ESF Companion works${NC}"
  echo ""
  echo "  ESF Companion protects your intellectual ownership of AI-assisted work."
  echo "  It does this through four moments in every session:"
  echo ""
  echo "    Direction check    Before drafting anything substantive, asks what"
  echo "                       you are making so AI builds from your intent."
  echo ""
  echo "    Drift detection    Surfaces when your work has moved away from"
  echo "                       your stated direction across two or more exchanges."
  echo ""
  echo "    Rejection capture  When you push back on an AI suggestion, offers"
  echo "                       to log it as a Record of Resistance."
  echo ""
  echo "    Ownership check    Before you finalize anything, asks about specific"
  echo "                       choices so you can speak to them confidently."
  echo ""
  echo "  These moments can run automatically or on demand:"
  echo ""
  echo "    Ambient  ESF activates at the start of every Claude Code session."
  echo "             Recommended. You can turn it off later."
  echo ""
  echo "    Manual   You run /esf-project when you want ESF active."
  echo "             Better if you only want ESF for specific projects."
  echo ""
  echo "──────────────────────────────────────"
  read -r -p "Run ESF automatically every session? [Y/n]: " AMBIENT_CHOICE </dev/tty
  if [[ "$AMBIENT_CHOICE" =~ ^[Nn]$ ]]; then
    AMBIENT=false
  else
    AMBIENT=true
  fi
fi

# Create directory structure
mkdir -p .claude/agents
mkdir -p .claude/skills/esf-onboarding
mkdir -p .claude/skills/esf-project
mkdir -p .claude/reference
mkdir -p prompts
mkdir -p templates

# Download the static agent. User-specific state now lives in projects/_esf/.
echo "  Fetching agents..."
curl -fsSL "$TOOLKIT_BASE/.claude/agents/esf-companion.md" -o .claude/agents/esf-companion.md

# Download skills
echo "  Fetching skills..."
curl -fsSL "$TOOLKIT_BASE/.claude/skills/esf-onboarding/SKILL.md" -o .claude/skills/esf-onboarding/SKILL.md
curl -fsSL "$TOOLKIT_BASE/.claude/skills/esf-project/SKILL.md"    -o .claude/skills/esf-project/SKILL.md
mkdir -p .claude/skills/esf-git .claude/skills/esf-verify .claude/skills/esf-update .claude/skills/esf-cognitive
curl -fsSL "$TOOLKIT_BASE/.claude/skills/esf-git/SKILL.md"        -o .claude/skills/esf-git/SKILL.md
curl -fsSL "$TOOLKIT_BASE/.claude/skills/esf-verify/SKILL.md"     -o .claude/skills/esf-verify/SKILL.md
curl -fsSL "$TOOLKIT_BASE/.claude/skills/esf-update/SKILL.md"     -o .claude/skills/esf-update/SKILL.md
curl -fsSL "$TOOLKIT_BASE/.claude/skills/esf-cognitive/SKILL.md"  -o .claude/skills/esf-cognitive/SKILL.md

# Download version file
curl -fsSL "$TOOLKIT_BASE/.claude/esf-version" -o .claude/esf-version

# Download and register the session-status hook
echo "  Fetching hooks..."
mkdir -p .claude/hooks
curl -fsSL "$TOOLKIT_BASE/.claude/hooks/esf-session-status.sh" -o .claude/hooks/esf-session-status.sh
chmod +x .claude/hooks/esf-session-status.sh

# Wire the SessionStart hook into .claude/settings.json (project-level, committed to git).
# Uses Python so the merge is safe regardless of existing settings.json content.
python3 - << 'PY'
import json, sys
from pathlib import Path

p = Path('.claude/settings.json')
data = json.loads(p.read_text()) if p.exists() else {}

hooks = data.setdefault('hooks', {})
ss = hooks.setdefault('SessionStart', [])

cmd = 'bash .claude/hooks/esf-session-status.sh'
already = any(
    any(h.get('command', '') == cmd for h in g.get('hooks', []))
    for g in ss if isinstance(g, dict)
)
if not already:
    ss.append({'hooks': [{'type': 'command', 'command': cmd, 'timeout': 10}]})
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2) + '\n')
PY

# Download prompts
echo "  Fetching prompts..."
fetch_if_missing "$TOOLKIT_BASE/prompts/companion.md" prompts/companion.md
fetch_if_missing "$TOOLKIT_BASE/prompts/esf-companion.md" prompts/esf-companion.md
fetch_if_missing "$TOOLKIT_BASE/prompts/project-workflow.md" prompts/project-workflow.md
fetch_if_missing "$TOOLKIT_BASE/prompts/cowork.md" prompts/cowork.md
fetch_if_missing "$TOOLKIT_BASE/prompts/README.md" prompts/README.md

# Download templates
echo "  Fetching templates..."
fetch_if_missing "$TOOLKIT_BASE/templates/position-statement-template.md" templates/position-statement-template.md
fetch_if_missing "$TOOLKIT_BASE/templates/position-statement.md" templates/position-statement.md
fetch_if_missing "$TOOLKIT_BASE/templates/ai-use-log-template.md" templates/ai-use-log-template.md
fetch_if_missing "$TOOLKIT_BASE/templates/ai-use-log-lite-template.md" templates/ai-use-log-lite-template.md
fetch_if_missing "$TOOLKIT_BASE/templates/ai-use-log.md" templates/ai-use-log.md
fetch_if_missing "$TOOLKIT_BASE/templates/companion-state-template.md" templates/companion-state-template.md
fetch_if_missing "$TOOLKIT_BASE/templates/companion-notes-template.md" templates/companion-notes-template.md
fetch_if_missing "$TOOLKIT_BASE/templates/record-of-resistance-template.md" templates/record-of-resistance-template.md
fetch_if_missing "$TOOLKIT_BASE/templates/record-of-resistance.md" templates/record-of-resistance.md
fetch_if_missing "$TOOLKIT_BASE/templates/five-questions-checklist.md" templates/five-questions-checklist.md
fetch_if_missing "$TOOLKIT_BASE/templates/disclosure-statement.md" templates/disclosure-statement.md
fetch_if_missing "$TOOLKIT_BASE/templates/evolution-log-template.md" templates/evolution-log-template.md
fetch_if_missing "$TOOLKIT_BASE/templates/session-log-template.md" templates/session-log-template.md
fetch_if_missing "$TOOLKIT_BASE/templates/reflection-template.md" templates/reflection-template.md
fetch_if_missing "$TOOLKIT_BASE/templates/project-brief-template.md" templates/project-brief-template.md
fetch_if_missing "$TOOLKIT_BASE/templates/project-plan.md" templates/project-plan.md
fetch_if_missing "$TOOLKIT_BASE/templates/project-scope-template.md" templates/project-scope-template.md

# Download reference files
echo "  Fetching reference files..."
curl -fsSL "$TOOLKIT_BASE/.claude/reference/esf-guide.md"           -o .claude/reference/esf-guide.md
curl -fsSL "$TOOLKIT_BASE/.claude/reference/disclosure-protocol.md" -o .claude/reference/disclosure-protocol.md
curl -fsSL "$TOOLKIT_BASE/.claude/reference/evolution-protocol.md"  -o .claude/reference/evolution-protocol.md

# Download workflow diagram and onboarding guide (skip if already exists)
if [ ! -f "WORKFLOW.md" ]; then
  curl -fsSL "$TOOLKIT_BASE/WORKFLOW.md" -o WORKFLOW.md
fi
fetch_if_missing "$TOOLKIT_BASE/START_HERE.md" START_HERE.md

# Write ambient activation block to CLAUDE.md if requested
if [ "$AMBIENT" = true ]; then
  ESF_SECTION_MARKER="## ESF Companion (Always On)"
  if [ -f "CLAUDE.md" ] && grep -q "$ESF_SECTION_MARKER" CLAUDE.md 2>/dev/null; then
    echo -e "  ${YELLOW}ESF ambient block already present in CLAUDE.md — skipping.${NC}"
  else
    if [ ! -f "CLAUDE.md" ]; then
      echo "# CLAUDE.md" > CLAUDE.md
      echo "" >> CLAUDE.md
      echo "Project configuration for Claude Code." >> CLAUDE.md
      echo "" >> CLAUDE.md
    else
      echo "" >> CLAUDE.md
    fi
    cat >> CLAUDE.md << 'ESF_AMBIENT_EOF'
## ESF Companion (Always On)

ESF Companion behaviors apply to every Claude Code session in this directory. The full spec is at `.claude/agents/esf-companion.md`; read it for detailed insight-block wording, scaffolding-level behaviors, and edge cases. The session-critical behaviors summarized here must fire on every session.

### Session start

1. Resolve companion-state.md: check context/companion-state.md first, then projects/_esf/companion-state.md, then workspace root. If not found, tell the user to run /esf-onboarding and stop.
2. Read companion-notes.md (same location). Apply Active Corrections before any other behavior.
3. Extract current project, phase, and scaffolding level.
4. **Emit the activation status line before any other output:**
   `ESF Companion active. Project: [name or "not set"]. Context: [code or "none"]. Active corrections: [N]. Session buffer: [path or "will create on first decision"]. Last session log: [path or "none"].`
   If companion-state.md is missing or unreadable, surface the failure explicitly and stop. Never silently proceed.
5. If a current project is set, display the progress indicator.

### Session buffer (mandatory)

Path: `projects/[context]/logs/.session-buffer.md`. On the first Write, Edit, or Moment trigger of a session, if the file does not exist, create `projects/[context]/logs/` and write the buffer with a header block. Append a single line immediately (never batch, never narrate) for: any Moment firing, phase transition, Position Statement save/update, gate bypass, agency-drift signal, cognitive technique offer, ad hoc project logging, bulk-production trigger, content-weight-High classification, ready-status gate firing, brief creation via forcing function, or every 10 substantive exchanges (checkpoint).

### Four key moments

- **Direction (Moment 1) — two modes.**

  **Nudge mode (default).** When producing substantive content and no Position Statement exists for the work, prepend a one-line nudge to the response: `[ESF: no Position Statement for [doc] — note one?]`. PS lookup reads Current Project and Context from `companion-state.md`, then checks `[context base-path]/esf/position-statements/[project-slug].md`. If that file exists, no nudge. If Current Project is "not set," the ad-hoc project forcing function fires first; the nudge runs only after a project is logged.

  Fire once on the first Write or Edit to a document in a session. Re-fire on structural edits: changes to a claim's assertion, a first-person observation presented as evidence, an attributed quote, a specific datum, or the document's argument or frame. Formatting, phrasing, typo or citation tidying, wikilink repair, and frontmatter corrections do not trigger.

  Decline logic: max two nudges per document per session. First decline ("skip," "later," "no," or equivalent) silences the first-touch nudge for that doc. A structural edit re-fires once more with a contextual message: `[ESF: this edit changes [what] — still no Position Statement. Note one?]`. Second decline silences all nudges for that doc for the session. Nudge count is in-context only (no file write); it resets at session start.

  If the user responds with a PS: save to the Position Statement path for this context, confirm briefly ("Saved. I'll check the work against this as we go."), and continue.

  **Gate mode.** Any command producing more than one substantive artifact ("draft all," "generate the set," "write the N posts") triggers Moment 1 as a full pause-and-elicit gate, regardless of how much direction the user has already articulated. **Task-is-clear ≠ Position-Statement-exists:** the gate fires even when the deliverable is obvious from the first message.
- **Drift (Moment 2):** When work moves away from a stated Position Statement across two or more exchanges, surface the observation.
- **Rejection capture (Moment 3):** When the user pushes back, redirects scope, corrects framing, corrects the audience/context read, or signals "not that" in any form, offer to log a Record of Resistance. Bar is low on purpose: scope corrections and framing redirections count even when phrased calmly. Formatting cleanup and tool-use corrections do not trigger.
- **Ownership check (Moment 4):** When the user signals wrap-up, ask about specific choices before finalizing.

### Pre-draft and pre-ready gates

- **Content weight check:** before drafting or materially editing substantive first-person content, classify by weight. Material edits include: changing what a factual claim asserts, adding a first-person biographical assertion, revising a teaching observation presented as evidence. Formatting, punctuation, phrasing cleanup, and targeted factual corrections (e.g., fixing a product name or URL) do not trigger. High weight includes: first-person biographical claims, teaching observations presented as evidence, professional observations from the user's practice, specific factual claims (numbers, dates, attributed quotes, cited studies), and anything published under the user's name asserting personal authority. For High-weight content, stop and ask whether the claim is based on specific sources, the user's own observation with specifics, or plausible construction. Do not draft biographical content from inference; ask the user to state the path in their own words.
- **Ready-status transition gate:** before any deliverable moves from draft to ready (frontmatter change or user says "done," "ready to post," "submit," etc.) and contains specific factual claims, surface each claim with a verified-source / own-observation / plausible-inference question. Hold the status change on anything flagged as inference until verified or explicitly accepted as unverifiable with disclosure.

### Ad hoc project and brief forcing functions

- If Current Project is "not set" and substantial content is requested, pause and offer to log the project before producing anything.
- If a bulk command fires and no brief exists for the project, stop and run the four-question minimal-brief flow (project in one sentence, success criterion, audience, non-negotiable) before drafting. Save to `projects/[context]/briefs/[project-name]-brief.md`, then run Moment 1 against the brief.
- **Install hygiene.** All ESF artifacts for a context live in `[context base-path]/esf/` — `position-statements/`, `records-of-resistance/`, `ai-use-logs/`. Never scattered into project folders. Folders are created lazily: the first time an artifact is written, its parent folder is created if missing. Empty folders are not pre-created at install.

### Late initialization

If the first Write or Edit of a session arrives before the activation status line has been emitted, run session-start steps 1–4 now and emit the status line prefixed with `(late init on first content action)`. If state is missing or unreadable, surface the step-4 failure message and stop; do not produce content.

### Session end

Wrap-up offer fires on any of: 4+ substantive exchanges in Make or Reflect without a continuation signal; 12+ substantive exchanges in any phase; user says "done for today," "wrap up," "save this session," or equivalent. On user confirmation, generate the AI Use Log from buffer entries only (do not fabricate), write the session log to `projects/[context]/logs/session-[ISO-date].md` with a "Next Session" section, update companion-state.md, and append a final buffer entry.

Full spec with insight-block wording, scaffolding levels, drift detection details, gate mode, and boundaries: `.claude/agents/esf-companion.md`.
ESF_AMBIENT_EOF
    echo -e "  ${GREEN}ESF ambient mode written to CLAUDE.md.${NC}"
  fi
fi

# Ensure .session-buffer.md is gitignored (covers fresh and existing repos)
touch .gitignore
if ! grep -q '.session-buffer.md' .gitignore 2>/dev/null; then
  printf '\n# ESF session buffer (ephemeral, not versioned)\n.session-buffer.md\n' >> .gitignore
fi


# Install sample data if --sample flag was passed
if [ "$SAMPLE" = true ]; then
  echo "  Installing BUILD-level sample data (Alex Rivera)..."
  mkdir -p projects/_esf
  mkdir -p projects/build-course/briefs
  mkdir -p projects/build-course/position-statements
  mkdir -p projects/build-course/records-of-resistance
  mkdir -p projects/build-course/ai-use-logs
  mkdir -p projects/build-course/gate-records
  mkdir -p projects/build-course/reflections
  mkdir -p projects/build-course/logs
  mkdir -p projects/build-course/work
  curl -fsSL "$TOOLKIT_BASE/sample/projects/_esf/companion-state.md" \
    -o projects/_esf/companion-state.md
  curl -fsSL "$TOOLKIT_BASE/sample/projects/build-course/briefs/p2-responsive-system.md" \
    -o projects/build-course/briefs/p2-responsive-system.md
  curl -fsSL "$TOOLKIT_BASE/sample/projects/build-course/position-statements/responsive-system.md" \
    -o projects/build-course/position-statements/responsive-system.md
  curl -fsSL "$TOOLKIT_BASE/sample/projects/build-course/records-of-resistance/responsive-system-ror-01.md" \
    -o projects/build-course/records-of-resistance/responsive-system-ror-01.md
  curl -fsSL "$TOOLKIT_BASE/sample/projects/build-course/records-of-resistance/responsive-system-ror-02.md" \
    -o projects/build-course/records-of-resistance/responsive-system-ror-02.md
fi

# Auto-commit only Companion files if in a git repo (do not stage unrelated work)
if [ -d ".git" ]; then
  git add .claude/ prompts/ templates/ WORKFLOW.md START_HERE.md 2>/dev/null
  [ -f .gitignore ] && git add .gitignore 2>/dev/null
  [ -f CLAUDE.md ]  && git add CLAUDE.md 2>/dev/null
  [ -f .claude/settings.json ] && git add .claude/settings.json 2>/dev/null

  # Sample installs also create tracked demo project files.
  if [ "$SAMPLE" = true ] && [ -d "projects" ]; then
    git add projects/ 2>/dev/null
  fi

  # Check git identity before committing
  if git config user.name > /dev/null 2>&1 && git config user.email > /dev/null 2>&1; then
    git commit -m "Install ESF Companion" --quiet 2>/dev/null && \
      echo -e "  ${GREEN}Companion files committed to git.${NC}" || true
  else
    echo -e "  ${YELLOW}Note:${NC} Git identity not configured. Run:"
    echo "    git config --global user.name \"Your Name\""
    echo "    git config --global user.email \"you@example.com\""
    echo "  Then commit manually: git commit -m \"Install ESF Companion\""
  fi
fi

echo ""
echo -e "${GREEN}ESF Companion installed.${NC}"
echo ""
echo "  Installed to: $(pwd)"
echo ""
echo "──────────────────────────────────────"
echo -e "${CYAN}Next steps:${NC}"
echo ""

if [ "$SAMPLE" = true ]; then
  echo "  Sample data installed. Open Claude Code and try:"
  echo "     cd $(pwd) && claude"
  echo "  Then: \"I want to keep working on my responsive system.\""
  echo ""
  echo "  When you're ready to set up your own profile, run:"
  echo "     /esf-onboarding"
else
  echo "  1. Open Claude Code in your project folder:"
  echo "     cd $(pwd) && claude"
  echo ""
  echo "  2. Run onboarding to personalize your workspace:"
  echo "     /esf-onboarding"
  echo ""
  echo "  Onboarding takes about 5 minutes and sets up your identity,"
  echo "  project context, and folder structure."
  echo ""
  echo "  For a quick overview, read START_HERE.md"
  echo ""
  echo "  Starting a new project later? Re-run /esf-onboarding and say 'update'."
fi

echo "──────────────────────────────────────"
echo ""
