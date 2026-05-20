import pymysql
from db import conectar
from auth import requer_perfil
from flask import render_template, request, redirect, url_for, flash


def registrar(app):

    @app.route('/cadastrar_local')
    @requer_perfil('diretor', 'secretaria')
    def cadastrar_local():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM `local` ORDER BY nome")
            locais = cursor.fetchall()
        return render_template('cadastro_local.html', locais=locais)

    @app.route('/salvar_local', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def salvar_local():
        nome = request.form.get('nome', '').strip()
        tipo = request.form.get('tipo', '').strip()

        if not nome:
            flash("O nome do local é obrigatório.", 'erro')
            return redirect(url_for('cadastrar_local'))
        if not tipo:
            flash("O tipo do local é obrigatório.", 'erro')
            return redirect(url_for('cadastrar_local'))

        try:
            with conectar() as conexao:
                cursor = conexao.cursor()
                cursor.execute("INSERT INTO `local` (nome, tipo) VALUES (%s, %s)", (nome, tipo))
                conexao.commit()
            return redirect(url_for('listar_locais'))
        except pymysql.IntegrityError:
            flash("Já existe um local com esse nome.", 'erro')
            return redirect(url_for('cadastrar_local'))

    @app.route('/locais')
    @requer_perfil('diretor', 'secretaria')
    def listar_locais():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM `local` ORDER BY nome")
            locais = cursor.fetchall()
        return render_template('locais.html', locais=locais, local_edicao=None)

    @app.route('/editar_local/<int:id_local>')
    @requer_perfil('diretor', 'secretaria')
    def editar_local(id_local):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute('SELECT * FROM `local` ORDER BY nome')
            locais = cursor.fetchall()
            cursor.execute('SELECT * FROM `local` WHERE id_local = %s', (id_local,))
            local_edicao = cursor.fetchone()
        return render_template('locais.html', locais=locais, local_edicao=local_edicao)

    @app.route('/atualizar_local/<int:id_local>', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def atualizar_local(id_local):
        nome = request.form.get('nome', '').strip()
        tipo = request.form.get('tipo', '').strip()
        status = request.form.get('status', 'ativo')

        if not nome:
            flash("O nome do local é obrigatório.", 'erro')
            return redirect(url_for('editar_local', id_local=id_local))

        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                UPDATE `local` SET nome = %s, tipo = %s, status = %s
                WHERE id_local = %s
            """, (nome, tipo, status, id_local))
            conexao.commit()
        return redirect(url_for('listar_locais'))

    @app.route('/deletar_local/<int:id_local>', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def deletar_local(id_local):
        try:
            with conectar() as conexao:
                cursor = conexao.cursor()
                cursor.execute('DELETE FROM `local` WHERE id_local = %s', (id_local,))
                conexao.commit()
        except pymysql.IntegrityError:
            flash("Não é possível excluir este local pois ele está sendo usado em alocações. "
                  "Remova as alocações relacionadas ou desative o local.", 'erro')
        return redirect(url_for('listar_locais'))
