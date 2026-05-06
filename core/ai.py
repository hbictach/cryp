def analyze_news(title):
    t = title.lower()

    sentiment = "neutral"
    impact = "MEDIUM"

    bullish_words = ("surge", "rise", "rally", "gain", "soar", "jump", "breakout", "record high")
    bearish_words = ("drop", "fall", "crash", "plunge", "slump", "selloff", "liquidation")
    high_impact_words = (
        "sec", "etf", "fed", "hack", "exploit", "lawsuit", "ban", "approval",
        "blackrock", "binance", "coinbase", "whale", "regulation",
    )

    if any(word in t for word in bullish_words):
        sentiment = "bullish"
        impact = "HIGH"

    if any(word in t for word in bearish_words):
        sentiment = "bearish"
        impact = "HIGH"

    if any(word in t for word in high_impact_words):
        impact = "HIGH"

    summary = title[:120]

    return {
        "sentiment": sentiment,
        "impact": impact,
        "summary": summary,
    }


def detect_category(title):
    t = title.lower()

    if "bitcoin" in t or "btc" in t:
        return "bitcoin"
    if "ethereum" in t or "eth" in t:
        return "ethereum"
    if "solana" in t or "sol" in t:
        return "solana"
    if "xrp" in t or "ripple" in t:
        return "xrp"
    if "binance" in t or "bnb" in t:
        return "binance"
    if "memecoin" in t or "meme coin" in t or "dogecoin" in t or "shib" in t:
        return "memecoins"
    if "defi" in t or "staking" in t or "yield" in t:
        return "defi"
    if "nft" in t or "ordinals" in t:
        return "nft"
    if "etf" in t or "sec" in t or "regulation" in t or "lawsuit" in t:
        return "regulation"
    if "ai" in t or "artificial intelligence" in t or "depin" in t:
        return "ai"
    if "hack" in t or "exploit" in t or "security" in t:
        return "security"

    return "general"
