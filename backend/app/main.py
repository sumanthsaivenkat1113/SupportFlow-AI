from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.api.users import router as users_router
from app.api.workspaces import router as workspaces_router
from app.api.ticket_normaliser import router as ticket_normalise
from app.api.ticket_classifier import (
    global_router as ticket_classifier_global_router,
    router as ticket_classifier_router,
)
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
app.include_router(ticket_normalise)

# Register the global (workspace-less) list route BEFORE the
# workspace-scoped router, so `/workspaces/ticket-classifications`
# is matched before any `/workspaces/{workspace_id}/...` patterns.
app.include_router(ticket_classifier_global_router)
app.include_router(ticket_classifier_router)


# ------------------------------------------------------------
# Root
# ------------------------------------------------------------


@app.get("/")
def root():
    return {"message": "SupportFlow AI API is running successfully"}


# ------------------------------------------------------------
# Custom OpenAPI
# ------------------------------------------------------------


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version="0.1.0",
        routes=app.routes,
    )

    components = schema.get("components", {})
    schemas = components.get("schemas", {})

    for component in schemas.values():
        properties = component.get("properties", {})

        for property_schema in properties.values():

            # Convert OpenAPI 3.1 contentMediaType
            # into the format Swagger UI expects.
            if property_schema.get("contentMediaType") == "application/octet-stream":
                property_schema.pop("contentMediaType", None)
                property_schema["format"] = "binary"

            # Handle arrays of uploaded files.
            items = property_schema.get("items", {})

            if items.get("contentMediaType") == "application/octet-stream":
                items.pop("contentMediaType", None)
                items["format"] = "binary"

    app.openapi_schema = schema

    return app.openapi_schema


app.openapi = custom_openapi
