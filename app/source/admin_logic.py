import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from secret.jwt import jwt_coder
from fastapi import HTTPException

class admin:

    engine = create_engine("mysql+pymysql://root:@localhost/Manager")

    def _check_admin(self, token):

        token = jwt_coder.check_token(token)
        if not token:
            return None
        
        login = token.get('login')
        if not login:
            return None
        
        sql = "SELECT role FROM profiles WHERE user_id = (SELECT id FROM users WHERE login = :login)"
        
        with self.engine.connect() as conn:
            result = conn.execute(text(sql), {'login': login}).fetchone()
        
        if result and result[0] == 'admin':
            return login
        return None

    def create_department(self, token, name, head_login):

        admin_login = self._check_admin(token)
        if not admin_login:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
        
        sql_check_user = "SELECT id FROM users WHERE login = :head_login"
        sql_check_head = "SELECT id FROM departments WHERE head_id = :head_id"
        sql_create = "INSERT INTO departments (name, head_id) VALUES (:name, :head_id)"
        sql_member = "INSERT INTO department_members (department_id, member_id) VALUES (:department_id, :member_id)"
        
        with self.engine.connect() as conn:
            head_user = conn.execute(text(sql_check_user), {'head_login': head_login}).fetchone()
            
            if not head_user:
                raise HTTPException(status_code=404, detail="Пользователь не найден")
            
            existing_head = conn.execute(text(sql_check_head), {'head_id': head_user[0]}).fetchone()
            
            if existing_head:
                raise HTTPException(status_code=409, detail="Пользователь уже руководитель другого отдела")
            
            try:
                result = conn.execute(text(sql_create), {'name': name, 'head_id': head_user[0]})
                department_id = result.lastrowid
                
                conn.execute(text(sql_member), {'department_id': department_id, 'member_id': head_user[0]})
                
                conn.commit()
                
                return {
                    'department_id': department_id,
                    'name': name,
                    'head_login': head_login,
                    'message': 'Отдел успешно создан'
                }
            except IntegrityError:
                conn.rollback()
                raise HTTPException(status_code=409, detail="IntegrityError")

    def update_department_head(self, token, department_id, new_head_login):

        admin_login = self._check_admin(token)
        if not admin_login:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
        
        sql_check_dep = "SELECT id FROM departments WHERE id = :department_id"
        sql_check_user = "SELECT id FROM users WHERE login = :new_head_login"
        sql_check_head = "SELECT id FROM departments WHERE head_id = :head_id AND id != :department_id"
        sql_update = "UPDATE departments SET head_id = :head_id WHERE id = :department_id"
        sql_check_member = "SELECT id FROM department_members WHERE department_id = :department_id AND member_id = :member_id"
        sql_add_member = "INSERT INTO department_members (department_id, member_id) VALUES (:department_id, :member_id)"
        
        with self.engine.connect() as conn:
            department = conn.execute(text(sql_check_dep), {'department_id': department_id}).fetchone()
            
            if not department:
                raise HTTPException(status_code=404, detail="Отдел не найден")
            
            new_head = conn.execute(text(sql_check_user), {'new_head_login': new_head_login}).fetchone()
            
            if not new_head:
                raise HTTPException(status_code=404, detail="Пользователь не найден")
            
            existing_head = conn.execute(text(sql_check_head), {'head_id': new_head[0], 'department_id': department_id}).fetchone()
            
            if existing_head:
                raise HTTPException(status_code=409, detail="Пользователь уже руководитель другого отдела")
            
            conn.execute(text(sql_update), {'head_id': new_head[0], 'department_id': department_id})
            
            is_member = conn.execute(text(sql_check_member), {'department_id': department_id, 'member_id': new_head[0]}).fetchone()
            
            if not is_member:
                conn.execute(text(sql_add_member), {'department_id': department_id, 'member_id': new_head[0]})
            
            conn.commit()
            
            return {
                'department_id': department_id,
                'new_head_login': new_head_login,
                'message': 'Руководитель отдела успешно обновлен'
            }

    def delete_department(self, token, department_id):

        admin_login = self._check_admin(token)
        if not admin_login:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
        
        sql_check = "SELECT id, name FROM departments WHERE id = :department_id"
        sql_delete_members = "DELETE FROM department_members WHERE department_id = :department_id"
        sql_delete = "DELETE FROM departments WHERE id = :department_id"
        
        with self.engine.connect() as conn:
            department = conn.execute(text(sql_check), {'department_id': department_id}).fetchone()
            
            if not department:
                raise HTTPException(status_code=404, detail="Отдел не найден")
            
            conn.execute(text(sql_delete_members), {'department_id': department_id})
            conn.execute(text(sql_delete), {'department_id': department_id})
            
            conn.commit()
            
            return {
                'department_id': department_id,
                'department_name': department[1],
                'message': 'Отдел успешно удален'
            }

    def delete_account(self, token, login):

        admin_login = self._check_admin(token)

        if login == "root":
            raise HTTPException(status_code=403, detail="Нельзя удалить главного администратора root")

        if not admin_login:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
        
        if login == admin_login:
            raise HTTPException(status_code=403, detail="Нельзя удалить свой аккаунт")
        
        sql_get_user = "SELECT id FROM users WHERE login = :login"
        
        with self.engine.connect() as conn:
            user = conn.execute(text(sql_get_user), {'login': login}).fetchone()
            
            if not user:
                raise HTTPException(status_code=404, detail="Пользователь не найден")
            
            user_id = user[0]
            
            try:
                conn.execute(text("DELETE FROM task_members WHERE user_id = :user_id"), {'user_id': user_id})
                conn.execute(text("DELETE FROM department_members WHERE member_id = :user_id"), {'user_id': user_id})
                conn.execute(text("DELETE FROM report_attachments WHERE report_id IN (SELECT id FROM reports WHERE user_id = :user_id)"), {'user_id': user_id})
                conn.execute(text("DELETE FROM reports WHERE user_id = :user_id"), {'user_id': user_id})
                conn.execute(text("DELETE FROM task_attachments WHERE task_id IN (SELECT id FROM tasks WHERE created_by = :user_id)"), {'user_id': user_id})
                conn.execute(text("DELETE FROM tasks WHERE created_by = :user_id"), {'user_id': user_id})
                conn.execute(text("DELETE FROM profiles WHERE user_id = :user_id"), {'user_id': user_id})
                conn.execute(text("DELETE FROM users WHERE id = :user_id"), {'user_id': user_id})
                
                conn.commit()
                
                return {
                    'deleted_login': login,
                    'message': f'Аккаунт {login} успешно удален'
                }
            except IntegrityError:
                conn.rollback()
                raise HTTPException(status_code=409, detail="IntegrityError")

    def change_password(self, token, login, new_password):

        admin_login = self._check_admin(token)
        if not admin_login:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
        
        if not new_password or len(new_password) < 4:
            raise HTTPException(status_code=400, detail="Пароль должен содержать минимум 4 символа")
        
        sql_update = "UPDATE users SET password = :new_password WHERE login = :login"
        
        with self.engine.connect() as conn:
            result = conn.execute(text(sql_update), {'new_password': new_password, 'login': login})
            conn.commit()
            
            if result.rowcount > 0:
                return {
                    'login': login,
                    'message': f'Пароль для {login} успешно изменен'
                }
            raise HTTPException(status_code=404, detail="Пользователь не найден")

    def clear_user_data(self, token, login, clear_tasks=False, clear_reports=False, reset_profile=True):

        admin_login = self._check_admin(token)
        if not admin_login:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
        
        sql_get_user = "SELECT id FROM users WHERE login = :login"
        sql_reset_profile = "UPDATE profiles SET name = NULL, contact_info = NULL, avatar = NULL WHERE user_id = :user_id"
        
        with self.engine.connect() as conn:
            user = conn.execute(text(sql_get_user), {'login': login}).fetchone()
            
            if not user:
                raise HTTPException(status_code=404, detail="Пользователь не найден")
            
            user_id = user[0]
            cleared_data = []
            
            if clear_tasks:
                conn.execute(text("DELETE FROM task_members WHERE user_id = :user_id"), {'user_id': user_id})
                cleared_data.append("задачи")
            
            if clear_reports:
                conn.execute(text("DELETE FROM report_attachments WHERE report_id IN (SELECT id FROM reports WHERE user_id = :user_id)"), {'user_id': user_id})
                conn.execute(text("DELETE FROM reports WHERE user_id = :user_id"), {'user_id': user_id})
                cleared_data.append("отчеты")
            
            if reset_profile:
                conn.execute(text(sql_reset_profile), {'user_id': user_id})
                cleared_data.append("профиль")
            
            conn.commit()
            
            return {
                'login': login,
                'cleared_data': cleared_data,
                'message': f'Данные пользователя {login} очищены: {", ".join(cleared_data)}'
            }

    def get_all_users(self, token):

        admin_login = self._check_admin(token)
        if not admin_login:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
        
        sql = "SELECT u.login, p.role, p.name, p.contact_info, p.registered_at, (SELECT COUNT(*) FROM tasks WHERE created_by = u.id) as created_tasks, (SELECT COUNT(*) FROM task_members WHERE user_id = u.id) as assigned_tasks, (SELECT COUNT(*) FROM reports WHERE user_id = u.id) as reports_count FROM users u LEFT JOIN profiles p ON u.id = p.user_id ORDER BY u.login"
        
        with self.engine.connect() as conn:
            result = conn.execute(text(sql)).fetchall()
        
        return [dict(row._mapping) for row in result] if result else []

    def get_all_departments(self, token):

        admin_login = self._check_admin(token)
        if not admin_login:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
        
        sql = "SELECT d.id, d.name, (SELECT login FROM users WHERE id = d.head_id) as head_login, (SELECT name FROM profiles WHERE user_id = d.head_id) as head_name, (SELECT COUNT(*) FROM department_members WHERE department_id = d.id) as members_count FROM departments d ORDER BY d.name"
        
        with self.engine.connect() as conn:
            result = conn.execute(text(sql)).fetchall()
        
        return [dict(row._mapping) for row in result] if result else []

    def get_user_details(self, token, login):

        admin_login = self._check_admin(token)
        if not admin_login:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
        
        sql = "SELECT u.login, u.password, p.role, p.name, p.contact_info, p.avatar, p.registered_at, (SELECT name FROM departments d JOIN department_members dm ON d.id = dm.department_id WHERE dm.member_id = u.id LIMIT 1) as department_name, (SELECT login FROM users WHERE id = d.head_id) as department_head_login FROM users u LEFT JOIN profiles p ON u.id = p.user_id LEFT JOIN department_members dm ON u.id = dm.member_id LEFT JOIN departments d ON dm.department_id = d.id WHERE u.login = :login"
        
        with self.engine.connect() as conn:
            result = conn.execute(text(sql), {'login': login}).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        user_data = dict(result._mapping)
        
        sql_tasks = "SELECT t.id, t.title, t.status, t.deadline, (SELECT login FROM users WHERE id = t.created_by) as created_by FROM tasks t JOIN task_members tm ON t.id = tm.task_id WHERE tm.user_id = (SELECT id FROM users WHERE login = :login)"
        
        with self.engine.connect() as conn:
            tasks = conn.execute(text(sql_tasks), {'login': login}).fetchall()
        
        user_data['tasks'] = [dict(task._mapping) for task in tasks] if tasks else []
        
        sql_reports = "SELECT r.id, r.title, r.status, r.date, t.title as task_title FROM reports r JOIN tasks t ON r.task_id = t.id WHERE r.user_id = (SELECT id FROM users WHERE login = :login) ORDER BY r.date DESC"
        
        with self.engine.connect() as conn:
            reports = conn.execute(text(sql_reports), {'login': login}).fetchall()
        
        user_data['reports'] = [dict(report._mapping) for report in reports] if reports else []
        
        return user_data

    def _check_root_admin(self, login):
        return login == "root"

    def promote_to_admin(self, token, login):
        admin_login = self._check_admin(token)
        if not admin_login:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
        
        sql_check_user = "SELECT id, login FROM users WHERE login = :login"
        
        with self.engine.connect() as conn:
            user = conn.execute(text(sql_check_user), {'login': login}).fetchone()
            
            if not user:
                raise HTTPException(status_code=404, detail="Пользователь не найден")
            
            sql_check_role = "SELECT role FROM profiles WHERE user_id = :user_id"
            current_role = conn.execute(text(sql_check_role), {'user_id': user[0]}).fetchone()
            
            if current_role and current_role[0] == 'admin':
                raise HTTPException(status_code=409, detail="Пользователь уже является администратором")
            
            sql_update_role = "UPDATE profiles SET role = 'admin' WHERE user_id = :user_id"
            result = conn.execute(text(sql_update_role), {'user_id': user[0]})
            
            if result.rowcount == 0:
                sql_insert_profile = "INSERT INTO profiles (user_id, role, registered_at) VALUES (:user_id, 'admin', CURDATE())"
                conn.execute(text(sql_insert_profile), {'user_id': user[0]})
            
            conn.commit()
            
            return {
                'login': login,
                'new_role': 'admin',
                'message': f'Пользователь {login} повышен до администратора'
            }

    def demote_from_admin(self, token, login):
        admin_login = self._check_admin(token)
        if not admin_login:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
        
        if login == "root":
            raise HTTPException(status_code=403, detail="Нельзя понизить главного администратора root")
        
        if login == admin_login:
            raise HTTPException(status_code=403, detail="Нельзя понизить свой собственный статус администратора")
        
        sql_check_user = "SELECT id FROM users WHERE login = :login"
        
        with self.engine.connect() as conn:
            user = conn.execute(text(sql_check_user), {'login': login}).fetchone()
            
            if not user:
                raise HTTPException(status_code=404, detail="Пользователь не найден")
            
            sql_check_role = "SELECT role FROM profiles WHERE user_id = :user_id"
            current_role = conn.execute(text(sql_check_role), {'user_id': user[0]}).fetchone()
            
            if not current_role or current_role[0] != 'admin':
                raise HTTPException(status_code=409, detail="Пользователь не является администратором")
            
            sql_update_role = "UPDATE profiles SET role = 'user' WHERE user_id = :user_id"
            conn.execute(text(sql_update_role), {'user_id': user[0]})
            conn.commit()
            
            return {
                'login': login,
                'new_role': 'user',
                'message': f'Пользователь {login} понижен до обычного пользователя'
            }

    def get_all_admins(self, token):
        admin_login = self._check_admin(token)
        if not admin_login:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
        
        sql = "SELECT u.login, p.name, p.contact_info, p.registered_at, (SELECT COUNT(*) FROM tasks WHERE created_by = u.id) as created_tasks, (SELECT COUNT(*) FROM reports WHERE user_id = u.id) as reports_count, CASE WHEN u.login = 'root' THEN true ELSE false END as is_root FROM users u JOIN profiles p ON u.id = p.user_id WHERE p.role = 'admin' ORDER BY CASE WHEN u.login = 'root' THEN 0 ELSE 1 END, u.login"        
        
        with self.engine.connect() as conn:
            result = conn.execute(text(sql)).fetchall()
        
        return [dict(row._mapping) for row in result] if result else []