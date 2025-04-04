from app import db

class Productos(db.Model):
   __tablename__ = 'productos'
   idProducto = db.Column(db.Integer, primary_key=True)
   nameProducto = db.Column(db.String(255), nullable=False)
   tipoProducto = db.Column(db.String(255), nullable=False)
   
