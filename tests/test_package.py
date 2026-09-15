"""Portable package checks; no private data or Codex runtime required."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills' / 'finance-empirical-research'


class PackageTests(unittest.TestCase):
    def test_skill_metadata(self):
        text = (SKILL / 'SKILL.md').read_text(encoding='utf-8')
        self.assertTrue(text.startswith('---\n'))
        metadata = text.split('---', 2)[1]
        self.assertIn('name: finance-empirical-research', metadata)
        self.assertRegex(metadata, r'description: \S')

    def test_local_markdown_links(self):
        for path in [ROOT / 'README.md', *SKILL.rglob('*.md')]:
            text = path.read_text(encoding='utf-8')
            for target in re.findall(r'\]\(([^)]+)\)', text):
                if '://' in target or target.startswith('#'):
                    continue
                with self.subTest(path=path.name, target=target):
                    self.assertTrue((path.parent / target.split('#')[0]).is_file())

    def test_small_skill_payload(self):
        files = [p for p in SKILL.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
        self.assertEqual(len(files), 9)
        for path in files:
            self.assertFalse(path.is_symlink())
            self.assertLess(path.stat().st_size, 100_000)


if __name__ == '__main__':
    unittest.main()
