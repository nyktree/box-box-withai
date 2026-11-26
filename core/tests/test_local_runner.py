from pathlib import Path
from django.conf import settings
from django.test import SimpleTestCase

class LocalRunnerTests(SimpleTestCase):
    def test_windows_runner_contains_required_startup_steps(self):
        path = Path(settings.BASE_DIR) / "run-boxbox.bat"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8").lower()
        for required in ("%~dp0", "python -m venv .venv", "requirements.txt", "manage.py migrate", "manage.py runserver 127.0.0.1:8000", "if errorlevel 1 goto :error"):
            with self.subTest(required=required): self.assertIn(required, text)
