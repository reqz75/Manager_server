import sys
import os
from fastapi import FastAPI, Header, Form, APIRouter, File, UploadFile
from pydantic import BaseModel
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from source.profile_logic import sessions

router = APIRouter()
sessions = sessions()


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    contact_info: Optional[str] = None

@router.post("/profile")
def load_profile(authorization: str = Header(...)):
    result = sessions.load_profile(authorization)
    return result

@router.post("/profile-edit")
def edit_profile(
    authorization: str = Header(...),
    name: str = Form(None),
    contact_info: str = Form(None),
    avatar: UploadFile = File(None)):
   
    result = sessions.edit_profile(
        authorization, 
        name, 
        contact_info, 
        avatar
    )
    return result

@router.get("/profile/{login}")
def load_other_profile(login: str):
    result = sessions.load_profile_login(login)
    return result

