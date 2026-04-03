#!/usr/bin/env bash
# ESF Companion Installer
# Installs the ESF Companion into your current directory.
#
# Usage (run from your project directory):
#   curl -fsSL https://raw.githubusercontent.com/nmadrid27/esf-companion/main/install.sh | bash
#
# Options:
#   --sample    Install pre-filled BUILD-level test data (Alex Rivera)
#   --force     Skip all interactive prompts (for scripted installs)
#   --platform  Set platform without prompting
#               Values: claude, conversation, chatgpt, gemini, codex
#
# Examples:
#   curl -fsSL ... | bash -s -- --force --platform claude
#   curl -fsSL ... | bash -s -- --force --platform chatgpt
#   curl -fsSL ... | bash -s -- --force --platform gemini
#   curl -fsSL ... | bash -s -- --force --platform codex
#   curl -fsSL ... | bash -s -- --sample

set -e

SAMPLE=false
FORCE=false
PLATFORM_FLAG=""
PLATFORM_NEXT=false
for arg in "$@"; do
  if [ "$PLATFORM_NEXT" = true ]; then
    PLATFORM_FLAG="$arg"
    PLATFORM_NEXT=false
  elif [ "$arg" = "--sample" ]; then
    SAMPLE=true
  elif [ "$arg" = "--force" ]; then
    FORCE=true
  elif [[ "$arg" == --platform=* ]]; then
    PLATFORM_FLAG="${arg#--platform=}"
  elif [ "$arg" = "--platform" ]; then
    PLATFORM_NEXT=true
  fi
done

TOOLKIT_BASE="https://raw.githubusercontent.com/nmadrid27/esf-companion/main"
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
    claude|conversation|chatgpt|gemini|codex)
      PLATFORM="$PLATFORM_FLAG"
      echo "Platform: $PLATFORM (set via --platform flag)"
      ;;
    *)
      echo -e "${RED}Error: --platform must be one of: claude, conversation, chatgpt, gemini, codex. Got: '$PLATFORM_FLAG'${NC}"
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
  echo "  6) Not sure yet"
  echo ""
  read -r -p "Choose [1-6]: " PLATFORM_CHOICE </dev/tty
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
      PLATFORM="conversation"
      ;;
    *)
      PLATFORM="claude"
      ;;
  esac
fi

echo "Installing..."

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
  fetch_if_missing "$TOOLKIT_BASE/prompts/README.md" prompts/README.md

  echo "  Fetching templates..."
  fetch_if_missing "$TOOLKIT_BASE/templates/position-statement-template.md" templates/position-statement-template.md
  fetch_if_missing "$TOOLKIT_BASE/templates/position-statement.md" templates/position-statement.md
  fetch_if_missing "$TOOLKIT_BASE/templates/record-of-resistance-template.md" templates/record-of-resistance-template.md
  fetch_if_missing "$TOOLKIT_BASE/templates/record-of-resistance.md" templates/record-of-resistance.md
  fetch_if_missing "$TOOLKIT_BASE/templates/ai-use-log-template.md" templates/ai-use-log-template.md
  fetch_if_missing "$TOOLKIT_BASE/templates/ai-use-log.md" templates/ai-use-log.md
  fetch_if_missing "$TOOLKIT_BASE/templates/companion-state-template.md" templates/companion-state-template.md
  fetch_if_missing "$TOOLKIT_BASE/templates/five-questions-checklist.md" templates/five-questions-checklist.md
  fetch_if_missing "$TOOLKIT_BASE/templates/disclosure-statement.md" templates/disclosure-statement.md

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

# Download prompts
echo "  Fetching prompts..."
fetch_if_missing "$TOOLKIT_BASE/prompts/companion.md" prompts/companion.md
fetch_if_missing "$TOOLKIT_BASE/prompts/esf-companion.md" prompts/esf-companion.md
fetch_if_missing "$TOOLKIT_BASE/prompts/project-workflow.md" prompts/project-workflow.md
fetch_if_missing "$TOOLKIT_BASE/prompts/README.md" prompts/README.md

# Download templates
echo "  Fetching templates..."
fetch_if_missing "$TOOLKIT_BASE/templates/position-statement-template.md" templates/position-statement-template.md
fetch_if_missing "$TOOLKIT_BASE/templates/position-statement.md" templates/position-statement.md
fetch_if_missing "$TOOLKIT_BASE/templates/ai-use-log-template.md" templates/ai-use-log-template.md
fetch_if_missing "$TOOLKIT_BASE/templates/ai-use-log-lite-template.md" templates/ai-use-log-lite-template.md
fetch_if_missing "$TOOLKIT_BASE/templates/ai-use-log.md" templates/ai-use-log.md
fetch_if_missing "$TOOLKIT_BASE/templates/companion-state-template.md" templates/companion-state-template.md
fetch_if_missing "$TOOLKIT_BASE/templates/record-of-resistance-template.md" templates/record-of-resistance-template.md
fetch_if_missing "$TOOLKIT_BASE/templates/record-of-resistance.md" templates/record-of-resistance.md
fetch_if_missing "$TOOLKIT_BASE/templates/five-questions-checklist.md" templates/five-questions-checklist.md
fetch_if_missing "$TOOLKIT_BASE/templates/disclosure-statement.md" templates/disclosure-statement.md
fetch_if_missing "$TOOLKIT_BASE/templates/evolution-log-template.md" templates/evolution-log-template.md
fetch_if_missing "$TOOLKIT_BASE/templates/session-log-template.md" templates/session-log-template.md
fetch_if_missing "$TOOLKIT_BASE/templates/reflection-template.md" templates/reflection-template.md

# Download reference files
echo "  Fetching reference files..."
curl -fsSL "$TOOLKIT_BASE/.claude/reference/esf-guide.md"   -o .claude/reference/esf-guide.md
curl -fsSL "$TOOLKIT_BASE/.claude/reference/disclosure-protocol.md" -o .claude/reference/disclosure-protocol.md

# Download workflow diagram and onboarding guide (skip if already exists)
if [ ! -f "WORKFLOW.md" ]; then
  curl -fsSL "$TOOLKIT_BASE/WORKFLOW.md" -o WORKFLOW.md
fi
fetch_if_missing "$TOOLKIT_BASE/START_HERE.md" START_HERE.md

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
  curl -fsSL "$TOOLKIT_BASE/sample/projects/build-course/records-of-resistance/ror-01.md" \
    -o projects/build-course/records-of-resistance/ror-01.md
fi

# Auto-commit only Companion files if in a git repo (do not stage unrelated work)
if [ -d ".git" ]; then
  git add .claude/ prompts/ templates/ WORKFLOW.md START_HERE.md 2>/dev/null
  [ -f .gitignore ] && git add .gitignore 2>/dev/null

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
