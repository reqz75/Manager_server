import sys
import os
import uuid
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from secret.jwt import jwt_coder


class sessions:

    engine = create_engine("mysql+pymysql://root:@localhost/Manager")

    def edit_profile(self, token, name=None, contact_info=None, avatar=None):

            DecToken = jwt_coder.check_token(token)
            if not DecToken or not DecToken.get('login'):
                return None

            login = DecToken.get('login')

            update_fields = []
            params = {'login': login}

            if name is not None:
                update_fields.append("name = :name")
                params['name'] = name

            if contact_info is not None:
                update_fields.append("contact_info = :contact_info")
                params['contact_info'] = contact_info

            if avatar is not None and avatar.filename:
                try:
                    os.makedirs("uploads/avatars", exist_ok=True)
                    
                    ext = avatar.filename.split('.')[-1].lower() if '.' in avatar.filename else 'jpg'
                    unique_name = f"{uuid.uuid4()}.{ext}"
                    file_path = f"uploads/avatars/{unique_name}"

                    content = avatar.file.read()

                    with open(file_path, "wb") as buffer:
                        buffer.write(content)

                    update_fields.append("avatar = :avatar")
                    params['avatar'] = file_path

                except Exception as e:
                    print(f"Avatar save error: {e}")

            if not update_fields:
                return self.load_profile(token)

            sql = f"UPDATE profiles SET {', '.join(update_fields)} WHERE user_id = (SELECT id FROM users WHERE login = :login)"


            try:
                with self.engine.connect() as conn:
                    conn.execute(text(sql), params)
                    conn.commit()
            except Exception as e:
                print(f"Update profile error: {e}")
                return None

            return self.load_profile(token)

    def load_profile(self, token):
        sql = "SELECT role, name, contact_info, avatar, registered_at FROM profiles WHERE user_id = (SELECT id FROM users WHERE login = :login)"
        
        token = jwt_coder.check_token(token)
        if not token:
            return None

        login = token.get('login')
        if not login:
            return None

        with self.engine.connect() as conn:
            result = conn.execute(text(sql), {'login': login}).fetchone()
        return dict(result._mapping) if result else None

    def load_profile_login(self, login: str):
        sql = "SELECT role, name, contact_info, avatar, registered_at FROM profiles WHERE user_id = (SELECT id FROM users WHERE login = :login)"
        
        with self.engine.connect() as conn:
            result = conn.execute(text(sql), {'login': login}).fetchone()
        
        return dict(result._mapping) if result else None
        
    def load_avatars(self, filename: str):
        file_path = f"uploads/avatars/{filename}"
        
        if os.path.exists(file_path):
            return FileResponse(file_path)
        
        raise HTTPException(status_code=404, detail="аватар не найден")
