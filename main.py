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
        print("⑥ ChatGPT応答:", reply_text)

        # LINEに返信
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

        print("⑦ LINE応答ステータス:", line_response.status_code)
        print("⑧ LINE応答内容:", line_response.text)

        return "OK", 200

    except Exception as e:
        print("⚠️ エラー内容:", e)
        return "Internal Server Error", 500


# Flaskアプリ起動設定（Render向け）
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
