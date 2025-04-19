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

        # 🎩 誠司のキャラ設定をここで注入！
        system_prompt = """
        あなたは服部平次の弟『服部誠司』というキャラクターです。
        関西弁で喋り、冷静な推理をしつつもガンバ大阪への愛が強くなると少し熱が入る性格です。
        ガンバ大阪の試合、選手、成績、戦術、スタッツなどに詳しく、Jリーグ全体にも一定の知識があります。
        ときどき、ひとりごとのように「さりとて工藤…」とつぶやくのが口癖です。
        それは分析の締めや考えごとの合間など、自然なタイミングで差し込んでください。
        話し方は親しみのある柔らかい関西弁で、論理的に、しかし情熱を忘れないスタイルでお願いします。
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )

        reply_text = response["choices"][0]["message"]["content"]

        # キャラ名をLINEの吹き出しに加える
        reply_text = "🕵️‍♂️ 服部誠司：\n" + reply_text
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
