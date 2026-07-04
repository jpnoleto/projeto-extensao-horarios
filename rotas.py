import os
from dotenv import load_dotenv
load_dotenv()
from flask import Flask
import auth

from blueprints import (
    autenticacao, professores, disciplinas, turmas, horarios,
    disponibilidade, alocacao, relatorio
)

DEBUG = os.environ.get('FLASK_DEBUG', '').lower() in ('1', 'true', 'yes')
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        print('[AVISO] SECRET_KEY nao definida -- usando fallback inseguro apenas para desenvolvimento local.')
        SECRET_KEY = 'dev-local-fallback-not-secure-do-not-use-in-production'
    else:
        raise RuntimeError(
            'SECRET_KEY é obrigatória em produção. Defina a variável de ambiente '
            'SECRET_KEY com um valor aleatório (ex: openssl rand -hex 32).'
        )

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config.update(
    TEMPLATES_AUTO_RELOAD=DEBUG,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=not DEBUG,  # HTTPS-only em produção
)

autenticacao.registrar(app)
professores.registrar(app)
disciplinas.registrar(app)
turmas.registrar(app)
horarios.registrar(app)
disponibilidade.registrar(app)
alocacao.registrar(app)
relatorio.registrar(app)


@app.context_processor
def injetar_usuario():
    return dict(usuario_atual=auth.usuario_logado())


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=DEBUG, use_reloader=False)
