import sys
import os
from typing import Optional
from datetime import date
from fastapi import FastAPI, Header, Form, APIRouter, File, UploadFile
from pydantic import BaseModel
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from source.work_logic import work

router = APIRouter()
work = work()

class TaskFilter(BaseModel):
    status: Optional[str] = None
    created_at_from: Optional[date] = None
    created_at_to: Optional[date] = None
    deadline_from: Optional[date] = None
    deadline_to: Optional[date] = None
    title: Optional[str] = None

class OneTask(BaseModel):
    task_id: int


@router.post("/load_my_dep")
def load_my_dep(authorization: str = Header(...)):
    result = work.load_my_dep(authorization)
    return result

@router.post("/load_my_tasks")
def load_my_tasks(authorization: str = Header(...)):
    result = work.load_my_tasks(authorization)
    return result

@router.post("/load_my_filter_tasks")
def load_my_filter_tasks(filters: TaskFilter, authorization: str = Header(...)):
    result = work.load_my_filter_tasks(
        authorization,
        status=filters.status,
        created_at_from=filters.created_at_from,
        created_at_to=filters.created_at_to,
        deadline_from=filters.deadline_from,
        deadline_to=filters.deadline_to,
        title=filters.title)    
    return result

@router.post("/load_task")
def load_task(request: OneTask, authorization: str = Header(...)):
    result = work.load_task(authorization, request.task_id)
    return result

@router.get("/uploads/tasks/{filename}")
def get_task_att(filename: str):
    result = work.get_task_att(filename)
    return result