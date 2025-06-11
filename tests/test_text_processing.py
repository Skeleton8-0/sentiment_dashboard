import unittest
from utils.text_processing import extract_keywords, explain_sentiment

class TestTextProcessing(unittest.TestCase):
    def test_extract_keywords_returns_keywords(self):
        text = "Artificial intelligence is transforming the technology industry rapidly."
        keywords = extract_keywords(text, top_n=3)
        self.assertIsInstance(keywords, list)
        self.assertTrue(len(keywords) <= 3)
        for kw in keywords:
            self.assertIsInstance(kw, str)
            self.assertTrue(len(kw) > 0)

    def test_extract_keywords_handles_empty_text(self):
        text = ""
        keywords = extract_keywords(text)
        self.assertEqual(keywords, [])

    def test_explain_sentiment_with_valid_result(self):
        result = [
            {"label": "positive", "score": 0.92},
            {"label": "neutral", "score": 0.06},
            {"label": "negative", "score": 0.02},
        ]
        explanation = explain_sentiment(result)
        self.assertIn("positive", explanation.lower())
        self.assertIn("%", explanation)

    def test_explain_sentiment_with_error(self):
        result = {"error": "API error"}
        explanation = explain_sentiment(result)
        self.assertIn("could not be analyzed", explanation.lower())

    def test_explain_sentiment_with_empty_list(self):
        result = []
        explanation = explain_sentiment(result)
        self.assertIn("no sentiment", explanation.lower())

    if __name__ == "__main__":
        unittest.main()