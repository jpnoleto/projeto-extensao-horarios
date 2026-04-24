import pymysql
from db import conectar
from auth import requer_perfil
from flask import render_template, request, redirect, url_for, flash


def registrar(app):

    @app.route('/cadastrar_disciplina')
    @requer_perfil('diretor', 'secretaria')
    def cadastrar_disciplina():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute('SELECT * FROM disciplina ORDER BY nome')
            disciplinas = cursor.fetchall()
        return render_template('cadastro_disciplina.html', disciplinas=disciplinas)

    @app.route('/salvar_disciplina', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def salvar_disciplina():
        nome = request.form.get('nome', '').strip()
        sigla = request.form.get('sigla', '').strip()
        cor = request.form.get('cor', '#ffffff').strip()
        carga = request.form.get('carga_horaria_semanal', '').strip()

        if not nome:
            flash("O nome é obrigatório.", 'erro')
            return redirect(url_for('cadastrar_disciplina'))
        if not sigla:
            flash("A sigla é obrigatória.", 'erro')
            return redirect(url_for('cadastrar_disciplina'))
        if not carga:
            flash("A carga horária é obrigatória.", 'erro')
            return redirect(url_for('cadastrar_disciplina'))

        try:
            with conectar() as conexao:
                cursor = conexao.cursor()
                cursor.execute("""
                    INSERT INTO disciplina (nome, sigla, cor, carga_horaria_semanal)
                    VALUES (%s, %s, %s, %s)
                """, (nome, sigla, cor, carga))
                conexao.commit()
            return redirect(url_for('listar_disciplinas'))
        except pymysql.IntegrityError:
            flash("Já existe uma disciplina com esse nome ou sigla.", 'erro')
            return redirect(url_for('cadastrar_disciplina'))

    @app.route('/disciplinas')
    @requer_perfil('diretor', 'secretaria')
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
    @requer_perfil('diretor', 'secretaria')
    def editar_disciplina(id_disciplina):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute('SELECT * FROM disciplina ORDER BY nome')
            disciplinas = cursor.fetchall()
            cursor.execute('SELECT * FROM disciplina WHERE id_disciplina = %s', (id_disciplina,))
            disciplina_edicao = cursor.fetchone()
        return render_template('disciplinas.html', disciplinas=disciplinas, disciplina_edicao=disciplina_edicao)

    @app.route('/atualizar_disciplina/<int:id_disciplina>', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def atualizar_disciplina(id_disciplina):
        nome = request.form.get('nome', '').strip()
        sigla = request.form.get('sigla', '').strip()
        cor = request.form.get('cor', '#ffffff').strip()
        carga = request.form.get('carga_horaria_semanal', '').strip()

        if not nome:
            flash("O nome é obrigatório.", 'erro')
            return redirect(url_for('editar_disciplina', id_disciplina=id_disciplina))

        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                UPDATE disciplina
                SET nome = %s, sigla = %s, cor = %s, carga_horaria_semanal = %s
                WHERE id_disciplina = %s
            """, (nome, sigla, cor, carga, id_disciplina))
            cursor.execute(
                "UPDATE grade_curricular SET aulas_semanais = %s WHERE id_disciplina = %s",
                (carga, id_disciplina)
            )
            conexao.commit()
        return redirect(url_for('listar_disciplinas'))

    @app.route('/deletar_disciplina/<int:id_disciplina>', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def deletar_disciplina(id_disciplina):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute('DELETE FROM disciplina WHERE id_disciplina = %s', (id_disciplina,))
            conexao.commit()
        return redirect(url_for('listar_disciplinas'))
