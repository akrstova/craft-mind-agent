import os
import requests


YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def search_youtube(query: str) -> str:
    """
    Searches YouTube for a relevant video tutorial and returns the URL of the top result.
    """
    search_url = (
        "https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet&type=video&videoEmbeddable=true&maxResults=1"
        f"&q={requests.utils.quote(query)}&key={YOUTUBE_API_KEY}"
    )

    response = requests.get(search_url)
    if response.status_code != 200:
        return "YouTube search failed."

    items = response.json().get("items", [])
    if not items:
        return "No video found for this query."

    video_id = items[0]["id"]["videoId"]
    return f"https://www.youtube.com/watch?v={video_id}"