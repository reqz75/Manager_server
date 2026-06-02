import sys
import os
from fastapi import FastAPI, Header, Form, APIRouter, File, UploadFile
from pydantic import BaseModel
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from source.report_logic import report
from typing import Optional, List

router = APIRouter()
report = report()

class getTaskId(BaseModel):
    task_id: int

class getReportId(BaseModel):
    report_id: int

class setStatus(BaseModel):
    report_id: int
    status: str 

class createRep(BaseModel):
    task_id: int
    title: str
    description: str
    attachments: Optional[List[str]] = None

@router.post("/manager/load_full_report")
def load_full_report(request: getReportId, authorization: str = Header(...)):
    result = report.load_full_report(authorization, request.report_id)
    return result

@router.post("/manager/create_report")
def create_report(request: createRep, authorization: str = Header(...)):
    result = report.create_report(authorization, request.task_id, request.title, request.description, request.attachments)
    return result

@router.post("/manager/del_report")
def del_report(request: getReportId, authorization: str = Header(...)):
    result = report.del_report(authorization, request.report_id)
    return result

@router.post("/manager/report_set_status")
def report_set_status(request: setStatus, authorization: str = Header(...)):
    result = report.report_set_status(authorization, request.report_id, request.status)
    return result

@router.post("/manager/load_reports")
def load_reports(request: getTaskId, authorization: str = Header(...)):
    result = report.load_reports(authorization, request.task_id, None)
    return result

@router.get("/manager/uploads/reports/{filename}")
def get_report_att(filename: str):
    result = report.get_report_att(filename)
    return result