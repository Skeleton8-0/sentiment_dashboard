import unittest
from unittest.mock import patch, Mock
from utils import api_client

class TestAPIClient(unittest.TestCase):
    def setUp(self):
        self.sample_text = "I love the new features in this product!"
        self.sample_response = [
            {"label": "LABEL_2", "score": 0.91},
            {"label": "LABEL_1", "score": 0.07},
            {"label": "LABEL_0", "score": 0.02}
            ]
    
    @patch("utils.api_client.requests.post")
    def test_analyze_sentiment_success(self, mock_post):
        mock_post.return_value = Mock(status_code=200)
        mock_post.return_value.json.return_value = [self.sample_response]

        result = api_client.analyze_sentiment(self.sample_text)
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["label"], "positive")
        self.assertGreater(result[0]["score"], 0.8)

    @patch("utils.api_client.requests.post")
    def test_analyze_sentiment_failure(self, mock_post):
        mock_post.return_value = Mock(status_code=403, text="Forbidden")
        result = api_client.analyze_sentiment(self.sample_text)
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    @patch("utils.api_client.analyze_sentiment")
    @patch("utils.api_client.extract_keywords")
    def test_batch_analyze_sentiment_with_keywords(self, mock_keywords, mock_sentiment):
        mock_sentiment.return_value = [
            {"label": "positive", "score": 0.91},
            {"label": "neutral", "score": 0.06},
            {"label": "negative", "score": 0.03}
        ]
        mock_keywords.return_value = ["features", "product"]

        input_texts = ["Love it", "Not great"]
        results = api_client.batch_analyze_sentiment_with_keywords(input_texts, delay=0)

        self.assertEqual(len(results), 2)
        for r in results:
            self.assertIn("text", r)
            self.assertIn("sentiment", r)
            self.assertIn("keywords", r)

    @patch("utils.api_client.analyze_sentiment", side_effect=Exception("Test error"))
    def test_batch_handles_exception(self, mock_sentiment):
        input_texts = ["This will fail"]
        results = api_client.batch_analyze_sentiment_with_keywords(input_texts, delay=0)

        self.assertEqual(len(results), 1)
        self.assertIn("error", results[0])
        self.assertIn("text", results[0])

    if __name__ == "__main__":
        unittest.main()