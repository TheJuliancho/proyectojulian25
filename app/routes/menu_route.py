from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.menu import Menu
from app import db
from app.models.carrito import Carrito
from flask_login import current_user, login_required
from app.decorators import admin_required 
import os
from werkzeug.utils import secure_filename
import uuid  # Para generar nombres aleatorios únicos
bp = Blueprint('menu', __name__)

@bp.route('/menu')
@login_required
def index():
    # Obtener todos los menús de tipo 'postre'
    menus = Menu.query.filter_by(tipo='postre').all()

    # Obtener todos los ítems del carrito del usuario actual
    carritos = Carrito.query.filter_by(idUser=current_user.idUser).all()

    # Extraer todos los ID de productos en el carrito
    ids_productos = [carrito.idProducto for carrito in carritos]

    # Consultar solo los menús necesarios y convertirlos en un diccionario
    menus_dict = {menu.idProducto: menu for menu in Menu.query.filter(Menu.idProducto.in_(ids_productos)).all()}

    total = 0
    productos_carrito = []

    for carrito in carritos:
        menu = menus_dict.get(carrito.idProducto)

        if menu is None:
            # Si no se encuentra el producto, lo ignoramos
            print(f"Producto con ID {carrito.idProducto} no encontrado")
            continue

        subtotal = menu.precioProducto * carrito.cantidad
        total += subtotal
        productos_carrito.append((carrito, menu))

    return render_template('menu/index.html', data=menus, carrito=productos_carrito, total=total)




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
@login_required
@admin_required
def add():
    if request.method == 'POST':
        name = request.form['nameProducto']
        DescripcionProducto = request.form['DescripcionProducto']
        precioProducto = request.form['precioProducto']
        tipo = request.form['tipo']  # Capturamos el tipo

        # Crear el objeto de menú con los datos del formulario
        menu = Menu(nameProducto=name, 
                    DescripcionProducto=DescripcionProducto, 
                    precioProducto=precioProducto, 
                    tipo=tipo)  # Asignamos el tipo

        # Subir la imagen del producto
        imagenProducto = subir_imagen(request.files.get('imagenProducto'))
        menu.imagenProducto = imagenProducto

        # Guardar en la base de datos
        db.session.add(menu)
        db.session.commit()

        return redirect(url_for('menu.index'))
    
    return render_template('menu/add.html')

    

