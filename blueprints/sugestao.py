import json
import random
import pymysql
from db import conectar
from auth import requer_perfil
from flask import render_template, request, redirect, url_for, flash

_DIAS = ['segunda', 'terca', 'quarta', 'quinta', 'sexta']
_SEEDS = [42, 137, 999]


def _slots_disponiveis(pid_str, tid_str, disponibilidades, ocup_prof, ocup_turma, horario_ids):
    # Professor sem nenhuma disponibilidade cadastrada → considera disponível em todos os horários
    sem_restricao = pid_str not in disponibilidades
    available = []
    for dia in _DIAS:
        disp_set = set(disponibilidades.get(pid_str, {}).get(dia, []))
        prof_ocup = ocup_prof.get(pid_str, {}).get(dia, set())
        turma_ocup = ocup_turma.get(tid_str, {}).get(dia, set())
        for hid in horario_ids:
            livre_prof = sem_restricao or (hid in disp_set)
            if livre_prof and hid not in prof_ocup and hid not in turma_ocup:
                available.append((dia, hid))
    return available


def _capacidade(pid_str, disponibilidades, horario_ids):
    """Slots teóricos disponíveis para o professor (ignora ocupação atual)."""
    if pid_str not in disponibilidades:
        return len(horario_ids) * len(_DIAS)
    return sum(len(disponibilidades[pid_str].get(d, [])) for d in _DIAS)


