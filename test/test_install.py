"""Installer regressions. Runs only in temporary repositories and homes."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.workspace = self.base / 'workspace'
        self.workspace.mkdir()
        self.env = dict(os.environ, HOME=str(self.base / 'home'))
        Path(self.env['HOME']).mkdir()
        self.git('init', '-q')
        self.git('config', 'user.name', 'Install Test')
        self.git('config', 'user.email', 'test@example.invalid')

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.workspace, env=self.env,
                              text=True, capture_output=True, check=True)

    def install(self, platform='codex', *args, success=True):
        result = subprocess.run(['bash', str(ROOT / 'install.sh'), '--force',
                                 '--source', str(ROOT), '--platform', platform, *args],
                                cwd=self.workspace, env=self.env,
                                text=True, capture_output=True)
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        return result

    def test_preserves_git_index_and_unrelated_work(self):
        (self.workspace / 'unrelated.txt').write_text('User work\n')
        self.git('add', 'unrelated.txt')
        before = self.git('diff', '--cached').stdout
        for platform in ('chatgpt', 'claude'):
            self.install(platform, '--scope', 'project')
            self.assertEqual(self.git('diff', '--cached').stdout, before)
            self.assertEqual(self.git('log', '--all', '--oneline').stdout, '')
        self.assertEqual(self.git('ls-files').stdout, 'unrelated.txt\n')

    def test_ignored_toolkit_does_not_abort(self):
        (self.workspace / '.gitignore').write_text('esf/\n')
        self.install('chatgpt')
        self.assertTrue((self.workspace / 'esf/toolkit/chatgpt-instructions.md').exists())

    def test_fresh_claude_user_scope(self):
        self.install('claude', '--scope', 'user')
        self.assertTrue((Path(self.env['HOME']) / '.claude/statusline-command.sh').exists())

    def test_invalid_arguments_fail_before_installing(self):
        for args in [('--platform',), ('--scope',), ('--source',), ('--platform=',),
                     ('--platform', ''), ('--platform', '--no-ambient'), ('--typo',)]:
            with self.subTest(args=args):
                self.install('chatgpt', *args, success=False)
                self.assertFalse((self.workspace / 'esf').exists())

    def test_codex_refresh_disable_and_buffer_ignore(self):
        self.install()
        agents = self.workspace / 'AGENTS.md'
        text = agents.read_text().replace('### Session start', '### Outdated session start')
        agents.write_text('# User rules\n' + text + '\n## Other user rules\nKeep this.\n')
        self.install()
        self.assertNotIn('Outdated', agents.read_text())
        self.assertIn('Keep this.', agents.read_text())
        self.assertEqual(agents.read_text().count('## ESF Companion (Always On)'), 1)
        self.git('check-ignore', 'esf/demo/logs/.session-buffer.md')
        self.install('codex', '--no-ambient')
        self.assertNotIn('Always On', agents.read_text())
        self.assertIn('Keep this.', agents.read_text())

    def test_claude_refresh_and_disable(self):
        self.install('claude', '--scope', 'project')
        path = self.workspace / 'CLAUDE.md'
        path.write_text(path.read_text().replace('### Session start', '### Outdated session start')
                        + '\n## User rules\nKeep this.\n')
        self.install('claude', '--scope', 'project')
        self.assertNotIn('Outdated', path.read_text())
        self.install('claude', '--scope', 'project', '--no-ambient')
        self.assertNotIn('Always On', path.read_text())
        self.assertIn('Keep this.', path.read_text())

    def test_unknown_ambient_boundary_is_preserved(self):
        agents = self.workspace / 'AGENTS.md'
        original = '# User rules\n## ESF Companion (Always On)\nUnknown old block\n'
        agents.write_text(original)
        self.install(success=False)
        self.assertEqual(agents.read_text(), original)

    def test_failed_download_retry_and_managed_file_preservation(self):
        mock = self.base / 'bin'
        mock.mkdir()
        curl = mock / 'curl'
        real = shutil.which('curl')
        for platform, target in [('chatgpt', 'esf/toolkit/prompts/companion.md'),
                                 ('claude', '.claude/agents/esf-companion.md')]:
            with self.subTest(platform=platform):
                path = self.workspace / target
                path.parent.mkdir(parents=True, exist_ok=True)
                if platform == 'claude':
                    path.write_text('Existing managed file\n')
                curl.write_text('#!/usr/bin/env bash\n'
                                f'if [[ "$*" == *"/{target.removeprefix("esf/toolkit/")}"* ]]; then\n'
                                ' while [ "$#" -gt 0 ]; do\n'
                                '  if [ "$1" = -o ]; then printf "partial" > "$2"; exit 18; fi\n'
                                '  shift\n done\nfi\n'
                                f'exec "{real}" "$@"\n')
                curl.chmod(0o755)
                original_path = self.env['PATH']
                self.env['PATH'] = str(mock) + ':' + original_path
                self.install(platform, '--scope', 'project', success=False)
                self.env['PATH'] = original_path
                if platform == 'claude':
                    self.assertEqual(path.read_text(), 'Existing managed file\n')
                else:
                    self.assertFalse(path.exists())
                self.install(platform, '--scope', 'project')
                self.assertEqual(path.read_bytes(), (ROOT / target.removeprefix('esf/toolkit/')).read_bytes())

    def test_chatgpt_explains_state_initialization(self):
        result = self.install('chatgpt')
        self.assertIn('Copy it to esf/companion-state.md', result.stdout)
        self.assertFalse((self.workspace / 'esf/companion-state.md').exists())


if __name__ == '__main__':
    unittest.main()
