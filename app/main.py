from fastapi import FastAPI, WebSocket
from uuid import UUID
from db import get_db_pool
from websocket import handle_session

app = FastAPI()
pool = None

@app.on_event("startup")
async def startup():
    global pool
    pool = await get_db_pool()

@app.websocket("/ws/session/{session_id}")
async def ws_endpoint(websocket: WebSocket, session_id: UUID):
    await handle_session(websocket, session_id, pool)
