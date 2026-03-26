from fastapi import FastAPI
from .pessoas_fisica_routes import pessoa_fisica_router

app = FastAPI(
    title="Bot Portal da Transparência"
)

app.include_router(pessoa_fisica_router)