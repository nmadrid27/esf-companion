# Changelog

All notable changes to the ESF Companion are documented here.

## [Unreleased]

### Added
- Frontmatter schema explanations in `templates/project-brief-template.md`: inline comments explaining `required`, `optional`, and `not-required` values for each ESF field.

### Changed
- Cowork plugin v0.5.0: four behavioral parity fixes brought over from the Claude Code agent (commit `4eb05d9`), addressing ambient-mode failures observed during live session use.
  - `/esf-start` now emits an activation status line (`ESF Companion active. Project: ... Context: ... Active corrections: N.`) before any other output when resuming a project, and surfaces explicit failure messages when `companion-state.md` is missing or unreadable rather than proceeding silently.
  - Cowork `esf-project` Records of Resistance trigger lowered: scope corrections, framing redirections, audience-read corrections, and "not that" signals now trigger RoR offers. Pure formatting cleanup and tool-use corrections still pass silently. Offer language updated.
  - Cowork `esf-project` Position Statement Gate is context-aware: activates on brief frontmatter OR companion-state.md context-level requirement OR ad hoc substantial work without a logged project.
  - Cowork `esf-project` explicitly rejects "a clear task instruction satisfies the Position Statement requirement" as a rationalization. The gate stands even when the deliverable is obvious from the first message.
  - Cowork `esf-project` adds an ad hoc project logging offer when Current Project is "not set" and substantial content is requested, with a declined-path note in the session buffer.
- Cowork plugin version check in `/esf-start`: on session start, fetches the remote `plugin.json` from GitHub main, compares to the version baked into the command, and emits a one-line notice if a newer version is available (`Cowork plugin update available: v[remote] (you have v0.5.0). Run /plugin to update.`). Fails silently on any fetch error. Does not block, does not auto-update. Mirrors the Claude Code agent's `.claude/esf-version` pattern.

## [3.10] - 2026-04-13

### Added
- `prompts/quick-start.md`: single-paste prompt for conversation platforms (ChatGPT, Gemini, Claude). Fill in four fields at the top, paste the whole document. Replaces the previous two-step paste workflow for new users.
- Three new examples from non-design, non-student contexts: `examples/position-statement-consultant.md` (management consulting, market entry analysis), `examples/position-statement-writer.md` (narrative nonfiction, book chapter), `examples/record-of-resistance-researcher.md` (academic dissertation, literature review).
- User-facing roadmap section at the top of `ROADMAP.md`: plain-language summary of what is shipped, what is coming, and what is planned.
- Onboarding now opens with ESF overview before collecting user information (Step 1 reordered). Users understand what they are setting up before providing context.
- Quick-start evaluation path in onboarding Step 1: users can say "quick start" to write a Position Statement for one project without full setup, then continue to full onboarding after.
- Session-end reminder in agent: after 4+ substantive exchanges in Make/Reflect without a continuation signal, the Companion mentions once that it can generate a session log when the user is ready to wrap up.
- Phase 1 redirect reframed: preparation guidance toward the user's next step rather than a directive to close the tool.
- Version display at session start when no update is available: "ESF Companion v[version]" shown as part of session greeting.
- Educator cross-reference added to onboarding Step 2b: educators are directed to `docs/institutional-adoption.md` at the point where the educator path is introduced.
- Claude.ai named explicitly throughout docs (previously listed only as "or other conversation tool").
- Claude.ai Projects setup instructions added to `WALKTHROUGH.md`, `START_HERE.md`, and `prompts/README.md`: upload `companion.md` and brief as project knowledge, set `esf-companion.md` as system prompt, skip the manual paste workflow for returning sessions.
- Ambient mode on by default for Claude Code installs: `install.sh` initializes `AMBIENT=true` so `--force` installs write the CLAUDE.md activation block without prompting. Interactive installs prompt with `[Y/n]` and include a four-moment explainer before the question.
- Cowork post-install output includes the Claude.ai Projects path as the recommended route to automatic ESF activation per session.
- Smoke test suite (`test/smoke-test.sh`): 32 assertions across Claude install, conversation install, onboarding, and setup-repo guard.
- Git identity check in `install.sh`: warns instead of silently failing on first commit.
- `.gitignore` creation for fresh installs.
- Sample data: THINK-level course content (position statements, records of resistance, AI use log, process blog).
- `esf-cognitive` skill for cognitive technique triggers.
- Two agent boundaries from PRD: "does not diagnose," "does not enforce beyond its mode."

### Changed
- `START_HERE.md` simplified to a redirect page pointing to `WALKTHROUGH.md` as the primary guide.
- `GETTING_STARTED.md` header updated to clearly label the document as a technical first-session walkthrough.
- `README.md` Quick Start section updated: primary link now points to `WALKTHROUGH.md`. Examples description updated to mention multi-discipline coverage.
- `README.md` FAQ updated: prompt file descriptions now include `quick-start.md` and clarify the purpose of each option.
- `prompts/README.md` reorganized: new "Which File Should I Use?" table at top directs new users to `quick-start.md` immediately.
- Universal language pass: "student" replaced with "user" across all agent-facing files.
- Phase names in docs standardized to canonical Inquire/Position/Explore/Make/Reflect.
- Records of Resistance: proactive workflow (one file per decision, pre-filled AI section, declined path tracked).
- Install script: `fetch_if_missing` preserves user customizations on reinstall.

