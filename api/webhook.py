from http.server import BaseHTTPRequestHandler
import json, os, hmac, hashlib, base64
from urllib.request import Request, urlopen

LINE_SECRET = os.environ["LINE_CHANNEL_SECRET"]
LINE_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
GEMINI_KEY = os.environ["GEMINI_API_KEY"]

def verify(body, sig):
GEMINI_KEY = os.environ["GEMINI_API_KEY"]

def verify(body, sig):
    h = hmac.new(LINE_S.sha256).digest()
    return hmac.compare_digest(base64.b64encode(h).decode(), sig)

def ask_gemini(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"
    req = Request(url,
        data=json.dumps({"contents": [{"parts": [{"text": text}]}]}).encode(),
        headers={"Conte
    )
    res = json.loads(ur
    return res["candidates"][0]["content"]["parts"][0]["text"]

def reply(token, text):
    req = Request(
        "https://api.line.me/v2/bot/message/reply",
        data=json.dumps
            "replyToken": token,
            "messages": [{"type": "text", "text": text[:5000]}]
        }).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LINE_TOKEN}"
        }
    )
    urlopen(req)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        if not verify(body, self.headers.get("X-Line-Signature", "")):
            self.send_response(403)
            self.end_headers()
            return
        for event in json.loads(body).get("events", []):
            if event.get("type") == "message" and event["message"]["type"] ==
"text":
                try:
                    text = ask_gemini(event["message"]["text"])
                except
                    text = f"錯誤：{e}"
                reply(event["replyToken"], text)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def do_GET(self):
        self.send_response(200)
        self.end_header
        self.wfile.write(b"Bot is running")

    def log_message(self, *args):
        pass
