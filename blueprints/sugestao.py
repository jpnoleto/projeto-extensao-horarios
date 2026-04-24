import json
import random
import pymysql
from db import conectar
from auth import requer_perfil
from flask import render_template, request, redirect, url_for, flash

_DIAS = ['segunda', 'terca', 'quarta', 'quinta', 'sexta']
_SEEDS = [42, 137, 999]


def _garantir_tabela():
    with conectar() as conexao:
        cursor = conexao.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sugestao_grade (
                id_sugestao INT AUTO_INCREMENT PRIMARY KEY,
                id_turno INT NOT NULL,
                nome VARCHAR(100) NOT NULL,
                dados_json LONGTEXT NOT NULL,
                cobertura_pct INT DEFAULT 0,
                nao_alocados INT DEFAULT 0,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_turno) REFERENCES turno(id_turno)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        conexao.commit()


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


def _gerar_sugestao(grade_por_turma, disponibilidades, horario_ids, locais,
                    ocup_prof_base, ocup_turma_base, seed):
    rng = random.Random(seed)
    default_local = locais[0]['id'] if locais else 1

    ocup_prof = {pid: {dia: set(hids) for dia, hids in dias.items()}
                 for pid, dias in ocup_prof_base.items()}
    ocup_turma = {tid: {dia: set(hids) for dia, hids in dias.items()}
                  for tid, dias in ocup_turma_base.items()}

    slots_resultado = []
    nao_alocados = []

    turma_ids = list(grade_por_turma.keys())
    rng.shuffle(turma_ids)

    for id_turma in turma_ids:
        disciplinas = list(grade_por_turma[id_turma])
        rng.shuffle(disciplinas)
        disciplinas.sort(key=lambda d: d['aulas_semanais'], reverse=True)

        tid = str(id_turma)

        for disc in disciplinas:
            needed = disc['aulas_semanais']
            professores = disc.get('professores', [])

            if not professores:
                nao_alocados.append({
                    'id_turma': id_turma,
                    'id_disciplina': disc['id_disciplina'],
                    'nome': disc['nome_disciplina'],
                    'faltam': needed,
                    'motivo': 'sem professor vinculado',
                })
                continue

            # Escolhe o professor com mais slots disponíveis (balanceamento de carga)
            best_prof = None
            best_slots = None
            best_count = -1
            for prof in professores:
                pid_str = str(prof['id'])
                avail = _slots_disponiveis(pid_str, tid, disponibilidades, ocup_prof, ocup_turma, horario_ids)
                if len(avail) > best_count:
                    best_count = len(avail)
                    best_prof = prof
                    best_slots = avail

            pid = str(best_prof['id'])
            available = best_slots or []
            rng.shuffle(available)

            # Distribui priorizando dias diferentes
            chosen = []
            day_counts = {dia: 0 for dia in _DIAS}
            for dia, hid in available:
                if len(chosen) >= needed:
                    break
                if day_counts[dia] == 0:
                    chosen.append((dia, hid))
                    day_counts[dia] += 1
            if len(chosen) < needed:
                for dia, hid in available:
                    if (dia, hid) in chosen:
                        continue
                    if len(chosen) >= needed:
                        break
                    chosen.append((dia, hid))

            for dia, hid in chosen:
                ocup_prof.setdefault(pid, {}).setdefault(dia, set()).add(hid)
                ocup_turma.setdefault(tid, {}).setdefault(dia, set()).add(hid)
                slots_resultado.append({
                    'id_turma': id_turma,
                    'id_disciplina': disc['id_disciplina'],
                    'id_professor': best_prof['id'],
                    'id_local': default_local,
                    'dia': dia,
                    'id_horario': hid,
                    'sigla': disc['sigla'],
                    'cor': disc['cor'],
                    'prof': (best_prof['nome'] or '').split()[0],
                    'nome_disciplina': disc['nome_disciplina'],
                })

            faltam = needed - len(chosen)
            if faltam > 0:
                nao_alocados.append({
                    'id_turma': id_turma,
                    'id_disciplina': disc['id_disciplina'],
                    'nome': disc['nome_disciplina'],
                    'faltam': faltam,
                    'motivo': 'sem slots disponíveis',
                })

    return slots_resultado, nao_alocados


def registrar(app):
    _garantir_tabela()

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

            # Disponibilidades
            cursor.execute("""
                SELECT id_professor, dia_semana, id_horario
                FROM disponibilidade_professor WHERE disponivel = 1
            """)
            disponibilidades = {}
            for d in cursor.fetchall():
                pid = str(d['id_professor'])
                disponibilidades.setdefault(pid, {}).setdefault(d['dia_semana'], []).append(d['id_horario'])

            # A sugestão representa o horário ideal completo — alocações existentes
            # NÃO bloqueiam a geração. Conflitos são resolvidos via SAVEPOINT ao aplicar.
            ocup_prof_base = {}
            ocup_turma_base = {}

            # Total de aulas esperadas para calcular cobertura
            total_esperado = sum(d['aulas_semanais'] for ds in grade_por_turma.values() for d in ds)

            # Gerar sugestões com seeds diferentes
            geradas = 0
            for i, seed in enumerate(_SEEDS[:num_sugestoes]):
                slots, nao_aloc = _gerar_sugestao(
                    grade_por_turma, disponibilidades, horario_ids, locais,
                    ocup_prof_base, ocup_turma_base, seed
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

        sem_disp = sum(
            1 for pid in set(
                str(p['id'])
                for ds in grade_por_turma.values()
                for disc in ds
                for p in disc['professores']
            )
            if pid not in disponibilidades
        )
        msg = f"{geradas} sugestão(ões) gerada(s) com sucesso!"
        if sem_disp:
            msg += (f" Atenção: {sem_disp} professor(es) sem disponibilidade cadastrada "
                    f"foram tratados como disponíveis em todos os horários.")
        flash(msg, 'sucesso')
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