### Fixed
- Smoke test path bug (Test 4 used relative path after CWD change).
- Install script silent commit failure when git identity missing.
- Workspace-relative path discipline in agent and skill.
- Claude state moved out of `.claude/` to `projects/_esf/`.

### Security
- Added `SECURITY.md` with responsible disclosure policy.
- Added CI workflow for install script validation.

## [3.9] - 2026-04-09

### Changed

**Agent architecture: insight-block-as-default model**
- The agent's default behavior is now the ESF framework, not skill invocation. Skills (`/esf-project`, etc.) are optional deep dives, not the primary entry point.
- Hard Phase 1/2 redirect ("close Claude Code") replaced with Socratic articulation mode: agent stays in session, asks questions, helps the user discover their own thinking without generating content.
- Hard gates replaced with visible-reasoning insight blocks. Gate mode (for `position-statement: required` briefs) is now one explicit acknowledgment stop, not a loop.
- "How to Work With This User" section replaced with six Core Principles.
- Scaffolding levels (Guided/Supported/Independent) now control insight block cadence, verbosity, sensitivity threshold, and Socratic articulation depth.
- Moment 1 escalation: three-level progressive explanation for repeated direction declines — informative, not blocking.
- AI Use Log made universal across all scaffolding levels; brief is the source of all institutional requirements.

**Universalization**
- Removed all program-specific vocabulary (level names, course codes, institutional framework names) from agent, WORKFLOW.md, GETTING_STARTED.md, and ROADMAP.md.
- "The brief is the source of institutional requirements" added explicitly. Agent adapts to what the brief specifies, not to assumptions about any particular program or course.

**Anthropomorphization sweep**
- Agent self-description updated throughout: cognition verbs (notice, think, want) replaced with disclosure verbs (registers as, counts toward, logs as).
- "thinking partner" removed from all agent-facing language.

## [3.8] - 2026-03-29

### Added

**Multi-platform support (v2)**
- `chatgpt-instructions.md`: ChatGPT Custom Instructions format. Paste Section 1 into "What to know," Section 2 into "How to respond"
- `GEMINI.md`: Gemini session prompt. Paste at the start of any Gemini conversation
- `.codex/AGENTS.md`: Codex CLI agent config. Reads automatically when Codex opens in your project directory
- `install.sh` expanded platform menu: choose Claude Code, Claude.ai, ChatGPT, Gemini, or Codex CLI. Each gets tailored install and next-steps instructions
- `--platform` flag now accepts `chatgpt`, `gemini`, and `codex` in addition to `claude` and `conversation`

**Accessibility additions (v2)**
- Checkpoint saves: say "save where I am" or "checkpoint" to write a mid-session checkpoint without closing the session. Resumes from that point next time
- Thread tracking: the Companion tracks multiple concurrent project aspects and orients you when switching between them
- Structured alternatives to open-ended Socratic questions: available to any user who finds open questions difficult to process. Offer explicit choices rather than blank questions

**Platform migration (v2)**
- Onboarding now detects when a user has an existing workspace and is switching platforms. Offers migrate (transfer identity and context), fresh start, or cancel

**Framework Evolution Protocol (v3)**
- Users can now propose changes to their ESF practice. The Companion walks through the reasoning, reflects the consequences honestly, and records confirmed evolutions in `projects/_esf/evolution-log.md`
- Active evolutions are loaded at session start and applied going forward
- Full protocol spec: `.claude/reference/evolution-protocol.md`
- Template updated: `templates/evolution-log-template.md` now supports both FEP entries and project-level reflections

**Cohort homogenization detection (v3)**
- Opt-in educator feature: collect consenting students' Position Statements, ask the Companion to run a cohort analysis. Surfaces shared vocabulary, direction overlap, and concept space gaps across the cohort
- No student attribution by default. Local only. No data leaves the classroom context
- Full guide: `docs/cohort-analysis.md`

**Educator course configs**
- `courses/README.md`: documents the purpose of the `courses/` folder (optional educator course templates for distribution). Includes format guide and example

### Changed
- ROADMAP.md v2 and v3 sections updated: all shipped features marked [SHIPPED]. Remaining items marked [ROADMAP]
- esf-onboarding educator path updated to mention cohort-analysis.md at the point where institutional adoption is introduced

## [3.7] - 2026-03-27

### Added
- Automatic update: Companion now auto-updates on session start when a new version is available
- Visual progress indicator (✓ ▶ ○) shows your current phase at session start and transitions
- Project Scope step between Explore and Make (defines what you're building before you build it)
- Pacing rule in Explore: one thread at a time instead of all options at once
- Technical decisions rule in Make: options explained in context of your position and scope

### Changed
- Position Statement: paste it in chat and the Companion saves it for you (no manual file saving)
- Phase 1 (Inquire) focuses on processing the material; Phase 2 (Position) focuses on taking a stance. No more overlap
- Readability pass always displays the full statement text in chat
- Phase overview text updated to match new workflow (paste PS, project scope, one-at-a-time exploration)

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
