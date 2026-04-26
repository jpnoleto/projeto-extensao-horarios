# Alocação e Sugestões

Módulo: `blueprints/sugestao.py`

## Alocação Automática

Cria alocações diretamente na tabela `alocacao` a partir da grade curricular.

**Rotas:**
- `GET /alocacao_automatica` → seleção de turno
- `POST /executar_alocacao_automatica` → executa e redireciona para as alocações

**Fluxo:**
1. Carrega grade curricular do turno (todas as séries)
2. Chama `_gerar_sugestao(..., seed=42)` sem restrição de disponibilidade
3. Insere cada slot na tabela `alocacao` via SAVEPOINT
4. Conflitos com alocações existentes são ignorados silenciosamente
5. Flash com resultado: inseridos / conflitos / disciplinas sem slots

**Template:** `templates/alocacao_automatica.html`
**Link no dashboard:** Módulo Planejamento → "⚡ Alocação Automática por Turno"

---

## Sugestões de Alocação

Gera sugestões salvas em `sugestao_grade` (até 3 por geração, seeds diferentes).
Permite revisar antes de aplicar.

**Rotas:**
- `GET /sugestoes` → listar sugestões salvas
- `POST /gerar_sugestoes` → gera novas (1–3 variações)
- `GET /sugestao/<id>` → visualizar grade da sugestão
- `POST /sugestao/<id>/aplicar` → inserir na `alocacao` (tudo ou por turma)
- `POST /sugestao/<id>/excluir` → remover

---

## Algoritmo `_gerar_sugestao`

```python
_gerar_sugestao(grade_por_turma, disponibilidades, horario_ids, locais,
                ocup_prof_base, ocup_turma_base, seed)
```

Chamado com `disponibilidades = {}` → sem restrição de disponibilidade do professor.
As únicas restrições são conflitos de horário (professor ou turma já ocupados no mesmo slot).

### Passo 1 — Ordenação por restrição
Disciplinas com **menos professores habilitados** são processadas primeiro.
Garante que Ed. Física (professor único) reserve seu professor antes de ser monopolizado.

### Passo 2 — Pré-atribuição de professor fixo
Para cada demand `(turma, disciplina)`:
```python
best_prof = max(professores,
    key=lambda p: capacidade(p) - carga_já_atribuída(p))
```
Professor é fixo para toda a alocação — evita troca entre rodadas que causava fragmentação.

### Passo 3 — Round-robin com professor fixo
- 1 slot por demand por rodada
- Prefere dia ainda não usado pela disciplina nessa turma
- Continua até todos os demands estarem satisfeitos ou sem slots disponíveis

### Saída
```python
slots = [
    {id_turma, id_disciplina, id_professor, id_local,
     dia, id_horario, sigla, cor, prof, nome_disciplina},
    ...
]
nao_alocados = [
    {id_turma, id_disciplina, nome, faltam, motivo},
    ...
]
```

---

## Diagnóstico: disciplinas sem slots

Se `total_aulas_turma > horarios_disponiveis × 5_dias`, o algoritmo nunca consegue alocar tudo.
A rota `gerar_sugestoes` emite um flash de aviso nesse caso.

Solução: reduzir `aulas_semanais` na grade curricular ou cadastrar mais horários.
