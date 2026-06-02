import sys
import os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import APIRouter
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from source.auth_logic import auth

router = APIRouter()
auth = auth()

class AythData(BaseModel):
    login: str
    password: str



@router.post("/manager/registration")
def registration(data: AythData):
    result = auth.register(data.login, data.password)
    return result

@router.post("/manager/login")
def login(data: AythData):
    result = auth.auto(data.login, data.password)
    return result