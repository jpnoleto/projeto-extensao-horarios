import pymysql
from db import conectar
from auth import requer_login
from flask import render_template, request, redirect, url_for, flash


def registrar(app):

    @app.route('/cadastrar_professor')
    @requer_login
    def cadastrar_professor():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute('SELECT * FROM professor ORDER BY nome')
            professores = cursor.fetchall()
        return render_template('cadastro_professor.html', professores=professores)

    @app.route('/salvar_professor', methods=['POST'])
    @requer_login
    def salvar_professor():
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        telefone = request.form.get('telefone', '').strip()

        if not nome:
            flash("O nome é obrigatório.", 'erro')
            return redirect(url_for('cadastrar_professor'))

        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                INSERT INTO professor (nome, email, telefone)
                VALUES (%s, %s, %s)
            """, (nome, email, telefone))
            conexao.commit()
        return redirect(url_for('listar_professores'))

    @app.route('/professores')
    @requer_login
    def listar_professores():
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = 20
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute('SELECT COUNT(*) AS total FROM professor')
            total = cursor.fetchone()['total']
            cursor.execute('SELECT * FROM professor ORDER BY nome LIMIT %s OFFSET %s',
                           (por_pagina, (pagina - 1) * por_pagina))
            professores = cursor.fetchall()
        total_paginas = max(1, (total + por_pagina - 1) // por_pagina)
        return render_template('professores.html', professores=professores,
                               pagina=pagina, total_paginas=total_paginas, total=total)

    @app.route('/editar_professor/<int:id_professor>')
    @requer_login
    def editar_professor(id_professor):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute('SELECT * FROM professor ORDER BY nome')
            professores = cursor.fetchall()
            cursor.execute('SELECT * FROM professor WHERE id_professor = %s', (id_professor,))
            professor_edicao = cursor.fetchone()
        return render_template('professores.html', professores=professores,
                               professor_edicao=professor_edicao)

    @app.route('/atualizar_professor/<int:id_professor>', methods=['POST'])
    @requer_login
    def atualizar_professor(id_professor):
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        telefone = request.form.get('telefone', '').strip()
        status = request.form.get('status', 'ativo')

        if not nome:
            flash("O nome é obrigatório.", 'erro')
            return redirect(url_for('editar_professor', id_professor=id_professor))

        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                UPDATE professor
                SET nome = %s, email = %s, telefone = %s, status = %s
                WHERE id_professor = %s
            """, (nome, email, telefone, status, id_professor))
            conexao.commit()
        return redirect(url_for('listar_professores'))

    @app.route('/deletar_professor/<int:id_professor>', methods=['POST'])
    @requer_login
    def deletar_professor(id_professor):
        try:
            with conectar() as conexao:
                cursor = conexao.cursor()
                cursor.execute('DELETE FROM professor WHERE id_professor = %s', (id_professor,))
                conexao.commit()
        except pymysql.IntegrityError:
            flash("Não é possível excluir: o professor tem disponibilidades ou aulas alocadas. "
                  "Remova-as antes ou marque o professor como inativo.", 'erro')
        return redirect(url_for('listar_professores'))
