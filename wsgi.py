from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "🚀 CryptoAlertAlpha is running"

@app.route("/health")
def health():
    return {"status": "ok"}
