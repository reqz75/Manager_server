import jwt
import datetime

SECRET_KEY = "my-very-long-secret-key-2024-min-32-characters"

class jwt_coder:
    def create_token(login):
        payload = {
            'login': login,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

    def check_token(token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None  # токен просрочен
        except jwt.InvalidTokenError:
            return None  # токен поддельный