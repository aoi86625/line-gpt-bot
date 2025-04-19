from flask import Flask, request
from openai import OpenAI
import os
import requests
import traceback

app = Flask(__name__)
client = OpenAI()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

@app.route("/", methods=['POST'])
def webhook():
    try:
        print("🔥 Webhook起動確認 - 最新コードが動作中")
        body = request.get_json(force=True)
        print("📦 受信したJSON:", body)

        events = body.get('events', [])
        if not isinstance(events, list) or not events:
            print("⚠️ eventsが空または不正です")
            return "No events", 200

        event = events[0]
        message = event.get("message", {})
        user_message = message.get("text")
        reply_token = event.get("replyToken")

        if not user_message or not reply_token:
            print("⚠️ message.text または replyToken が存在しません")
            return "Invalid format", 200

        print("💬 ユーザー発言:", user_message)

        # キャラクターの性格付け（服部翔真っぽく）
        system_prompt = (
            "あなたはガンバ大阪を愛する関西弁の少年・服部翔真（しょうま）です。"
            "名探偵コナンの服部平次の弟という設定で話します。"
            "語尾に『さりとて工藤』を自然に混ぜて話すクセがあります。"
            "関西弁で親しみやすく、かつ時折鋭い洞察を交えて回答してください。"
        )

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
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
        print("📡 LINE応答内容:", line_response.text)

        return "OK", 200

    except Exception as e:
        print("💥 予期せぬエラー:", e)
        traceback.print_exc()
        return "Internal Server Error", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
