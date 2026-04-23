import json
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_

from .database import engine, Base, get_db
from .models import User, Message
from .auth import get_password_hash, verify_password, create_access_token, decode_access_token
from .websocket_manager import manager
from .blockchain import blockchain_instance

app = FastAPI(title="Secure E2EE Chat")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# We will mount the frontend static files at root
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # Tables are created on Supabase or SQLite depending on .env
        await conn.run_sync(Base.metadata.create_all)

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("frontend/index.html", "r") as f:
        return f.read()

@app.get("/chat", response_class=HTMLResponse)
async def read_chat():
    with open("frontend/chat.html", "r") as f:
        return f.read()

@app.post("/register")
async def register(request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    public_key = data.get("public_key")
    
    if not username or not password or not public_key:
        raise HTTPException(status_code=400, detail="Missing fields")
        
    result = await db.execute(select(User).where(User.username == username))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
        
    hashed_password = get_password_hash(password)
    new_user = User(username=username, password_hash=hashed_password, public_key=public_key)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # 1. Add to Blockchain for Immutable ID Verification
    blockchain_instance.add_block({
        "user_id": new_user.id,
        "username": username,
        "public_key": public_key
    })
    
    return {"message": "User created successfully"}

@app.post("/login")
async def login(request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    token = create_access_token(data={"sub": user.username, "id": user.id})
    return {"access_token": token, "token_type": "bearer", "user_id": user.id, "username": user.username}

@app.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User.id, User.username, User.public_key))
    users = result.all()
    return [{"id": row.id, "username": row.username, "public_key": row.public_key} for row in users]

@app.get("/blockchain")
async def get_blockchain():
    return {
        "chain": [b.__dict__ for b in blockchain_instance.chain],
        "is_valid": blockchain_instance.is_chain_valid()
    }

@app.get("/messages/{contact_id}")
async def get_messages(contact_id: int, token: str, db: AsyncSession = Depends(get_db)):
    user_info = decode_access_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = user_info["id"]

    result = await db.execute(
        select(Message).where(
            or_(
                and_(Message.sender_id == user_id, Message.receiver_id == contact_id),
                and_(Message.sender_id == contact_id, Message.receiver_id == user_id)
            )
        ).order_by(Message.id)
    )
    messages = result.scalars().all()
    return messages

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str, db: AsyncSession = Depends(get_db)):
    user_info = decode_access_token(token)
    if not user_info:
        await websocket.close(code=1008)
        return
        
    user_id = user_info["id"]
    await manager.connect(user_id, websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            
            receiver_id = payload.get("receiver_id")
            enc_msg = payload.get("encrypted_message")
            enc_aes = payload.get("encrypted_aes_key")
            
            if receiver_id and enc_msg and enc_aes:
                timestamp = datetime.utcnow().isoformat()
                
                new_msg = Message(
                    sender_id=user_id,
                    receiver_id=receiver_id,
                    encrypted_message=enc_msg,
                    encrypted_aes_key=enc_aes,
                    timestamp=timestamp
                )
                db.add(new_msg)
                await db.commit()
                await db.refresh(new_msg)
                
                msg_to_send = {
                    "id": new_msg.id,
                    "sender_id": user_id,
                    "receiver_id": receiver_id,
                    "encrypted_message": enc_msg,
                    "encrypted_aes_key": enc_aes,
                    "timestamp": timestamp
                }
                await manager.send_personal_message(msg_to_send, receiver_id)
                await manager.send_personal_message(msg_to_send, user_id)
                
    except WebSocketDisconnect:
        manager.disconnect(user_id)
