from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.comentario import Comentario
from app.forms import ComentarioForm

bp = Blueprint('comentarios', __name__, url_prefix='/comentarios')

@bp.route('/', methods=['GET'])
@login_required
def listar_comentarios():
    comentarios = Comentario.query.order_by(Comentario.fecha.desc()).all()
    return render_template('comentarios/list.html', comentarios=comentarios)

@bp.route('/nuevo', methods=['GET','POST'])
@login_required
def nuevo_comentario():
    form = ComentarioForm()
    if form.validate_on_submit():
        c = Comentario(
            contenido    = form.contenido.data,
            calificacion = form.calificacion.data,  # ✅ Guardamos la calificación
            user_id      = current_user.idUser
        )
        db.session.add(c)
        db.session.commit()
        flash("¡Gracias por tu comentario!", "success")
        return redirect(url_for('comentarios.listar_comentarios'))
    return render_template('comentarios/new.html', form=form)

@bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_comentario(id):
    if current_user.rol != 'admin':
        flash("No tienes permiso para eliminar comentarios.", "danger")
        return redirect(url_for('comentarios.listar_comentarios'))

    comentario = Comentario.query.get_or_404(id)
    db.session.delete(comentario)
    db.session.commit()
    flash("Comentario eliminado correctamente.", "success")
    return redirect(url_for('comentarios.listar_comentarios'))
