import pymysql
from db import conectar
from auth import requer_login
from flask import render_template, request, redirect, url_for, flash

TURNOS = ['Matutino', 'Vespertino', 'Noturno']


def registrar(app):

    @app.route('/cadastrar_turma')
    @requer_login
    def cadastrar_turma():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT id_turma, nome, serie, turno
                FROM turma ORDER BY turno, serie, nome
            """)
            turmas = cursor.fetchall()
        return render_template('cadastro_turma.html', turnos=TURNOS, turmas=turmas)

    @app.route('/salvar_turma', methods=['POST'])
    @requer_login
    def salvar_turma():
        nome = request.form.get('nome', '').strip()
        serie = request.form.get('serie', '').strip()
        turno = request.form.get('turno', '').strip()

        if not nome:
            flash("O nome da turma é obrigatório.", 'erro')
            return redirect(url_for('cadastrar_turma'))
        if not serie:
            flash("A série é obrigatória.", 'erro')
            return redirect(url_for('cadastrar_turma'))
        if turno not in TURNOS:
            flash("Selecione um turno válido.", 'erro')
            return redirect(url_for('cadastrar_turma'))

        try:
            with conectar() as conexao:
                cursor = conexao.cursor()
                cursor.execute("""
                    INSERT INTO turma (nome, serie, turno)
                    VALUES (%s, %s, %s)
                """, (nome, serie, turno))
                conexao.commit()
            return redirect(url_for('listar_turmas'))
        except pymysql.IntegrityError:
            flash("Essa turma já existe.", 'erro')
            return redirect(url_for('cadastrar_turma'))

    @app.route('/turmas')
    @requer_login
    def listar_turmas():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT id_turma, nome, serie, turno
                FROM turma ORDER BY turno, serie, nome
            """)
            turmas = cursor.fetchall()
        return render_template('turmas.html', turmas=turmas, turnos=TURNOS, turma_edicao=None)

    @app.route('/editar_turma/<int:id_turma>')
    @requer_login
    def editar_turma(id_turma):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT id_turma, nome, serie, turno
                FROM turma ORDER BY turno, serie, nome
            """)
            turmas = cursor.fetchall()
            cursor.execute("SELECT * FROM turma WHERE id_turma = %s", (id_turma,))
            turma_edicao = cursor.fetchone()
        return render_template('turmas.html', turmas=turmas, turnos=TURNOS, turma_edicao=turma_edicao)

    @app.route('/atualizar_turma/<int:id_turma>', methods=['POST'])
    @requer_login
    def atualizar_turma(id_turma):
        nome = request.form.get('nome', '').strip()
        serie = request.form.get('serie', '').strip()
        turno = request.form.get('turno', '').strip()

        if not nome:
            flash("O nome da turma é obrigatório.", 'erro')
            return redirect(url_for('editar_turma', id_turma=id_turma))
        if turno not in TURNOS:
            flash("Selecione um turno válido.", 'erro')
            return redirect(url_for('editar_turma', id_turma=id_turma))

        try:
            with conectar() as conexao:
                cursor = conexao.cursor()
                cursor.execute("""
                    UPDATE turma SET nome = %s, serie = %s, turno = %s
                    WHERE id_turma = %s
                """, (nome, serie, turno, id_turma))
                conexao.commit()
            return redirect(url_for('listar_turmas'))
        except pymysql.IntegrityError:
            flash("Já existe uma turma com esse nome, série e turno.", 'erro')
            return redirect(url_for('editar_turma', id_turma=id_turma))

    @app.route('/deletar_turma/<int:id_turma>', methods=['POST'])
    @requer_login
    def deletar_turma(id_turma):
        try:
            with conectar() as conexao:
                cursor = conexao.cursor()
                cursor.execute('DELETE FROM turma WHERE id_turma = %s', (id_turma,))
                conexao.commit()
        except pymysql.IntegrityError:
            flash("Não é possível excluir: a turma tem aulas alocadas. Remova a grade dela antes.", 'erro')
        return redirect(url_for('listar_turmas'))
