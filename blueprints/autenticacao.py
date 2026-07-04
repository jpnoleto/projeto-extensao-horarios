from db import conectar
from auth import requer_login, usuario_logado
from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash


def registrar(app):

    @app.route('/')
    @requer_login
    def index():
        stats = dict(total_professores=0, total_turmas=0,
                     total_disciplinas=0, total_alocacoes=0)
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT COUNT(*) AS total FROM professor WHERE status='ativo'")
            stats['total_professores'] = cursor.fetchone()['total']
            cursor.execute("SELECT COUNT(*) AS total FROM turma")
            stats['total_turmas'] = cursor.fetchone()['total']
            cursor.execute("SELECT COUNT(*) AS total FROM disciplina")
            stats['total_disciplinas'] = cursor.fetchone()['total']
            cursor.execute("SELECT COUNT(*) AS total FROM alocacao")
            stats['total_alocacoes'] = cursor.fetchone()['total']
        return render_template('index.html', **stats)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if usuario_logado():
            return redirect(url_for('index'))
        if request.method == 'POST':
            email = request.form.get('email', '').strip()
            senha = request.form.get('senha', '')
            with conectar() as conexao:
                cursor = conexao.cursor()
                cursor.execute("SELECT * FROM usuario WHERE email = %s", (email,))
                usuario = cursor.fetchone()
            if usuario and check_password_hash(usuario['senha_hash'], senha):
                session.clear()
                session['usuario_id'] = usuario['id_usuario']
                session['usuario_nome'] = usuario['nome']
                return redirect(url_for('index'))
            flash("E-mail ou senha inválidos.", 'erro')
        return render_template('login.html')

    @app.route('/logout', methods=['POST'])
    def logout():
        session.clear()
        return redirect(url_for('login'))
