from flask import Blueprint, render_template, redirect, url_for, flash, send_file
from flask_login import current_user, login_required
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet

from app.models.carrito import Carrito
from app.models.menu import Menu
from app.models.factura import Factura, DetalleFactura
from app import db

bp = Blueprint('factura', __name__)

# ✅ Función mejorada para generar el PDF de factura
def generar_factura(datos_factura):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=40)

    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    style_normal = styles['Normal']
    style_bold = styles['Heading2']
    
    # Logo de la empresa (se asume que el logo está en la carpeta 'static')
    logo = "static/imagenes/logo.jfif"  # Cambia esta ruta según tu estructura
    img = Image(logo, width=200, height=50)
    elements.append(img)
    elements.append(Spacer(1, 12))

    # Título y datos de la factura
    elements.append(Paragraph(f"<b>Factura:</b> {datos_factura['numero']}", style_bold))
    elements.append(Paragraph(f"<b>Cliente:</b> {datos_factura['cliente']}", style_normal))
    elements.append(Paragraph(f"<b>Dirección:</b> {datos_factura['direccion']}", style_normal))
    elements.append(Paragraph(f"<b>Fecha:</b> {datos_factura['fecha']}", style_normal))
    elements.append(Spacer(1, 12))

    # Tabla de productos
    data = [["Producto", "Cantidad", "Precio Unitario", "Total"]]
    for item in datos_factura['items']:
        data.append([
            item['descripcion'],
            str(item['cantidad']),
            f"${item['precio_unitario']:.2f}",
            f"${item['total']:.2f}"
        ])

    # Totales
    data.append(["", "", "Subtotal:", f"${datos_factura['subtotal']:.2f}"])
    data.append(["", "", "IVA (16%):", f"${datos_factura['iva']:.2f}"])
    data.append(["", "", "Total:", f"${datos_factura['total']:.2f}"])

    table = Table(data, colWidths=[200, 80, 100, 100])
    
    # Estilo de la tabla
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f2f2f2")),  # Color de fondo en el encabezado
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
    ])
    table.setStyle(style)

    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ✅ Ruta para procesar la compra y generar la factura
@bp.route('/carrito/comprar', methods=['POST'])
@login_required
def comprar_carrito():
    carritos = Carrito.query.filter_by(idUser=current_user.idUser).all()
    if not carritos:
        flash('Tu carrito está vacío', 'error')
        return redirect(url_for('carrito.index'))

    items = []
    subtotal = 0
    cliente = current_user.nombre  # Asegúrate que estos atributos existan
    direccion = current_user.direccion
    fecha = datetime.now().strftime("%d/%m/%Y")
    numero = f"FAC-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    for carrito in carritos:
        menu = Menu.query.get(carrito.idProducto)
        if menu:
            total_producto = menu.precioProducto * carrito.cantidad
            subtotal += total_producto
            items.append({
                'descripcion': menu.nameProducto,
                'cantidad': carrito.cantidad,
                'precio_unitario': menu.precioProducto,
                'total': total_producto,
                'idProducto': menu.idProducto
            })
        else:
            flash('Producto no encontrado', 'error')

    iva = subtotal * 0.16
    total = subtotal + iva

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

    # Guardar en BD
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

    for item in items:
        detalle = DetalleFactura(
            factura_id=factura.id,
            producto_id=item['idProducto'],
            cantidad=item['cantidad'],
            precio_unitario=item['precio_unitario'],
            total=item['total']
        )
        db.session.add(detalle)
    db.session.commit()

    # Limpiar carrito
    for carrito in carritos:
        db.session.delete(carrito)
    db.session.commit()

    # Redirigir a descargar factura
    return redirect(url_for('factura.descargar_factura', factura_id=factura.id))

# ✅ Ruta para descargar el PDF de la factura
@bp.route('/factura/descargar/<int:factura_id>')
@login_required
def descargar_factura(factura_id):
    factura = Factura.query.get(factura_id)
    if not factura:
        return "Factura no encontrada", 404

    datos_factura = {
        'cliente': factura.cliente.nombre,
        'direccion': factura.cliente.direccion,
        'fecha': factura.fecha.strftime("%d/%m/%Y"),
        'numero': factura.numero,
        'items': [
            {
                'descripcion': item.producto.nameProducto if item.producto else 'Producto eliminado',
                'cantidad': item.cantidad,
                'precio_unitario': item.precio_unitario,
                'total': item.total
            }
            for item in factura.detalles
        ],
        'subtotal': factura.subtotal,
        'iva': factura.iva,
        'total': factura.total
    }

    pdf = generar_factura(datos_factura)
    return send_file(
        pdf,
        mimetype='application/pdf',
        download_name=f'factura_{factura.numero}.pdf',
        as_attachment=True
    )
