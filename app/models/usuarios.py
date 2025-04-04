from app import db

class Usuarios(db.Model):
   __tablename__ = 'usuario'
   idUsuario = db.Column(db.Integer, primary_key=True)
   nameUsuario = db.Column(db.String(255), nullable=False)