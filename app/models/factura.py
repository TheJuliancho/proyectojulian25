from app import db
from app.models.users import Users


class Factura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('user.idUser'), nullable=False)
    cliente = db.relationship('Users', backref=db.backref('facturas', lazy=True))
    fecha = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    numero = db.Column(db.String(20), nullable=False)
    subtotal = db.Column(db.Float, nullable=False) 
    iva = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'Factura({self.numero}, {self.fecha})'

class DetalleFactura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    factura_id = db.Column(db.Integer, db.ForeignKey('factura.id'), nullable=False)
    factura = db.relationship('Factura', backref=db.backref('detalles', lazy=True))
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.idProducto'), nullable=False)
    producto = db.relationship('Productos', backref=db.backref('detalles_factura', lazy=True))
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'DetalleFactura({self.factura.numero}, {self.producto.nombre})'
