from app import db

class Contacto (db.Model):
   __tablename__ = 'contacto'
   idContacto = db.Column(db.Integer, primary_key=True)
   nameContacto = db.Column(db.String(255), nullable=False)
   cellContacto = db.Column(db.String(255), nullable=False)
   Email = db.Column(db.String(255), nullable=False)