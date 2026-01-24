"""Routers package"""
from routers.auth import router as auth_router
from routers.elections import router as elections_router
from routers.voting import router as voting_router
from routers.clubs import router as clubs_router
from routers.dashboard import router as dashboard_router

__all__ = [
    "auth_router",
    "elections_router",
    "voting_router",
    "clubs_router",
    "dashboard_router",
]
