# BUCC AI Assistant — Frontend

Next.js chat interface for the BUCC AI Assistant FastAPI backend.

## Setup

```bash
npm install
```

Create a `.env.local` file (copy from `.env.local.example`):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Run locally

Make sure your FastAPI backend is running first:
```bash
# In your backend folder
uvicorn main:app --reload
```

Then start the frontend:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Deploy

### Frontend → Vercel
1. Push this folder to a GitHub repo
2. Import the repo on [vercel.com](https://vercel.com)
3. Set `NEXT_PUBLIC_API_URL` to your Render backend URL in Vercel environment variables

### Backend → Render
1. Push your FastAPI project to GitHub
2. Create a new **Web Service** on [render.com](https://render.com)
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port 8000`

## Features

- Conversational onboarding (program + level)
- Remembers your profile in localStorage
- Quick suggestion chips
- Typing indicator
- Mobile friendly
- Connects to FastAPI `/ask` endpoint
