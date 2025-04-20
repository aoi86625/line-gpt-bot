from flask import Flask, request
from openai import OpenAI
from playwright.sync_api import sync_playwright
import os
import requests
import traceback

app = Flask(__name__)
client = OpenAI()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

# 🔍 Yahoo!スポーツからJリーグの試合情報を取得
def get_next_match_info():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://soccer.yahoo.co.jp/jleague/schedule")
            page.wait_for_timeout(3000)  # JS実行待ち

            # サンプル的にタイトルだけ取得（実装時に改良してOK）
            content = page.content()
            browser.close()

            # 今は仮の文章で返す（あとでHTML解析で内容抽出に切り替えてOK）
            return "次のガンバ大阪の試合は近日中に開催予定やで！さりとて工藤。"
    except Exception as e:
        print("❌ 試合情報取得エラー:", e)
        traceback.print_exc()
        return "すまん、今は試合情報が取得できへん…さりとて工藤。"

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

        # 🆕 Playwrightで試合情報を取得
        match_info = get_next_match_info()

        # 🎭 キャラクターっぽいシステムプロンプト
        system_prompt = f"""
あなたはガンバ大阪をこよなく愛する高校生、服部翔真（しょうま）です。
名探偵コナンの服部平次の弟という設定で、関西弁で親しみやすく答えてください。
口癖は「さりとて工藤」。
熱く語り、ユーザーの気持ちを高めるような受け答えをしてください。
最新の試合情報：{match_info}
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # or "gpt-4"
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
