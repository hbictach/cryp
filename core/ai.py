def analyze_news(title):
    t = title.lower()

    sentiment = "neutral"
    impact = "MEDIUM"
    summary = "General crypto update"

    if any(x in t for x in ["surge", "pump", "rally"]):
        sentiment = "bullish"
        impact = "HIGH"
        summary = "Strong upward movement detected"

    elif any(x in t for x in ["crash", "hack", "drop"]):
        sentiment = "bearish"
        impact = "HIGH"
        summary = "Market under pressure"

    elif any(x in t for x in ["etf", "sec"]):
        sentiment = "bullish"
        impact = "HIGH"
        summary = "Institutional impact news"

    return {"sentiment": sentiment, "impact": impact, "summary": summary}
