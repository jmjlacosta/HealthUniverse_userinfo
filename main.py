from typing import Optional
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Pydantic models
class Input(BaseModel):
    session_id: Optional[str] = None
    user_role: Optional[str] = None
    user_agent_override: Optional[str] = None

class Output(BaseModel):
    client_ip: str
    method: str
    url: str
    headers: dict
    query_params: dict
    cookies: dict
    form_input: Input

# FastAPI app
app = FastAPI(
    title="Whoami Tool",
    description="Returns information about the incoming request and any JSON input provided.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/call/", response_model=Output)
async def call(request: Request, data: Input) -> Output:
    return Output(
        client_ip=request.client.host,
        method=request.method,
        url=str(request.url),
        headers=dict(request.headers),
        query_params=dict(request.query_params),
        cookies=request.cookies,
        form_input=data,
    )

@app.get("/health", response_class=JSONResponse)
async def health_check():
    return {"status": "Application is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)