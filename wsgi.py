"""
WSGI entry point para PythonAnywhere.

No painel do PythonAnywhere (aba Web > Code), edite o arquivo
/var/www/<seu_usuario>_pythonanywhere_com_wsgi.py
e cole/importe este módulo.

Em outras plataformas (Railway, Render, Fly.io), o app é importado
via Procfile/gunicorn — este arquivo é IGNORADO.
"""
import os
import sys

# Garante que o diretório do projeto está no path
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# Carrega .env do diretório do projeto antes de importar rotas
from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_DIR, '.env'))

from rotas import app as application  # noqa: E402
