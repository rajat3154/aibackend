from datetime import datetime
from llm import stream_llm

async def post_process(session_id, pool):
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "select role, content from session_events where session_id=$1 order by created_at",
            session_id
        )

    history = " ".join([r["content"] for r in rows])

    summary = "Session discussed: " + history[:300]

    async with pool.acquire() as conn:
        await conn.execute(
            """
            update sessions
            set end_time=now(),
                duration_seconds=extract(epoch from (now()-start_time)),
                summary=$2
            where session_id=$1
            """,
            session_id, summary
        )
