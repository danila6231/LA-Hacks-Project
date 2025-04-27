from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from routes.entries import router as entries_router
from routes.websocket import websocket_endpoint
import uuid

app = FastAPI(
    title="AR Classroom Assistant API",
    description="API for AR classroom assistance with live captioning, translation, and note-taking",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(entries_router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "Welcome to AR Classroom Assistant API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

@app.websocket("/ws/{client_id}")
async def websocket_route(websocket: WebSocket, client_id: str):
    await websocket_endpoint(websocket, client_id)

'''
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 
'''