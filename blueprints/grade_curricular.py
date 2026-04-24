import pymysql
from db import conectar
from auth import requer_perfil
from flask import render_template, request, redirect, url_for, flash


def registrar(app):

    @app.route('/cadastrar_grade_curricular', methods=['GET', 'POST'])
    @requer_perfil('diretor', 'secretaria')
    def cadastrar_grade_curricular():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT id_turno, nome FROM turno ORDER BY nome")
            turnos = cursor.fetchall()
            cursor.execute(
                "SELECT id_disciplina, nome, sigla, cor, carga_horaria_semanal FROM disciplina ORDER BY nome"
            )
            disciplinas = cursor.fetchall()

            cursor.execute("SELECT DISTINCT id_turno, serie FROM turma ORDER BY id_turno, serie")
            series_por_turno = {}
            for row in cursor.fetchall():
                series_por_turno.setdefault(str(row['id_turno']), []).append(row['serie'])

            cursor.execute("SELECT id_turno, serie, id_disciplina, aulas_semanais FROM grade_curricular")
            grades_existentes = {}
            for g in cursor.fetchall():
                key_turno = str(g['id_turno'])
                key_serie = str(g['serie'])
                grades_existentes.setdefault(key_turno, {}).setdefault(key_serie, {})[
                    str(g['id_disciplina'])
                ] = g['aulas_semanais']

            if request.method == 'POST':
                id_turno = request.form.get('id_turno', '').strip()
                serie    = request.form.get('serie', '').strip()
                if not id_turno or not serie:
                    flash("Selecione um turno e uma série.", 'erro')
                    return render_template('cadastro_grade_curricular.html',
                                           turnos=turnos, disciplinas=disciplinas,
                                           series_por_turno=series_por_turno,
                                           grades_existentes=grades_existentes)

                inseridos = 0
                repetidos = 0

                for disciplina in disciplinas:
                    campo = f"aulas_semanais_{disciplina['id_disciplina']}"
                    valor = request.form.get(campo, '').strip()
                    if not valor:
                        continue
                    try:
                        aulas_semanais = int(valor)
                    except ValueError:
                        flash("Digite apenas números válidos nas aulas semanais.", 'erro')
                        return render_template('cadastro_grade_curricular.html',
                                               turnos=turnos, disciplinas=disciplinas,
                                               series_por_turno=series_por_turno,
                                               grades_existentes=grades_existentes)
                    if aulas_semanais <= 0:
                        continue

                    cursor.execute("""
                        SELECT 1 FROM grade_curricular
                        WHERE id_turno = %s AND serie = %s AND id_disciplina = %s
                    """, (id_turno, serie, disciplina['id_disciplina']))
                    if cursor.fetchone():
                        repetidos += 1
                    else:
                        cursor.execute("""
                            INSERT INTO grade_curricular (id_turno, serie, id_disciplina, aulas_semanais)
                            VALUES (%s, %s, %s, %s)
                        """, (id_turno, serie, disciplina['id_disciplina'], aulas_semanais))
                        inseridos += 1

                conexao.commit()

                if inseridos > 0:
                    return redirect(url_for('selecionar_turno_grades'))
                elif repetidos > 0:
                    flash("Todas as disciplinas preenchidas já estavam cadastradas para essa série.", 'erro')
                else:
                    flash("Preencha pelo menos uma disciplina com a quantidade de aulas semanais.", 'erro')

        return render_template('cadastro_grade_curricular.html',
                               turnos=turnos, disciplinas=disciplinas,
                               series_por_turno=series_por_turno,
                               grades_existentes=grades_existentes)

    @app.route('/selecionar_turno_grades')
    @requer_perfil('diretor', 'secretaria')
    def selecionar_turno_grades():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM turno ORDER BY nome")
            turnos = cursor.fetchall()
        return render_template('selecionar_turno_grades.html', turnos=turnos)

    @app.route('/grades_curriculares/<int:id_turno>')
    @requer_perfil('diretor', 'secretaria')
    def listar_grades_curriculares(id_turno):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM turno WHERE id_turno = %s", (id_turno,))
            turno = cursor.fetchone()
            cursor.execute("""
                SELECT gc.id_grade, gc.id_turno, gc.serie, gc.id_disciplina, gc.aulas_semanais,
                       tr.nome AS nome_turno, d.nome AS nome_disciplina, d.sigla, d.cor
                FROM grade_curricular gc
                JOIN turno tr ON gc.id_turno = tr.id_turno
                JOIN disciplina d ON gc.id_disciplina = d.id_disciplina
                WHERE gc.id_turno = %s
                ORDER BY gc.serie, d.nome
            """, (id_turno,))
            registros = cursor.fetchall()

        grades_por_serie, ordem_series = _agregar_grades(registros)
        return render_template('grade_curricular.html', turno=turno,
                               grades_por_serie=grades_por_serie,
                               ordem_series=ordem_series, grade_edicao=None)

    @app.route('/editar_grade_curricular/<int:id_grade>')
    @requer_perfil('diretor', 'secretaria')
    def editar_grade_curricular(id_grade):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT gc.id_grade, gc.id_turno, gc.serie, gc.id_disciplina, gc.aulas_semanais,
                       tr.nome AS nome_turno
                FROM grade_curricular gc
                JOIN turno tr ON gc.id_turno = tr.id_turno
                WHERE gc.id_grade = %s
            """, (id_grade,))
            grade_edicao = cursor.fetchone()
            if not grade_edicao:
                return redirect(url_for('selecionar_turno_grades'))

            id_turno = grade_edicao['id_turno']
            cursor.execute("SELECT * FROM turno WHERE id_turno = %s", (id_turno,))
            turno = cursor.fetchone()
            cursor.execute("""
                SELECT gc.id_grade, gc.id_turno, gc.serie, gc.id_disciplina, gc.aulas_semanais,
                       tr.nome AS nome_turno, d.nome AS nome_disciplina, d.sigla, d.cor
                FROM grade_curricular gc
                JOIN turno tr ON gc.id_turno = tr.id_turno
                JOIN disciplina d ON gc.id_disciplina = d.id_disciplina
                WHERE gc.id_turno = %s ORDER BY gc.serie, d.nome
            """, (id_turno,))
            registros = cursor.fetchall()
            cursor.execute("SELECT * FROM turno ORDER BY nome")
            turnos = cursor.fetchall()
            cursor.execute("SELECT DISTINCT serie FROM turma ORDER BY serie")
            series_disponiveis = [r['serie'] for r in cursor.fetchall()]
            cursor.execute("SELECT * FROM disciplina ORDER BY nome")
            disciplinas = cursor.fetchall()

        grades_por_serie, ordem_series = _agregar_grades(registros)
        return render_template('grade_curricular.html', turno=turno,
                               grades_por_serie=grades_por_serie,
                               ordem_series=ordem_series, grade_edicao=grade_edicao,
                               turnos=turnos, series_disponiveis=series_disponiveis,
                               disciplinas=disciplinas)

    @app.route('/atualizar_grade_curricular/<int:id_grade>', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def atualizar_grade_curricular(id_grade):
        id_turno       = request.form['id_turno']
        serie          = request.form['serie']
        id_disciplina  = request.form['id_disciplina']
        aulas_semanais = request.form['aulas_semanais']

        try:
            with conectar() as conexao:
                cursor = conexao.cursor()
                cursor.execute("""
                    UPDATE grade_curricular
                    SET id_turno = %s, serie = %s, id_disciplina = %s, aulas_semanais = %s
                    WHERE id_grade = %s
                """, (id_turno, serie, id_disciplina, aulas_semanais, id_grade))
                cursor.execute(
                    "UPDATE disciplina SET carga_horaria_semanal = %s WHERE id_disciplina = %s",
                    (aulas_semanais, id_disciplina)
                )
                conexao.commit()
            return redirect(url_for('selecionar_turno_grades'))
        except pymysql.IntegrityError:
            flash("Já existe essa disciplina cadastrada para essa série neste turno.", 'erro')
            return redirect(url_for('editar_grade_curricular', id_grade=id_grade))

    @app.route('/deletar_grade_curricular/<int:id_grade>', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def deletar_grade_curricular(id_grade):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM grade_curricular WHERE id_grade = %s", (id_grade,))
            conexao.commit()
        return redirect(url_for('selecionar_turno_grades'))

    @app.route('/api/grade_turma/<int:id_turma>')
    @requer_perfil('diretor', 'secretaria')
    def api_grade_turma(id_turma):
        from flask import jsonify
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT gc.id_disciplina, gc.aulas_semanais
                FROM grade_curricular gc
                JOIN turma t ON gc.id_turno = t.id_turno AND gc.serie = t.serie
                WHERE t.id_turma = %s
            """, (id_turma,))
            rows = cursor.fetchall()
        return jsonify({str(r['id_disciplina']): r['aulas_semanais'] for r in rows})


def _agregar_grades(registros):
    grades_por_serie = {}
    ordem_series = []
    for r in registros:
        serie = r['serie']
        if serie not in grades_por_serie:
            grades_por_serie[serie] = {'disciplinas': [], 'nome_turno': r['nome_turno']}
            ordem_series.append(serie)
        grades_por_serie[serie]['disciplinas'].append({
            'id_grade':        r['id_grade'],
            'nome_disciplina': r['nome_disciplina'],
            'sigla':           r['sigla'],
            'cor':             r['cor'],
            'aulas_semanais':  r['aulas_semanais'],
        })
    return grades_por_serie, ordem_series
