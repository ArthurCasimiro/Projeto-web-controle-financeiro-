from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('home_page'))
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('home_page'))
        if current_user.role != 'admin':
            flash('Acesso restrito a administradores.', 'erro')
            return redirect(url_for('dashboard.painel'))
        return f(*args, **kwargs)
    return wrapper
