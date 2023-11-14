from fastapi import FastAPI

from .users.endpoints import router as users_router

app = FastAPI()

app.include_router(users_router)
