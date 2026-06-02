import sys
import os
from typing import Optional, List
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

class CreateTask(BaseModel):
    title: str
    description: str
    deadline: date
    attachments: Optional[List[str]] = None

class DeleteTask(BaseModel):
    task_id: int

class DepartmentMember(BaseModel):
    member_login: str

class TaskMember(BaseModel):
    task_id: int
    member_login: str

@router.post("/manager/load_my_dep")
def load_my_dep(authorization: str = Header(...)):
    result = work.load_my_dep(authorization)
    return result

@router.post("/manager/load_my_tasks")
def load_my_tasks(authorization: str = Header(...)):
    result = work.load_my_tasks(authorization)
    return result

@router.post("/manager/load_my_filter_tasks")
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

@router.post("/manager/load_task")
def load_task(request: OneTask, authorization: str = Header(...)):
    result = work.load_task(authorization, request.task_id)
    return result

@router.get("/manager/uploads/tasks/{filename}")
def get_task_att(filename: str):
    result = work.get_task_att(filename)
    return result

@router.post("/manager/create_task")
def create_task(request: CreateTask, authorization: str = Header(...)):
    result = work.create_task(authorization, request.title, request.description, request.deadline, request.attachments)
    return result

@router.post("/manager/delete_task")
def delete_task(request: DeleteTask, authorization: str = Header(...)):
    result = work.delete_task(authorization, request.task_id)
    return result

@router.post("/manager/add_member_to_department")
def add_member_to_department(request: DepartmentMember, authorization: str = Header(...)):
    result = work.add_member_to_department(authorization, request.member_login)
    return result

@router.post("/manager/remove_member_from_department")
def remove_member_from_department(request: DepartmentMember, authorization: str = Header(...)):
    result = work.remove_member_from_department(authorization, request.member_login)
    return result

@router.post("/manager/attach_member_to_task")
def attach_member_to_task(request: TaskMember, authorization: str = Header(...)):
    result = work.attach_member_to_task(authorization, request.task_id, request.member_login)
    return result

@router.post("/manager/remove_member_from_task")
def remove_member_from_task(request: TaskMember, authorization: str = Header(...)):
    result = work.remove_member_from_task(authorization, request.task_id, request.member_login)
    return result

@router.post("/manager/get_department_members")
def get_department_members(authorization: str = Header(...)):
    result = work.get_department_members(authorization)
    return result

@router.post("/manager/get_task_members")
def get_task_members(request: OneTask, authorization: str = Header(...)):
    result = work.get_task_members(authorization, request.task_id)
    return result