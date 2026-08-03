# Changelog

All notable changes to the ESF Companion are documented here.

## [Unreleased]

### Fixed
- **Template prompt questions were rendered as the student's own words.** `quote_content` documented itself as extracting prose from a `> ` blockquote, but took every line in the section and stripped italics only from the end. Because every shipped template puts its prompt question above the `>` slot, a filled-in `position-statement-template.md` returned the prompt with the answer glued onto it (`*What creative direction am I exploring?* I want to make...`), and that string was presented in the Defense Pack as the student's stance. A section containing blockquote lines now yields only those lines; a section with none still takes every line, so artifacts written as plain prose keep parsing. **This changes rendered output for artifacts already written from the shipped templates:** the prompt text disappears from the affected fields. The test fixtures never caught this because they carry no prompt line, only the blockquote.
- **Defense Pack dropped four fields when re-reading `pack.json`.** `render.py` rehydrated `DefensePack` from a hand-written argument list that omitted `resist_count`, `default_count`, `shift_count`, and `process_blog_sources`. The HTML renderer displays all four, so a pack recording 147 `@resist` moments rendered as 0 and the process-blog section vanished. Rehydration is now driven off `fields(DefensePack)`, so a field added to the schema later cannot be silently dropped again. Older packs still load: a missing field falls back to its dataclass default, or `""` for the required identity scalars.
- **An AI Use Log that parsed to entirely empty produced no warning.** Gap detection only checked for a missing log. The simplest template (`ai-use-log.md`) uses per-session tables whose headings the parser does not recognise, so it produced a log object with every field blank, rendered as an empty section, with nothing flagged. A log with no interactions, no intervention summary, and no pattern analysis is now a WARNING gap, so the student sees it before the defense rather than during it.
- **Records of Resistance written from the frontmatter-free template carried no date.** `parse_record_of_resistance` now falls back to the `**Date:**` preamble line when frontmatter is absent. `**Project:**` is deliberately not read: the aggregator drops any record whose project does not match the workspace project name, so a free-text label would silently delete the record. An unfilled `[YYYY-MM-DD]` placeholder still counts as absent, and frontmatter wins wherever present.

### Changed
- **The frontmatter-free "Default" templates mark their fill-in slots with `>`** instead of `[Write here]`, so answers parse as the student's words rather than blending into the surrounding prompt text. `position-statement.md` and `record-of-resistance.md` stay frontmatter-free, which is their documented differentiator from the Institutional `-template.md` variants (see `templates/README.md`).

### Docs
- **README folder-structure accuracy.** The `skills/` annotation in the post-install folder diagram now lists `status` and `defense pack`, added after the original diagram was written.

