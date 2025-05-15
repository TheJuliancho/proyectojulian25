from flask_login import UserMixin
from app import db

class Users(db.Model, UserMixin):
    __tablename__ = 'user'
    idUser = db.Column(db.Integer, primary_key=True)
    nameUser = db.Column(db.String(80), unique=True, nullable=False)
    passwordUser = db.Column(db.String(120), nullable=False)
    direccion = db.Column(db.String(255)) 
    rol = db.Column(db.String(50), nullable=False, default='cliente')  # Rol por defecto: cliente

    def __init__(self, nameUser, passwordUser, rol='cliente'):
        self.nameUser = nameUser
        self.passwordUser = passwordUser
        self.rol = rol


    def get_id(self):
        return str(self.idUser)