from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.menu import Menu
from app import db
from app.models.carrito import Carrito
from flask_login import current_user, login_required
import os
from werkzeug.utils import secure_filename
import uuid  # Para generar nombres aleatorios únicos
bp = Blueprint('menu', __name__)

@bp.route('/menu')
@login_required
def index():
    menus = Menu.query.all()  # Obtiene todos los productos del menú
    carritos = Carrito.query.filter_by(idUser=current_user.idUser).all()
    productos_carrito = []
    
    for carrito in carritos:
        menu = Menu.query.get(carrito.idProducto)
        productos_carrito.append((carrito, menu))
    
    return render_template('menu/index.html', data=menus, carrito=productos_carrito)



# Configuración para la subida de imágenes
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif','jfif','webp','bmp'}
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app', 'static', 'imagenes')  # Ruta absoluta

# Verificar que la carpeta existe, si no, crearla
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    """Verifica si la extensión del archivo es válida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def subir_imagen(img, img_actual=None):
    """Guarda una imagen con un nombre aleatorio y elimina la anterior si existe."""
    if img and allowed_file(img.filename):
        # Generar un nombre único aleatorio con la misma extensión
        ext = img.filename.rsplit('.', 1)[1].lower()
        nuevo_nombre = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(UPLOAD_FOLDER, nuevo_nombre)

        try:
            # Guardar la nueva imagen
            img.save(filepath)
            print(f"✅ Imagen guardada: {filepath}")

            # Eliminar la imagen anterior si existe y no es la predeterminada
            if img_actual and img_actual != "menu.jpg":
                path_anterior = os.path.join(UPLOAD_FOLDER, img_actual)
                if os.path.exists(path_anterior):
                    os.remove(path_anterior)
                    print(f"🗑 Imagen anterior eliminada: {path_anterior}")

            return nuevo_nombre  # Devuelve el nuevo nombre del archivo

        except Exception as e:
            flash(f"❌ Error al guardar la imagen: {str(e)}", "error")
            print(f"❌ Error al guardar la imagen: {str(e)}")

    return "menu.jpg"  # Si hay error o la imagen no es válida, usa la predeterminada
@bp.route('/menu/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['nameProducto']
        DescripcionProducto = request.form['DescripcionProducto']
        precioProducto = request.form['precioProducto']
        menu = Menu(nameProducto=name,DescripcionProducto=DescripcionProducto,precioProducto=precioProducto )
        imagenProducto = subir_imagen(request.files.get('imagenProducto'))
        menu.imagenProducto= imagenProducto
        db.session.add(menu)
        db.session.commit()

        
        return redirect(url_for('menu.index'))
    
    return render_template('menu/add.html')
    

@bp.route('/menu/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    menu = Menu.query.get_or_404(id)

    if request.method == 'POST':
        menu.nameProducto = request.form['nameProducto']
        menu.DescripcionProducto = request.form['DescripcionProducto']
        menu.precioProducto = request.form['precioProducto']

        # Subir imagen si se proporciona
        imagen_nueva = request.files.get('imagenProducto')
        if imagen_nueva:
            imagen_actual = menu.imagenProducto
            menu.imagenProducto = subir_imagen(imagen_nueva, imagen_actual)

        db.session.commit()
        return redirect(url_for('menu.index'))
    
    return render_template('menu/edit.html', menu=menu)


@bp.route('/menu/delete/<int:id>')
def delete(id):    
    menu =Menu.query.get_or_404(id)
    db.session.delete(menu)
    db.session.commit()

    return redirect(url_for('menu.index'))