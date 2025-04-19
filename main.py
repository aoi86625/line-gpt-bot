from flask import Flask, request
import openai
import os
import requests

app = Flask(__name__)

# 環境変数の取得
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY


@app.route("/", methods=['POST'])
def webhook():
    try:
        print("✅ Webhook受信: 開始")

        # JSONデータを取得
        print("① JSON取得前")
        print("🧪 request.data:", request.data)  # ← ここで生のデータを確認！
        body = request.get_json(force=True)
        print("② JSON取得後:", body)

        # eventsの中身を確認
        events = body.get("events", [])
        if not isinstance(events, list) or not events:
            print("⚠️ eventsが空または不正です")
            return "No events", 200

        event = events[0]
        print("③ 最初のevent:", event)

        # ユーザーメッセージの取得
        message = event.get("message", {})
        user_message = message.get("text")
        reply_token = event.get("replyToken")

        if not user_message or not reply_token:
            print("⚠️ message.text または replyToken が存在しません")
            return "Invalid format", 200

        print(f"④ ユーザーからのメッセージ: {user_message}")
        print(f"⑤ reply_token: {reply_token}")

        # ChatGPTに問い合わせ
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        reply_text = response["choices"][0]["message"]["content"]
