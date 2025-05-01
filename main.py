from typing import Optional
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from jose import jwt, JWTError
import json

# --- Input and Output models ---
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
    clerk_claims: Optional[dict] = None
    jwt_token_found: bool = False
    raw_body: Optional[str] = None
    parsed_json_body: Optional[dict] = None

# --- App setup ---
app = FastAPI(
    title="User Info Extraction",
    description="Returns all metadata available about the requesting Navigator session, including Clerk identity if available.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Clerk token decoding ---
def extract_clerk_claims(token: str) -> dict:
    try:
        return jwt.get_unverified_claims(token)
    except JWTError:
        return {}

# --- Main endpoint ---
@app.post("/call/", response_model=Output)
async def call(request: Request, data: Input) -> Output:
    headers = dict(request.headers)
    cookies = request.cookies

    # Raw + parsed body (for debugging purposes)
    try:
        body_bytes = await request.body()
        body_text = body_bytes.decode("utf-8", errors="replace")
        body_json = json.loads(body_text) if body_text.strip().startswith("{") else None
    except Exception:
        body_text = None
        body_json = None

    # Look for Clerk JWT token in Authorization header or __session cookie
    token_sources = [
        headers.get("authorization", "").replace("Bearer ", ""),
        cookies.get("__session", ""),
    ]
    jwt_token = next((t for t in token_sources if t), None)
    clerk_claims = extract_clerk_claims(jwt_token) if jwt_token else None

    return Output(
        client_ip=request.client.host,
        method=request.method,
        url=str(request.url),
        headers=headers,
        query_params=dict(request.query_params),
        cookies=cookies,
        form_input=data,
        clerk_claims=clerk_claims,
        jwt_token_found=bool(jwt_token),
        raw_body=body_text,
        parsed_json_body=body_json,
    )

@app.get("/health", response_class=JSONResponse)
async def health_check():
    return {"status": "Application is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
