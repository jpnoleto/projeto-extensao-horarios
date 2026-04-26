from db import conectar
from auth import requer_perfil
from flask import render_template, request, redirect, url_for, flash


def registrar(app):

    @app.route('/cadastrar_disponibilidade_professor', methods=['GET', 'POST'])
    @requer_perfil('diretor', 'secretaria')
    def cadastrar_disponibilidade_professor():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM professor ORDER BY nome")
            professores = cursor.fetchall()
            cursor.execute("SELECT * FROM horario_aula ORDER BY hora_inicio")
            horarios = cursor.fetchall()
            cursor.execute("""
                SELECT nome FROM professor
                WHERE status = 'ativo'
                  AND id_professor NOT IN (SELECT DISTINCT id_professor FROM disponibilidade_professor)
                ORDER BY nome
            """)
            sem_disponibilidade = [r['nome'] for r in cursor.fetchall()]

            if request.method == 'POST':
                id_professor = request.form.get('id_professor', '').strip()
                dias_semana = request.form.getlist('dias_semana')
                horarios_marcados = request.form.getlist('id_horario')
                disponivel = request.form.get('disponivel', '1')

                if not id_professor:
                    flash("Selecione um professor.", 'erro')
                elif not dias_semana:
                    flash("Selecione pelo menos um dia.", 'erro')
                elif not horarios_marcados:
                    flash("Selecione pelo menos um horário.", 'erro')
                else:
                    inseridos = 0
                    for dia in dias_semana:
                        for id_horario in horarios_marcados:
                            cursor.execute("""
                                SELECT 1 FROM disponibilidade_professor
                                WHERE id_professor = %s AND dia_semana = %s AND id_horario = %s
                            """, (id_professor, dia, id_horario))
                            if not cursor.fetchone():
                                cursor.execute("""
                                    INSERT INTO disponibilidade_professor
                                        (id_professor, dia_semana, id_horario, disponivel)
                                    VALUES (%s, %s, %s, %s)
                                """, (id_professor, dia, id_horario, disponivel))
                                inseridos += 1
                    conexao.commit()

                    if inseridos > 0:
                        return redirect(url_for('grade_disponibilidades'))
                    else:
                        flash("Todas as combinações selecionadas já estavam cadastradas.", 'erro')

        return render_template('cadastro_disponibilidade.html',
                               professores=professores, horarios=horarios,
                               sem_disponibilidade=sem_disponibilidade)

    @app.route('/disponibilidade_professor')
    @requer_perfil('diretor', 'secretaria')
    def listar_disponibilidade_professor():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT dp.id_disponibilidade, dp.id_professor, dp.dia_semana,
                       dp.id_horario, dp.disponivel,
                       p.nome AS nome_professor,
                       h.hora_inicio, h.hora_fim
                FROM disponibilidade_professor dp
                JOIN professor p ON dp.id_professor = p.id_professor
                JOIN horario_aula h ON dp.id_horario = h.id_horario
                ORDER BY p.nome, dp.dia_semana, h.hora_inicio
            """)
            disponibilidades = cursor.fetchall()
        return render_template('disponibilidade.html',
                               disponibilidades=disponibilidades,
                               disponibilidade_edicao=None)

    @app.route('/editar_disponibilidade_professor/<int:id_disponibilidade>')
    @requer_perfil('diretor', 'secretaria')
    def editar_disponibilidade_professor(id_disponibilidade):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT dp.id_disponibilidade, dp.id_professor, dp.dia_semana,
                       dp.id_horario, dp.disponivel,
                       p.nome AS nome_professor, h.hora_inicio, h.hora_fim
                FROM disponibilidade_professor dp
                JOIN professor p ON dp.id_professor = p.id_professor
                JOIN horario_aula h ON dp.id_horario = h.id_horario
                ORDER BY p.nome, dp.dia_semana, h.hora_inicio
            """)
            disponibilidades = cursor.fetchall()
            cursor.execute("SELECT * FROM professor ORDER BY nome")
            professores = cursor.fetchall()
            cursor.execute("SELECT * FROM horario_aula ORDER BY hora_inicio")
            horarios = cursor.fetchall()
            cursor.execute("SELECT * FROM disponibilidade_professor WHERE id_disponibilidade = %s",
                           (id_disponibilidade,))
            disponibilidade_edicao = cursor.fetchone()
        return render_template('disponibilidade.html',
                               disponibilidades=disponibilidades,
                               disponibilidade_edicao=disponibilidade_edicao,
                               professores=professores,
                               horarios=horarios)

    @app.route('/grade_disponibilidades')
    @requer_perfil('diretor', 'secretaria')
    def grade_disponibilidades():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT dp.id_disponibilidade, dp.id_professor, dp.dia_semana,
                       dp.id_horario, dp.disponivel,
                       p.nome AS nome_professor, h.hora_inicio, h.hora_fim
                FROM disponibilidade_professor dp
                JOIN professor p ON dp.id_professor = p.id_professor
                JOIN horario_aula h ON dp.id_horario = h.id_horario
                ORDER BY p.nome,
                    CASE dp.dia_semana
                        WHEN 'segunda' THEN 1 WHEN 'terca' THEN 2
                        WHEN 'quarta' THEN 3 WHEN 'quinta' THEN 4
                        WHEN 'sexta' THEN 5 END,
                    h.hora_inicio
            """)
            registros = cursor.fetchall()
            cursor.execute("SELECT * FROM professor ORDER BY nome")
            professores = cursor.fetchall()
            cursor.execute("SELECT * FROM horario_aula ORDER BY hora_inicio")
            horarios = cursor.fetchall()

        dias = ['segunda', 'terca', 'quarta', 'quinta', 'sexta']
        grade = {}
        professores_ordem = []

        for r in registros:
            prof = r['nome_professor']
            if prof not in grade:
                grade[prof] = {'id_professor': r['id_professor'], 'dias': {d: [] for d in dias}}
                professores_ordem.append(prof)
            grade[prof]['dias'][r['dia_semana']].append({
                'id_disponibilidade': r['id_disponibilidade'],
                'horario': f"{r['hora_inicio']} às {r['hora_fim']}",
                'disponivel': r['disponivel']
            })

        return render_template('grade_disponibilidades.html',
                               grade=grade, professores_ordem=professores_ordem, dias=dias,
                               disponibilidade_edicao=None,
                               professores=professores, horarios=horarios)

    @app.route('/editar_disponibilidade_dia/<int:id_professor>/<dia_semana>')
    @requer_perfil('diretor', 'secretaria')
    def editar_disponibilidade_dia(id_professor, dia_semana):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM professor WHERE id_professor = %s", (id_professor,))
            professor = cursor.fetchone()
            cursor.execute("SELECT * FROM horario_aula ORDER BY hora_inicio")
            horarios = cursor.fetchall()
            cursor.execute("""
                SELECT id_horario FROM disponibilidade_professor
                WHERE id_professor = %s AND dia_semana = %s AND disponivel = 1
            """, (id_professor, dia_semana))
            horarios_selecionados = [row['id_horario'] for row in cursor.fetchall()]
        return render_template('editar_disponibilidade_dia.html',
                               professor=professor, dia_semana=dia_semana,
                               horarios=horarios, horarios_selecionados=horarios_selecionados)

    @app.route('/atualizar_disponibilidade_professor/<int:id_disponibilidade>', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def atualizar_disponibilidade_professor(id_disponibilidade):
        id_professor = request.form['id_professor']
        dia_semana = request.form['dia_semana']
        id_horario = request.form['id_horario']
        disponivel = request.form['disponivel']

        try:
            with conectar() as conexao:
                cursor = conexao.cursor()
                cursor.execute("""
                    UPDATE disponibilidade_professor
                    SET id_professor = %s, dia_semana = %s, id_horario = %s, disponivel = %s
                    WHERE id_disponibilidade = %s
                """, (id_professor, dia_semana, id_horario, disponivel, id_disponibilidade))
                conexao.commit()
            return redirect(url_for('grade_disponibilidades'))
        except Exception:
            flash("Já existe um cadastro igual para esse professor, dia e horário.", 'erro')
            return redirect(url_for('editar_disponibilidade_professor',
                                    id_disponibilidade=id_disponibilidade))

    @app.route('/atualizar_disponibilidade_dia/<int:id_professor>/<dia_semana>', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def atualizar_disponibilidade_dia(id_professor, dia_semana):
        horarios_marcados = request.form.getlist('id_horario')
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                DELETE FROM disponibilidade_professor
                WHERE id_professor = %s AND dia_semana = %s
            """, (id_professor, dia_semana))
            for id_horario in horarios_marcados:
                cursor.execute("""
                    INSERT INTO disponibilidade_professor
                        (id_professor, dia_semana, id_horario, disponivel)
                    VALUES (%s, %s, %s, 1)
                """, (id_professor, dia_semana, id_horario))
            conexao.commit()
        return redirect(url_for('grade_disponibilidades'))

    @app.route('/deletar_disponibilidade_professor/<int:id_disponibilidade>', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def deletar_disponibilidade_professor(id_disponibilidade):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                DELETE FROM disponibilidade_professor WHERE id_disponibilidade = %s
            """, (id_disponibilidade,))
            conexao.commit()
        return redirect(url_for('listar_disponibilidade_professor'))
