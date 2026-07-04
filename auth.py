from functools import wraps
from flask import session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash


def usuario_logado():
    if 'usuario_id' not in session:
        return None
    return {
        'id': session['usuario_id'],
        'nome': session['usuario_nome'],
    }


def requer_login(f):
    @wraps(f)
    def decorado(*args, **kwargs):
        if not usuario_logado():
            flash("Faça login para continuar.", 'erro')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorado


# Sistema com um único perfil (administrador). Mantido como alias de `requer_login`
# para não reescrever o decorator em cada rota dos blueprints — só exige login.
def requer_perfil(*_perfis):
    return requer_login
