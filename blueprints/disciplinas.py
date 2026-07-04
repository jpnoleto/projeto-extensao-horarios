import pymysql
from db import conectar
from auth import requer_login
from flask import render_template, request, redirect, url_for, flash


def registrar(app):

    @app.route('/cadastrar_disciplina')
    @requer_login
    def cadastrar_disciplina():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute('SELECT * FROM disciplina ORDER BY nome')
            disciplinas = cursor.fetchall()
        return render_template('cadastro_disciplina.html', disciplinas=disciplinas)

    @app.route('/salvar_disciplina', methods=['POST'])
    @requer_login
    def salvar_disciplina():
        nome = request.form.get('nome', '').strip()
        sigla = request.form.get('sigla', '').strip()
        cor = request.form.get('cor', '#ffffff').strip()

        if not nome:
            flash("O nome é obrigatório.", 'erro')
            return redirect(url_for('cadastrar_disciplina'))
        if not sigla:
            flash("A sigla é obrigatória.", 'erro')
            return redirect(url_for('cadastrar_disciplina'))

        try:
            with conectar() as conexao:
                cursor = conexao.cursor()
                cursor.execute("""
                    INSERT INTO disciplina (nome, sigla, cor)
                    VALUES (%s, %s, %s)
                """, (nome, sigla, cor))
                conexao.commit()
            return redirect(url_for('listar_disciplinas'))
        except pymysql.IntegrityError:
            flash("Já existe uma disciplina com esse nome ou sigla.", 'erro')
            return redirect(url_for('cadastrar_disciplina'))

    @app.route('/disciplinas')
    @requer_login
    def listar_disciplinas():
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = 20
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute('SELECT COUNT(*) AS total FROM disciplina')
            total = cursor.fetchone()['total']
            cursor.execute('SELECT * FROM disciplina ORDER BY nome LIMIT %s OFFSET %s',
                           (por_pagina, (pagina - 1) * por_pagina))
            disciplinas = cursor.fetchall()
        total_paginas = max(1, (total + por_pagina - 1) // por_pagina)
        return render_template('disciplinas.html', disciplinas=disciplinas,
                               pagina=pagina, total_paginas=total_paginas, total=total)

    @app.route('/editar_disciplina/<int:id_disciplina>')
    @requer_login
    def editar_disciplina(id_disciplina):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute('SELECT * FROM disciplina ORDER BY nome')
            disciplinas = cursor.fetchall()
            cursor.execute('SELECT * FROM disciplina WHERE id_disciplina = %s', (id_disciplina,))
            disciplina_edicao = cursor.fetchone()
        return render_template('disciplinas.html', disciplinas=disciplinas, disciplina_edicao=disciplina_edicao)

    @app.route('/atualizar_disciplina/<int:id_disciplina>', methods=['POST'])
    @requer_login
    def atualizar_disciplina(id_disciplina):
        nome = request.form.get('nome', '').strip()
        sigla = request.form.get('sigla', '').strip()
        cor = request.form.get('cor', '#ffffff').strip()

        if not nome:
            flash("O nome é obrigatório.", 'erro')
            return redirect(url_for('editar_disciplina', id_disciplina=id_disciplina))

        try:
            with conectar() as conexao:
                cursor = conexao.cursor()
                cursor.execute("""
                    UPDATE disciplina
                    SET nome = %s, sigla = %s, cor = %s
                    WHERE id_disciplina = %s
                """, (nome, sigla, cor, id_disciplina))
                conexao.commit()
            return redirect(url_for('listar_disciplinas'))
        except pymysql.IntegrityError:
            flash("Já existe uma disciplina com esse nome ou sigla.", 'erro')
            return redirect(url_for('editar_disciplina', id_disciplina=id_disciplina))

    @app.route('/deletar_disciplina/<int:id_disciplina>', methods=['POST'])
    @requer_login
    def deletar_disciplina(id_disciplina):
        try:
            with conectar() as conexao:
                cursor = conexao.cursor()
                cursor.execute('DELETE FROM disciplina WHERE id_disciplina = %s', (id_disciplina,))
                conexao.commit()
        except pymysql.IntegrityError:
            flash("Não é possível excluir: a disciplina está alocada em algum horário. "
                  "Remova as aulas dela antes.", 'erro')
        return redirect(url_for('listar_disciplinas'))
