from fastapi import FastAPI
from app.api.v1 import auth, users, reports, blocks, admin

app = FastAPI(title="Anon Chat API")

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(blocks.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}