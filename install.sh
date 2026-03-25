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
#   --course    Fetch course-specific config (e.g., --course ai-180)
#
# Examples:
#   curl -fsSL ... | bash -s -- --course ai-180
#   curl -fsSL ... | bash -s -- --force --course ai-201
#   curl -fsSL ... | bash -s -- --sample

set -e

SAMPLE=false
FORCE=false
COURSE=""
COURSE_NEXT=false
for arg in "$@"; do
  if [ "$COURSE_NEXT" = true ]; then
    COURSE="$arg"
    COURSE_NEXT=false
  elif [ "$arg" = "--sample" ]; then
    SAMPLE=true
  elif [ "$arg" = "--force" ]; then
    FORCE=true
  elif [[ "$arg" == --course=* ]]; then
    COURSE="${arg#--course=}"
  elif [ "$arg" = "--course" ]; then
    COURSE_NEXT=true
  fi
done

TOOLKIT_BASE="https://raw.githubusercontent.com/nmadrid27/esf-companion/main"
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo -e "${CYAN}ESF Companion - Installer${NC}"
echo "──────────────────────────────────────"

# Warn if already installed
if [ -d ".claude/agents" ] && [ -f ".claude/agents/esf-companion.md" ]; then
  if [ "$FORCE" = true ]; then
    echo -e "${YELLOW}Force mode: overwriting existing installation.${NC}"
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
    echo "The toolkit works best inside a git repo (your project directory)."
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

# Ask which AI tool the user will use
PLATFORM="claude"
if [ "$FORCE" != true ]; then
  echo ""
  echo "What AI tool will you use with ESF Companion?"
  echo ""
  echo "  1) Claude Code (full experience: agent, skills, drift detection)"
  echo "  2) ChatGPT, Gemini, or other conversation tool"
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

  echo "  Fetching companion prompt..."
  curl -fsSL "$TOOLKIT_BASE/prompts/companion.md"        -o prompts/companion.md
  curl -fsSL "$TOOLKIT_BASE/prompts/project-workflow.md"  -o prompts/project-workflow.md
  curl -fsSL "$TOOLKIT_BASE/prompts/README.md"            -o prompts/README.md

  echo "  Fetching templates..."
  curl -fsSL "$TOOLKIT_BASE/templates/position-statement-template.md"    -o templates/position-statement-template.md
  curl -fsSL "$TOOLKIT_BASE/templates/record-of-resistance-template.md"  -o templates/record-of-resistance-template.md
  curl -fsSL "$TOOLKIT_BASE/templates/ai-use-log-template.md"           -o templates/ai-use-log-template.md

  if [ ! -f "WORKFLOW.md" ]; then
    curl -fsSL "$TOOLKIT_BASE/WORKFLOW.md" -o WORKFLOW.md
  fi

  echo ""
  echo -e "${GREEN}ESF Companion installed (conversation tool mode).${NC}"
  echo ""
  echo "──────────────────────────────────────"
  echo -e "${CYAN}Next steps:${NC}"
  echo ""
  echo "  1. Open prompts/companion.md"
  echo "  2. Copy its contents into your AI tool's custom instructions"
  echo "     (ChatGPT: Settings > Personalization > Custom Instructions)"
  echo "     (Gemini: paste at the start of your conversation)"
  echo ""
  echo "  3. Start a new conversation and tell it what you are working on."
  echo "     It will guide you through writing a Position Statement"
  echo "     and the rest of the ESF process."
  echo ""
  echo "  Templates are in the templates/ folder."
  echo "  The visual process diagram is in WORKFLOW.md."
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

# Download agents (preserve personalized agent on re-install)
echo "  Fetching agents..."
if [ "$FORCE" != true ] && [ -f ".claude/agents/esf-companion.md" ] && grep -q "NAME\|^- \*\*Name:\*\*" .claude/agents/esf-companion.md 2>/dev/null && ! grep -q "\[NAME\]" .claude/agents/esf-companion.md 2>/dev/null; then
  echo -e "  ${YELLOW}Personalized agent file found; skipping to preserve your profile.${NC}"
  echo "  To force update: re-run with --force flag."
else
  curl -fsSL "$TOOLKIT_BASE/.claude/agents/esf-companion.md" -o .claude/agents/esf-companion.md
fi

# Download skills
echo "  Fetching skills..."
curl -fsSL "$TOOLKIT_BASE/.claude/skills/esf-onboarding/SKILL.md" -o .claude/skills/esf-onboarding/SKILL.md
curl -fsSL "$TOOLKIT_BASE/.claude/skills/esf-project/SKILL.md"    -o .claude/skills/esf-project/SKILL.md
mkdir -p .claude/skills/esf-git .claude/skills/esf-verify .claude/skills/esf-update
curl -fsSL "$TOOLKIT_BASE/.claude/skills/esf-git/SKILL.md"        -o .claude/skills/esf-git/SKILL.md
curl -fsSL "$TOOLKIT_BASE/.claude/skills/esf-verify/SKILL.md"     -o .claude/skills/esf-verify/SKILL.md
curl -fsSL "$TOOLKIT_BASE/.claude/skills/esf-update/SKILL.md"     -o .claude/skills/esf-update/SKILL.md

# Download version file
curl -fsSL "$TOOLKIT_BASE/.claude/esf-version" -o .claude/esf-version

