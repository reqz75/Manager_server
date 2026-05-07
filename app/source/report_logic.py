import sys
import os
import uuid
from fastapi.responses import FileResponse
from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from secret.jwt import jwt_coder



class report:



    engine = create_engine("mysql+pymysql://root:@localhost/Manager")

    def load_full_report(self, token, report_id):
        token = jwt_coder.check_token(token)
        if not token:
            return None

        login = token.get('login')
        if not login:
            return None

        sql = "SELECT r.id, r.task_id, r.user_id, r.date, r.title, r.description, r.status, (SELECT login FROM users WHERE id = r.user_id) AS user_login, (SELECT name FROM profiles WHERE user_id = r.user_id) AS user_name, (SELECT title FROM tasks WHERE id = r.task_id) AS task_title, (SELECT description FROM tasks WHERE id = r.task_id) AS task_description, (SELECT GROUP_CONCAT(attachment_link SEPARATOR '; ') FROM report_attachments WHERE report_id = r.id) AS attachments FROM reports r WHERE r.id = :report_id AND EXISTS (SELECT 1 FROM task_members tm WHERE tm.task_id = r.task_id AND tm.user_id = (SELECT id FROM users WHERE login = :login))"
        
        with self.engine.connect() as conn:
            result = conn.execute(text(sql), {'login': login, 'report_id': report_id}).fetchone()
        
        return dict(result._mapping) if result else None

    def create_report(self, authorization, task_id, title, description, attachments):
        token = jwt_coder.check_token(authorization)
        if not token:
            return None

        login = token.get('login')
        if not login:
            return None

        if attachments is None:
            attachments = []

        with self.engine.connect() as conn:
            sql = "INSERT INTO reports (task_id, user_id, date, title, description, status) SELECT :task_id, (SELECT id FROM users WHERE login = :login), CURDATE(), :title, :description, 'pending' FROM DUAL WHERE EXISTS (SELECT 1 FROM task_members tm WHERE tm.task_id = :task_id AND tm.user_id = (SELECT id FROM users WHERE login = :login))"
            result = conn.execute(text(sql), {'task_id': task_id, 'login': login, 'title': title, 'description': description})
            
            if result.rowcount == 0:
                return None
            
            report_id = result.lastrowid
            
            for attachment in attachments:
                sql_att = "INSERT INTO report_attachments (report_id, attachment_link) VALUES (:report_id, :attachment_link)"
                conn.execute(text(sql_att), {'report_id': report_id, 'attachment_link': attachment})
            
            conn.commit()
            
            result = self.load_full_report(token, report_id)
            
            return result


    def del_report(self, token, report_id):
        token = jwt_coder.check_token(token)
        if not token:
            return None

        login = token.get('login')
        if not login:
            return None

        sql = "DELETE FROM reports WHERE id = :report_id AND (user_id = (SELECT id FROM users WHERE login = :login) OR EXISTS (SELECT 1 FROM departments d WHERE d.head_id = (SELECT id FROM users WHERE login = :login) AND EXISTS (SELECT 1 FROM task_members tm WHERE tm.task_id = reports.task_id AND tm.user_id = d.head_id)))"
        with self.engine.connect() as conn:
            result = conn.execute(text(sql), {'login': login, 'report_id': report_id})
            conn.commit()

        if result.rowcount > 0:
            return {'отчет удалн': report_id}
        else:
            return None

    def report_set_status(self, token, report_id, status):
        token = jwt_coder.check_token(token)
        if not token:
            return None

        login = token.get('login')
        if not login:
            return None
        sql = "UPDATE reports r SET r.status = :status WHERE r.id = :report_id AND EXISTS (SELECT 1 FROM departments d JOIN task_members tm ON tm.user_id = d.head_id WHERE d.head_id = (SELECT id FROM users WHERE login = :login) AND tm.task_id = r.task_id)"
        
        with self.engine.connect() as conn:
            result = conn.execute(text(sql), {'login': login, 'report_id': report_id, 'status': status})
            conn.commit()
        return result.rowcount > 0



    def load_reports(self, token, task_id, status):
        token = jwt_coder.check_token(token)
        if not token:
            return None

        login = token.get('login')
        if not login:
            return None

        sql = "SELECT r.id, r.task_id, r.user_id, r.date, r.title, r.description, r.status, (SELECT login FROM users WHERE id = r.user_id) AS user_login, (SELECT name FROM profiles WHERE user_id = r.user_id) AS user_name, (SELECT GROUP_CONCAT(attachment_link SEPARATOR '; ') FROM report_attachments WHERE report_id = r.id) AS attachments FROM reports r WHERE r.task_id = :task_id AND EXISTS (SELECT 1 FROM task_members tm WHERE tm.task_id = r.task_id AND tm.user_id = (SELECT id FROM users WHERE login = :login)) ORDER BY r.date DESC"        
        with self.engine.connect() as conn:
            result = conn.execute(text(sql), {'login': login, 'task_id': task_id, 'status': status}).fetchall()
        
        return [dict(row._mapping) for row in result] if result else []

        
    def get_report_att(self, filename: str):
        file_path = f"uploads/reports/{filename}"
        
        if os.path.exists(file_path):
            return FileResponse(file_path)
        
        raise HTTPException(status_code=404, detail="приложение к отчету не найдено")
