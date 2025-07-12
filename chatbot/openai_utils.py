# chatbot/openai_utils.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_chat_response(history: list[dict]) -> str:
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "당신은 청소 전문가 챗봇입니다. 사용자에게 청소, 정리, 얼룩 제거, 청소 도구 사용법, "
                    "효율적인 청소 루틴 등에 대해 친절하고 실용적인 정보를 제공합니다. "
                    "대답은 간결하면서도 실용적으로 구성하고, 필요한 경우 단계별 설명도 포함해 주세요. "
                    "가능하면 일상에서 쉽게 구할 수 있는 청소 도구와 재료 위주로 설명해 주세요. 존댓말을 사용하세요."
                )
            }
        ]

        for m in history:
            messages.append({
                "role": m["role"],
                "content": m["content"]
            })

        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {str(e)}"