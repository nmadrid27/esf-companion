# Contributing to the ESF Companion

Thank you for your interest. The ESF Companion is an open framework for maintaining intellectual ownership in AI-assisted work, and community input strengthens it.

## How to Contribute

### Report Issues

Found a broken link, unclear instruction, or factual error? [Open an issue](https://github.com/nmadrid27/esf-companion/issues) with:

- A clear description of the problem
- The file and section where you found it
- A suggested fix, if you have one

### Suggest Improvements

Have an idea for a new template, a better workflow step, or an adaptation for your domain? Open an issue tagged `enhancement` and describe:

- What you want to change or add
- Why the current version falls short
- How your suggestion serves the Companion's core purpose (intellectual ownership in AI-assisted work)

### Submit Changes

1. Fork the repository
2. Create a branch (`git checkout -b your-change`)
3. Make your edits
4. Submit a pull request with a clear description of what changed and why

### Share Your Adaptation

The Companion is designed to be adapted. If you customize it for your domain, team, or institution, consider sharing:

- Open a PR adding your adaptation to a `community/` folder
- Or link to your fork in a GitHub Discussion

## Guidelines

- **Keep it concrete.** The Companion values specificity over abstraction. Contributions should follow the same principle.
- **Write clearly.** Plain language, active voice, short sentences.
- **Cite sources.** If your contribution references research, include full citations. The ESF has zero tolerance for fabricated references.
- **Test your changes.** If you modify templates or install scripts, verify they work before submitting.

## Maintainer tooling (Claude Code)

If you work in this repo with Claude Code, a committed `.claude/settings.json` wires three path-gated `PostToolUse` hooks that run on your edits:

- Editing a Defense Pack module under `.claude/skills/esf-defense-pack/bin/` or `render/` re-runs the MANIFEST guard, so a new module missing from `MANIFEST.txt` is caught before CI.
- Editing a `.sh` file runs `bash -n` (and `shellcheck` if installed).
- Editing a `.py` file runs Pyright against `pyrightconfig.json` (skipped if Pyright is not installed). Note: `pyrightconfig.json` currently excludes the Defense Pack `bin/` tree from analysis (see issue #46), so for those files the hook prints a transparent "not analyzed" note rather than a type-check pass; `test/` and other Python are checked normally.

These are maintainer-only quality gates, not part of the product. They are fail-open, they fire only on the files they target, and `install.sh` never ships them (it fetches shipped hooks by explicit name). The scripts live in `.claude/hooks/dev-*.sh`. To opt out locally, drop the hook from `.claude/settings.json` or override it in the gitignored `.claude/settings.local.json`.

The repo also carries maintainer-only review agents and skills (likewise unshipped). Two subagents: `distribution-integrity-reviewer` (audits the `install.sh` / MANIFEST / cross-platform / release-gate contract) and `skill-frontmatter-reviewer` (validates `SKILL.md` and agent frontmatter). Two user-invocable skills: `/release-notes` (drafts the CHANGELOG `[Unreleased]` section from commits since the last tag) and `/scaffold-esf-skill` (scaffolds a new shipped skill with cross-platform parity and installer registration built in).

## Code of Conduct

All contributors are expected to follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## License

The ESF Companion is released under a dual license. By submitting a contribution, you agree that it will be licensed under the same license that applies to the file or area you are contributing to:

- **Content contributions** (framework material, documentation, templates, prompts, examples, sample projects, course materials, skill definitions) are licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE-CONTENT).
- **Code contributions** (shell scripts, GitHub Actions, plugin manifests, configuration, web assets) are licensed under the [MIT License](LICENSE-CODE).

See [LICENSE](LICENSE) for the full scope of each license and how to determine which applies to a given file. If your contribution touches both code and content, each file is governed by the license appropriate to its type.

When adding a new shell script or other software file, please include the SPDX header on the line directly under the shebang:

```
#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
```

If you do not want to release your contribution under these terms, please open an issue to discuss before submitting a pull request.

## Questions

Open a [GitHub Discussion](https://github.com/nmadrid27/esf-companion/discussions) or reach out via the repository's issue tracker.
