import sys
import os
from sqlalchemy import create_engine, text
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from fastapi.responses import FileResponse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from secret.jwt import jwt_coder


class work:

    engine = create_engine("mysql+pymysql://root:@localhost/Manager")

    def load_my_dep(self, token):
        token = jwt_coder.check_token(token)

        if not token:
            return None

        login = token.get('login')
        if not login:
            return None

        sql = "SELECT (SELECT name FROM departments WHERE id = dm.department_id) AS department_name, (SELECT login FROM users WHERE id = (SELECT head_id FROM departments WHERE id = dm.department_id)) AS head_login, (SELECT name FROM profiles WHERE user_id = (SELECT head_id FROM departments WHERE id = dm.department_id)) AS head_name FROM department_members dm WHERE dm.member_id = (SELECT id FROM users WHERE login = :login) LIMIT 1"
        with self.engine.connect() as conn:
            result = conn.execute(text(sql), {'login': login}).fetchone()
        
        return dict(result._mapping) if result else None

    def load_my_tasks(self, token):
        token = jwt_coder.check_token(token)

        if not token:
            return None

        login = token.get('login')
        if not login:
            return None

        sql = "SELECT id, title, description, created_at, deadline, status FROM tasks WHERE id IN (SELECT task_id FROM task_members WHERE user_id = (SELECT id FROM users WHERE login = :login)) ORDER BY deadline ASC, created_at DESC"
        
        with self.engine.connect() as conn:
            result = conn.execute(text(sql), {'login': login}).fetchall()
        
        return [dict(row._mapping) for row in result] if result else []

    def load_my_filter_tasks(self, token, status=None, created_at_from=None, created_at_to=None, deadline_from=None, deadline_to=None, title=None):
        token = jwt_coder.check_token(token)

        if not token:
            return None

        login = token.get('login')
        if not login:
            return None

        sql = "SELECT id, title, description, created_at, deadline, status FROM tasks WHERE id IN (SELECT task_id FROM task_members WHERE user_id = (SELECT id FROM users WHERE login = :login)) AND (:status IS NULL OR status = :status) AND (:created_at_from IS NULL OR created_at >= :created_at_from) AND (:created_at_to IS NULL OR created_at <= :created_at_to) AND (:deadline_from IS NULL OR deadline >= :deadline_from) AND (:deadline_to IS NULL OR deadline <= :deadline_to) AND (:title IS NULL OR title LIKE CONCAT('%', :title, '%')) ORDER BY deadline ASC, created_at DESC"

        with self.engine.connect() as conn:
            result = conn.execute(text(sql), {'login': login, 'status': status, 'created_at_from': created_at_from, 'created_at_to': created_at_to, 'deadline_from': deadline_from, 'deadline_to': deadline_to, 'title': title}).fetchall()
        
        return [dict(row._mapping) for row in result] if result else []

    def load_task(self, token, task_id):

        token = jwt_coder.check_token(token)

        if not token:
            return None

        login = token.get('login')
        if not login:
            return None

        sql = "SELECT t.id, t.title, t.description, t.created_at, t.deadline, t.status, (SELECT login FROM users WHERE id = t.created_by) AS created_by_login, (SELECT name FROM profiles WHERE user_id = t.created_by) AS created_by_name, (SELECT GROUP_CONCAT(attachment_link SEPARATOR '; ') FROM task_attachments WHERE task_id = t.id) AS attachments FROM tasks t WHERE t.id = :task_id AND EXISTS (SELECT 1 FROM task_members tm WHERE tm.task_id = t.id AND tm.user_id = (SELECT id FROM users WHERE login = :login))"
        
        with self.engine.connect() as conn:
            result = conn.execute(text(sql), {'task_id': task_id, 'login': login}).fetchone()
        
        return dict(result._mapping) if result else None

    def get_task_att(self, filename: str):
        file_path = f"uploads/tasks/{filename}"
        
        if os.path.exists(file_path):
            return FileResponse(file_path)
        
        raise HTTPException(status_code=404, detail="отчет не найден")

    def create_task(self, token, title, description, deadline, attachments):
        token = jwt_coder.check_token(token)
        if not token:
            return None

        login = token.get('login')
        if not login:
            return None

        if attachments is None:
            attachments = []

        with self.engine.connect() as conn:
            sql_check = "SELECT id FROM departments WHERE head_id = (SELECT id FROM users WHERE login = :login) LIMIT 1"
            department = conn.execute(text(sql_check), {'login': login}).fetchone()
            
            if not department:
                return None
            
            department_id = department[0]

            sql_task = "INSERT INTO tasks (title, description, created_by, deadline, status) VALUES (:title, :description, (SELECT id FROM users WHERE login = :login), :deadline, 'pending')"
            result = conn.execute(text(sql_task), {'title': title, 'description': description, 'login': login, 'deadline': deadline})
            task_id = result.lastrowid

            for attachment in attachments:
                sql_att = "INSERT INTO task_attachments (task_id, attachment_link) VALUES (:task_id, :attachment_link)"
                conn.execute(text(sql_att), {'task_id': task_id, 'attachment_link': attachment})

            conn.commit()
            
            return self.load_task(token, task_id)

    def delete_task(self, token, task_id):
        token = jwt_coder.check_token(token)
        if not token:
            return None

        login = token.get('login')
        if not login:
            return None

        sql = "DELETE FROM tasks WHERE id = :task_id AND EXISTS (SELECT 1 FROM departments WHERE head_id = (SELECT id FROM users WHERE login = :login))"
        
        with self.engine.connect() as conn:
            result = conn.execute(text(sql), {'login': login, 'task_id': task_id})
            conn.commit()

        if result.rowcount > 0:
            return {'task_deleted': task_id}
        return None


    def add_member_to_department(self, token, member_login):
        token = jwt_coder.check_token(token)
        if not token:
            return None

        login = token.get('login')
        if not login:
            return None

        with self.engine.connect() as conn:
            sql_check = "SELECT id FROM departments WHERE head_id = (SELECT id FROM users WHERE login = :login) LIMIT 1"
            department = conn.execute(text(sql_check), {'login': login}).fetchone()
            
            if not department:
                return None
            
            department_id = department[0]

            sql_user = "SELECT id FROM users WHERE login = :member_login"
            user = conn.execute(text(sql_user), {'member_login': member_login}).fetchone()
            
            if not user:
                return None
            
            user_id = user[0]

            sql_insert = "INSERT INTO department_members (department_id, member_id) VALUES (:department_id, :member_id)"
            
            try:
                conn.execute(text(sql_insert), {'department_id': department_id, 'member_id': user_id})
                conn.commit()
                return {'added': member_login}
            except IntegrityError:
                conn.rollback()
                return None


    def remove_member_from_department(self, token, member_login):
        token = jwt_coder.check_token(token)
        if not token:
            return None

        login = token.get('login')
        if not login:
            return None

        with self.engine.connect() as conn:
            sql_check = "SELECT id FROM departments WHERE head_id = (SELECT id FROM users WHERE login = :login) LIMIT 1"
            department = conn.execute(text(sql_check), {'login': login}).fetchone()
            
            if not department:
                return None
            
            department_id = department[0]

            sql_user = "SELECT id FROM users WHERE login = :member_login"
            user = conn.execute(text(sql_user), {'member_login': member_login}).fetchone()
            
            if not user:
                return None
            
            user_id = user[0]

            sql_delete = "DELETE FROM department_members WHERE department_id = :department_id AND member_id = :member_id"
            result = conn.execute(text(sql_delete), {'department_id': department_id, 'member_id': user_id})
            conn.commit()

            if result.rowcount > 0:
                return {'removed': member_login}
            return None

    def attach_member_to_task(self, token, task_id, member_login):
        token = jwt_coder.check_token(token)
        if not token:
            return None

        login = token.get('login')
        if not login:
            return None

        with self.engine.connect() as conn:
            sql = "SELECT 1 FROM tasks t WHERE t.id = :task_id AND EXISTS (SELECT 1 FROM departments d WHERE d.head_id = (SELECT id FROM users WHERE login = :login) AND EXISTS (SELECT 1 FROM department_members dm WHERE dm.department_id = d.id AND dm.member_id = t.created_by))"
            check = conn.execute(text(sql), {'login': login, 'task_id': task_id}).fetchone()
            
            if not check:
                return None

            sql_user = "SELECT id FROM users WHERE login = :member_login"
            user = conn.execute(text(sql_user), {'member_login': member_login}).fetchone()
            
            if not user:
                return None
            
            user_id = user[0]

            sql_insert = "INSERT INTO task_members (task_id, user_id) VALUES (:task_id, :user_id)"
            
            try:
                conn.execute(text(sql_insert), {'task_id': task_id, 'user_id': user_id})
                conn.commit()
                return {'attached': member_login, 'task_id': task_id}
            except IntegrityError:
                conn.rollback()
                return None


    def remove_member_from_task(self, token, task_id, member_login):
        token = jwt_coder.check_token(token)
        if not token:
            return None

        login = token.get('login')
        if not login:
            return None

        with self.engine.connect() as conn:
            sql = "DELETE FROM task_members WHERE task_id = :task_id AND user_id = (SELECT id FROM users WHERE login = :member_login) AND EXISTS (SELECT 1 FROM departments d WHERE d.head_id = (SELECT id FROM users WHERE login = :login) AND EXISTS (SELECT 1 FROM department_members dm WHERE dm.department_id = d.id AND dm.member_id = (SELECT created_by FROM tasks WHERE id = :task_id)))"
            
            result = conn.execute(text(sql), {'login': login, 'task_id': task_id, 'member_login': member_login})
            conn.commit()

            if result.rowcount > 0:
                return {'removed': member_login, 'task_id': task_id}
            return None