def _gerar_sugestao(grade_por_turma, disponibilidades, horario_ids, locais,
                    ocup_prof_base, ocup_turma_base, seed, ocup_local_base=None):
    rng = random.Random(seed)
    ids_locais = [l['id'] for l in locais] if locais else [1]

    ocup_prof = {pid: {dia: set(hids) for dia, hids in dias.items()}
                 for pid, dias in ocup_prof_base.items()}
    ocup_turma = {tid: {dia: set(hids) for dia, hids in dias.items()}
                  for tid, dias in ocup_turma_base.items()}
    # ocup_local: {id_local: {dia: set(id_horario)}}
    ocup_local = {}
    if ocup_local_base:
        ocup_local = {lid: {dia: set(hids) for dia, hids in dias.items()}
                      for lid, dias in ocup_local_base.items()}

    slots_resultado = []
    nao_alocados = []

    # ── Passo 1: montar lista bruta e ordenar do mais restrito para o menos ──
    # "Mais restrito" = menos professores elegíveis para a disciplina.
    # Isso garante que disciplinas com professor único (ex: Ed. Física)
    # recebam seu professor antes que demandas com mais opções o esgotem.
    brutos = []
    for id_turma, disciplinas in grade_por_turma.items():
        tid = str(id_turma)
        for disc in disciplinas:
            professores = disc.get('professores', [])
            if not professores:
                nao_alocados.append({
                    'id_turma': id_turma,
                    'id_disciplina': disc['id_disciplina'],
                    'nome': disc['nome_disciplina'],
                    'faltam': disc['aulas_semanais'],
                    'motivo': 'sem professor vinculado',
                })
                continue
            brutos.append((id_turma, tid, disc, professores))

    brutos.sort(key=lambda x: len(x[3]))  # menos opções de professor = processa primeiro

    # ── Passo 2: pré-atribuir professor fixo a cada demand ──
    # Escolhe o professor com maior capacidade remanescente (balanceia carga).
    # Professor é FIXO para toda a alocação — impede troca entre rodadas,
    # que causava fragmentação e aumentava conflitos.
    demands = []
    prof_carga = {}  # pid → aulas já atribuídas na pré-fase

    for id_turma, tid, disc, professores in brutos:
        best_prof = max(
            professores,
            key=lambda p: _capacidade(str(p['id']), disponibilidades, horario_ids)
                          - prof_carga.get(str(p['id']), 0)
        )
        pid = str(best_prof['id'])
        prof_carga[pid] = prof_carga.get(pid, 0) + disc['aulas_semanais']
        demands.append({
            'id_turma': id_turma,
            'tid': tid,
            'disc': disc,
            'remaining': disc['aulas_semanais'],
            'day_counts': {d: 0 for d in _DIAS},
            'pid': pid,
            'professor': best_prof,
        })

    rng.shuffle(demands)

    # ── Passo 3: Most Constrained Variable (MCV) com professor fixo ──
    # A cada iteração, agenda a demanda com MENOS slots disponíveis primeiro.
    # Isso evita deadlocks greedy onde, com zero folga (30 aulas = 30 slots),
    # o round-robin estático preenche os últimos slots de uma turma com outras
    # disciplinas antes que a demanda mais restrita consiga um lugar.
    while True:
        candidatos = []
        for demand in demands:
            if demand['remaining'] <= 0:
                continue
            avail = _slots_disponiveis(demand['pid'], demand['tid'], disponibilidades,
                                       ocup_prof, ocup_turma, horario_ids)
            if avail:
                candidatos.append((len(avail), demand, avail))

        if not candidatos:
            break

        # Ordena pelo mais restrito (menos slots disponíveis)
        candidatos.sort(key=lambda x: x[0])
        _, demand, avail = candidatos[0]

        rng.shuffle(avail)
        # Prefere um dia ainda não usado por esta disciplina nesta turma
        slot = next(
            ((d, h) for d, h in avail if demand['day_counts'][d] == 0),
            avail[0]
        )
        dia, hid = slot

        pid = demand['pid']
        tid = demand['tid']
        # Escolher local livre neste (dia, hid)
        local_livre = next(
            (lid for lid in ids_locais
             if hid not in ocup_local.get(lid, {}).get(dia, set())),
            ids_locais[0]
        )
        ocup_prof.setdefault(pid, {}).setdefault(dia, set()).add(hid)
        ocup_turma.setdefault(tid, {}).setdefault(dia, set()).add(hid)
        ocup_local.setdefault(local_livre, {}).setdefault(dia, set()).add(hid)
        demand['day_counts'][dia] += 1
        demand['remaining'] -= 1
        slots_resultado.append({
            'id_turma': demand['id_turma'],
            'id_disciplina': demand['disc']['id_disciplina'],
            'id_professor': demand['professor']['id'],
            'id_local': local_livre,
            'dia': dia,
            'id_horario': hid,
            'sigla': demand['disc']['sigla'],
            'cor': demand['disc']['cor'],
            'prof': (demand['professor']['nome'] or '').split()[0],
            'nome_disciplina': demand['disc']['nome_disciplina'],
        })

    # Demands que ficaram sem slots suficientes
    for demand in demands:
        if demand['remaining'] > 0:
            nao_alocados.append({
                'id_turma': demand['id_turma'],
                'id_disciplina': demand['disc']['id_disciplina'],
                'nome': demand['disc']['nome_disciplina'],
                'faltam': demand['remaining'],
                'motivo': 'sem slots disponíveis',
            })

    return slots_resultado, nao_alocados


