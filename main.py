from fastapi import FastAPI
from api.routes import router

app = FastAPI(
    title="BUCC AI Assistant API",
    version="1.0.0",
    description="Backend API for BUCC academic assistant"
)

app.include_router(router)


@app.get("/")
def health_check():
    return {"status": "ok"}
