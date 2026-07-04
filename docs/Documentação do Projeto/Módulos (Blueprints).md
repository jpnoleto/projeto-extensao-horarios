# Módulos (Blueprints)

Cada arquivo em `blueprints/` exporta `registrar(app)` que define rotas diretamente no app Flask.
Sem Blueprint class → `url_for('nome_funcao')` sem namespace.

## Lista de módulos

| Módulo | Responsabilidade |
|--------|------------------|
| `autenticacao.py` | `/` (dashboard com stats), `/login`, `/logout` |
| `professores.py` | CRUD de professor (nome, email, telefone, status) + paginação (20/pág) |
| `disciplinas.py` | CRUD de disciplina (nome, sigla, cor) + color picker + paginação |
| `turmas.py` | CRUD de turma (nome, série, turno como texto) |
| `horarios.py` | CRUD de horário de aula (com flag intervalo) |
| `disponibilidade.py` | Disponibilidade do professor (dia × horário) + grade visual |
| `alocacao.py` | **Montagem manual da grade por turma** — ver [[Montagem da Grade]] |
| `relatorio.py` | Relatório de horário **por turma** (1 página, impressão) |

> Módulos removidos na reformulação: `turnos.py`, `locais.py`, `professor_disciplina.py`,
> `grade_curricular.py`, `sugestao.py` e `usuarios.py`.

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
Exclusões de itens em uso capturam `pymysql.IntegrityError` e avisam por `flash`.

## Fluxos especiais

### Montagem da grade (`alocacao.py`)
Fluxo de dois passos, por turma:
`selecionar_turma_montagem` (`/montar_grade`) → `montar_grade` (`/montar_grade/<id_turma>`).

Grid interativo (dias × horários) com modal para escolher disciplina + professor, filtrando
professores por disponibilidade e ocupação. Detalhes em [[Montagem da Grade]].

### Relatório por turma (`relatorio.py`)
`selecionar_turma_relatorio` (`/relatorio`) → `relatorio_turma` (`/relatorio/<id_turma>`).

- `_montar_dados_relatorio(id_turma)` monta `grade[id_horario][dia] = {sigla, cor, nome_disciplina, professor_curto}`.
- Campos opcionais **nome da escola** e **data** via query string.
- Template `relatorio.html` standalone, A4 paisagem, 1 página, `print-color-adjust: exact`.

### Disponibilidade (`disponibilidade.py`)
Cadastro por professor (dia × horário) + grade visual consolidada (`grade_disponibilidades`).
Edição por dia via `editar_disponibilidade_dia`.
