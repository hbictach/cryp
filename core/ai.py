import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_news(title):
    try:
        prompt = f"""
        Analyze this crypto news:

        "{title}"

        Return JSON:
        - summary (short)
        - sentiment (bullish/bearish/neutral)
        - impact (LOW/MEDIUM/HIGH)
        - insight (what it means for traders)
        """

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.choices[0].message.content

        # hack بسيط (حتى نسرعو)
        return {
            "summary": text,
            "sentiment": "🟢",
            "impact": "HIGH",
            "insight": text
        }

    except Exception as e:
        print("AI error:", e)
        return {
            "summary": "Market update",
            "sentiment": "⚪",
            "impact": "MEDIUM",
            "insight": "No data"
        }
