import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from secret.jwt import jwt_coder
from fastapi import HTTPException

class auth:

    engine = create_engine("mysql+pymysql://root:@localhost/Manager")

    def register(self, login, password):
        sql = "INSERT INTO users (login, password) VALUES (:login, :password)"
        
        try:

            with self.engine.connect() as conn:
                conn.execute(text(sql), {'login': login, 'password': password})
                conn.commit()
                return login

        except IntegrityError:

            conn.rollback()
            return {"error": "IntegrityError"}
    
    def auto(self, login, password):
        sql = "SELECT * FROM users WHERE login = :login AND password = :password"
        
        with self.engine.connect() as conn:
            result = conn.execute(text(sql), {'login': login, 'password': password}).fetchone()
            export = jwt_coder.create_token(login)
            if result is not None:
                return {"token": export}
            else:
                raise HTTPException(status_code=401, detail="неправильные данные")

