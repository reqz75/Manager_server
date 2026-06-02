import jwt
import datetime

SECRET_KEY = None

def init_jwt(secret_key):
    global SECRET_KEY
    SECRET_KEY = secret_key

class jwt_coder:
    def create_token(login):
        if not SECRET_KEY:
            raise ValueError("Need SECRET_KEY")
        payload = {
            'login': login,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

    def check_token(token):
        if not SECRET_KEY:
            raise ValueError("Need SECRET_KEY")
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None  # токен просрочен
        except jwt.InvalidTokenError:
            return None  # токен поддельный