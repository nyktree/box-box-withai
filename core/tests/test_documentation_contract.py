from pathlib import Path
from django.test import SimpleTestCase

ROOT = Path(__file__).resolve().parents[2]

class DocumentationContractTests(SimpleTestCase):
    def test_readme_has_reproducible_commands_and_docs_exist(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for text in ("python -m venv", "pip install -r requirements.txt", "python manage.py migrate", "python manage.py seed_demo", "python manage.py test"):
            self.assertIn(text, readme)
        for name in ("requirements.md", "architecture.md", "database.md", "testing.md", "limitations.md"):
            self.assertTrue((ROOT / "docs" / name).exists())
