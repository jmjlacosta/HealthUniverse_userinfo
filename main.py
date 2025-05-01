from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Annotated, Optional

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set specific origins in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/whoami")
async def who_is_asking(
    request: Request,
    session_id: Annotated[Optional[str], Form()] = None,
    user_role: Annotated[Optional[str], Form()] = None,
    user_agent_override: Annotated[Optional[str], Form()] = None,
):
    return JSONResponse({
        "client_ip": request.client.host,
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "query_params": dict(request.query_params),
        "cookies": request.cookies,
        "form_input": {
            "session_id": session_id,
            "user_role": user_role,
            "user_agent_override": user_agent_override,
        },
    })
