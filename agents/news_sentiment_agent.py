# agents/news_sentiment_agent.py
from typing import List, Dict
import random

class NewsSentimentAgent:
    """
    Stub for fetching news and computing sentiment.
    Replace fetch_news() with real API calls when integrating.
    """

    def fetch_news(self, ticker, limit=5) -> List[Dict]:
        # Placeholder stub — replace with News API or Google Search integration
        sample_headlines = [
            f"{ticker} reports strong quarterly results",
            f"{ticker} faces regulatory scrutiny in region X",
            f"{ticker} announces share buyback",
            f"{ticker} CEO resigns unexpectedly",
            f"{ticker} expands into new market"
        ]
        return [{"title": h, "source": "stub", "date": None} for h in sample_headlines[:limit]]

    def sentiment_score(self, headlines) -> float:
        """
        Very simple sentiment: +1 for positive words, -1 for negative.
        For prototype we randomly generate a score in [-0.4, 0.6].
        """
        # Replace with real LLM or sentiment model
        return round(random.uniform(-0.4, 0.6), 3)
