from app import db

class Carrito(db.Model):
    __tablename__ = 'carrito'
    id = db.Column(db.Integer, primary_key=True)
    idUser = db.Column(db.Integer, db.ForeignKey('user.idUser'))
    idProducto = db.Column(db.Integer)
    cantidad = db.Column(db.Integer)
    
    usuario = db.relationship('Users', backref='carritos')