def registrar(app):

    @app.route('/sugestoes')
    @requer_perfil('diretor', 'secretaria')
    def listar_sugestoes():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM turno ORDER BY nome")
            turnos = cursor.fetchall()
            cursor.execute("""
                SELECT s.*, t.nome AS nome_turno
                FROM sugestao_grade s
                JOIN turno t ON s.id_turno = t.id_turno
                ORDER BY s.criado_em DESC
            """)
            sugestoes = cursor.fetchall()
        return render_template('sugestoes.html', turnos=turnos, sugestoes=sugestoes)

    @app.route('/gerar_sugestoes', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def gerar_sugestoes():
        id_turno = request.form.get('id_turno', '').strip()
        num_sugestoes = min(max(int(request.form.get('num_sugestoes', 3)), 1), 3)
        if not id_turno:
            flash("Selecione um turno.", 'erro')
            return redirect(url_for('listar_sugestoes'))

        with conectar() as conexao:
            cursor = conexao.cursor()

            cursor.execute("SELECT * FROM turno WHERE id_turno = %s", (id_turno,))
            turno = cursor.fetchone()
            if not turno:
                flash("Turno não encontrado.", 'erro')
                return redirect(url_for('listar_sugestoes'))

            # Grade curricular — todas as linhas (1 por professor habilitado)
            cursor.execute("""
                SELECT t.id_turma, gc.id_disciplina, gc.aulas_semanais,
                       d.nome AS nome_disciplina, d.sigla, d.cor,
                       p.id_professor, p.nome AS nome_professor
                FROM grade_curricular gc
                JOIN turma t ON gc.id_turno = t.id_turno AND gc.serie = t.serie
                JOIN disciplina d ON gc.id_disciplina = d.id_disciplina
                LEFT JOIN professor_disciplina pd ON pd.id_disciplina = gc.id_disciplina
                LEFT JOIN professor p ON p.id_professor = pd.id_professor AND p.status = 'ativo'
                WHERE gc.id_turno = %s
                ORDER BY t.id_turma, gc.id_disciplina, p.id_professor
            """, (id_turno,))
            grade_rows = cursor.fetchall()

            if not grade_rows:
                flash("Nenhuma grade curricular cadastrada para este turno.", 'erro')
                return redirect(url_for('listar_sugestoes'))

            # Agrupa: cada disciplina recebe lista de todos os professores habilitados
            grade_por_turma = {}
            _disc_map = {}  # (id_turma, id_disciplina) → entrada na lista
            for r in grade_rows:
                key = (r['id_turma'], r['id_disciplina'])
                if key not in _disc_map:
                    entry = {
                        'id_disciplina': r['id_disciplina'],
                        'aulas_semanais': r['aulas_semanais'],
                        'nome_disciplina': r['nome_disciplina'],
                        'sigla': r['sigla'],
                        'cor': r['cor'],
                        'professores': [],
                    }
                    _disc_map[key] = entry
                    grade_por_turma.setdefault(r['id_turma'], []).append(entry)
                if r['id_professor']:
                    _disc_map[key]['professores'].append({
                        'id': r['id_professor'],
                        'nome': r['nome_professor'],
                    })

            # Horários (sem intervalo)
            cursor.execute("SELECT id_horario FROM horario_aula WHERE eh_intervalo = 0 ORDER BY hora_inicio")
            horario_ids = [h['id_horario'] for h in cursor.fetchall()]

            # Locais ativos
            cursor.execute("SELECT id_local AS id, nome FROM `local` WHERE status = 'ativo' ORDER BY nome")
            locais = cursor.fetchall()

            # Carregar alocações existentes para não sugerir o que já está alocado
            cursor.execute("""
                SELECT a.id_turma, a.id_disciplina, a.id_professor, a.id_local, a.dia_semana, a.id_horario
                FROM alocacao a
                JOIN turma t ON a.id_turma = t.id_turma
                WHERE t.id_turno = %s
            """, (id_turno,))
            existentes = cursor.fetchall()

            from collections import Counter
            ocup_prof_base = {}
            ocup_turma_base = {}
            ocup_local_base = {}
            ja_alocados = Counter()
            for e in existentes:
                pid = str(e['id_professor'])
                tid = str(e['id_turma'])
                lid = e['id_local']
                ocup_prof_base.setdefault(pid, {}).setdefault(e['dia_semana'], set()).add(e['id_horario'])
                ocup_turma_base.setdefault(tid, {}).setdefault(e['dia_semana'], set()).add(e['id_horario'])
                ocup_local_base.setdefault(lid, {}).setdefault(e['dia_semana'], set()).add(e['id_horario'])
                ja_alocados[(e['id_turma'], e['id_disciplina'])] += 1

            # Reduzir demanda pelo que já foi alocado
            for id_turma, discs in grade_por_turma.items():
                for disc in discs:
                    ja = ja_alocados.get((id_turma, disc['id_disciplina']), 0)
                    disc['aulas_semanais'] = max(0, disc['aulas_semanais'] - ja)
            grade_por_turma = {
                tid: [d for d in discs if d['aulas_semanais'] > 0]
                for tid, discs in grade_por_turma.items()
            }
            grade_por_turma = {tid: discs for tid, discs in grade_por_turma.items() if discs}

            # Total de aulas restantes para calcular cobertura
            total_esperado = sum(d['aulas_semanais'] for ds in grade_por_turma.values() for d in ds)

            # Gerar sugestões com seeds diferentes
            if not grade_por_turma:
                flash("Todas as aulas da grade curricular já estão alocadas.", 'sucesso')
                return redirect(url_for('listar_sugestoes'))

            geradas = 0
            for i, seed in enumerate(_SEEDS[:num_sugestoes]):
                slots, nao_aloc = _gerar_sugestao(
                    grade_por_turma, {}, horario_ids, locais,
                    ocup_prof_base, ocup_turma_base, seed,
                    ocup_local_base=ocup_local_base
                )
                cobertura = round((len(slots) / total_esperado) * 100) if total_esperado else 0
                nome = f"Sugestão {i+1} — {turno['nome']} (seed {seed})"
                dados = {
                    'slots': slots,
                    'nao_alocados': nao_aloc,
                }
                cursor.execute("""
                    INSERT INTO sugestao_grade (id_turno, nome, dados_json, cobertura_pct, nao_alocados)
                    VALUES (%s, %s, %s, %s, %s)
                """, (id_turno, nome, json.dumps(dados, default=str), cobertura, len(nao_aloc)))
                geradas += 1

            conexao.commit()

        # Diagnóstico: verifica se alguma turma tem mais aulas restantes do que slots livres
        n_slots_semana = len(horario_ids) * len(_DIAS)
        for id_turma, discs in grade_por_turma.items():
            slots_livres = n_slots_semana - sum(
                len(s) for s in ocup_turma_base.get(str(id_turma), {}).values()
            )
            total_restante_turma = sum(d['aulas_semanais'] for d in discs)
            if total_restante_turma > slots_livres:
                flash(
                    f"Atenção: a grade curricular ultrapassa o número de horários "
                    f"disponíveis ({n_slots_semana}/semana). Algumas aulas nunca poderão "
                    f"ser alocadas. Reduza aulas_semanais ou cadastre mais horários.",
                    'erro'
                )
                break

        flash(f"{geradas} sugestão(ões) gerada(s) com sucesso!", 'sucesso')
        return redirect(url_for('listar_sugestoes'))

    @app.route('/sugestao/<int:id_sugestao>')
    @requer_perfil('diretor', 'secretaria')
    def ver_sugestao(id_sugestao):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT s.*, t.nome AS nome_turno
                FROM sugestao_grade s
                JOIN turno t ON s.id_turno = t.id_turno
                WHERE s.id_sugestao = %s
            """, (id_sugestao,))
            sugestao = cursor.fetchone()
            if not sugestao:
                flash("Sugestão não encontrada.", 'erro')
                return redirect(url_for('listar_sugestoes'))

            dados = json.loads(sugestao['dados_json'])
            slots = dados.get('slots', [])
            nao_alocados = dados.get('nao_alocados', [])

            # Turmas do turno ordenadas por série/nome
            cursor.execute("""
                SELECT t.id_turma, t.nome, t.serie, tr.nome AS nome_turno
                FROM turma t JOIN turno tr ON t.id_turno = tr.id_turno
                WHERE t.id_turno = %s ORDER BY t.serie, t.nome
            """, (sugestao['id_turno'],))
            turmas_lista = cursor.fetchall()
            turmas = {t['id_turma']: t for t in turmas_lista}

            # Todos os horários (incluindo intervalos para exibição correta)
            cursor.execute("SELECT * FROM horario_aula ORDER BY hora_inicio")
            horarios_lista = cursor.fetchall()

        # grade_map: {id_turma: {dia: {id_horario: slot}}} — lookup O(1) no template
        grade_map = {}
        for s in slots:
            tid = s['id_turma']
            grade_map.setdefault(tid, {}).setdefault(s['dia'], {})[s['id_horario']] = s

        return render_template('ver_sugestao.html',
            sugestao=sugestao,
            grade_map=grade_map,
            turmas_lista=turmas_lista,
            horarios_lista=horarios_lista,
            nao_alocados=nao_alocados,
            dias=_DIAS,
        )

    @app.route('/sugestao/<int:id_sugestao>/excluir', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def excluir_sugestao(id_sugestao):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM sugestao_grade WHERE id_sugestao = %s", (id_sugestao,))
            conexao.commit()
        flash("Sugestão excluída.", 'sucesso')
        return redirect(url_for('listar_sugestoes'))

    @app.route('/sugestao/<int:id_sugestao>/aplicar', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def aplicar_sugestao(id_sugestao):
        id_turma_filtro = request.form.get('id_turma', '').strip()

        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM sugestao_grade WHERE id_sugestao = %s", (id_sugestao,))
            sugestao = cursor.fetchone()
            if not sugestao:
                flash("Sugestão não encontrada.", 'erro')
                return redirect(url_for('listar_sugestoes'))

            dados = json.loads(sugestao['dados_json'])
            slots = dados.get('slots', [])

            if id_turma_filtro:
                slots = [s for s in slots if str(s['id_turma']) == id_turma_filtro]

            inseridos = conflitos = 0
            for s in slots:
                try:
                    cursor.execute("SAVEPOINT sp_sug")
                    cursor.execute("""
                        INSERT INTO alocacao
                            (id_turma, id_disciplina, id_professor, id_local, dia_semana, id_horario)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (s['id_turma'], s['id_disciplina'], s['id_professor'],
                          s['id_local'], s['dia'], s['id_horario']))
                    cursor.execute("RELEASE SAVEPOINT sp_sug")
                    inseridos += 1
                except pymysql.IntegrityError:
                    cursor.execute("ROLLBACK TO SAVEPOINT sp_sug")
                    conflitos += 1
            conexao.commit()

        if conflitos:
            flash(f"{conflitos} conflito(s) ignorado(s).", 'erro')
        if inseridos:
            flash(f"{inseridos} alocação(ões) aplicada(s) com sucesso!", 'sucesso')

        if id_turma_filtro:
            return redirect(url_for('alocar_turma_completa', id_turma=id_turma_filtro))
        return redirect(url_for('listar_sugestoes'))

    # ── Alocação Automática ────────────────────────────────────────────────

    @app.route('/alocacao_automatica')
    @requer_perfil('diretor', 'secretaria')
    def alocacao_automatica():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM turno ORDER BY nome")
            turnos = cursor.fetchall()
        return render_template('alocacao_automatica.html', turnos=turnos)

    @app.route('/executar_alocacao_automatica', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def executar_alocacao_automatica():
        id_turno = request.form.get('id_turno', '').strip()
        if not id_turno:
            flash("Selecione um turno.", 'erro')
            return redirect(url_for('alocacao_automatica'))

        with conectar() as conexao:
            cursor = conexao.cursor()

            cursor.execute("SELECT * FROM turno WHERE id_turno = %s", (id_turno,))
            turno = cursor.fetchone()
            if not turno:
                flash("Turno não encontrado.", 'erro')
                return redirect(url_for('alocacao_automatica'))

            # Mesma query de grade da rota gerar_sugestoes
            cursor.execute("""
                SELECT t.id_turma, gc.id_disciplina, gc.aulas_semanais,
                       d.nome AS nome_disciplina, d.sigla, d.cor,
                       p.id_professor, p.nome AS nome_professor
                FROM grade_curricular gc
                JOIN turma t ON gc.id_turno = t.id_turno AND gc.serie = t.serie
                JOIN disciplina d ON gc.id_disciplina = d.id_disciplina
                LEFT JOIN professor_disciplina pd ON pd.id_disciplina = gc.id_disciplina
                LEFT JOIN professor p ON p.id_professor = pd.id_professor AND p.status = 'ativo'
                WHERE gc.id_turno = %s
                ORDER BY t.id_turma, gc.id_disciplina, p.id_professor
            """, (id_turno,))
            grade_rows = cursor.fetchall()

            if not grade_rows:
                flash("Nenhuma grade curricular cadastrada para este turno.", 'erro')
                return redirect(url_for('alocacao_automatica'))

            grade_por_turma = {}
            _disc_map = {}
            for r in grade_rows:
                key = (r['id_turma'], r['id_disciplina'])
                if key not in _disc_map:
                    entry = {
                        'id_disciplina': r['id_disciplina'],
                        'aulas_semanais': r['aulas_semanais'],
                        'nome_disciplina': r['nome_disciplina'],
                        'sigla': r['sigla'],
                        'cor': r['cor'],
                        'professores': [],
                    }
                    _disc_map[key] = entry
                    grade_por_turma.setdefault(r['id_turma'], []).append(entry)
                if r['id_professor']:
                    _disc_map[key]['professores'].append({
                        'id': r['id_professor'],
                        'nome': r['nome_professor'],
                    })

            cursor.execute("SELECT id_horario FROM horario_aula WHERE eh_intervalo = 0 ORDER BY hora_inicio")
            horario_ids = [h['id_horario'] for h in cursor.fetchall()]

            cursor.execute("SELECT id_local AS id, nome FROM `local` WHERE status = 'ativo' ORDER BY nome")
            locais = cursor.fetchall()

            if not horario_ids:
                flash("Nenhum horário de aula cadastrado.", 'erro')
                return redirect(url_for('alocacao_automatica'))

            if not locais:
                flash("Nenhum local ativo cadastrado.", 'erro')
                return redirect(url_for('alocacao_automatica'))

            # Carregar alocações existentes para evitar conflitos e não re-gerar o que já existe
            cursor.execute("""
                SELECT a.id_turma, a.id_disciplina, a.id_professor, a.id_local, a.dia_semana, a.id_horario
                FROM alocacao a
                JOIN turma t ON a.id_turma = t.id_turma
                WHERE t.id_turno = %s
            """, (id_turno,))
            existentes = cursor.fetchall()

            # Mapas de ocupação para o algoritmo respeitar o que já está no banco
            from collections import Counter
            ocup_prof_base = {}
            ocup_turma_base = {}
            ocup_local_base = {}
            ja_alocados = Counter()
            for e in existentes:
                pid = str(e['id_professor'])
                tid = str(e['id_turma'])
                lid = e['id_local']
                dia = e['dia_semana']
                hid = e['id_horario']
                ocup_prof_base.setdefault(pid, {}).setdefault(dia, set()).add(hid)
                ocup_turma_base.setdefault(tid, {}).setdefault(dia, set()).add(hid)
                ocup_local_base.setdefault(lid, {}).setdefault(dia, set()).add(hid)
                ja_alocados[(e['id_turma'], e['id_disciplina'])] += 1

            # Reduzir demanda pelo que já foi alocado; remover demands já satisfeitas
            for id_turma, discs in grade_por_turma.items():
                for disc in discs:
                    ja = ja_alocados.get((id_turma, disc['id_disciplina']), 0)
                    disc['aulas_semanais'] = max(0, disc['aulas_semanais'] - ja)
            grade_por_turma = {
                tid: [d for d in discs if d['aulas_semanais'] > 0]
                for tid, discs in grade_por_turma.items()
            }
            grade_por_turma = {tid: discs for tid, discs in grade_por_turma.items() if discs}

            slots, nao_aloc = _gerar_sugestao(
                grade_por_turma, {}, horario_ids, locais,
                ocup_prof_base, ocup_turma_base, seed=42,
                ocup_local_base=ocup_local_base
            )

            inseridos = conflitos = 0
            for s in slots:
                try:
                    cursor.execute("SAVEPOINT sp_auto")
                    cursor.execute("""
                        INSERT INTO alocacao
                            (id_turma, id_disciplina, id_professor, id_local, dia_semana, id_horario)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (s['id_turma'], s['id_disciplina'], s['id_professor'],
                          s['id_local'], s['dia'], s['id_horario']))
                    cursor.execute("RELEASE SAVEPOINT sp_auto")
                    inseridos += 1
                except pymysql.IntegrityError:
                    cursor.execute("ROLLBACK TO SAVEPOINT sp_auto")
                    conflitos += 1
            conexao.commit()

        if nao_aloc:
            flash(f"{len(nao_aloc)} disciplina(s) sem slots suficientes — reduza aulas_semanais ou cadastre mais horários.", 'erro')
        if conflitos:
            flash(f"{conflitos} slot(s) ignorado(s) por conflito com alocações existentes.", 'erro')
        flash(f"{inseridos} alocação(ões) criada(s) para o turno {turno['nome']}.", 'sucesso')
        return redirect(url_for('listar_alocacoes_turno', id_turno=id_turno))
