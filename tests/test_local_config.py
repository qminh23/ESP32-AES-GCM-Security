import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "main"))
from local_config import load_local_environment


class LocalConfigTests(unittest.TestCase):
    def test_quotes_comments_and_environment_priority(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {"MQTT_PORT": "9999"}, clear=True):
            path = Path(directory) / ".env.local"
            path.write_text("export MQTT_BROKER='broker.example'\nMQTT_PORT=8883\nMQTT_PASS='pass # with spaces=$literal' # comment\n")
            load_local_environment(path)
            self.assertEqual(os.environ["MQTT_BROKER"], "broker.example")
            self.assertEqual(os.environ["MQTT_PORT"], "9999")
            self.assertEqual(os.environ["MQTT_PASS"], "pass # with spaces=$literal")

    def test_missing_file(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {}, clear=True):
            load_local_environment(Path(directory) / "missing")
            self.assertEqual(dict(os.environ), {})

    def test_invalid_file_preserves_environment_and_hides_secrets(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {}, clear=True):
            path = Path(directory) / ".env.local"
            path.write_text("MQTT_BROKER=broker.example\nMQTT_PASS='secret")
            with self.assertRaises(ValueError) as error:
                load_local_environment(path)
            self.assertNotIn("secret", str(error.exception))
            self.assertEqual(dict(os.environ), {})
