# Changelog

All notable changes to the ESF Companion are documented here.

## [3.7] - 2026-03-27

### Added
- Automatic update: Companion now auto-updates on session start when a new version is available
- Visual progress indicator (✓ ▶ ○) shows your current phase at session start and transitions
- Project Scope step between Explore and Make — defines what you're building before you build it
- Pacing rule in Explore: one thread at a time instead of all options at once
- Technical decisions rule in Make: options explained in context of your position and scope

### Changed
- Position Statement: paste it in chat and the Companion saves it for you (no manual file saving)
- Phase 1 (Inquire) focuses on processing the material; Phase 2 (Position) focuses on taking a stance — no more overlap
- Readability pass always displays the full statement text in chat
- Phase overview text updated to match new workflow (paste PS, project scope, one-at-a-time exploration)

## [Unreleased]

### Added
- `prompts/quick-start.md`: single-paste prompt for conversation platforms (ChatGPT, Gemini, Claude). Fill in four fields at the top, paste the whole document. Replaces the previous two-step paste workflow for new users.
- Three new examples from non-design, non-student contexts: `examples/position-statement-consultant.md` (management consulting, market entry analysis), `examples/position-statement-writer.md` (narrative nonfiction, book chapter), `examples/record-of-resistance-researcher.md` (academic dissertation, literature review).
- User-facing roadmap section at the top of `ROADMAP.md`: plain-language summary of what is shipped, what is coming in v2, and what is planned for v3. Full PRD remains below it.
- Onboarding now opens with ESF overview before collecting user information (Step 1 reordered). Users understand what they are setting up before providing context.
- Quick-start evaluation path in onboarding Step 1: users can say "quick start" to write a Position Statement for one project without full setup, then continue to full onboarding after.
- Session-end reminder in agent: after 4+ substantive exchanges in Make/Reflect without a continuation signal, the Companion mentions once that it can generate a session log when the user is ready to wrap up.
- Phase 1 redirect reframed: instead of "close this tool," users now receive preparation guidance oriented toward their next step (writing the Position Statement and returning).
- Version display at session start when no update is available: "ESF Companion v[version]" shown as part of session greeting so users always know which version they are running.
- Frontmatter schema explanations added directly to `templates/project-brief-template.md`: inline comments explain `required`, `optional`, and `not-required` values for each ESF field.
- Educator cross-reference added to onboarding Step 2b: educators are directed to `docs/institutional-adoption.md` at the point where the educator path is introduced.
- Session-end handling in agent: explicit session end behavior with one-time reminder after extended Make/Reflect work.

### Changed
- `START_HERE.md` simplified to a redirect page pointing to `WALKTHROUGH.md` as the primary guide.
- `GETTING_STARTED.md` header updated to clearly label the document as a technical first-session walkthrough and direct users to `WALKTHROUGH.md` for the primary guide.
- `README.md` Quick Start section updated: primary link now points to `WALKTHROUGH.md` rather than `START_HERE.md`. Examples description updated to mention multi-discipline coverage.
- `README.md` FAQ updated: prompt file descriptions now include `quick-start.md` and clarify the purpose of each option.
- `prompts/README.md` reorganized: new "Which File Should I Use?" table at top directs new users to `quick-start.md` immediately.

### [Previous entries continue below]
- Smoke test suite (`test/smoke-test.sh`): 32 assertions across Claude install, conversation install, onboarding, and setup-repo guard
- Git identity check in install.sh (warns instead of silently failing)
- `.gitignore` creation for fresh installs (no longer requires pre-existing file)
- Sample data: THINK-level course content (position statements, records of resistance, AI use log, process blog)
- `esf-cognitive` skill for cognitive technique triggers
- `GETTING_STARTED.md` detailed first-session walkthrough
- `START_HERE.md` quick-start guide (installed in both Claude and conversation modes)
- Two agent boundaries from PRD: "does not diagnose," "does not enforce beyond its mode"

### Changed
- Universal language pass: "student" replaced with "user" across all agent-facing files
- "ESF Community Toolkit" renamed to "ESF Companion" across all files
- Phase names in docs standardized to canonical Inquire/Position/Explore/Make/Reflect
- Position Statement terminology standardized ("what matters most" replaces "emphasis")
- Onboarding flow uses single open question per PRD Section 7
- Agent and skills aligned with PRD: drift reference points (direction, priority, boundary), mirror/gate mode, scaffolding levels
- Records of Resistance: proactive workflow (one file per decision, pre-filled AI section, declined path tracked)
- Conversation mode: PROJECT.md generation at session end, disclosure drafting
- Install script: platform flag (`--platform claude|conversation`), `--force` for reinstall, `--sample` for demo data, `fetch_if_missing` preserves user customizations
- Removed duplicate `evolution-log-template.md` fetch from install script

### Fixed
- Smoke test path bug (Test 4 used relative path after CWD change)
- Install script silent commit failure when git identity missing
- `setup-repo.sh` header and git identity check
- Workspace-relative path discipline in agent and skill (never expand to absolute paths)
- Sample install commit staging
- Claude state moved out of `.claude/` to `projects/_esf/`

### Security
- Added `SECURITY.md` with responsible disclosure policy
- Added CI workflow for install script validation

## [1.0.0] - 2026-03-13

### Added
- Framework documentation (`docs/what-is-esf.md`, `docs/essentials.md`)
- Open-source infrastructure (`CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `CITATION.cff`)
- This changelog

### Changed
- README updated with "Understanding ESF" section linking to framework docs

## [0.9.0] - 2026-03-12

### Added
- Initial release
- Five templates (Position Statement, Record of Resistance, AI Use Log, Five Questions Checklist, Disclosure Statement)
- Workflow diagram (`WORKFLOW.md`)
- Paste-anywhere companion prompt (`prompts/esf-companion.md`)
- Claude Code agent and reference guide
- Install script with 3-option handler (setup repo, install without git, cancel)
- Institutional adoption guide in README
- `curl -fsSL` across all install commands (fail on HTTP errors)
