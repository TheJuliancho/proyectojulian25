
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from app.models.carrito import Carrito
from app.models.menu import Menu
from app import db

bp = Blueprint('carrito', __name__)



@bp.route('/carrito')
@login_required
def index():
    carritos = Carrito.query.filter_by(idUser=current_user.idUser).all()
    productos_carrito = []
    
    for carrito in carritos:
        menu = Menu.query.get(carrito.idProducto)
        productos_carrito.append((carrito, menu))
    
    if not productos_carrito:
        flash('El carrito está vacío', 'info')
    
    return render_template('menu/index.html', data=productos_carrito)

@bp.route('/carrito/comprar', methods=['POST'])
@login_required
def comprar_carrito():
    carritos = Carrito.query.filter_by(idUser=current_user.idUser).all()
    total = 0
    
    for carrito in carritos:
        menu = Menu.query.get(carrito.idProducto)
        
        if menu and carrito:
            total += int(menu.precioProducto) * int(carrito.cantidad)
        else:
            flash('Error al obtener los productos del carrito', 'error')
    
    # Realiza la transacción (pago, actualizar stock, etc.)
    try:
        # Código para realizar la transacción...
        # Por ejemplo, puedes usar una API de pago o actualizar el stock de los productos
        
        # Limpiar el carrito después de la compra
        for carrito in carritos:
            db.session.delete(carrito)
        db.session.commit()
        
        flash('Compra realizada correctamente', 'success')
    except Exception as e:
        flash(f"Error al realizar la compra: {str(e)}", "error")
    
    return redirect(url_for('carrito.index'))





@bp.route('/carrito/add/<int:idProducto>', methods=['GET', 'POST'])
@login_required
def agregar_carrito(idProducto):
    # Verifica si el producto existe
    menu = Menu.query.get(idProducto)
    if not menu:
        flash('El producto no existe', 'error')
        return redirect(url_for('menu.index'))
    
    carrito = Carrito.query.filter_by(idUser=current_user.idUser, idProducto=idProducto).first()
    
    try:
        if carrito:
            carrito.cantidad += 1
        else:
            carrito = Carrito(idUser=current_user.idUser, idProducto=idProducto, cantidad=1)
            db.session.add(carrito)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash('Error al agregar al carrito', 'error')
    
    return redirect(url_for('menu.index'))



@bp.route('/carrito/delete/<int:id>')
@login_required
def eliminar_carrito(idCarrito):
    carrito = Carrito.query.get_or_404(idCarrito)
    
    if carrito.idUser == current_user.idUser:
        db.session.delete(carrito)
        db.session.commit()
    
    return redirect(url_for('carrito.index'))
