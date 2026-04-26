# Módulos (Blueprints)

Cada arquivo em `blueprints/` exporta `registrar(app)` que define rotas diretamente no app Flask.
Sem Blueprint class → `url_for('nome_funcao')` sem namespace.

## Lista de módulos

| Módulo | Entidade | Arquivo |
|--------|----------|---------|
| `professores.py` | Professor | CRUD + paginação (20/pág) |
| `disciplinas.py` | Disciplina | CRUD + color picker + paginação |
| `turnos.py` | Turno | CRUD simples |
| `turmas.py` | Turma | CRUD |
| `locais.py` | Local | CRUD |
| `horarios.py` | Horário de Aula | CRUD + flag intervalo |
| `professor_disciplina.py` | Professor × Disciplina | Vínculo N:N |
| `disponibilidade.py` | Disponibilidade + Grade | Grade visual |
| `grade_curricular.py` | Grade Curricular | Fluxo 2 passos (turno → grade) |
| `alocacao.py` | Alocação de Aulas | Grade visual interativa |
| `relatorio.py` | Relatório + Meu Horário | Impressão + view professor |
| `sugestao.py` | Sugestões + Alocação Auto | Algoritmo greedy |

## Padrão de rotas CRUD

```
GET  /cadastrar_<entidade>        → formulário de criação
POST /salvar_<entidade>           → validação + INSERT
GET  /<entidades>                 → listagem
GET  /editar_<entidade>/<id>      → formulário inline (mesma página)
POST /atualizar_<entidade>/<id>   → UPDATE
POST /deletar_<entidade>/<id>     → DELETE
```

Erros de validação: `flash(msg, 'erro')` + redirect (nunca `erro=` para template).

## Fluxos especiais

### Dois passos (seleção de turno antes de listar)
- `grade_curricular` → `selecionar_turno_grades` → `listar_grade_curricular/<id_turno>`
- `alocacao` → `selecionar_turno_alocacoes` → `listar_alocacoes_turno/<id_turno>`
- `relatorio` → `selecionar_turno_relatorio` → `relatorio_horario_turno/<id_turno>`

### Alocação por turma (`alocacao.py`)
Rota: `GET /alocar_turma/<id_turma>`

O template recebe JSONs para a grade visual:
- `disponibilidades_json` — disponibilidade do professor selecionado
- `alocacoes_existentes_json` — slots já ocupados da turma
- `ocupacao_professor_json` — outros slots do professor
- `horarios_json`, `locais_json`

POST recebe `slots_json`: `[{dia, id_horario, id_local}, ...]`
Cada slot inserido via SAVEPOINT para tolerar conflito.

### Sugestões + Alocação Automática (`sugestao.py`)
Ver [[Alocação e Sugestões]].
