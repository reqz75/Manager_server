from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import sys

from routers.auth import router as auth_router
from routers.users import router as users_router
from routers.works import router as works_router
from routers.reports import router as report_router
from secret.jwt import init_jwt
from routers.admin import router as admin_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(works_router)
app.include_router(report_router)
app.include_router(admin_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)



if __name__ == "__main__":

    hostAdres = sys.argv[1]
    port = int(sys.argv[2])
    jwt_secret_key = sys.argv[3]

    init_jwt(jwt_secret_key)

    uvicorn.run(app, host=hostAdres, port=port)
    #uvicorn.run(app, host="0.0.0.0", port=8000)
    #uvicorn.run(app, host="localhost", port=8000)