from flask import Flask, request
from openai import OpenAI
import os
import requests
import traceback

app = Flask(__name__)
client = OpenAI()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

# 🗂 キャッシュされた試合情報を読み込む関数
def load_match_info():
    try:
        with open("cache/match_info.txt", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print("⚠️ キャッシュ読込エラー:", e)
        return "すまん、まだ試合情報がキャッシュされてへんみたいや…さりとて工藤。"

@app.route("/", methods=['POST'])
def webhook():
    try:
        print("🔥 Webhook起動確認")
        body = request.get_json(force=True)
        print("📦 受信JSON:", body)

        events = body.get('events', [])
        if not events or not isinstance(events, list):
            return "No events", 200

        event = events[0]
        message = event.get("message", {})
        user_message = message.get("text")
        reply_token = event.get("replyToken")

        if not user_message or not reply_token:
            return "Invalid message format", 200

        print("💬 ユーザー発言:", user_message)

        # 📄 キャッシュから試合情報を読み込む
        match_info = load_match_info()

        # 🎭 キャラプロンプト
        system_prompt = f"""
あなたはガンバ大阪をこよなく愛する高校生「服部翔真（しょうま）」です。
名探偵コナンの服部平次の弟という設定で、関西弁で親しみやすく答えてください。
口癖は「さりとて工藤」。熱く、時におちゃめに、応援の気持ちを込めて回答してください。

【最新の試合情報】
{match_info}
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # 必要に応じて "gpt-4" に変更可
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )

        reply_text = response.choices[0].message.content.strip()
        print("🤖 ChatGPT応答:", reply_text)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
        }
        payload = {
            "replyToken": reply_token,
            "messages": [{
                "type": "text",
                "text": reply_text
            }]
        }

        line_response = requests.post(
            "https://api.line.me/v2/bot/message/reply",
            headers=headers,
            json=payload
        )

        print("📡 LINE応答ステータス:", line_response.status_code)
        return "OK", 200

    except Exception as e:
        print("❌ Webhook処理エラー:", e)
        traceback.print_exc()
        return "Internal Server Error", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
