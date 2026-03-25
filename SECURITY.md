# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in the ESF Companion (including the install script, setup script, or any file that executes code), please report it privately.

**Do not open a public issue.**

Email: nathan@nathanmadrid.com

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact

I will respond within 72 hours and work with you on a fix before any public disclosure.

## What This Repo Executes

The ESF Companion includes shell scripts that fetch remote content:

- `install.sh` downloads files from this GitHub repository via `curl`
- `setup-repo.sh` creates a local git repository and optionally pushes to GitHub

No data is sent to any external service. All files are installed locally. The scripts do not collect, transmit, or store user data beyond what is written to the local file system.

## Scope

This policy covers:
- `install.sh`
- `setup-repo.sh`
- Any file in `.claude/` that executes or instructs AI tool behavior

Content files (templates, prompts, documentation) are not executable and are out of scope for security reports.
