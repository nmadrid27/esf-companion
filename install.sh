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
#   --platform  Set platform without prompting (claude or conversation)
#
# Examples:
#   curl -fsSL ... | bash -s -- --force --platform claude
#   curl -fsSL ... | bash -s -- --force --platform conversation
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
  if [ "$PLATFORM_FLAG" = "claude" ] || [ "$PLATFORM_FLAG" = "conversation" ]; then
    PLATFORM="$PLATFORM_FLAG"
    echo "Platform: $PLATFORM (set via --platform flag)"
  else
    echo -e "${RED}Error: --platform must be 'claude' or 'conversation'. Got: '$PLATFORM_FLAG'${NC}"
    exit 1
  fi
elif [ "$FORCE" != true ]; then
  echo ""
  echo "What AI tool will you use with ESF Companion?"
  echo ""
  echo "  1) Claude Code (full experience: agent, skills, drift detection)"
  echo "  2) Claude.ai, ChatGPT, Gemini, or other conversation tool"
  echo "  3) Not sure yet"
  echo ""
  read -r -p "Choose [1/2/3]: " PLATFORM_CHOICE </dev/tty
  case "$PLATFORM_CHOICE" in
    2)
      PLATFORM="conversation"
      ;;
    3)
      PLATFORM="conversation"
      ;;
    *)
      PLATFORM="claude"
      ;;
  esac
fi

echo "Installing..."

if [ "$PLATFORM" = "conversation" ]; then
  # Warn if --sample was passed (sample data requires Claude Code)
  if [ "$SAMPLE" = true ]; then
    echo -e "${YELLOW}Note: --sample requires Claude Code. Sample data not installed in conversation mode.${NC}"
  fi

  # Lightweight install for conversation-based tools
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

  # Auto-commit conversation Companion files if in a git repo
  if [ -d ".git" ]; then
    git add prompts/ templates/ WORKFLOW.md START_HERE.md 2>/dev/null; [ -f .gitignore ] && git add .gitignore 2>/dev/null
    git commit -m "Install ESF Companion (conversation mode)" --quiet 2>/dev/null && \
      echo -e "  ${GREEN}Companion files committed to git.${NC}" || true
  fi

  echo ""
  echo -e "${GREEN}ESF Companion installed (conversation tool mode).${NC}"
  echo ""
  echo "──────────────────────────────────────"
  echo -e "${CYAN}Next steps:${NC}"
  echo ""
  echo "  1. Open prompts/quick-start.md, fill in the four fields at the top,"
  echo "     and paste the whole document as your first message."
  echo ""
  echo "  Or set up custom instructions for your tool:"
  echo "     Claude.ai:  Settings > Custom Instructions (or use a Project)"
  echo "     ChatGPT:    Settings > Personalization > Custom Instructions"
  echo "     Gemini:     Paste at the start of your conversation"
  echo ""
  echo "  Claude.ai Projects (recommended for returning users):"
  echo "     Create a project, upload companion-state.md and your brief"
  echo "     as knowledge files, set prompts/esf-companion.md as the"
  echo "     system prompt. Context loads automatically every session."
  echo ""
  echo "  2. Start a conversation and tell it what you are working on."
  echo "     It will guide you through writing a Position Statement"
  echo "     and the rest of the ESF process."
  echo ""
  echo "  Templates are in the templates/ folder."
  echo "  The visual process diagram is in WORKFLOW.md."
  echo ""
  echo "  For a quick overview, read START_HERE.md"
  echo ""
  echo "  Want the full experience later? Re-run with Claude Code (option 1)."
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

# Create a project folder if not already in one
if [ ! -f "README.md" ] && [ ! -f "WORKFLOW.md" ]; then
  echo ""
  echo -e "${CYAN}Let's set up your project folder.${NC}"
  echo ""
  read -r -p "Project name (e.g., portfolio-redesign, client-rebrand, thesis): " PROJECT_NAME </dev/tty
  if [ -n "$PROJECT_NAME" ]; then
    # Sanitize: lowercase, replace spaces with hyphens
    FOLDER_NAME=$(echo "$PROJECT_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-')
    mkdir -p "$FOLDER_NAME"
    # Move installed files into the project folder
    for item in .claude prompts templates WORKFLOW.md; do
      [ -e "$item" ] && mv "$item" "$FOLDER_NAME/" 2>/dev/null
    done
    cd "$FOLDER_NAME"
    echo -e "  ${GREEN}Created project folder: $FOLDER_NAME/${NC}"
    echo "  Installed files are inside this folder."
  fi
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
