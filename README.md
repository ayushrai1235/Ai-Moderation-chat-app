# 🛡️ AI Moderation Chat App

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95%2B-009688)
![WebSockets](https://img.shields.io/badge/WebSockets-Real--Time-orange)
![React](https://img.shields.io/badge/React-18-61DAFB)
![License](https://img.shields.io/badge/License-MIT-green)

A professional, real-time chat application featuring **private 1-on-1 messaging**, **secure authentication**, and **AI-powered content moderation** using Google Gemini 2.5 Flash. Designed with a modern, WhatsApp-inspired UI.

---

## 🚀 Features

### 💬 Real-time Communication
*   **Private Chats**: Secure 1-on-1 conversations with real-time delivery via **WebSockets**.
*   **Live Status**: Online/Offline indicators for connectivity.
*   **User Search**: Find and connect with other users instantly.

### 🤖 AI-Powered Moderation
*   **Text Analysis**: Detects toxicity, hate speech, and harassment in real-time.
*   **Image Safety**: Scans uploaded images for unsafe content.
*   **Intelligent Filtering**:
    *   **Block**: Harmful content is blocked and visible *only* to the sender (shadow ban).
    *   **Warn**: Potentially unsafe content is flagged with a warning label.
    *   **Allow**: Safe content is broadcast instantly.
*   **Explanations**: AI provides reasons for flagged/blocked content.

### 📂 Media Sharing
*   **File Uploads**: Securely upload images, videos, and documents.
*   **Cloud Storage**: Integrated with **Cloudinary** for scalable asset management.
*   **Previews**: Rich interaction with image/video previews in the chat bubble.

### 🔐 Security & Auth
*   **Authentication**: Full Register/Login flow with Argon2 password hashing.
*   **Session Management**: Redis-backed session storage with TTL.
*   **Database**: robust data persistence using **Supabase (PostgreSQL)**.

---

## 🏗️ Architecture

The application follows a clean, modular architecture separating concerns between the frontend client, API server, and background services.

```mermaid
graph TD
    Client[React Frontend] <-->|WebSocket/HTTP| API[FastAPI Backend]
    
    subgraph Backend Services
        API -->|Auth/Data| DB[(Supabase Postgres)]
        API -->|Buffer/PubSub| Redis[(Redis)]
        API -->|Moderation| AI[Google Gemini API]
        API -->|Media| Cloud[Cloudinary]
    end
    
    Redis -->|Queue| Pipeline[Moderation Pipeline]
    Pipeline --> AI
    Pipeline -->|Result| Redis
```

### Tech Stack

| Component | Technology | Description |
|-----------|------------|-------------|
| **Frontend** | React, Tailwind CSS | Vite-powered SPA with Lucide icons. |
| **Backend** | FastAPI | High-performance async Python framework. |
| **Real-time** | **WebSockets** | Native bi-directional communication protocol. |
| **Database** | Supabase (PostgreSQL) | Primary data store for users and chats. |
| **Cache/PubSub** | Redis | Message buffering and real-time events. |
| **AI Model** | Google Gemini 2.5 Flash | Multimodal content analysis. |
| **Storage** | Cloudinary | Secure media upload and hosting. |

---

## 🛠️ Setup & Installation

Follow these steps to run the project locally.

### Prerequisites
*   Python 3.10+
*   Node.js 16+ & npm
*   Redis (running locally on port 6379)
*   Supabase Account (URL & Key)
*   Cloudinary Account (Cloud Name, API Key, Secret)
*   Google Gemini API Key

### 1. Backend Setup

1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```

2.  Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  Configure Environment Variables:
    Create a `.env` file in `backend/` with the following:
    ```ini
    DATABASE_URL=postgresql://user:pass@host:5432/postgres
    REDIS_URL=redis://localhost:6379/0
    GEMINI_API_KEY=your_gemini_key
    CLOUDINARY_CLOUD_NAME=your_cloud_name
    CLOUDINARY_API_KEY=your_api_key
    CLOUDINARY_API_SECRET=your_api_secret
    SUPABASE_URL=your_supabase_url
    SUPABASE_KEY=your_supabase_anon_key
    ```

5.  Run the Server:
    The application will automatically initialize the database tables on startup.
    ```bash
    uvicorn app.main:app --reload
    ```
    *Server will start at `http://localhost:8000`*

### 2. Frontend Setup

1.  Navigate to the frontend directory:
    ```bash
    cd frontend
    ```

2.  Install dependencies:
    ```bash
    npm install
    ```

3.  Start the Development Server:
    ```bash
    npm run dev
    ```
    *App will run at `http://localhost:5173`*

---

## 📖 API Documentation

The backend provides auto-generated Swagger UI documentation.
Once the backend is running, visit:
**`http://localhost:8000/docs`**

### Key Endpoints
*   `POST /api/auth/register` - Create a new account
*   `POST /api/auth/login` - Authenticate and get session
*   `GET /api/users/search` - Find users by username/email
*   `POST /api/conversations` - Start a private chat
*   `WS /ws/{room_id}/{token}` - Real-time chat connection

---

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.
