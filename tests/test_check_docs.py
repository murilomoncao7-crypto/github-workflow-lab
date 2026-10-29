"""Behavioral examples for the deliberately small documentation checker."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_docs import check_file, check_repository  # noqa: E402


class DocumentationChecks(unittest.TestCase):
    def setUp(self):
        # Fixtures stay within the checkout and are never committed.
        self.temp = tempfile.TemporaryDirectory(prefix=".docs-test-", dir=ROOT)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_existing_relative_links_images_and_encoded_spaces(self):
        self.write("docs/guia com espaco.md", "# Guia\n")
        self.write("image.png", "fixture")
        path = self.write(
            "README.md",
            "[Guia](docs/guia%20com%20espaco.md#titulo)\n"
            "[Guia](<docs/guia com espaco.md>)\n![Imagem](image.png)\n",
        )
        self.assertEqual(check_file(path, self.root), [])

    def test_missing_link_reports_source_line(self):
        path = self.write("README.md", "# Lab\n\n[Guia](missing.md)\n")
        self.assertEqual(
            check_file(path, self.root),
            ["README.md:3: link local inexistente: missing.md"],
        )

    def test_fenced_and_inline_examples_are_not_links(self):
        path = self.write(
            "README.md",
            "`[Exemplo](missing.md)`\n```md\n[Exemplo](missing.md)\n```\n",
        )
        self.assertEqual(check_file(path, self.root), [])

    def test_long_fence_is_not_closed_by_short_fence(self):
        path = self.write("README.md", "````md\n```\n")
        self.assertEqual(check_file(path, self.root), ["README.md:1: bloco de codigo sem fechamento"])

    def test_tilde_fences_close_only_with_matching_marker(self):
        path = self.write("README.md", "~~~text\n```\n~~~\n")
        self.assertEqual(check_file(path, self.root), [])

    def test_link_cannot_escape_repository(self):
        path = self.write("README.md", "[Fora](../README.md)\n")
        self.assertEqual(check_file(path, self.root), ["README.md:1: link sai da raiz do repositorio"])

    def test_external_urls_and_anchor_only_links_need_no_network(self):
        path = self.write("README.md", "[Web](https://example.invalid/x)\n[Secao](#nao-validado)\n")
        self.assertEqual(check_file(path, self.root), [])

    def test_invalid_utf8_is_a_failure(self):
        path = self.root / "README.md"
        path.write_bytes(b"\xff")
        self.assertIn("UTF-8", check_file(path, self.root)[0])

    def test_scans_root_and_nested_docs_but_not_unrelated_directories(self):
        self.write("README.md", "# Lab\n")
        self.write("docs/avancado/guia.md", "[Voltar](../../README.md)\n")
        self.write("fixtures/not-scanned.md", "[Exemplo](missing.md)\n")
        files, errors = check_repository(self.root)
        self.assertEqual(len(files), 2)
        self.assertEqual(errors, [])

    def test_missing_root_and_empty_repository_fail(self):
        self.assertTrue(check_repository(self.root / "missing")[1])
        self.assertTrue(check_repository(self.root)[1])

    def test_cli_exit_codes_are_usable_by_ci(self):
        path = self.write("README.md", "[Erro](missing.md)\n")
        command = [sys.executable, str(ROOT / "scripts/check_docs.py"), "--root", str(self.root)]
        failed = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertEqual(failed.returncode, 1)
        self.assertIn("README.md:1", failed.stdout)
        path.write_text("# Corrigido\n", encoding="utf-8")
        self.assertEqual(subprocess.run(command, capture_output=True, check=False).returncode, 0)


if __name__ == "__main__":
    unittest.main()
