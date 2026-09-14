from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.users import router as users_router
from app.api.workspaces import router as workspaces_router
from app.core.config import settings

app = FastAPI(
    title="SupportFlow AI API",
)


# ------------------------------------------------------------
# CORS
# ------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------
# Routes
# ------------------------------------------------------------

app.include_router(users_router)
app.include_router(workspaces_router)


# ------------------------------------------------------------
# Root
# ------------------------------------------------------------


@app.get("/")
def root():
    return {"message": "SupportFlow AI API is running successfully"}
