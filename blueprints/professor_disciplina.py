import pymysql
from db import conectar
from auth import requer_perfil
from flask import render_template, request, redirect, url_for, flash


def registrar(app):

    @app.route('/cadastrar_professor_disciplina', methods=['GET', 'POST'])
    @requer_perfil('diretor', 'secretaria')
    def cadastrar_professor_disciplina():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute('SELECT * FROM professor ORDER BY nome')
            professores = cursor.fetchall()
            cursor.execute('SELECT * FROM disciplina ORDER BY nome')
            disciplinas = cursor.fetchall()
            cursor.execute("""
                SELECT p.nome AS nome_professor, d.nome AS nome_disciplina, d.sigla
                FROM professor_disciplina pd
                JOIN professor p ON pd.id_professor = p.id_professor
                JOIN disciplina d ON pd.id_disciplina = d.id_disciplina
                ORDER BY p.nome, d.nome
            """)
            relacoes = cursor.fetchall()
            cursor.execute("""
                SELECT nome FROM professor
                WHERE status = 'ativo'
                  AND id_professor NOT IN (SELECT DISTINCT id_professor FROM professor_disciplina)
                ORDER BY nome
            """)
            sem_vinculo = [r['nome'] for r in cursor.fetchall()]

            if request.method == 'POST':
                id_professor = request.form.get('id_professor', '').strip()
                id_disciplina = request.form.get('id_disciplina', '').strip()

                if not id_professor or not id_disciplina:
                    flash("Selecione professor e disciplina.", 'erro')
                    return render_template('cadastro_professor_disciplina.html',
                                           professores=professores, disciplinas=disciplinas)
                try:
                    cursor.execute("""
                        INSERT INTO professor_disciplina (id_professor, id_disciplina)
                        VALUES (%s, %s)
                    """, (id_professor, id_disciplina))
                    conexao.commit()
                    return redirect(url_for('listar_professores_disciplinas'))
                except pymysql.IntegrityError:
                    flash("Essa relação entre professor e disciplina já existe.", 'erro')
                    conexao.rollback()

        return render_template('cadastro_professor_disciplina.html',
                               professores=professores, disciplinas=disciplinas,
                               relacoes=relacoes, sem_vinculo=sem_vinculo)

    @app.route('/professores_disciplinas')
    @requer_perfil('diretor', 'secretaria')
    def listar_professores_disciplinas():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT pd.id_professor, pd.id_disciplina,
                       p.nome AS nome_professor,
                       d.nome AS nome_disciplina, d.sigla
                FROM professor_disciplina pd
                JOIN professor p ON pd.id_professor = p.id_professor
                JOIN disciplina d ON pd.id_disciplina = d.id_disciplina
                ORDER BY p.nome, d.nome
            """)
            professores_disciplinas = cursor.fetchall()
        return render_template('professor_disciplina.html',
                               professores_disciplinas=professores_disciplinas,
                               professor_disciplina_edicao=None)

    @app.route('/editar_professor_disciplina/<int:id_professor>/<int:id_disciplina>')
    @requer_perfil('diretor', 'secretaria')
    def editar_professor_disciplina(id_professor, id_disciplina):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT pd.id_professor, pd.id_disciplina,
                       p.nome AS nome_professor,
                       d.nome AS nome_disciplina, d.sigla
                FROM professor_disciplina pd
                JOIN professor p ON pd.id_professor = p.id_professor
                JOIN disciplina d ON pd.id_disciplina = d.id_disciplina
                ORDER BY p.nome, d.nome
            """)
            professores_disciplinas = cursor.fetchall()
            cursor.execute('SELECT * FROM professor ORDER BY nome')
            professores = cursor.fetchall()
            cursor.execute('SELECT * FROM disciplina ORDER BY nome')
            disciplinas = cursor.fetchall()
            cursor.execute("""
                SELECT * FROM professor_disciplina
                WHERE id_professor = %s AND id_disciplina = %s
            """, (id_professor, id_disciplina))
            professor_disciplina_edicao = cursor.fetchone()
        return render_template('professor_disciplina.html',
                               professores_disciplinas=professores_disciplinas,
                               professor_disciplina_edicao=professor_disciplina_edicao,
                               professores=professores,
                               disciplinas=disciplinas)

    @app.route('/atualizar_professor_disciplina', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def atualizar_professor_disciplina():
        id_professor_antigo = request.form['id_professor_antigo']
        id_disciplina_antiga = request.form['id_disciplina_antiga']
        id_professor = request.form['id_professor']
        id_disciplina = request.form['id_disciplina']

        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                UPDATE professor_disciplina
                SET id_professor = %s, id_disciplina = %s
                WHERE id_professor = %s AND id_disciplina = %s
            """, (id_professor, id_disciplina, id_professor_antigo, id_disciplina_antiga))
            conexao.commit()
        return redirect(url_for('listar_professores_disciplinas'))

    @app.route('/deletar_professor_disciplina/<int:id_professor>/<int:id_disciplina>', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def deletar_professor_disciplina(id_professor, id_disciplina):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                DELETE FROM professor_disciplina
                WHERE id_professor = %s AND id_disciplina = %s
            """, (id_professor, id_disciplina))
            conexao.commit()
        return redirect(url_for('listar_professores_disciplinas'))
