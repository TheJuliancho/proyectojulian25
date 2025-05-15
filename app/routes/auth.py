from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.decorators import admin_required 
from app.models.users import Users
from app.models.productos import Productos
from app.models.menu import Menu
from app.models.contacto import Contacto
from app.models.carrito import Carrito
from werkzeug.security import check_password_hash
from app import db 
bp = Blueprint('auth', __name__)

@bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nameUser = request.form['nameUser']
        clave = request.form['passwordUser']
        print(clave)
        # Buscar al usuario en la base de datos
        user = Users.query.filter_by(nameUser=nameUser, passwordUser = clave).first()
        print(user)
        if user:  # Compara usando hash
            login_user(user)
            
            # Redirigir según el rol del usuario
            if user.rol == 'admin':
                flash(f"¡Bienvenido  Admin, {current_user.nameUser}!", "success")
                return redirect(url_for('auth.dashboard')) 
            else:
                flash(f"¡Bienvenido cliente, {current_user.nameUser}!", "success")
                return redirect(url_for('auth.dashboard'))  
            
        # Si las credenciales son incorrectas
        flash('Credenciales inválidas. Intenta nuevamente.', 'danger')

    if current_user.is_authenticated:
        # Redirigir a un dashboard si ya está autenticado
        return redirect(url_for('auth.dashboard'))  
    
    # Si no está autenticado, mostrar el formulario de login
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
        nameUser = request.form['nameUser']
        clave = request.form['passwordUser']
        rol = request.form.get('rol', 'cliente')  # Por defecto: cliente

        # Verificar si el nombre de usuario ya existe
    
        usuario_existente = Users.query.filter_by(nameUser=nameUser).first()
        if usuario_existente:
            flash(f"El usuario '{nameUser}' ya existe. Intenta con otro nombre.", 'error')
            return redirect(url_for('auth.add'))

        # Crear el nuevo usuario
        new_user = Users(nameUser=nameUser, passwordUser=clave, rol=rol)
        db.session.add(new_user)
        try:
            db.session.commit()
            flash('Usuario creado exitosamente.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar el usuario: {str(e)}', 'error')

    return render_template('/add.html')

