
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import current_user, login_required
from app.models.factura import Factura, DetalleFactura
from app.models.carrito import Carrito
from reportlab.pdfgen import canvas
from app.models.menu import Menu
from datetime import datetime
from reportlab.lib.pagesizes import letter
from app import db
import io

bp = Blueprint('carrito', __name__)



@bp.route('/carrito')
@login_required
def index():
    carritos = Carrito.query.filter_by(idUser=current_user.idUser).all()
    productos_carrito = []
    
    print("entra a index")
    for carrito in carritos:
        menu = Menu.query.get(carrito.idProducto)
        if menu:
            productos_carrito.append((carrito, menu))

    return render_template('menu/index.html', carrito=productos_carrito)


# app/routes/carrito_routes.py
from reportlab.lib.pagesizes import letter

def generar_factura(datos_factura):
    # Crear un archivo PDF en memoria utilizando BytesIO
    pdf_output = io.BytesIO()

    # Crear el objeto canvas, apuntando al objeto en memoria
    c = canvas.Canvas(pdf_output, pagesize=letter)

    # Escribir los datos en el PDF (como en el código original)
    c.drawString(100, 750, f"Factura: {datos_factura['numero']}")
    c.drawString(100, 730, f"Cliente: {datos_factura['cliente']}")
    c.drawString(100, 710, f"Fecha: {datos_factura['fecha']}")
    c.drawString(100, 690, f"Subtotal: ${datos_factura['subtotal']}")
    c.drawString(100, 670, f"IVA: ${datos_factura['iva']}")
    c.drawString(100, 650, f"Total: ${datos_factura['total']}")
    
    # Finalizar la creación del PDF
    c.save()

    # Mover el puntero a la posición inicial para que pueda enviarse el archivo
    pdf_output.seek(0)

    return pdf_output

@bp.route('/carrito/comprar', methods=['POST'])
@login_required
def comprar_carrito():
    # Obtener los productos del carrito del usuario actual
    carritos = Carrito.query.filter_by(idUser=current_user.idUser).all()
    if not carritos:
        flash('Tu carrito está vacío', 'error')
        return redirect(url_for('carrito.index'))

    # Inicializar variables
    items = []
    subtotal = 0
    iva = 0
    total = 0
    cliente = current_user.nameUser
    direccion = current_user.direccion
    fecha = datetime.now().strftime("%d/%m/%Y")
    numero = f"FAC-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Calcular subtotal, IVA y total
    for carrito in carritos:
        menu = Menu.query.get(carrito.idProducto)
        if menu:
            precio = float(menu.precioProducto)
            cantidad = int(carrito.cantidad)
            total_producto = precio * cantidad
            subtotal += total_producto
            items.append({
                'idProducto': menu.idProducto,  # ✅ agregamos idProducto aquí
                'descripcion': menu.nameProducto,
                'cantidad': cantidad,
                'precio_unitario': precio,
                'total': total_producto
            })
        else:
            flash('Error al obtener algunos productos del carrito', 'error')

    iva = subtotal * 0.16
    total = subtotal + iva

    # Datos para la factura (opcional: usado para generar PDF)
    datos_factura = {
        'cliente': cliente,
        'direccion': direccion,
        'fecha': fecha,
        'numero': numero,
        'items': items,
        'subtotal': subtotal,
        'iva': iva,
        'total': total
    }

    # Generar factura en PDF
    pdf = generar_factura(datos_factura)

    # Guardar la factura en la base de datos
    print("antes de la factura")
    print(current_user.idUser)
    
    factura = Factura( 
        cliente_id=current_user.idUser,
        fecha=datetime.now(),
        numero=numero,
        subtotal=subtotal,
        iva=iva,
        total=total
    )

    db.session.add(factura)
    db.session.commit()

    # Agregar detalles de la factura
    for item in items:
        detalle = DetalleFactura(
            factura_id=factura.id,
            producto_id=item['idProducto'],  # ✅ ahora correcto
            cantidad=item['cantidad'],
            precio_unitario=item['precio_unitario'],
            total=item['total']
        )
        db.session.add(detalle)
    db.session.commit()

    # Vaciar carrito del usuario
    for carrito in carritos:
        db.session.delete(carrito)
    db.session.commit()

    # Redirigir a la página de confirmación
    return redirect(url_for('carrito.mostrar_confirmacion_factura', factura_id=factura.id))


@bp.route('/factura/confirmacion/<int:factura_id>')
@login_required

def mostrar_confirmacion_factura(factura_id):
    print("mostrar factura")
    factura = Factura.query.get(factura_id)
    if not factura:
        flash('Factura no encontrada', 'error')
        return redirect(url_for('carrito.index'))
    
    return render_template('facturas/facturas.html', factura=factura)

@bp.route('/factura/descargar/<int:factura_id>')
def descargar_factura(factura_id):
    factura = Factura.query.get(factura_id)
    if factura:
        # Recopilar los datos de la factura
        datos_factura = {
            'cliente': factura.cliente.nameUser,
            'direccion': factura.cliente.direccion,
            'fecha': factura.fecha.strftime("%d/%m/%Y"),
            'numero': factura.numero,
            'items': [
                {'descripcion': item.producto.nameProducto if item.producto else 'Producto no encontrado',
                'cantidad': item.cantidad, 'precio_unitario': item.precio_unitario, 'total': item.total}
                for item in factura.detalles
            ],
            'subtotal': factura.subtotal,
            'iva': factura.iva,
            'total': factura.total
        }

        # Generar el archivo PDF en memoria
        pdf = generar_factura(datos_factura)

        # Usar send_file para devolver el archivo generado en memoria
        return send_file(
            pdf,
            mimetype='application/pdf',
            download_name=f'factura_{factura.numero}.pdf',
            as_attachment=True
        )
    else:
        return "Factura no encontrada", 404

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
    flash(f'Agregado al carrito {menu.nameProducto}', 'success')
    return redirect(url_for('menu.index'))



@bp.route('/carrito/delete/<int:id>')
@login_required
def eliminar_carrito(id):
    carrito = Carrito.query.get_or_404(id)
    if carrito.idUser == current_user.idUser:
        db.session.delete(carrito)
        db.session.commit()
    return redirect(url_for('productos.index'))



