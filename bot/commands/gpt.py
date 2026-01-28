# bot/commands/gpt.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
MODEL = "deepseek/deepseek-chat" 


def handle_gpt(args: list[str]) -> str:
    if not args:
        return "Usage: gpt <question>"

    if not OPENROUTER_API_KEY:
        return "OPENROUTER_API_KEY not set"

    question = " ".join(args)

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/panayotoff/meshtastic-sof-bot",
                "X-Title": "Meshtastic Sofia Bot",
            },
            json={
                "model": MODEL,
                "max_tokens": 80,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant on a mesh radio network. Keep responses VERY short (under 200 characters). Be direct and concise. No markdown.",
                    },
                    {"role": "user", "content": question},
                ],
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        answer = data["choices"][0]["message"]["content"].strip()
        return answer[:240]
    except requests.Timeout:
        return "Request timed out"
    except Exception as e:
        return f"Error: {str(e)[:50]}"
