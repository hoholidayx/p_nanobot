"""FastAPI application for RPG World."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from rpg_world.api.routers import character, context, lorebook

app = FastAPI(title="RPG World API")

# CORS — allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers — each delegates to the corresponding rpg_core module
app.include_router(character.router, prefix="/api/v1")
app.include_router(lorebook.router, prefix="/api/v1")
app.include_router(context.router, prefix="/api/v1")
