import json
import pymysql
from db import conectar
from auth import requer_perfil
from flask import render_template, request, redirect, url_for, flash


def registrar(app):

    # ─── EDITOR DE GRADE COMPLETA POR TURMA ────────────────────────────────

    @app.route('/alocar_turma')
    @requer_perfil('diretor', 'secretaria')
    def selecionar_turma_alocacao():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT t.id_turma, t.nome, t.serie, tr.nome AS nome_turno,
                       COUNT(gc.id_grade) AS total_disc,
                       COUNT(a.id_alocacao) AS total_aloc
                FROM turma t
                JOIN turno tr ON t.id_turno = tr.id_turno
                LEFT JOIN grade_curricular gc ON gc.id_turno = t.id_turno AND gc.serie = t.serie
                LEFT JOIN alocacao a ON a.id_turma = t.id_turma
                GROUP BY t.id_turma, t.nome, t.serie, tr.nome
                ORDER BY tr.nome, t.serie, t.nome
            """)
            turmas = cursor.fetchall()
        return render_template('selecionar_turma_alocacao.html', turmas=turmas)

    @app.route('/alocar_turma/<int:id_turma>', methods=['GET', 'POST'])
    @requer_perfil('diretor', 'secretaria')
    def alocar_turma_completa(id_turma):
        sugestao_id = request.args.get('sugestao_id', type=int)
        with conectar() as conexao:
            cursor = conexao.cursor()

            cursor.execute("""
                SELECT t.*, tr.nome AS nome_turno FROM turma t
                JOIN turno tr ON t.id_turno = tr.id_turno WHERE t.id_turma = %s
            """, (id_turma,))
            turma = cursor.fetchone()
            if not turma:
                return redirect(url_for('selecionar_turma_alocacao'))

            # Grade curricular — contagem de alocadas por disciplina
            cursor.execute("""
                SELECT gc.id_disciplina, gc.aulas_semanais,
                       d.nome AS nome_disciplina, d.sigla, d.cor,
                       COUNT(DISTINCT a.id_alocacao) AS ja_alocadas
                FROM grade_curricular gc
                JOIN turma t ON gc.id_turno = t.id_turno AND gc.serie = t.serie
                JOIN disciplina d ON gc.id_disciplina = d.id_disciplina
                LEFT JOIN alocacao a ON a.id_turma = t.id_turma AND a.id_disciplina = gc.id_disciplina
                WHERE t.id_turma = %s
                GROUP BY gc.id_disciplina, gc.aulas_semanais, d.nome, d.sigla, d.cor
                ORDER BY d.nome
            """, (id_turma,))
            grade_base = cursor.fetchall()

            # Todos os professores habilitados por disciplina
            cursor.execute("""
                SELECT pd.id_disciplina, p.id_professor, p.nome
                FROM professor_disciplina pd
                JOIN professor p ON p.id_professor = pd.id_professor AND p.status = 'ativo'
            """)
            profs_por_disc = {}
            for row in cursor.fetchall():
                profs_por_disc.setdefault(row['id_disciplina'], []).append(
                    {'id': row['id_professor'], 'nome': row['nome']}
                )

            grade = []
            for g in grade_base:
                g = dict(g)
                g['professores'] = profs_por_disc.get(g['id_disciplina'], [])
                first = g['professores'][0] if g['professores'] else {}
                g['id_professor']   = first.get('id')
                g['nome_professor'] = first.get('nome')
                grade.append(g)

            # Alocações atuais desta turma
            cursor.execute("""
                SELECT a.id_alocacao, a.dia_semana, a.id_horario,
                       a.id_disciplina, a.id_professor, a.id_local,
                       d.sigla, d.cor, p.nome AS prof_nome
                FROM alocacao a
                JOIN disciplina d ON a.id_disciplina = d.id_disciplina
                JOIN professor p ON a.id_professor = p.id_professor
                WHERE a.id_turma = %s
            """, (id_turma,))
            alocacoes_atuais = {}
            for a in cursor.fetchall():
                dia = a['dia_semana']
                hid = str(a['id_horario'])
                alocacoes_atuais.setdefault(dia, {})[hid] = {
                    'id_alocacao':   a['id_alocacao'],
                    'id_disciplina': a['id_disciplina'],
                    'id_local':      a['id_local'],
                    'sigla': a['sigla'],
                    'cor':   a['cor'],
                    'prof':  (a['prof_nome'] or '').split()[0],
                }

            # Ocupação de TODOS os professores e locais (para detectar conflitos)
            cursor.execute("""
                SELECT a.id_professor, a.id_local, a.dia_semana, a.id_horario, t.nome AS nome_turma
                FROM alocacao a
                JOIN turma t ON a.id_turma = t.id_turma
            """)
            ocupacao = {}
            ocupacao_detalhada = {}
            ocupacao_local = {}  # {id_local: {dia: [id_horario, ...]}}
            for a in cursor.fetchall():
                pid = str(a['id_professor'])
                lid = str(a['id_local'])
                ocupacao.setdefault(pid, {}).setdefault(a['dia_semana'], []).append(a['id_horario'])
                ocupacao_detalhada.setdefault(pid, {}).setdefault(a['dia_semana'], {})[a['id_horario']] = a['nome_turma']
                ocupacao_local.setdefault(lid, {}).setdefault(a['dia_semana'], []).append(a['id_horario'])

            # Disponibilidades dos professores
            cursor.execute("""
                SELECT id_professor, dia_semana, id_horario
                FROM disponibilidade_professor WHERE disponivel = 1
            """)
            disponibilidades = {}
            for d in cursor.fetchall():
                pid = str(d['id_professor'])
                disponibilidades.setdefault(pid, {}).setdefault(d['dia_semana'], []).append(d['id_horario'])

            cursor.execute("SELECT * FROM horario_aula WHERE eh_intervalo = 0 ORDER BY hora_inicio")
            horarios = cursor.fetchall()

            cursor.execute("SELECT * FROM `local` WHERE status = 'ativo' ORDER BY nome")
            locais = cursor.fetchall()

            cursor.execute("SELECT id_professor, nome FROM professor WHERE status = 'ativo' ORDER BY nome")
            todos_professores = cursor.fetchall()

            # Carregar pendentes de sugestão, se solicitado
            sugestao_pendentes = {}
            if sugestao_id:
                try:
                    cursor.execute(
                        "SELECT dados_json FROM sugestao_grade WHERE id_sugestao = %s",
                        (sugestao_id,)
                    )
                    row = cursor.fetchone()
                    if row:
                        dados_sug = json.loads(row['dados_json'])
                        for s in dados_sug.get('slots', []):
                            if s['id_turma'] == id_turma:
                                key = f"{s['dia']}|{s['id_horario']}"
                                sugestao_pendentes[key] = {
                                    'id_disciplina': s['id_disciplina'],
                                    'id_professor':  s['id_professor'],
                                    'id_local':      s['id_local'],
                                    'dia':           s['dia'],
                                    'id_horario':    s['id_horario'],
                                    'sigla':         s['sigla'],
                                    'cor':           s['cor'],
                                    'prof':          s['prof'],
                                }
                except Exception:
                    pass

            if request.method == 'POST':
                slots_raw = request.form.get('slots_json', '[]')
                try:
                    slots = json.loads(slots_raw)
                except Exception:
                    slots = []

                if not slots:
                    flash("Nenhuma alocação para salvar.", 'erro')
                else:
                    inseridos = 0
                    erros_prof = []
                    erros_local = []
                    erros_turma = []
                    for s in slots:
                        id_disc = s.get('id_disciplina')
                        id_prof = s.get('id_professor')
                        id_loc  = s.get('id_local')
                        dia     = s.get('dia')
                        id_hor  = s.get('id_horario')
                        if not all([id_disc, id_prof, id_loc, dia, id_hor]):
                            continue
                        try:
                            cursor.execute("SAVEPOINT sp")
                            cursor.execute("""
                                INSERT INTO alocacao
                                    (id_turma,id_disciplina,id_professor,id_local,dia_semana,id_horario)
                                VALUES (%s,%s,%s,%s,%s,%s)
                            """, (id_turma, id_disc, id_prof, id_loc, dia, id_hor))
                            cursor.execute("RELEASE SAVEPOINT sp")
                            inseridos += 1
                        except pymysql.IntegrityError as e:
                            cursor.execute("ROLLBACK TO SAVEPOINT sp")
                            err = str(e.args[1]) if len(e.args) > 1 else ''
                            if 'id_local' in err:
                                erros_local.append(dia)
                            elif 'id_professor' in err:
                                erros_prof.append(dia)
                            else:
                                erros_turma.append(dia)
                    conexao.commit()
                    if erros_local:
                        flash(f"Local já ocupado neste horário ({', '.join(erros_local)}). Escolha outro local.", 'erro')
                    if erros_prof:
                        flash(f"Professor já alocado em outra turma ({', '.join(erros_prof)}).", 'erro')
                    if erros_turma:
                        flash(f"Turma já possui aula neste horário ({', '.join(erros_turma)}).", 'erro')
                    if inseridos:
                        flash(f"{inseridos} alocação(ões) salvas com sucesso!", 'sucesso')
                    return redirect(url_for('alocar_turma_completa', id_turma=id_turma))

        grade_json = json.dumps([{
            'id':             g['id_disciplina'],
            'nome':           g['nome_disciplina'],
            'sigla':          g['sigla'],
            'cor':            g['cor'],
            'professores':    g['professores'],
            'id_professor':   g['id_professor'],
            'nome_professor': g['nome_professor'] or '—',
            'aulas_semanais': g['aulas_semanais'],
            'ja_alocadas':    g['ja_alocadas'],
        } for g in grade])

        return render_template('alocar_turma.html',
            turma=turma, grade=grade, horarios=horarios, locais=locais,
            grade_json=grade_json,
            alocacoes_json=json.dumps(alocacoes_atuais),
            ocupacao_json=json.dumps(ocupacao),
            disponibilidades_json=json.dumps(disponibilidades),
            horarios_json=json.dumps([{
                'id': h['id_horario'],
                'hora_inicio': h['hora_inicio'],
                'hora_fim': h['hora_fim'],
            } for h in horarios]),
            locais_json=json.dumps([{
                'id': l['id_local'], 'nome': l['nome']
            } for l in locais]),
            todos_professores_json=json.dumps([{'id': p['id_professor'], 'nome': p['nome']} for p in todos_professores]),
            ocupacao_detalhada_json=json.dumps(ocupacao_detalhada),
            ocupacao_local_json=json.dumps(ocupacao_local),
            sugestao_pendentes_json=json.dumps(sugestao_pendentes),
            sugestao_id=sugestao_id,
        )

    @app.route('/atualizar_local_alocacao/<int:id_alocacao>', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def atualizar_local_alocacao(id_alocacao):
        id_local = request.form.get('id_local', '').strip()
        id_turma = request.form.get('id_turma', '').strip()
        if id_local:
            with conectar() as conexao:
                cursor = conexao.cursor()
                cursor.execute(
                    "UPDATE alocacao SET id_local = %s WHERE id_alocacao = %s",
                    (id_local, id_alocacao)
                )
                conexao.commit()
            flash("Local atualizado.", 'sucesso')
        return redirect(url_for('alocar_turma_completa', id_turma=id_turma))

    @app.route('/deletar_alocacao_turma/<int:id_turma>/<int:id_alocacao>', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def deletar_alocacao_turma(id_turma, id_alocacao):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM alocacao WHERE id_alocacao = %s", (id_alocacao,))
            conexao.commit()
        return redirect(url_for('alocar_turma_completa', id_turma=id_turma))

    # ─── CADASTRO INDIVIDUAL (mantido para edições pontuais) ────────────────

    @app.route('/cadastrar_alocacao', methods=['GET', 'POST'])
    @requer_perfil('diretor', 'secretaria')
    def cadastrar_alocacao():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT t.id_turma, t.nome, t.serie, tr.nome AS nome_turno
                FROM turma t JOIN turno tr ON t.id_turno = tr.id_turno
                ORDER BY tr.nome, t.serie, t.nome
            """)
            turmas = cursor.fetchall()
            cursor.execute("SELECT * FROM disciplina ORDER BY nome")
            disciplinas = cursor.fetchall()
            cursor.execute("SELECT * FROM professor WHERE status = 'ativo' ORDER BY nome")
            professores = cursor.fetchall()
            cursor.execute("SELECT * FROM `local` WHERE status = 'ativo' ORDER BY nome")
            locais = cursor.fetchall()
            cursor.execute("SELECT * FROM horario_aula WHERE eh_intervalo = 0 ORDER BY hora_inicio")
            horarios = cursor.fetchall()

            # Mapa de disponibilidade: {str(id_professor): {dia: [id_horario, ...]}}
            cursor.execute("""
                SELECT id_professor, dia_semana, id_horario
                FROM disponibilidade_professor WHERE disponivel = 1
            """)
            disponibilidades = {}
            for d in cursor.fetchall():
                pid = str(d['id_professor'])
                if pid not in disponibilidades:
                    disponibilidades[pid] = {}
                dia = d['dia_semana']
                if dia not in disponibilidades[pid]:
                    disponibilidades[pid][dia] = []
                disponibilidades[pid][dia].append(d['id_horario'])

            # Mapa de alocações existentes: {str(id_turma): {dia: {str(id_horario): "SIGLA/Prof"}}}
            cursor.execute("""
                SELECT a.id_turma, a.dia_semana, a.id_horario, d.sigla, p.nome AS prof_nome
                FROM alocacao a
                JOIN disciplina d ON a.id_disciplina = d.id_disciplina
                JOIN professor p ON a.id_professor = p.id_professor
            """)
            alocacoes_existentes = {}
            for a in cursor.fetchall():
                tid = str(a['id_turma'])
                if tid not in alocacoes_existentes:
                    alocacoes_existentes[tid] = {}
                dia = a['dia_semana']
                if dia not in alocacoes_existentes[tid]:
                    alocacoes_existentes[tid][dia] = {}
                primeiro_nome = (a['prof_nome'] or '').split()[0]
                alocacoes_existentes[tid][dia][str(a['id_horario'])] = f"{a['sigla']} / {primeiro_nome}"

            # Mapa de ocupação do professor: {str(id_professor): {dia: [id_horario, ...]}}
            cursor.execute("""
                SELECT a.id_professor, a.dia_semana, a.id_horario
                FROM alocacao a
            """)
            ocupacao_professor = {}
            for a in cursor.fetchall():
                pid = str(a['id_professor'])
                if pid not in ocupacao_professor:
                    ocupacao_professor[pid] = {}
                dia = a['dia_semana']
                if dia not in ocupacao_professor[pid]:
                    ocupacao_professor[pid][dia] = []
                ocupacao_professor[pid][dia].append(a['id_horario'])

            horarios_json = json.dumps([
                {'id': h['id_horario'], 'hora_inicio': h['hora_inicio'], 'hora_fim': h['hora_fim']}
                for h in horarios
            ])
            locais_json = json.dumps([
                {'id': l['id_local'], 'nome': l['nome'], 'tipo': l['tipo']}
                for l in locais
            ])

            if request.method == 'POST':
                id_turma     = request.form.get('id_turma', '').strip()
                id_disciplina = request.form.get('id_disciplina', '').strip()
                id_professor = request.form.get('id_professor', '').strip()
                slots_raw    = request.form.get('slots_json', '[]')

                try:
                    slots = json.loads(slots_raw)
                except (json.JSONDecodeError, ValueError):
                    slots = []

                if not all([id_turma, id_disciplina, id_professor]) or not slots:
                    flash("Selecione turma, disciplina, professor e ao menos um horário com local.", 'erro')
                else:
                    conflitos = 0
                    inseridos = 0
                    sem_local = 0
                    for slot in slots:
                        dia        = slot.get('dia', '')
                        id_horario = slot.get('id_horario', '')
                        id_local   = slot.get('id_local', '')
                        if not all([dia, id_horario, id_local]):
                            sem_local += 1
                            continue
                        try:
                            cursor.execute("SAVEPOINT sp_aloc")
                            cursor.execute("""
                                INSERT INTO alocacao
                                    (id_turma, id_disciplina, id_professor, id_local, dia_semana, id_horario)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """, (id_turma, id_disciplina, id_professor, id_local, dia, id_horario))
                            cursor.execute("RELEASE SAVEPOINT sp_aloc")
                            inseridos += 1
                        except pymysql.IntegrityError:
                            cursor.execute("ROLLBACK TO SAVEPOINT sp_aloc")
                            conflitos += 1
                    conexao.commit()
                    if sem_local:
                        flash(f"{sem_local} slot(s) ignorado(s) por falta de local selecionado.", 'erro')
                    if conflitos:
                        flash(f"{conflitos} conflito(s) ignorado(s): professor, turma ou local já ocupado naquele horário.", 'erro')
                    if inseridos:
                        flash(f"{inseridos} alocação(ões) cadastrada(s) com sucesso.", 'sucesso')
                        return redirect(url_for('selecionar_turno_alocacoes'))

        return render_template('cadastro_alocacao.html',
                               turmas=turmas, disciplinas=disciplinas,
                               professores=professores, locais=locais,
                               horarios=horarios,
                               disponibilidades_json=json.dumps(disponibilidades),
                               alocacoes_existentes_json=json.dumps(alocacoes_existentes),
                               ocupacao_professor_json=json.dumps(ocupacao_professor),
                               horarios_json=horarios_json,
                               locais_json=locais_json)

    @app.route('/selecionar_turno_alocacoes')
    @requer_perfil('diretor', 'secretaria')
    def selecionar_turno_alocacoes():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM turno ORDER BY nome")
            turnos = cursor.fetchall()
        return render_template('selecionar_turno_alocacoes.html', turnos=turnos)

    @app.route('/alocacoes/<int:id_turno>')
    @requer_perfil('diretor', 'secretaria')
    def listar_alocacoes_turno(id_turno):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM turno WHERE id_turno = %s", (id_turno,))
            turno = cursor.fetchone()
            cursor.execute("""
                SELECT a.id_alocacao, a.id_turma, a.id_disciplina, a.id_professor,
                       a.id_local, a.dia_semana, a.id_horario,
                       t.nome AS nome_turma, t.serie,
                       d.nome AS nome_disciplina, d.sigla, d.cor,
                       p.nome AS nome_professor,
                       l.nome AS nome_local,
                       h.hora_inicio, h.hora_fim
                FROM alocacao a
                JOIN turma t ON a.id_turma = t.id_turma
                JOIN disciplina d ON a.id_disciplina = d.id_disciplina
                JOIN professor p ON a.id_professor = p.id_professor
                JOIN `local` l ON a.id_local = l.id_local
                JOIN horario_aula h ON a.id_horario = h.id_horario
                WHERE t.id_turno = %s
                ORDER BY t.serie, t.nome,
                    CASE a.dia_semana
                        WHEN 'segunda' THEN 1 WHEN 'terca' THEN 2
                        WHEN 'quarta' THEN 3 WHEN 'quinta' THEN 4
                        WHEN 'sexta' THEN 5 END,
                    h.hora_inicio
            """, (id_turno,))
            registros = cursor.fetchall()

        alocacoes_por_serie, ordem_series = _agregar_alocacoes(registros)
        return render_template('alocacao.html', turno=turno,
                               alocacoes_por_serie=alocacoes_por_serie,
                               ordem_series=ordem_series, alocacao_edicao=None)

    @app.route('/editar_alocacao/<int:id_alocacao>')
    @requer_perfil('diretor', 'secretaria')
    def editar_alocacao(id_alocacao):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT a.*, t.id_turno FROM alocacao a
                JOIN turma t ON a.id_turma = t.id_turma WHERE a.id_alocacao = %s
            """, (id_alocacao,))
            alocacao_edicao = cursor.fetchone()
            if not alocacao_edicao:
                return redirect(url_for('selecionar_turno_alocacoes'))

            id_turno = alocacao_edicao['id_turno']
            cursor.execute("SELECT * FROM turno WHERE id_turno = %s", (id_turno,))
            turno = cursor.fetchone()
            cursor.execute("""
                SELECT a.id_alocacao, a.id_turma, a.id_disciplina, a.id_professor,
                       a.id_local, a.dia_semana, a.id_horario,
                       t.nome AS nome_turma, t.serie,
                       d.nome AS nome_disciplina, d.sigla, d.cor,
                       p.nome AS nome_professor,
                       l.nome AS nome_local,
                       h.hora_inicio, h.hora_fim
                FROM alocacao a
                JOIN turma t ON a.id_turma = t.id_turma
                JOIN disciplina d ON a.id_disciplina = d.id_disciplina
                JOIN professor p ON a.id_professor = p.id_professor
                JOIN `local` l ON a.id_local = l.id_local
                JOIN horario_aula h ON a.id_horario = h.id_horario
                WHERE t.id_turno = %s
                ORDER BY t.serie, t.nome,
                    CASE a.dia_semana
                        WHEN 'segunda' THEN 1 WHEN 'terca' THEN 2
                        WHEN 'quarta' THEN 3 WHEN 'quinta' THEN 4
                        WHEN 'sexta' THEN 5 END,
                    h.hora_inicio
            """, (id_turno,))
            registros = cursor.fetchall()
            cursor.execute("""
                SELECT t.id_turma, t.nome, t.serie, tr.nome AS nome_turno
                FROM turma t JOIN turno tr ON t.id_turno = tr.id_turno ORDER BY t.nome
            """)
            turmas = cursor.fetchall()
            cursor.execute("SELECT * FROM disciplina ORDER BY nome")
            disciplinas = cursor.fetchall()
            cursor.execute("SELECT * FROM professor ORDER BY nome")
            professores = cursor.fetchall()
            cursor.execute("SELECT * FROM `local` ORDER BY nome")
            locais = cursor.fetchall()
            cursor.execute("SELECT * FROM horario_aula ORDER BY hora_inicio")
            horarios = cursor.fetchall()

        alocacoes_por_serie, ordem_series = _agregar_alocacoes(registros)
        return render_template('alocacao.html', turno=turno,
                               alocacoes_por_serie=alocacoes_por_serie,
                               ordem_series=ordem_series, alocacao_edicao=alocacao_edicao,
                               turmas=turmas, disciplinas=disciplinas,
                               professores=professores, locais=locais, horarios=horarios)

    @app.route('/atualizar_alocacao/<int:id_alocacao>', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def atualizar_alocacao(id_alocacao):
        id_turma      = request.form['id_turma']
        id_disciplina = request.form['id_disciplina']
        id_professor  = request.form['id_professor']
        id_local      = request.form['id_local']
        dia_semana    = request.form['dia_semana']
        id_horario    = request.form['id_horario']

        try:
            with conectar() as conexao:
                cursor = conexao.cursor()
                cursor.execute("""
                    UPDATE alocacao
                    SET id_turma = %s, id_disciplina = %s, id_professor = %s,
                        id_local = %s, dia_semana = %s, id_horario = %s
                    WHERE id_alocacao = %s
                """, (id_turma, id_disciplina, id_professor, id_local,
                      dia_semana, id_horario, id_alocacao))
                conexao.commit()
            return redirect(url_for('selecionar_turno_alocacoes'))
        except pymysql.IntegrityError:
            flash("Conflito de horário: professor, turma ou local já está ocupado nesse dia e horário.", 'erro')
            return redirect(url_for('editar_alocacao', id_alocacao=id_alocacao))

    @app.route('/deletar_alocacao/<int:id_alocacao>', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def deletar_alocacao(id_alocacao):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM alocacao WHERE id_alocacao = %s", (id_alocacao,))
            conexao.commit()
        return redirect(url_for('selecionar_turno_alocacoes'))

    @app.route('/deletar_todas_alocacoes_turma/<int:id_turma>', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def deletar_todas_alocacoes_turma(id_turma):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT COUNT(*) AS total FROM alocacao WHERE id_turma = %s", (id_turma,))
            total = cursor.fetchone()['total']
            cursor.execute("DELETE FROM alocacao WHERE id_turma = %s", (id_turma,))
            conexao.commit()
        flash(f"{total} alocação(ões) excluída(s).", 'sucesso')
        return redirect(url_for('alocar_turma_completa', id_turma=id_turma))

    @app.route('/deletar_todas_alocacoes_turno/<int:id_turno>', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def deletar_todas_alocacoes_turno(id_turno):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT COUNT(*) AS total FROM alocacao a
                JOIN turma t ON a.id_turma = t.id_turma
                WHERE t.id_turno = %s
            """, (id_turno,))
            total = cursor.fetchone()['total']
            cursor.execute("""
                DELETE a FROM alocacao a
                JOIN turma t ON a.id_turma = t.id_turma
                WHERE t.id_turno = %s
            """, (id_turno,))
            conexao.commit()
        flash(f"{total} alocação(ões) excluída(s) do turno.", 'sucesso')
        return redirect(url_for('listar_alocacoes_turno', id_turno=id_turno))


def _agregar_alocacoes(registros):
    alocacoes_por_serie = {}
    ordem_series = []
    for r in registros:
        serie    = r['serie']
        id_turma = r['id_turma']
        if serie not in alocacoes_por_serie:
            alocacoes_por_serie[serie] = {}
            ordem_series.append(serie)
        if id_turma not in alocacoes_por_serie[serie]:
            alocacoes_por_serie[serie][id_turma] = {
                'id_turma': id_turma, 'nome_turma': r['nome_turma'], 'itens': []
            }
        alocacoes_por_serie[serie][id_turma]['itens'].append({
            'id_alocacao':     r['id_alocacao'],
            'dia_semana':      r['dia_semana'],
            'hora_inicio':     r['hora_inicio'],
            'hora_fim':        r['hora_fim'],
            'nome_disciplina': r['nome_disciplina'],
            'sigla':           r['sigla'],
            'cor':             r['cor'],
            'nome_professor':  r['nome_professor'],
            'nome_local':      r['nome_local'],
        })
    return alocacoes_por_serie, ordem_series
