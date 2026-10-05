from flask_login import UserMixin

class Usuario(UserMixin):
    def __init__(self, registro):
        self.id = registro['id']
        self.usuario = registro['usuario']