@bp.route('/menu/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    menu = Menu.query.get_or_404(id)

    if request.method == 'POST':
        menu.nameProducto = request.form['nameProducto']
        menu.DescripcionProducto = request.form['DescripcionProducto']
        menu.precioProducto = request.form['precioProducto']

        imagen_nueva = request.files.get('imagenProducto')
        if imagen_nueva:
            imagen_actual = menu.imagenProducto
            menu.imagenProducto = subir_imagen(imagen_nueva, imagen_actual)

        db.session.commit()
        return redirect(url_for('productos.index'))
    
    return render_template('menu/edit.html', menu=menu)


@bp.route('/menu/delete/<int:id>')
@login_required
@admin_required
def delete(id):    
    menu = Menu.query.get_or_404(id)
    db.session.delete(menu)
    db.session.commit()

    return redirect(url_for('productos.index'))

@bp.route('/menu/bebidas')
def bebidas():
    # Filtramos solo los productos cuyo tipo sea 'bebida'
    bebidas = Menu.query.filter_by(tipo='bebida').all()
    print(bebidas)
    return render_template('menu/bebidas.html', data=bebidas)

@bp.route('/menu/bebidasadd', methods=['GET', 'POST'])
@login_required
@admin_required
def bebidasadd():
    if request.method == 'POST':
        name = request.form['nameProducto']
        DescripcionProducto = request.form['DescripcionProducto']
        precioProducto = request.form['precioProducto']
        tipo = request.form['tipo']  # Capturamos el tipo

        # Crear el objeto de menú con los datos del formulario
        menu = Menu(nameProducto=name, 
                    DescripcionProducto=DescripcionProducto, 
                    precioProducto=precioProducto, 
                    tipo=tipo)  # Asignamos el tipo

        # Subir la imagen del producto
        imagenProducto = subir_imagen(request.files.get('imagenProducto'))
        menu.imagenProducto = imagenProducto

        # Guardar en la base de datos
        db.session.add(menu)
        db.session.commit()

        return redirect(url_for('menu.bebidas'))
    
    return render_template('menu/bebidasadd.html')

@bp.route('/menu/editbebibas/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editbebibas(id):
    menu = Menu.query.get_or_404(id)

    if request.method == 'POST':
        menu.nameProducto = request.form['nameProducto']
        menu.DescripcionProducto = request.form['DescripcionProducto']
        menu.precioProducto = request.form['precioProducto']

        imagen_nueva = request.files.get('imagenProducto')
        if imagen_nueva:
            imagen_actual = menu.imagenProducto
            menu.imagenProducto = subir_imagen(imagen_nueva, imagen_actual)

        db.session.commit()
        return redirect(url_for('menu.bebidas'))
    
    return render_template('menu/editbebidas.html', menu=menu)


@bp.route('/menu/pasteles')
def pasteles():
    pasteles = Menu.query.filter_by(tipo='pasteles').all()
    print(pasteles)
    return render_template('menu/pasteles.html', data=pasteles)

@bp.route('/menu/pastelesadd', methods=['GET', 'POST'])
@login_required
@admin_required
def pastelesadd():
    if request.method == 'POST':
        name = request.form['nameProducto']
        DescripcionProducto = request.form['DescripcionProducto']
        precioProducto = request.form['precioProducto']
        tipo = request.form['tipo']  # Capturamos el tipo

        # Crear el objeto de menú con los datos del formulario
        menu = Menu(nameProducto=name, 
                    DescripcionProducto=DescripcionProducto, 
                    precioProducto=precioProducto, 
                    tipo=tipo)  # Asignamos el tipo

        # Subir la imagen del producto
        imagenProducto = subir_imagen(request.files.get('imagenProducto'))
        menu.imagenProducto = imagenProducto

        # Guardar en la base de datos
        db.session.add(menu)
        db.session.commit()

        return redirect(url_for('menu.pasteles'))
    
    return render_template('menu/pastelesadd.html')


@bp.route('/menu/ensaladas')
def ensaladas():
    # Filtramos solo los productos cuyo tipo sea 'bebida'
    ensaladas = Menu.query.filter_by(tipo='ensaladas').all()
    print(ensaladas)
    return render_template('menu/ensaladas.html', data=ensaladas)

@bp.route('/menu/ensaladasadd', methods=['GET', 'POST'])
@login_required
@admin_required
def ensaladasadd():
    if request.method == 'POST':
        name = request.form['nameProducto']
        DescripcionProducto = request.form['DescripcionProducto']
        precioProducto = request.form['precioProducto']
        tipo = request.form['tipo']  # Capturamos el tipo

        # Crear el objeto de menú con los datos del formulario
        menu = Menu(nameProducto=name, 
                    DescripcionProducto=DescripcionProducto, 
                    precioProducto=precioProducto, 
                    tipo=tipo)  # Asignamos el tipo

        # Subir la imagen del producto
        imagenProducto = subir_imagen(request.files.get('imagenProducto'))
        menu.imagenProducto = imagenProducto

        # Guardar en la base de datos
        db.session.add(menu)
        db.session.commit()

        return redirect(url_for('menu.ensaladas'))
    
    return render_template('menu/ensaladasadd.html')


# LISTADO de galletas
@bp.route('/menu/galletas')
def galletas():
    galletas = Menu.query.filter_by(tipo='galletas').all()
    return render_template('menu/galletas.html', data=galletas)

# AÑADIR galletas
@bp.route('/menu/galletasadd', methods=['GET', 'POST'])
@login_required
@admin_required
def galletasadd():
    if request.method == 'POST':
        name  = request.form['nameProducto']
        desc  = request.form['DescripcionProducto']
        precio= request.form['precioProducto']
        # Forzamos el tipo aquí:
        nuevo = Menu(
            nameProducto       = name,
            DescripcionProducto= desc,
            precioProducto     = precio,
            tipo               = 'galletas'
        )
        nuevo.imagenProducto = subir_imagen(request.files.get('imagenProducto'))

        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for('menu.galletas'))

    return render_template('menu/galletasadd.html')





@bp.route('/combos')
def combos():
    return render_template('menu/combos.html')

@bp.route('/personalizados')
def personalizados():
    return render_template('menu/personalizados.html')