from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analyze, settings, analysis

app = FastAPI(
    title="GitHub Repository Health Check API",
    description="API for analyzing GitHub repository health and generating AI-powered evaluation",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router, prefix="/api", tags=["analysis"])
app.include_router(analysis.router, prefix="/api", tags=["analysis"])
app.include_router(settings.router, prefix="/api", tags=["settings"])


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)