from flask import Flask, request
import os
import requests
import traceback
from openai import OpenAI  # ✅ 最新版の書き方

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)  # ✅ クライアント生成


@app.route("/", methods=['POST'])
def webhook():
    try:
        print("★★ 最新コードが動いています")
        body = request.get_json(force=True)
        print("受信したJSON:", body)

        events = body.get('events', [])
        if not isinstance(events, list) or not events:
            print("eventsが空または不正です")
            return "No events", 200

        event = events[0]
        message = event.get("message", {})
        user_message = message.get("text")
        reply_token = event.get("replyToken")

        if not user_message or not reply_token:
            print("message.text または replyToken が存在しません")
            return "Invalid format", 200

        # ✅ ChatCompletion 最新版構文
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": user_message
            }]
        )
        reply_text = response.choices[0].message.content
        print("OpenAI応答:", reply_text)

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

        print("LINE応答ステータス:", line_response.status_code)
        print("LINE応答内容:", line_response.text)

        return "OK", 200

    except Exception as e:
        print("⚠️ エラー内容:", e)
        traceback.print_exc()
        return "Internal Server Error", 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
