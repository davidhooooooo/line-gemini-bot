from flask import Flask, request, abort
import json, os, hmac, hashlib, base64
from urllib.request import Request, urlopen

app = Flask(__name__)

LINE_SECRET = os.environ["LINE_CHANNEL_SECRET"]
LINE_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
GEMINI_KEY = os.environ["GEMINI_API_KEY"]

def verify(body, sig):
    h = hmac.new(LINE_SECRET.encode(), body, hashlib.sha256).digest()
    return hmac.compare_digest(base64.b64encode(h).decode(), sig)

def ask_gemini(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"
    req = Request(url,
        data=json.dumps({"contents": [{"parts": [{"text": text}]}]}).encode(),
        headers={"Content-Type": "application/json"}
    )
    res = json.loads(urlopen(req).read())
    return res["candidates"][0]["content"]["parts"][0]["text"]

def reply_line(token, text):
    req = Request(
        "https://api.line.me/v2/bot/message/reply",
        data=json.dumps({
            "replyToken": token,
            "messages": [{"type": "text", "text": text[:5000]}]
        }).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LINE_TOKEN}"
        }
    )
    urlopen(req)

@app.route("/", methods=["GET"])
def index():
    return "Bot is running"

@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.get_data()
    sig = request.headers.get("X-Line-Signature", "")
    #if not verify(body, sig):
    #    abort(403)
    for event in request.json.get("events", []):
        if event.get("type") == "message" and event["message"]["type"] == "text":
            try:
                text = ask_gemini(event["message"]["text"])
            except Exception as e:
                text = f"錯誤：{e}"
            reply_line(event["replyToken"], text)
    return "OK"
