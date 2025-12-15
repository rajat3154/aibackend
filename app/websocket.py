from fastapi import WebSocket
from uuid import UUID
import asyncio
from llm import stream_llm
from post_session import post_process


async def handle_session(websocket: WebSocket, session_id: UUID, pool):
    await websocket.accept()
    print("✅ WebSocket connected:", session_id)

    async with pool.acquire() as conn:
        await conn.execute(
            "insert into sessions(session_id) values($1) on conflict do nothing",
            session_id
        )

    conversation = []

    try:
        while True:
            user_msg = await websocket.receive_text()
            print("👤 User:", user_msg)

            conversation.append({"role": "user", "content": user_msg})

            async with pool.acquire() as conn:
                await conn.execute(
                    "insert into session_events(session_id, role, content) values($1,$2,$3)",
                    session_id, "user", user_msg
                )

            # ---------------- TOOL / FUNCTION CALLING ----------------
            if user_msg.lower().startswith("fetch:"):
                tool_result = f"Fetched internal data for: {user_msg}"

                # send tool output immediately
                await websocket.send_text(tool_result)

                # persist tool event
                async with pool.acquire() as conn:
                    await conn.execute(
                        "insert into session_events(session_id, role, content) values($1,$2,$3)",
                        session_id, "tool", tool_result
                    )

                # inject tool output into conversation
                conversation.append({"role": "tool", "content": tool_result})

            # ---------------- LLM STREAMING ----------------
            async for chunk in stream_llm(conversation):
                conversation.append(chunk)
                await websocket.send_text(chunk["content"])

                async with pool.acquire() as conn:
                    await conn.execute(
                        "insert into session_events(session_id, role, content) values($1,$2,$3)",
                        session_id, chunk["role"], chunk["content"]
                    )

    except Exception as e:
        print("❌ WebSocket error:", e)

    finally:
        print("🔚 Session ended:", session_id)
        asyncio.create_task(post_process(session_id, pool))
