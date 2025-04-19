from flask import Flask, request
import openai
import os
import traceback
import requests

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

@app.route("/", methods=["POST"])
def webhook():
    try:
        print("✅ webhook 起動中")
        body = request.get_json(force=True)
        print("📦 受信データ:", body)

        events = body.get("events", [])
        if not isinstance(events, list) or not events:
            print("⚠️ eventsが空または不正です")
            return "No events", 200

        event = events[0]
        message = event.get("message", {})
        user_message = message.get("text")
        reply_token = event.get("replyToken")

        if not user_message or not reply_token:
            print("⚠️ user_message または reply_token が存在しません")
            return "Invalid format", 200

        print("💬 ユーザーからのメッセージ:", user_message)

        # ✅ systemメッセージ追加（性格・知識の指定）
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "あなたはJリーグのサッカーチーム、ガンバ大阪専門のアナリストです。正確で親しみやすいトーンで、丁寧に回答してください。"
                },
                {"role": "user", "content": user_message}
            ]
        )

        reply_text = response["choices"][0]["message"]["content"]
        print("🤖 GPTからの返答:", reply_text)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
        }
        payload = {
            "replyToken": reply_token,
            "messages": [{"type": "text", "text": reply_text}]
        }

        line_response = requests.post(
            "https://api.line.me/v2/bot/message/reply",
            headers=headers,
            json=payload
        )

        print("📨 LINE送信ステータス:", line_response.status_code)
        print("📨 LINE送信内容:", line_response.text)

        return "OK", 200

    except Exception as e:
        print("🛑 例外エラー:", e)
        traceback.print_exc()
        return "Internal Server Error", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
