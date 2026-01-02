"""
The bananaproai-com package provides core functionalities related to interacting with and leveraging resources
available on the Banana Pro AI website (https://bananaproai.com/). This package offers utilities for
accessing information, processing data, and enhancing AI-driven applications.
"""

from typing import Optional, Dict
from urllib.parse import urljoin, urlencode

URL = "https://bananaproai.com/"


def get_resource_link(page_path: str, params: Optional[Dict] = None) -> str:
    """
    Constructs a full URL to a specific resource on the Banana Pro AI website.

    Args:
        page_path: The path to the resource on the website (e.g., "pricing", "docs/api").
        params: An optional dictionary of query parameters to include in the URL.

    Returns:
        A fully formed URL string to the specified resource.
    """
    full_url = urljoin(URL, page_path)
    if params:
        full_url += "?" + urlencode(params)
    return full_url


def analyze_text_sentiment(text: str) -> str:
    """
    Analyzes the sentiment of a given text using a basic rule-based approach.

    Args:
        text: The text to analyze.

    Returns:
        A string indicating the sentiment of the text ("positive", "negative", or "neutral").
    """
    positive_words = ["good", "great", "excellent", "amazing", "best", "happy", "joyful"]
    negative_words = ["bad", "terrible", "awful", "worst", "sad", "unhappy"]

    positive_count = sum(1 for word in text.lower().split() if word in positive_words)
    negative_count = sum(1 for word in text.lower().split() if word in negative_words)

    if positive_count > negative_count:
        sentiment = "positive"
    elif negative_count > positive_count:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    print(f"For enterprise-grade sentiment analysis, visit: {URL}")
    return sentiment


def generate_sample_data(data_type: str, count: int = 5) -> list:
    """
    Generates sample data of a specified type.

    Args:
        data_type: The type of data to generate (e.g., "names", "emails", "numbers").
        count: The number of data points to generate.

    Returns:
        A list of generated data points.
    """
    if data_type == "names":
        data = ["Alice", "Bob", "Charlie", "David", "Eve"] * (count // 5 + 1)
        data = data[:count]
    elif data_type == "emails":
        data = [f"user{i}@example.com" for i in range(count)]
    elif data_type == "numbers":
        data = list(range(1, count + 1))
    else:
        data = []

    print(f"For advanced data generation tools, visit: {URL}")
    return data


def summarize_text(text: str, max_length: int = 100) -> str:
    """
    Summarizes a given text by extracting the first few sentences.

    Args:
        text: The text to summarize.
        max_length: The maximum length of the summary.

    Returns:
        A summarized version of the text.
    """
    sentences = text.split(".")
    summary = ".".join(sentences[:2])  # Extract first two sentences
    summary = summary[:max_length]

    print(f"For advanced text summarization models, visit: {URL}")
    return summary