"""Provider endpoint configuration; never read the workspace .env or call a provider."""
import io
import json
import os
from pathlib import Path
import runpy
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "codebase"))


class EndpointTests(unittest.TestCase):
    def load_adapter(self, base_url=None):
        environment = {"MODEL_PROVIDER": "openai", "MODEL_NAME": "test-model",
                       "API_KEY": "test-placeholder"}
        if base_url is not None:
            environment["OPENAI_BASE_URL"] = base_url
        exists = os.path.exists
        # Skip load_env before it can open the user's file, even if it exists.
        with patch.dict(os.environ, environment, clear=True), patch(
                "os.path.exists", side_effect=lambda path: False if
                Path(path).name == ".env" else exists(path)):
            return runpy.run_path(str(ROOT / "codebase" / "ai.py"))

    def test_default_and_empty_use_openai(self):
        for base_url in (None, ""):
            with self.subTest(base_url=base_url):
                self.assertEqual(self.load_adapter(base_url)["OPENAI_URL"],
                                 "https://api.openai.com/v1/chat/completions")

    def test_custom_endpoint_request_and_api_usage(self):
        adapter = self.load_adapter("https://api.shopaikey.com/v1/")
        reply = {"choices": [{"message": {"content": "test response"}}],
                 "usage": {"prompt_tokens": 12, "completion_tokens": 7}}
        with patch("urllib.request.urlopen", return_value=io.BytesIO(
                json.dumps(reply).encode("utf-8"))) as opener:
            result = adapter["call_model"]("system", "user")
        request = opener.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.shopaikey.com/v1/chat/completions")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-placeholder")
        self.assertEqual(json.loads(request.data)["model"], "test-model")
        self.assertEqual((result["tokens_in"], result["tokens_out"]), (12, 7))


if __name__ == "__main__":
    unittest.main()
