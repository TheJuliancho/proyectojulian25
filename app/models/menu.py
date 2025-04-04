from app import db

class Menu (db.Model):
   __tablename__ = 'menu'
   idProducto = db.Column(db.Integer, primary_key=True)
   nameProducto = db.Column(db.String(255), nullable=False)
   DescripcionProducto = db.Column(db.String(255), nullable=False)
   precioProducto = db.Column(db.String(255), nullable=False)
   imagenProducto = db.Column(db.String(255), nullable=True)  # Columna para la imagen
   def get_img(self, img_attr):
      return getattr(self, img_attr) if getattr(self, img_attr) else "menu.jpg"