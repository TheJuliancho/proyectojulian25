from app import db

class Carrito(db.Model):
    __tablename__ = 'carrito'
    
    id = db.Column(db.Integer, primary_key=True)
    idUser = db.Column(db.Integer, db.ForeignKey('user.idUser', ondelete='CASCADE'))
    idProducto = db.Column(db.Integer, db.ForeignKey('menu.idProducto', ondelete='CASCADE'))
    cantidad = db.Column(db.Integer, nullable=False)
    
    # Relación con el modelo Users
    usuario = db.relationship('Users', backref=db.backref('carritos', lazy=True))
    
    # Relación con el modelo Menu (productos)
    producto = db.relationship('Menu', backref=db.backref('carritos', lazy=True))
    
    def __repr__(self):
        return f'Carrito(id={self.id}, usuario={self.usuario.nameUser}, producto={self.producto.nameProducto}, cantidad={self.cantidad})'
