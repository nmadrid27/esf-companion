# ESF Companion end-to-end tests

Behavioral tests that exercise the installed Companion as a real user would.
Each scenario installs the plugin into a fresh temp workspace, seeds state,
sends one or more user messages through `claude -p`, and asserts against the
transcript and the resulting workspace state.

This complements `test/smoke-test.sh` (which validates installer mechanics and
static content) by testing that the agent actually *fires* the behaviors the
spec describes.

## Requirements

- `bash`
- `claude` CLI on `PATH` (Claude Code; used to run the Companion under test)
- Network access (Claude Code needs to reach the Anthropic API)

## Usage

```bash
bash test/e2e/run-e2e.sh
```

Each scenario runs in an isolated workspace under `/tmp/esf-e2e/<scenario>`.
Workspaces are left on disk after the run so you can inspect them.

## Writing a scenario

A scenario is a bash script in `scenarios/` that:

1. Accepts two arguments: `WORKSPACE` (tmp dir to set up) and `REPO_ROOT`.
2. Installs the plugin via `install.sh --source "$REPO_ROOT" --force --platform claude`.
3. Seeds any pre-existing state the scenario requires.
4. Runs `claude -p` with one or more prompts.
5. Asserts against the response text and the workspace filesystem.
6. Exits 0 on pass, non-zero on fail.

See existing scenarios for the shape.

## Known limitations

- `claude -p` is a one-shot invocation. Multi-turn scenarios need to pass
  full conversation context in a single prompt, or use `--continue` if the
  version supports it.
- Scenarios depend on the Anthropic API; they can't run offline.
- Pattern matching on response text is fragile to wording changes in insight
  blocks. Keep assertions on distinctive tokens the spec mandates verbatim
  (e.g. "ESF Companion active", "★ Bulk production").
