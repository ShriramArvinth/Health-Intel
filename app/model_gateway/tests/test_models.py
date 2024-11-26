import sys
from pathlib import Path

sys.path[0] = str(Path(__file__).parent.parent.parent.parent)

import unittest
from anthropic import Anthropic
from app.model_gateway.src import (
    claude_sonnet,
    claude_haiku
)

class TestGateway(unittest.TestCase):
    def setUp(self) -> None:
        with open("../../secrets/anthropic_key.txt", "r") as f:
            api_key = f.readline().strip()
        self.client = Anthropic(api_key = api_key)

        # prompt for prompt caching
        self.prompt_w_caching = {
            "system": [{
                "type": "text",
                "text": "You are a helpful bot who just says 'Hello'" + "\n",
                "cache_control": {"type": "ephemeral"}
            }],
            "messages": [{
                "role": "user",
                "content": "respond with just 'Hello.'"
            }]
        }

        # prompt without prompt caching
        self.prompt_wo_caching = {
            "system": [{
                "type": "text",
                "text": "You are a helpful bot who just says 'Hello'" + "\n",
            }],
            "messages": [{
                "role": "user",
                "content": "respond with just 'Hello.'"
            }]
        }

    def tearDown(self) -> None:
        del self.client, self.prompt_w_caching, self.prompt_wo_caching

    def test_haiku(self):
        """Test Claude 3.5 Haiku response"""
        response_w_caching = claude_haiku.infer(client=self.client, prompt=self.prompt_w_caching)
        response_wo_caching = claude_haiku.infer(client=self.client, prompt=self.prompt_wo_caching)
        self.assertEqual(response_w_caching, response_wo_caching)

    def test_sonnet(self):
        """Test Claude 3.5 Sonnet Response"""
        response_w_caching = "".join(claude_sonnet.infer(client=self.client, prompt=self.prompt_w_caching))
        response_wo_caching = "".join(claude_sonnet.infer(client=self.client, prompt=self.prompt_wo_caching))
        self.assertEqual(response_w_caching, response_wo_caching)

if __name__ == "__main__":
    unittest.main(verbosity=2)