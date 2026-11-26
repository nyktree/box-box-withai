from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class BootstrapContractTests(unittest.TestCase):
    def test_project_entrypoint_and_settings_exist(self):
        self.assertTrue((ROOT / "manage.py").exists())
        self.assertTrue((ROOT / "boxbox" / "settings.py").exists())

    def test_login_template_exists(self):
        self.assertTrue((ROOT / "templates" / "registration" / "login.html").exists())


if __name__ == "__main__":
    unittest.main()
