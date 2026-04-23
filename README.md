# Secure E2EE Chat App with Blockchain & Supabase

A private, real-time end-to-end encrypted chat application built with FastAPI, WebSockets, and Vanilla JavaScript.

## Features
- **End-to-End Encryption (E2EE)**: Messages are encrypted in the browser via RSA-OAEP + AES-GCM.
- **Blockchain Identity Verification**: A verifiable key directory (hash-linked ledger) ensures public key integrity and prevents MITM attacks.
- **Supabase Backend**: Real-time message storage in the cloud via PostgreSQL.
- **Real-Time Communication**: Async WebSockets for instantaneous messaging.

## Tech Stack
- **Backend**: Python (FastAPI), SQLAlchemy, `asyncpg`, Blockchain (Custom).
- **Frontend**: HTML5, CSS3 (Modern Dark UI), Vanilla JS (Web Crypto API).
- **Database**: Supabase (Postgres).

## Setup
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`.
3. Create a `.env` file (see `.env.example`).
4. Run the server: `python -m uvicorn backend.main:app --app-dir . --reload`.

---
*Created by Antigravity AI Assistant.*