### Internal
- **`install.sh` fetches are list-driven.** 54 repeated `fetch_if_missing "$TOOLKIT_BASE/<path>" esf/toolkit/<path>` calls, each restating the path twice, collapse into `fetch_toolkit_files` over a bare path list, and the 14 always-overwrite/fail-fast fetches into `fetch_required`. The per-audience prompt and template lists stay separate on purpose (#42). The raw `curl` calls that overwrite on update and abort on failure are intentionally not folded into `fetch_if_missing`, which skips existing files and tolerates failure. Verified by running the old and new installer on both platforms and diffing the results: byte-for-byte identical trees.
- **Removed `docs/getting-started.md`**, a nine-line file whose only content was a pointer to `START_HERE.md` and `GETTING_STARTED.md`. Nothing linked to it.

## [companion-v0.10.1] - 2026-06-06

### Internal
- **Release tooling.** `scripts/release-drift.sh` reports unreleased commits since the latest `companion-v*` tag; a CI workflow keeps a single self-healing "Release pending" issue open until a release is cut; `scripts/release.sh` cuts a release (version bump, CHANGELOG dating, commit, annotated tag, GitHub release) in one guarded command with `--dry-run`. Prevents merged work from sitting unreleased on `main`. See `RELEASING.md`.

## [companion-v0.10.0] - 2026-06-06

### Added
- **Gap scanner (on-demand).** New Claude Code `esf-status` skill reports present and missing artifacts for the current project, scaffolding-aware, via the Defense Pack aggregator's `--scan-only` mode (now emitting a structured snapshot). Brief frontmatter `records-of-resistance-minimum` (alias `ror-minimum`) drives a below-minimum WARNING. Because the aggregator is shared, the Defense Pack export now also shows this WARNING when a brief sets a minimum and the RoR count is below it.
- **Update notifications.** Claude Code now surfaces a one-line "update available" nudge at session start (cached, non-naggy, network-free on the hot path; a detached background check refreshes at most once per 24h). `/esf-update` shows the CHANGELOG sections for everything new since your installed version, and `/esf-status` surfaces a read-only update line. Backed by a shared `esf-update-check.sh` helper with a per-user cache at `~/.claude/.esf-update-check`.
- **Cycle-based workspace auto-discovery.** The Defense Pack aggregator auto-detects milestone-directory layouts (e.g. `p2-break-through/`, `p3-next-steps/`) that hold artifacts directly, and surfaces an INFO gap naming which artifacts resolved through the cycle path. (#27, #34)

### Fixed
- **Five parser bugs** in the Defense Pack aggregator surfaced by review. (#29)
- **Render-pipeline polish.** Added `--strict` exit codes to the aggregator and renderer CLIs; multi-paragraph prose and decision-narration line breaks are now preserved in HTML and PDF; the UTF-8 BOM is stripped when re-reading `defense-narrative.md`; removed a dead render helper. (#30)

### Changed
- **Completed the v0.7 `projects/` to `esf/` workspace migration** across the Cowork plugin, top-level docs, and the Codex agent, so every surface points at the canonical `esf/[context]/` layout (legacy `projects/` paths kept as read fallbacks). (#36)
- **Defense Pack install file list is driven by `MANIFEST.txt`** with a CI guard. (#33)

### Internal
- Dataclass typing for `Narrative.decision_walkthrough` (#32); cycle-layout polish (#34); no-em-dash sweep across prose (#26); mechanical polish rollup (#35); gitignore for the agent worktree scratch dir (#31).

## [companion-v0.9.1] - 2026-05-23

### Fixed
- **Defense Pack Paths override accepted relative paths that contain `/`.** The validator was rejecting any value with a path separator; but override paths legitimately contain them (e.g. `projects/CORE-201/references/M2-position-statement.md`). The override mechanism was broken for any subdirectory target. Validator now allows `/`, still blocks `..`, absolute paths, and null bytes. Surfaced by validation against a second real student workspace (cycle-based directory layout) post-v0.9.0 release.

## [companion-v0.9.0] - 2026-05-23

### Added
- **`/esf-defense-pack`**: generate a portable Defense Pack (HTML + PDF + recording script) from existing ESF artifacts for use in oral defenses and crits. Aggregates Position Statement, Records of Resistance, AI Use Log, Reflection, and Disclosure into a single defensible artifact. PDF rendering uses WeasyPrint (optional; HTML and recording-script outputs always produced).
- **`templates/defense-narrative-template.md`** and **`templates/defense-pack-checklist.md`**: Path 1 (templates-only) manual-assembly support for users without Claude Code installed.
- **Path 2 (conversation tools) prompt updated** with Defense Pack conversational assembly guidance in `prompts/esf-companion.md`.
- **Aggregator `--scan-only` mode**: groundwork for a future periodic gap scanner that surfaces missing artifacts during a project, not just at export time. See [Defense Pack design §13](docs/2026-05-20-defense-pack-design.md).

### Defense Pack workspace flexibility
- **Tolerant workspace layout discovery.** `companion-state.md` is searched at the project root, `esf/`, `projects/_esf/`, and other known locations; works against pre-v0.8.0 installs without migration. Artifact paths fall through canonical → legacy → glob fallback so renamed files (`M2-position-statement.md`) are still found. Optional explicit override via a `## Defense Pack Paths` section in `companion-state.md`.
- **Position Statement heading flexibility.** Element headings are matched via alias sets and parenthetical handling: accepts canonical `## Element 1: My Stance` plus real-student variants like `## My Stance (Creative Direction)`, `## What Matters Most (Non-Negotiables)`, `## AI Boundaries (What I Will Not Compromise On)`.
- **Inline `@resist` / `@default` / `@shift` extraction from process-blog files.** Supports a taught inline-annotation convention where students annotate session narrative inline rather than (or in addition to) producing discrete RoR files. Each `@resist` tag becomes a supplementary Record of Resistance; `@default` / `@shift` counts surface as quantitative process evidence in the rendered pack.
- **Auto-numbering for records missing `record-number:` frontmatter**, so multiple records don't collide at #0.
- **Skip filter for compilation/summary/template files** in `records-of-resistance/`.

### Defense Pack visual model
- **Process-book-inspired single-page aesthetic.** Left-aligned hero (project + byline + frame sentence + metadata grid) replaces the centered cover. Equal-weight "section cards" near the top serve as scannable visual TOC.
- **Records of Resistance featured, not buried.** Formal records render as full-width sequential blocks with a `RoR N · date · @resist · headline` header pattern. Field labels in tracked uppercase sans; AI-suggested content as italic blockquote.
- **Process Blog Timeline** as collapsible session rows with per-session `@resist ×N` counts. Expand to read the records pulled from that session.
- **Key decisions as visible argument blocks.** Curated narrations render as the lead content of each decision (no longer hidden as presenter-only speaker notes). Source attribution prominent; underlying record as collapsible evidence.
- **Defensibility evidence on cover and in disclosure**: process tag counts ("92 @resist moments across 19 sessions") appended to auto-disclosure and shown in a metrics panel.

### Defense Pack rigor (anti-invention)
- **SKILL.md anti-invention guard** instructs Claude to mark unsupported claims `[verify: ...]` rather than fabricate. Voice extraction step requires landing at least two verbatim student phrases unchanged.
- **Narrative `## Disclosure` override**: when the student's narrative includes its own disclosure, it takes precedence over the auto-generated one. Otherwise the auto-disclosure mentions process metrics.
- **Validated against a real student project** (a GitHub-public workspace). The full pipeline (aggregator, fuzzy heading matcher, inline `@resist` extraction, key-decisions curation, narrative drafting under the anti-invention guard, HTML/PDF/recording-script render) produces a faculty-readable defense pack against unmodified student files.

### Infrastructure
- First Python module in the repo (`.claude/skills/esf-defense-pack/bin/esf_pack/`, stdlib-only). Installer adds non-blocking preflight notes for Python 3.10+ and WeasyPrint.
- `pyrightconfig.json` added with extraPaths for the skill module.
- 51 unit tests + 3 e2e tests covering parsers, aggregator, gap detection, schema round-trip, renderer correctness, project-frontmatter filtering, CRLF / BOM tolerance, and the full pipeline against three fixture workspaces (full / partial / minimal).

## [companion-v0.8.0] - 2026-05-18

### Changed
- **Install footprint consolidated under `esf/toolkit/`.** Previously the installer scattered five top-level folders (`prompts/`, `templates/`, `.claude/`, `esf/`, `.codex/`) and 3–4 files (`CLAUDE.md`, `WORKFLOW.md`, `START_HERE.md`, plus `GEMINI.md` or `chatgpt-instructions.md` depending on platform) into the user's project root. After v0.8.0, a fresh Claude Code install drops two visible folders (`esf/`, `.claude/`) and one file (`CLAUDE.md`) at the root; conversation/chatgpt/gemini installs drop just `esf/` plus an optional `.gitignore` (codex still adds `.codex/` because Codex CLI requires that path). Toolkit content (prompts, templates, WORKFLOW.md, START_HERE.md, the platform-specific paste-source files for ChatGPT and Gemini) lives under `esf/toolkit/`. This is especially valuable when installing into a folder that already has other files, like an Obsidian vault.
- **Skill and reference path instructions updated** to point at `esf/toolkit/templates/...` so the model writes from and reads to the new location at runtime. Documentation (README, GETTING_STARTED, WALKTHROUGH, START_HERE, the docs/ folder) similarly updated for post-install paths.
- **`setup-repo.sh`-generated README now describes the new `esf/toolkit/` layout** for new repositories the script bootstraps.

### Migration
- **Re-running the installer on a v0.7.x install auto-migrates legacy paths into `esf/toolkit/`.** The migration block detects `prompts/`, `templates/`, `WORKFLOW.md`, `START_HERE.md`, `GEMINI.md`, and `chatgpt-instructions.md` at the project root, snapshots them under `esf/.migration-snapshot-YYYY-MM-DD/` for rollback, then moves them under `esf/toolkit/`. Idempotent: re-running after a successful migration is a no-op.
- **No action required for users on `/esf-update`.** The next update run migrates automatically; the rollback snapshot is also added to the install commit so you can revert via `git` if needed.

### Compatibility
- **Repo source layout is unchanged.** Path 1 (the no-install workflow that downloads `templates/position-statement.md` directly from GitHub) keeps working against the same URLs. The GitHub download path and the installed path differ on purpose.
- **`.claude/`, `CLAUDE.md`, and `.codex/AGENTS.md` stay at root** because Claude Code and Codex CLI auto-load from those exact paths.

### Internal
- **Smoke test hardened** to not silently abort on `grep -c` returning zero matches under `set -e`. A pre-existing Cowork plugin version-sync FAIL became visible after this change; that FAIL is tracked separately and is unrelated to this release.

## [companion-v0.7.2] - 2026-05-14

### Fixed
- **esf-verify Purpose vs Step 2 surface contradiction.** The Purpose section said "help the user locate original sources" while Step 2 said "Help the user locate the source. ... Do not locate it for them." The intended distinction (offer search terms and database names but do not retrieve and read sources yourself) was coherent on close reading but contradicted on the surface, which could weight an agent's behavior inconsistently. Reworded both: Purpose now reads "point the user toward where to find original sources"; Step 2 now reads "Point the user toward the source ... The user does the lookup; you don't retrieve the source yourself." Same mechanic, no surface contradiction. Applied to both Cowork plugin variant and Claude Code variant.

### Notes
- Closes the variant-consolidation follow-up surfaced during the v0.7.0 spec review on 2026-05-12. The Cowork-vs-Claude-Code "bulk production Gate Mode condition" gap remains deferred (different flavor of variant drift; needs more design work).
- Docs-only change. No behavior change at the install or runtime level. Tagged so `/esf-update` carries the fix to users.

## [companion-v0.7.1] - 2026-05-13

### Fixed
- **Version check is now sound under the companion-vX.Y.Z namespace.** `.claude/esf-version` previously held the legacy `3.10` string (ESF Manuscript v3.x era). After the v0.7.0 namespace shift, a naive numeric or lexical comparison of `3.10` versus `0.7.0` would say "no update available" even when one was. New approach: `.claude/esf-version` holds the full tag string (e.g., `companion-v0.7.0`), and the version check (in `.claude/agents/esf-companion.md` and `.claude/skills/esf-update/SKILL.md`) compares it by string equality against the latest `companion-vX.Y.Z` tag resolved from the GitHub Tags API. Different string means update available. Same resolution code path as `install.sh`.
- **install.sh writes the resolved tag to `.claude/esf-version` directly** on the API install path. The repo's `.claude/esf-version` becomes informational; the installed file always matches the tag that was actually installed. The `--source` path still curls the local file for smoke-test parity.

### Changed
- **install.sh ambient block deduplicated.** The block written to vault `CLAUDE.md` carried three internal duplications: an orphan Nudge mode paragraph repeating Direction (Moment 1), a Pre-draft gates section duplicated by a more detailed Pre-draft and pre-ready gates section, and a Forcing functions section that re-listed Drift, Rejection, and Ownership Moments already covered above. Net: ten lines removed, one canonical statement of each behavior. Renamed Forcing functions to Position Statement gate modes to reflect what actually lives in the section after dedup.
- **Narration is not logging (ambient block clarification).** If the agent describes a Moment firing, walks through what a Moment would catch, or acknowledges that one just fired, the agent must also write the buffer entry. Test-mode prompts ("test moment N," "walk me through Moment N") log as walkthrough firings with a `test: true` flag.

### Notes
- Closes both Phase B follow-ups from the 2026-05-12 vault-repo separation work: the esf-version reconciliation and the install.sh ambient-block dedup.
- No user action required. Next `/esf-update` run installs companion-v0.7.1; subsequent version checks will use the new comparison logic automatically.

## [companion-v0.7.0] - 2026-05-12

### Added
- v0.7.0 hybrid Position Statement nudge ported to the Claude Code variant of `esf-project` (the Cowork plugin variant has carried this since the 2026-05-06 release). Selection card on structural-edit re-fire, four options, NUDGE-SELECTION telemetry to `.session-buffer.md`, Growth Snapshot distribution line.

### Changed
- `/esf-update` and `install.sh` now pull from the latest `companion-vX.Y.Z` tag instead of `main`. The vault runtime now follows tagged releases rather than whatever happens to be on `main`. No action required by users; the transition is automatic on the next `/esf-update` run.

### Notes
- New tag namespace: `companion-vX.Y.Z`. Older `vX.Y.Z` and `cowork-vX.Y.Z` tags are retained but no longer matched by the release-resolution logic. They are kept for historical reference.

## [0.7.0] - 2026-05-06

### Added
- **Hybrid nudge with selection card.** Moment 1 (Position Statement absence on substantive content) now uses two-tier behavior. First touch is a one-line inline reminder (`[ESF: no Position Statement for [doc]; note one?]`) the user can ignore, dismiss, or answer. On a structural edit (claim assertion, first-person observation-as-evidence, attributed quote, specific datum, document argument or frame) without a Position Statement on file, the Companion escalates to an `AskUserQuestion` selection card with four options: "Write one now (offline)," "Talk it through (3 questions)," "Skip for this document," "Skip for this session." Re-fire ceiling: max one selection card per document per session. After a selection, the first-touch inline nudge is also silenced for that document. `silent_mode: true` in `companion-state.md` suppresses both tiers; the Position Statement gate in Gate Mode contexts still applies regardless. Selection events are persisted as `NUDGE-SELECTION` blocks (timestamp, document path, trigger, exact label) in `.session-buffer.md` for telemetry. Growth Snapshot at project close includes the selection distribution (`[N write-now / N talk-through / N skip-doc / N skip-session]`) so reviewers can spot whether skip rates dominate before committing to a selection-card-first design in v0.8.0.
- **`/esf-demo` command.** Guided demo session of the full five-phase workflow on a sample studio project ("Critical Cartography", a series about absent Indigenous place names). Scaffolds a sandbox at `demo/critical-cartography/` with a brief and a rough planning note in user voice. Walks the user through the Position Statement gate (offers the "draft from your materials" path), readability pass, a single Explore challenge thread, condensed Project Scope, pre-seeded Build Practice pieces ([H/M/L] classification), the structural-edit selection card (deterministic firing), the drift detection prompt (deterministic firing at Phase 4 midpoint), Five Questions, reflection, and disclosure. Roughly three to five minutes end-to-end. `/esf-demo --reset` removes the sandbox and restores `companion-state.md` to its pre-demo state from a snapshot in the manifest. Files: `platforms/cowork/commands/esf-demo.md`, `platforms/cowork/templates/demo-project/`.
- **Demo Mode skill section.** New top-level section in `platforms/cowork/skills/esf-project/SKILL.md` between Silence Mode and The Five Phases. Activates via `.esf-demo` manifest in the project folder. Preserves all gates, prompts, and selection cards; substitutes pacing only (one-sentence phase intros, single Explore thread, condensed scope, pre-seeded Build Practice, Five Questions once at Phase 4 close, one reflection prompt). Sandbox boundary: writes only inside the demo project folder. If the user redirects to a real project mid-demo, the skill pauses and asks. Disclosure annotated with a demo-session line. Silent mode override: `/esf-demo` is explicit consent to full scaffolding.
- **Landing page (local, index.html).** Reviewed Figma Make prototype and built improved version: before/after scenario cards in the hero; "What is AI drift?" section preceding the process; amber gate callout mid-process; Five Questions moved below the process flow as numbered cards; Install section restructured with one dominant CTA card (curl + Claude Code) and three secondary cards; FAQ accordion with five blocking questions. File kept local and added to `.gitignore`, not in public repo.
- Frontmatter schema explanations in `templates/project-brief-template.md`: inline comments explaining `required`, `optional`, and `not-required` values for each ESF field.
- **Install hygiene directive.** All ESF artifacts for a context live in `[context base-path]/esf/`: `position-statements/`, `records-of-resistance/`, `ai-use-logs/`. Never scattered into project folders. Folders are created lazily: the first time an artifact is written, its parent folder is created if missing. Empty folders are not pre-created at install. Directive added to agent file, install.sh heredoc, and Cowork skill.
- **Position Statement lookup rule.** Both nudge and gate modes read Current Project and Context from `companion-state.md`, then check `[context base-path]/esf/position-statements/[project-slug].md`. If the file exists, neither mode fires. If Current Project is "not set," the ad-hoc project forcing function fires first; Moment 1 only runs after a project is logged.

### Changed
- Cowork plugin v0.6.0: four behavioral parity fixes brought over from the Claude Code agent (commit `4eb05d9`), addressing ambient-mode failures observed during live session use.
  - `/esf-start` now emits an activation status line (`ESF Companion active. Project: ... Context: ... Active corrections: N.`) before any other output when resuming a project, and surfaces explicit failure messages when `companion-state.md` is missing or unreadable rather than proceeding silently.
  - Cowork `esf-project` Records of Resistance trigger lowered: scope corrections, framing redirections, audience-read corrections, and "not that" signals now trigger RoR offers. Pure formatting cleanup and tool-use corrections still pass silently. Offer language updated.
  - Cowork `esf-project` Position Statement Gate is context-aware: activates on brief frontmatter OR companion-state.md context-level requirement OR ad hoc substantial work without a logged project.
  - Cowork `esf-project` explicitly rejects "a clear task instruction satisfies the Position Statement requirement" as a rationalization. The gate stands even when the deliverable is obvious from the first message.
  - Cowork `esf-project` adds an ad hoc project logging offer when Current Project is "not set" and substantial content is requested, with a declined-path note in the session buffer.
- Cowork plugin version check in `/esf-start`: on session start, fetches the remote `plugin.json` from GitHub main, compares to the version baked into the command, and emits a one-line notice if a newer version is available (`Cowork plugin update available: v[remote] (you have v0.6.0). Run /plugin to update.`). Fails silently on any fetch error. Does not block, does not auto-update. Mirrors the Claude Code agent's `.claude/esf-version` pattern.

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
- Moment 1 escalation: three-level progressive explanation for repeated direction declines, informative, not blocking.
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
