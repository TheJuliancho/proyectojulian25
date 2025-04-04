from flask import Blueprint, render_template, request, redirect, url_for
from app.models.productos import Productos
from app import db

bp = Blueprint('productos', __name__)


@bp.route('/productos')
def index():
    data = Productos.query.all()   
    return render_template('Productos/index.html', data=data)

    
@bp.route('/productos/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['nameProducto']
        producto = Productos(nameProducto=name )
        db.session.add(producto)
        db.session.commit()
        
        return redirect(url_for('productos.index'))
    
    return render_template('productos/add.html')
    

@bp.route('/productos/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    productos = Productos.query.get_or_404(id)

    if request.method == 'POST':
        productos.nameProductos= request.form['nameProductos']
        db.session.commit()
        return redirect(url_for('Productos.index'))
    return render_template('productos/edit.html', producto=productos)

@bp.route('/productos/delete/<int:id>')
def delete(id):    
    productos =Productos.query.get_or_404(id)
    db.session.delete(productos)
    db.session.commit()

    return redirect(url_for('productos.index'))
