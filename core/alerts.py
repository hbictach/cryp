ALERT_KEYWORDS = [
    "sec","etf","blackrock","approval","hack","exploit",
    "ban","regulation","lawsuit","crash","surge","whale",
    "bitcoin","ethereum"
]

def is_alert(title):
    t = title.lower()
    return any(k in t for k in ALERT_KEYWORDS)
