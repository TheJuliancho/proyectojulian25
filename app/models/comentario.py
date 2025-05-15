# app/models/comentario.py
from datetime import datetime
from app import db

class Comentario(db.Model):
    __tablename__ = 'comentarios'

    id          = db.Column(db.Integer, primary_key=True)
    contenido   = db.Column(db.Text, nullable=False)
    fecha       = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Aquí la corrección: tabla 'user', columna 'idUser'
    user_id     = db.Column(db.Integer,db.ForeignKey('user.idUser'),nullable=False)
    usuario     = db.relationship('Users', backref='comentarios', lazy=True)

    producto_id = db.Column(db.Integer,db.ForeignKey('menu.idProducto'),nullable=True)

    producto    = db.relationship('Menu', backref='comentarios_producto', lazy=True)
    calificacion = db.Column(db.Integer, nullable=False, default=0)