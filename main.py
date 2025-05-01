from typing import Optional, Annotated
from fastapi import FastAPI, Form, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

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


app = FastAPI(
    title="User Info Extraction",
    description="Returns information about the incoming request and any form input provided.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Form Parser ---

def as_form(
    session_id: Annotated[Optional[str], Form()] = None,
    user_role: Annotated[Optional[str], Form()] = None,
    user_agent_override: Annotated[Optional[str], Form()] = None,
) -> Input:
    return Input(
        session_id=session_id,
        user_role=user_role,
        user_agent_override=user_agent_override,
    )

# --- Endpoints ---

@app.post("/call/", response_model=Output)
async def call(
    request: Request,
    data: Annotated[Input, Depends(as_form)],
) -> Output:
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
