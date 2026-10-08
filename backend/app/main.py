from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.db.database import engine, Base
from backend.app.db.seed_data import seed_database
from backend.app.routers import emergency, dispatch, hospital, vitals

# Auto-initialize database tables and seed data
Base.metadata.create_all(bind=engine)
seed_database()

app = FastAPI(
    title="AI-Powered Emergency Healthcare Command Centre API",
    description="Backend API for emergency dispatch, AI priority classification, hospital recommendation, and IoT patient vitals streaming.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(emergency.router)
app.include_router(dispatch.router)
app.include_router(hospital.router)
app.include_router(vitals.router)

@app.get("/")
def root():
    return {
        "system": "AI-Powered Intelligent Emergency Healthcare Command Centre",
        "status": "ONLINE",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
