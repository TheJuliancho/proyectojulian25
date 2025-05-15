# app/decorators.py

from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol != 'admin':
            flash("Acceso denegado: se requiere permiso de administrador.", "danger")
            return redirect(url_for('menu.index'))
        return f(*args, **kwargs)
    return decorated_function
