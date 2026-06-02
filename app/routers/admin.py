import sys
import os
from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from datetime import date
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from source.admin_logic import admin

router = APIRouter()
admin = admin()

class CreateDepartment(BaseModel):
    name: str
    head_login: str

class UpdateDepartmentHead(BaseModel):
    department_id: int
    new_head_login: str

class DeleteDepartment(BaseModel):
    department_id: int

class DeleteAccount(BaseModel):
    login: str

class ChangePassword(BaseModel):
    login: str
    new_password: str

class ClearUserData(BaseModel):
    login: str
    clear_tasks: bool = False
    clear_reports: bool = False
    reset_profile: bool = True

class PromoteToAdmin(BaseModel):
    login: str

class DemoteFromAdmin(BaseModel):
    login: str

@router.post("/manager/admin/create_department")
def create_department(request: CreateDepartment, authorization: str = Header(...)):
    result = admin.create_department(authorization, request.name, request.head_login)
    if not result:
        raise HTTPException(status_code=403, detail="Доступ запрещен или ошибка создания")
    return result

@router.post("/manager/admin/update_department_head")
def update_department_head(request: UpdateDepartmentHead, authorization: str = Header(...)):
    result = admin.update_department_head(authorization, request.department_id, request.new_head_login)
    if not result:
        raise HTTPException(status_code=403, detail="Доступ запрещен или ошибка обновления")
    return result

@router.post("/manager/admin/delete_department")
def delete_department(request: DeleteDepartment, authorization: str = Header(...)):
    result = admin.delete_department(authorization, request.department_id)
    if not result:
        raise HTTPException(status_code=403, detail="Доступ запрещен или отдел не найден")
    return result

@router.post("/manager/admin/delete_account")
def delete_account(request: DeleteAccount, authorization: str = Header(...)):
    result = admin.delete_account(authorization, request.login)
    if not result:
        raise HTTPException(status_code=403, detail="Доступ запрещен или пользователь не найден")
    return result

@router.post("/manager/admin/change_password")
def change_password(request: ChangePassword, authorization: str = Header(...)):
    result = admin.change_password(authorization, request.login, request.new_password)
    if not result:
        raise HTTPException(status_code=403, detail="Доступ запрещен или ошибка смены пароля")
    return result

@router.post("/manager/admin/clear_user_data")
def clear_user_data(request: ClearUserData, authorization: str = Header(...)):
    result = admin.clear_user_data(authorization, request.login, request.clear_tasks, request.clear_reports, request.reset_profile)
    if not result:
        raise HTTPException(status_code=403, detail="Доступ запрещен или ошибка очистки данных")
    return result

@router.post("/manager/admin/get_all_users")
def get_all_users(authorization: str = Header(...)):
    result = admin.get_all_users(authorization)
    if not result:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    return result

@router.post("/manager/admin/get_all_departments")
def get_all_departments(authorization: str = Header(...)):
    result = admin.get_all_departments(authorization)
    if not result:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    return result

@router.post("/manager/admin/get_user_details")
def get_user_details(request: DeleteAccount, authorization: str = Header(...)):
    result = admin.get_user_details(authorization, request.login)
    if not result:
        raise HTTPException(status_code=403, detail="Доступ запрещен или пользователь не найден")
    return result

@router.post("/manager/admin/promote_to_admin")
def promote_to_admin(request: PromoteToAdmin, authorization: str = Header(...)):
    result = admin.promote_to_admin(authorization, request.login)
    if not result:
        raise HTTPException(status_code=403, detail="Доступ запрещен или ошибка повышения")
    return result

@router.post("/manager/admin/demote_from_admin")
def demote_from_admin(request: DemoteFromAdmin, authorization: str = Header(...)):
    result = admin.demote_from_admin(authorization, request.login)
    if not result:
        raise HTTPException(status_code=403, detail="Доступ запрещен или ошибка понижения")
    return result

@router.post("/manager/admin/get_all_admins")
def get_all_admins(authorization: str = Header(...)):
    result = admin.get_all_admins(authorization)
    if not result:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    return result