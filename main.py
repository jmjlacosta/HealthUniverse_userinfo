from typing import Annotated
from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(
    title="User Info Extraction",
    description="Returns request metadata and any provided form input.",
    version="1.0.0",
)

# Allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/call/")
async def whoami(
    request: Request,
    name: Annotated[str, Form()] = "anonymous",
):
    return JSONResponse({
        "client_ip": request.client.host,
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "query_params": dict(request.query_params),
        "cookies": request.cookies,
        "form_input": {
            "name": name,
        },
    })

@app.get("/health")
async def health_check():
    return {"status": "Application is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
