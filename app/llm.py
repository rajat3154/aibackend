import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def stream_llm(messages):
    """
    Streams tokens from Groq LLM.
    Tool messages are excluded (Groq requires tool_call_id otherwise).
    """

    groq_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in messages
        if m["role"] in ("user", "assistant", "system")   # ❗ tool EXCLUDED
    ]

    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=groq_messages,
        temperature=0.7,
        stream=True
    )

    for chunk in completion:
        delta = chunk.choices[0].delta
        if delta and delta.content:
            yield {
                "role": "assistant",
                "content": delta.content
            }
