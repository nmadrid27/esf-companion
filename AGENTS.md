# AGENTS.md

## Cursor Cloud specific instructions

The ESF Companion is a distribution/toolkit repo, not a long-running service. There is
**no package manager, no build step, and no server to start**. It is pure Bash plus a
Python (stdlib-only) "Defense Pack" tool under `.claude/skills/esf-defense-pack/bin/`.
Runtimes (`bash`, `python3`) are system-provided, so the startup update script is
effectively a no-op — there are no dependencies to refresh.

### Tests / checks

CI lives in `.github/workflows/` (`test-install.yml`, `test-defense-pack.yml`). Mirror it locally:

- Python unit tests (124 tests; run from repo root, set the import path):
  `PYTHONPATH=.claude/skills/esf-defense-pack/bin python3 -m unittest discover -s test -t .`
- Bash syntax: `bash -n install.sh setup-repo.sh scripts/release.sh scripts/release-drift.sh .claude/hooks/esf-update-check.sh`
- Defense Pack MANIFEST guard: `bash test/check-defense-pack-manifest.sh`
- Shell test suites: `bash test/test-update-check.sh` and `bash test/test-release-tooling.sh`

### Running the application (two entry points)

- **Installer** (`install.sh`): for local testing always pass `--source "$PWD" --force --platform <claude|conversation>` and run inside a git repo, otherwise it fetches from GitHub release tags. See `test-install.yml` for the exact assertions.
- **Defense Pack generator**: `aggregate.py <workspace> --out pack.json`, then `render.py pack.json narrative.md --out-dir <dir>` (run with the same `PYTHONPATH` as the tests). Fixtures live in `test/fixtures/defense-pack/`.

### Non-obvious gotchas

- **WeasyPrint is optional.** PDF rendering is skipped gracefully when `weasyprint` is absent (1 unit test reports `skipped`). HTML + recording-script outputs are always produced. Installing WeasyPrint pulls heavy system libs (pango/cairo); only do it if you specifically need PDF output.
- **`test/e2e/`** drives a real `claude` CLI (Claude Code, an external product). It is not installed here and is **not** part of CI — `run-e2e.sh` exits early with "claude CLI not found". Skip unless Claude Code is available.
- **`test/smoke-test.sh` has a pre-existing failing assertion** ("Cowork: esf-start.md baked-in version matches plugin.json"): `esf-start.md` was refactored to read the version dynamically from `plugin.json` (no hardcoded literal), but the assertion still greps for the literal. This is repo-level test drift, not an environment problem, and `smoke-test.sh` is not run by CI.
