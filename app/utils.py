# app/utils.py
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generar_factura(datos_factura):
    archivo_pdf = f"factura_{datos_factura['numero']}.pdf"
    c = canvas.Canvas(archivo_pdf, pagesize=letter)
    c.drawString(100, 750, f"Factura: {datos_factura['numero']}")
    c.drawString(100, 730, f"Cliente: {datos_factura['cliente']}")
    c.drawString(100, 710, f"Fecha: {datos_factura['fecha']}")
    c.drawString(100, 690, f"Subtotal: ${datos_factura['subtotal']}")
    c.drawString(100, 670, f"IVA: ${datos_factura['iva']}")
    c.drawString(100, 650, f"Total: ${datos_factura['total']}")
    c.save()

    return archivo_pdf  # Devuelve el nombre del archivo PDF generado
