import asyncio
import httpx

async def external_async_task(post_id: int, content: str) -> dict:
    """Simulate aI/O-bound external API call (sentiment analysis)"""
    await asyncio.sleep(1)  # Simulate network delay
    async with httpx.AsyncClient() as client:
        response = await client.get("https://httpbin.org/delay/0.5")
    # Mock sentiment based on content
    if "happy" in content.lower() or "good" in content.lower():
        sentiment = "positive"
        score = 0.9
    elif "sad" in content.lower() or "bad" in content.lower():
        sentiment = "negative"
        score = 0.1
    else:
        sentiment = "neutral"
        score = 0.5
    return {
        "post_id": post_id,
        "httpbin_response": response.json(),
        "sentiment": sentiment,
        "score": score
    }