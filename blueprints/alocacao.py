import json
import pymysql
from db import conectar
from auth import requer_login
from flask import render_template, request, redirect, url_for, flash

DIAS = ['segunda', 'terca', 'quarta', 'quinta', 'sexta']


def registrar(app):

    @app.route('/montar_grade')
    @requer_login
    def selecionar_turma_montagem():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT t.id_turma, t.nome, t.serie, t.turno,
                       COUNT(a.id_alocacao) AS total_aloc
                FROM turma t
                LEFT JOIN alocacao a ON a.id_turma = t.id_turma
                GROUP BY t.id_turma, t.nome, t.serie, t.turno
                ORDER BY t.turno, t.serie, t.nome
            """)
            turmas = cursor.fetchall()
        return render_template('selecionar_turma_montagem.html', turmas=turmas)

    @app.route('/montar_grade/<int:id_turma>')
    @requer_login
    def montar_grade(id_turma):
        with conectar() as conexao:
            cursor = conexao.cursor()

            cursor.execute("SELECT * FROM turma WHERE id_turma = %s", (id_turma,))
            turma = cursor.fetchone()
            if not turma:
                flash("Turma não encontrada.", 'erro')
                return redirect(url_for('selecionar_turma_montagem'))

            # Horários de aula (sem intervalos — intervalo não recebe aula)
            cursor.execute("SELECT * FROM horario_aula WHERE eh_intervalo = 0 ORDER BY hora_inicio")
            horarios = cursor.fetchall()

            cursor.execute("SELECT * FROM disciplina ORDER BY nome")
            disciplinas = cursor.fetchall()

            cursor.execute("SELECT id_professor, nome FROM professor WHERE status = 'ativo' ORDER BY nome")
            professores = cursor.fetchall()

            # Alocações atuais desta turma → grade[str(id_horario)][dia]
            cursor.execute("""
                SELECT a.id_alocacao, a.dia_semana, a.id_horario,
                       d.sigla, d.cor, d.nome AS nome_disciplina,
                       p.nome AS nome_professor
                FROM alocacao a
                JOIN disciplina d ON a.id_disciplina = d.id_disciplina
                JOIN professor p ON a.id_professor = p.id_professor
                WHERE a.id_turma = %s
            """, (id_turma,))
            grade = {}
            for a in cursor.fetchall():
                hid = str(a['id_horario'])
                grade.setdefault(hid, {})[a['dia_semana']] = {
                    'id_alocacao': a['id_alocacao'],
                    'sigla': a['sigla'],
                    'cor': a['cor'],
                    'nome_disciplina': a['nome_disciplina'],
                    'professor_curto': (a['nome_professor'] or '').split()[0] if a['nome_professor'] else '',
                }

            # Disponibilidade dos professores: {str(pid): {dia: [id_horario, ...]}}
            cursor.execute("""
                SELECT id_professor, dia_semana, id_horario
                FROM disponibilidade_professor WHERE disponivel = 1
            """)
            disponibilidades = {}
            for d in cursor.fetchall():
                pid = str(d['id_professor'])
                disponibilidades.setdefault(pid, {}).setdefault(d['dia_semana'], []).append(d['id_horario'])

            # Ocupação de professores em qualquer turma: {str(pid): {dia: [id_horario, ...]}}
            cursor.execute("SELECT id_professor, dia_semana, id_horario FROM alocacao")
            ocupacao = {}
            for a in cursor.fetchall():
                pid = str(a['id_professor'])
                ocupacao.setdefault(pid, {}).setdefault(a['dia_semana'], []).append(a['id_horario'])

        return render_template('montar_grade.html',
            turma=turma, horarios=horarios, dias=DIAS, grade=grade,
            disciplinas_json=json.dumps([
                {'id': d['id_disciplina'], 'nome': d['nome'], 'sigla': d['sigla'], 'cor': d['cor']}
                for d in disciplinas
            ]),
            professores_json=json.dumps([
                {'id': p['id_professor'], 'nome': p['nome']} for p in professores
            ]),
            disponibilidades_json=json.dumps(disponibilidades),
            ocupacao_json=json.dumps(ocupacao),
        )

    @app.route('/montar_grade/<int:id_turma>/alocar', methods=['POST'])
    @requer_login
    def alocar_slot(id_turma):
        id_disciplina = request.form.get('id_disciplina', '').strip()
        id_professor = request.form.get('id_professor', '').strip()
        dia = request.form.get('dia', '').strip()
        id_horario = request.form.get('id_horario', '').strip()

        if not all([id_disciplina, id_professor, dia, id_horario]) or dia not in DIAS:
            flash("Selecione disciplina e professor para o horário.", 'erro')
            return redirect(url_for('montar_grade', id_turma=id_turma))

        try:
            with conectar() as conexao:
                cursor = conexao.cursor()
                cursor.execute("""
                    INSERT INTO alocacao (id_turma, id_disciplina, id_professor, dia_semana, id_horario)
                    VALUES (%s, %s, %s, %s, %s)
                """, (id_turma, id_disciplina, id_professor, dia, id_horario))
                conexao.commit()
            flash("Aula alocada.", 'sucesso')
        except pymysql.IntegrityError as e:
            msg = str(e.args[1]) if len(e.args) > 1 else ''
            if 'id_professor' in msg:
                flash("Esse professor já tem aula em outra turma nesse dia e horário.", 'erro')
            elif 'id_turma' in msg:
                flash("A turma já tem uma aula nesse dia e horário.", 'erro')
            else:
                flash("Não foi possível alocar: conflito de horário.", 'erro')
        return redirect(url_for('montar_grade', id_turma=id_turma))

    @app.route('/montar_grade/<int:id_turma>/remover/<int:id_alocacao>', methods=['POST'])
    @requer_login
    def remover_slot(id_turma, id_alocacao):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM alocacao WHERE id_alocacao = %s AND id_turma = %s",
                           (id_alocacao, id_turma))
            conexao.commit()
        return redirect(url_for('montar_grade', id_turma=id_turma))

    @app.route('/montar_grade/<int:id_turma>/limpar', methods=['POST'])
    @requer_login
    def limpar_grade(id_turma):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT COUNT(*) AS total FROM alocacao WHERE id_turma = %s", (id_turma,))
            total = cursor.fetchone()['total']
            cursor.execute("DELETE FROM alocacao WHERE id_turma = %s", (id_turma,))
            conexao.commit()
        flash(f"{total} aula(s) removida(s) da grade.", 'sucesso')
        return redirect(url_for('montar_grade', id_turma=id_turma))
