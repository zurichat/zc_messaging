from config.settings import settings
from endpoints import members, messages, rooms, sync, threads
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    messages.router, prefix=settings.API_V1_STR, tags=["messages"]
)  # include urls from message.py
app.include_router(
    rooms.router, prefix=settings.API_V1_STR, tags=["rooms"]
)  # include urls from rooms.py
app.include_router(
    threads.router, prefix=settings.API_V1_STR, tags=["threads"]
)  # include urls from threads.py
app.include_router(
    members.router, prefix=settings.API_V1_STR, tags=["members"]
)  # include urls from members.py
app.include_router(
    sync.router, prefix=settings.API_V1_STR, tags=["sync"]
)  # include urls from sync.py


app.mount(
    "/",
    StaticFiles(directory="../frontend/zc_messaging/src/", html=True, check_dir=False),
    name="static",
)
