from flask import Blueprint, render_template, request, redirect, url_for
from app.models.contacto import Contacto
from app import db

bp = Blueprint('contacto', __name__)

@bp.route('/contacto')
def index():
    data = Contacto.query.all()   
    return render_template('contacto/index.html', data=data)
    
@bp.route('/contacto/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        contacto = request.form['nameContacto']
        contacto = Contacto(nameContacto=contacto )
        db.session.add(contacto)
        db.session.commit()
        
        return redirect(url_for('contacto.index'))
    
    return render_template('contacto/add.html')
    

@bp.route('/contacto/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    contacto = Contacto.query.get_or_404(id)

    if request.method == 'POST':
        contacto.nameContacto= request.form['nameContacto']
        db.session.commit()
        return redirect(url_for('contacto.index'))
    return render_template('contacto/edit.html', contacto=contacto)

@bp.route('/contacto/delete/<int:id>')
def delete(id):    
    contacto =Contacto.query.get_or_404(id)
    db.session.delete(contacto)
    db.session.commit()

    return redirect(url_for('contacto.index'))