#!/usr/bin/env bash
# ESF Companion - Repository Setup
# Creates a git repository for users who are new to GitHub.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/nmadrid27/esf-companion/main/setup-repo.sh -o setup-repo.sh && bash setup-repo.sh
#
# What it does:
#   1. Creates a portfolio directory
#   2. Initializes a git repository
#   3. Sets up .gitignore and initial README
#   4. Makes the first commit
#   5. Optionally creates a private GitHub repo (requires gh CLI)
#   6. Runs the ESF Companion installer

set -e

# Require an interactive terminal — prompts will not work in a piped context
if [ ! -t 0 ]; then
  echo "Error: This script requires an interactive terminal."
  echo "Download and run it directly:"
  echo "  curl -fsSL https://raw.githubusercontent.com/nmadrid27/esf-companion/main/setup-repo.sh -o setup-repo.sh && bash setup-repo.sh"
  exit 1
fi

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${CYAN}ESF Companion - Repository Setup${NC}"
echo "──────────────────────────────────────────"
echo ""
echo "This script creates a git repository for your ESF portfolio."
echo "No prior git or GitHub experience required."
echo ""

# Check for git
if ! command -v git &> /dev/null; then
  echo -e "${RED}Error: git is not installed.${NC}"
  echo ""
  echo "Install git first:"
  echo "  macOS:   brew install git"
  echo "  Windows: https://git-scm.com/download/win"
  echo "  Linux:   sudo apt install git (Ubuntu/Debian)"
  echo ""
  exit 1
fi

# Ask for repo name
DEFAULT_NAME="ai-portfolio"
read -r -p "Repository name (default: $DEFAULT_NAME): " REPO_NAME
REPO_NAME="${REPO_NAME:-$DEFAULT_NAME}"

# Sanitize: replace spaces with hyphens, lowercase
REPO_NAME=$(echo "$REPO_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd '[:alnum:]-_')

if [ -d "$REPO_NAME" ]; then
  echo -e "${RED}Error: Directory '$REPO_NAME' already exists.${NC}"
  echo "Choose a different name or delete the existing directory."
  exit 1
fi

# Ask for user name (used in README)
read -r -p "Your name (for the README): " USER_NAME

echo ""
echo -e "${CYAN}Creating repository...${NC}"

# Create directory and initialize git
mkdir -p "$REPO_NAME"
cd "$REPO_NAME"
git init -q -b main

# Create .gitignore
cat > .gitignore << 'GITIGNORE'
# OS files
.DS_Store
Thumbs.db

# Editor files
*.swp
*.swo
*~
.vscode/
.idea/

# Node (if using microsites or tools)
node_modules/
dist/

# Environment
.env
.env.local

# ESF session buffer (ephemeral, not versioned)
.session-buffer.md
GITIGNORE

# Create initial README
cat > README.md << README
# ${USER_NAME:-My} AI Portfolio

This repository holds my coursework, position statements, records of resistance, and project artifacts across the program.

Managed with the [Epistemic Stewardship Framework (ESF)](https://github.com/nmadrid27/esf-companion).

## Structure

After running the ESF Companion installer, the repository will contain:

- \`projects/\` — Course projects, organized by course
- \`templates/\` — ESF templates (position statements, records of resistance, AI use logs)
- \`.claude/\` — Toolkit configuration (if using Claude Code)
- \`prompts/\` — Plain-text prompts (if using other AI tools)

## Setup

If the toolkit is not yet installed, run:

\`\`\`bash
curl -fsSL https://raw.githubusercontent.com/nmadrid27/esf-companion/main/install.sh | bash
\`\`\`
README

# Ensure git identity is configured (required for commits)
if [ -z "$(git config --global user.name 2>/dev/null)" ] || [ -z "$(git config --global user.email 2>/dev/null)" ]; then
  echo ""
  echo -e "${YELLOW}Git needs your name and email before it can make commits.${NC}"
  read -r -p "Your name (e.g., Alex Rivera): " GIT_NAME
  read -r -p "Your email (e.g., alex@example.com): " GIT_EMAIL
  if [ -z "$GIT_NAME" ] || [ -z "$GIT_EMAIL" ]; then
    echo -e "${RED}Error: Name and email are required.${NC}"
    exit 1
  fi
  git config --global user.name "$GIT_NAME"
  git config --global user.email "$GIT_EMAIL"
  echo -e "${GREEN}  Git identity configured.${NC}"
fi

# First commit
git add .
git commit -q -m "Initial repository setup"

echo -e "${GREEN}  Repository created: $(pwd)${NC}"

# Offer to create GitHub remote
echo ""
if command -v gh &> /dev/null; then
  echo -e "${BOLD}Push to GitHub?${NC}"
  echo "This creates a private repository on your GitHub account."
  read -r -p "Create GitHub repo? (Y/n): " CREATE_REMOTE
  CREATE_REMOTE="${CREATE_REMOTE:-Y}"

  if [[ "$CREATE_REMOTE" =~ ^[Yy]$ ]]; then
    # Check if logged in
    if gh auth status &> /dev/null; then
      # Create the remote but don't push yet; install.sh will add toolkit files and auto-commit
      gh repo create "$REPO_NAME" --private --source=. -q 2>/dev/null && \
        PUSH_AFTER_INSTALL=true && \
        echo -e "${GREEN}  GitHub repo created. Will push after install completes.${NC}" || \
        echo -e "${YELLOW}  Could not create GitHub repo. You can do this later with: gh repo create${NC}"
    else
      echo -e "${YELLOW}  Not logged in to GitHub CLI. Run 'gh auth login' first.${NC}"
      echo "  You can push to GitHub later."
    fi
  fi
else
  echo -e "${YELLOW}Optional: Install the GitHub CLI (gh) to create a remote repo from the terminal.${NC}"
  echo "  macOS: brew install gh"
  echo "  Other: https://cli.github.com/"
  echo ""
  echo "  Or create a repo manually at https://github.com/new"
  echo "  then run:"
  echo "    git remote add origin https://github.com/YOUR-USERNAME/$REPO_NAME.git"
  echo "    git push -u origin main"
fi

# Run the ESF installer
echo ""
echo "──────────────────────────────────────────"
echo -e "${CYAN}Installing ESF Companion...${NC}"
echo ""

INSTALLER_URL="https://raw.githubusercontent.com/nmadrid27/esf-companion/main/install.sh"
curl -fsSL "$INSTALLER_URL" | bash

# Push to GitHub if remote was created earlier
if [ "$PUSH_AFTER_INSTALL" = true ]; then
  git push -u origin main --quiet 2>/dev/null && \
    echo -e "  ${GREEN}Pushed to GitHub (includes toolkit files).${NC}" || \
    echo -e "  ${YELLOW}Could not push. Run 'git push -u origin main' later.${NC}"
fi

echo ""
echo -e "${GREEN}All done.${NC} Your project repo is ready at: $(pwd)"
echo ""
