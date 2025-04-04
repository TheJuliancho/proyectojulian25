from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.users import Users
from app.models.productos import Productos
from app.models.menu import Menu
from app.models.contacto import Contacto
from app.models.carrito import Carrito

from app import db 
bp = Blueprint('auth', __name__)

@bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nameUser = request.form['nameUser']
        passwordUser = request.form['passwordUser']
        
        user = Users.query.filter_by(nameUser=nameUser, passwordUser=passwordUser).first()

        if user:
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for('auth.dashboard'))
        
        flash('Invalid credentials. Please try again.', 'danger')
    
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
    return render_template("login.html")

@bp.route('/dashboard')
@login_required
def dashboard():
    data = Productos.query.all()
    
    # Consulta de datos del carrito
    carritos = Carrito.query.filter_by(idUser=current_user.idUser).all()
    productos_carrito = []
    
    for carrito in carritos:
        producto = Productos.query.get(carrito.idProducto)
        productos_carrito.append((carrito, producto))
    
    # Pasar datos al template
    return render_template("productos/index.html", datapro=data, carrito=productos_carrito)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        nameuser = request.form['nameuser']
        clave = request.form['claveuser']
        new_user = Users (passwordUser=clave,nameUser= nameuser)
        db.session.add( new_user )
        db.session.commit()
        
        return redirect(url_for('auth.login'))

    return render_template('/add.html')
