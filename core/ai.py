def analyze_news(title):
    t = title.lower()

    sentiment = "neutral"
    impact = "MEDIUM"

    if "surge" in t or "rise" in t:
        sentiment = "bullish"
        impact = "HIGH"

    if "drop" in t or "fall" in t:
        sentiment = "bearish"
        impact = "HIGH"

    summary = title[:120]

    return {
        "sentiment": sentiment,
        "impact": impact,
        "summary": summary
    }

def detect_category(title):
    t = title.lower()

    if "bitcoin" in t or "btc" in t:
        return "bitcoin"
    if "ethereum" in t or "eth" in t:
        return "ethereum"
    if "defi" in t:
        return "defi"
    if "nft" in t:
        return "nft"

    return "general"
