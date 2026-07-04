from db import conectar
from auth import requer_login
from flask import render_template, request, redirect, url_for, flash

DIAS = ['segunda', 'terca', 'quarta', 'quinta', 'sexta']


def registrar(app):

    @app.route('/relatorio')
    @requer_login
    def selecionar_turma_relatorio():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT id_turma, nome, serie, turno
                FROM turma ORDER BY turno, serie, nome
            """)
            turmas = cursor.fetchall()
        return render_template('selecionar_turma_relatorio.html', turmas=turmas)

    @app.route('/relatorio/<int:id_turma>')
    @requer_login
    def relatorio_turma(id_turma):
        turma, horarios, grade = _montar_dados_relatorio(id_turma)
        if not turma:
            flash("Turma não encontrada.", 'erro')
            return redirect(url_for('selecionar_turma_relatorio'))
        nome_escola = request.args.get('nome_escola', '')
        data_rel = request.args.get('data_rel', '')
        return render_template('relatorio.html',
                               turma=turma, horarios=horarios, dias=DIAS, grade=grade,
                               nome_escola=nome_escola, data_rel=data_rel)


def _montar_dados_relatorio(id_turma):
    with conectar() as conexao:
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM turma WHERE id_turma = %s", (id_turma,))
        turma = cursor.fetchone()
        if not turma:
            return None, None, None
        cursor.execute("SELECT * FROM horario_aula ORDER BY hora_inicio")
        horarios = cursor.fetchall()
        cursor.execute("""
            SELECT a.dia_semana, a.id_horario,
                   d.nome AS nome_disciplina, d.sigla, d.cor,
                   p.nome AS professor
            FROM alocacao a
            JOIN disciplina d ON a.id_disciplina = d.id_disciplina
            JOIN professor p ON a.id_professor = p.id_professor
            WHERE a.id_turma = %s
        """, (id_turma,))
        alocacoes = cursor.fetchall()

    grade = {}
    for a in alocacoes:
        ih = a['id_horario']
        dia = a['dia_semana']
        nome_prof = a['professor'] or ''
        grade.setdefault(ih, {})[dia] = {
            'sigla': a['sigla'],
            'cor': a['cor'],
            'nome_disciplina': a['nome_disciplina'],
            'professor_curto': nome_prof.split()[0] if nome_prof else '',
        }
    return turma, horarios, grade
