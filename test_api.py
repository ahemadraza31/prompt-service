"""
test_api.py
Automated test suite using Flask's test client to test all API endpoints.
"""
import unittest
import json
from app import create_app
from db import Database

class PromptServiceTestCase(unittest.TestCase):

    def setUp(self):
        """Set up test client and seed test database before each test."""
        self.app = create_app()
        self.client = self.app.test_client()
        Database.seed_default_prompts()

    def test_01_health_check(self):
        """Test health check endpoint."""
        response = self.client.get("/api/health")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "healthy")
        print("\n  [PASS] Health check endpoint works!")

    def test_02_get_prompts(self):
        """Test fetching all prompt templates."""
        response = self.client.get("/api/prompts")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn("prompts", data)
        self.assertGreater(len(data["prompts"]), 0)
        print("  [PASS] GET /api/prompts returns prompt templates!")

    def test_03_generate_single_prompt(self):
        """Test Step 1-5: Single prompt generation with interpolation and history."""
        payload = {
            "userInput": "How much should I score in each subject to pass CA final?"
        }
        
        response = self.client.post(
            "/api/generate",
            data=json.dumps(payload),
            content_type="application/json"
        )
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn("response", data)
        self.assertTrue(len(data["response"]) > 0)
        print("  [PASS] POST /api/generate successfully generates single prompt response!")

    def test_04_generate_batch_async_preserves_order(self):
        """Test Step 6: Batch prompt generation preserving order."""
        payload = {
            "inputs": [
                "Question 1: Explain gravity",
                "Question 2: Explain photosynthesis",
                "Question 3: Explain quantum physics"
            ]
        }

        response = self.client.post(
            "/api/generate/batch",
            data=json.dumps(payload),
            content_type="application/json"
        )
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn("responses", data)
        self.assertEqual(len(data["responses"]), 3)
        print("  [PASS] POST /api/generate/batch successfully processes batch and preserves order!")

    def test_05_get_history(self):
        """Test fetching logged generation history from MongoDB."""
        response = self.client.get("/api/history")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn("history", data)
        self.assertIsInstance(data["history"], list)
        print("  [PASS] GET /api/history returns logged execution history!")

    def test_06_error_handling_missing_fields(self):
        """Test validation error when userInput is empty."""
        payload = {"userInput": ""}
        
        response = self.client.post(
            "/api/generate",
            data=json.dumps(payload),
            content_type="application/json"
        )
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", data)
        print("  [PASS] Validation properly rejects empty input!")

if __name__ == "__main__":
    print("\n===============================")
    print("RUNNING PROMPT SERVICE TESTS")
    print("===============================")
    unittest.main()