# Download prompts (for non-Claude Code users)
echo "  Fetching prompts..."
curl -fsSL "$TOOLKIT_BASE/prompts/companion.md"  -o prompts/companion.md
curl -fsSL "$TOOLKIT_BASE/prompts/project-workflow.md"   -o prompts/project-workflow.md
curl -fsSL "$TOOLKIT_BASE/prompts/README.md"             -o prompts/README.md

# Download templates
echo "  Fetching templates..."
curl -fsSL "$TOOLKIT_BASE/templates/position-statement-template.md"    -o templates/position-statement-template.md
curl -fsSL "$TOOLKIT_BASE/templates/ai-use-log-template.md"           -o templates/ai-use-log-template.md
curl -fsSL "$TOOLKIT_BASE/templates/ai-use-log-lite-template.md"     -o templates/ai-use-log-lite-template.md
curl -fsSL "$TOOLKIT_BASE/templates/record-of-resistance-template.md" -o templates/record-of-resistance-template.md
curl -fsSL "$TOOLKIT_BASE/templates/session-log-template.md"          -o templates/session-log-template.md
curl -fsSL "$TOOLKIT_BASE/templates/reflection-template.md"   -o templates/reflection-template.md
curl -fsSL "$TOOLKIT_BASE/templates/evolution-log-template.md"        -o templates/evolution-log-template.md

# Download reference files
echo "  Fetching reference files..."
curl -fsSL "$TOOLKIT_BASE/.claude/reference/esf-guide.md"   -o .claude/reference/esf-guide.md
curl -fsSL "$TOOLKIT_BASE/.claude/reference/disclosure-protocol.md" -o .claude/reference/disclosure-protocol.md

# Download workflow diagram (skip if file already exists; user may have customized it)
if [ ! -f "WORKFLOW.md" ]; then
  curl -fsSL "$TOOLKIT_BASE/WORKFLOW.md" -o WORKFLOW.md
fi

# Ensure .session-buffer.md is gitignored (covers install into existing repos)
if [ -f ".gitignore" ] && ! grep -q '.session-buffer.md' .gitignore 2>/dev/null; then
  printf '\n# ESF session buffer (ephemeral, not versioned)\n.session-buffer.md\n' >> .gitignore
fi

# Fetch course config if --course flag was provided
COURSE_LOADED=false
if [ -n "$COURSE" ]; then
  echo ""
  echo "  Fetching course configuration for $COURSE..."
  COURSE_LOWER=$(echo "$COURSE" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')

  # Try microsite
  COURSE_CONFIG_URL="https://astro-${COURSE_LOWER}.vercel.app/course-config.json"
  if curl -fsSL "$COURSE_CONFIG_URL" -o .claude/course-config.json 2>/dev/null; then
    echo -e "  ${GREEN}Course config loaded from microsite.${NC}"
    COURSE_LOADED=true
  else
    echo -e "  ${YELLOW}Could not fetch course config for '$COURSE'. Run /esf-onboarding to set up manually.${NC}"
  fi
fi

# Install sample data if --sample flag was passed
if [ "$SAMPLE" = true ]; then
  echo "  Installing BUILD-level sample data (Alex Rivera)..."
  mkdir -p projects/build-course/briefs
  mkdir -p projects/build-course/position-statements
  mkdir -p projects/build-course/records-of-resistance
  mkdir -p projects/build-course/ai-use-logs
  mkdir -p projects/build-course/gate-records
  mkdir -p projects/build-course/reflections
  mkdir -p projects/build-course/logs
  mkdir -p projects/build-course/work
  curl -fsSL "$TOOLKIT_BASE/sample/agents/esf-companion.md" \
    -o .claude/agents/esf-companion.md
  curl -fsSL "$TOOLKIT_BASE/sample/projects/build-course/briefs/p2-responsive-system.md" \
    -o projects/build-course/briefs/p2-responsive-system.md
  curl -fsSL "$TOOLKIT_BASE/sample/projects/build-course/position-statements/responsive-system.md" \
    -o projects/build-course/position-statements/responsive-system.md
  curl -fsSL "$TOOLKIT_BASE/sample/projects/build-course/records-of-resistance/ror-01.md" \
    -o projects/build-course/records-of-resistance/ror-01.md
fi

echo ""
echo -e "${GREEN}ESF Companion installed.${NC}"
echo ""
echo "──────────────────────────────────────"
echo -e "${CYAN}Next steps:${NC}"
echo ""

if [ "$SAMPLE" = true ]; then
  echo "  Sample data installed. Open Claude Code and try:"
  echo "     claude"
  echo "  Then: \"I want to keep working on my responsive system.\""
  echo ""
  echo "  When you're ready to set up your own profile, run:"
  echo "     /esf-onboarding"
elif [ "$COURSE_LOADED" = true ]; then
  echo "  Course config for '$COURSE' loaded. Open Claude Code and run onboarding:"
  echo "     claude"
  echo "     /esf-onboarding"
  echo ""
  echo "  Onboarding will detect your course config and auto-populate your setup."
  echo "  It takes about 2 minutes when a config is available."
else
  echo "  1. Open Claude Code in this directory:"
  echo "     claude"
  echo ""
  echo "  2. Run onboarding to personalize your workspace:"
  echo "     /esf-onboarding"
  echo ""
  echo "  Onboarding takes about 5 minutes and sets up your identity,"
  echo "  project context, and folder structure."
  echo ""
  echo "  Starting a new project later? Re-run /esf-onboarding and say 'update'."
fi

echo "──────────────────────────────────────"
echo ""
