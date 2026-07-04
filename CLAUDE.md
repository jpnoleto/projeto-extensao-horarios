# CLAUDE.md

Este arquivo orienta o Claude Code (claude.ai/code) ao trabalhar neste repositório.

## Visão Geral

Painel web para o **administrador montar horários escolares manualmente**. Fluxo linear:
cadastrar professores → cadastrar disciplinas → cadastrar turmas → cadastrar horários de aula →
cadastrar disponibilidades dos professores → **montar a grade de cada turma à mão** →
**imprimir o relatório de 1 página**.

Professores e disciplinas são cadastrados de forma independente; a associação (qual professor dá
qual disciplina, em qual dia/horário) é feita manualmente pelo administrador na montagem da grade,
respeitando a disponibilidade cadastrada. Flask monolítico com Jinja2 server-side e banco **MySQL**.

Interface totalmente em Português. Projeto de extensão universitária.

## Comandos Essenciais

```bash
# Variável de ambiente obrigatória (ou usar .env)
export DATABASE_URL="mysql://usuario:senha@host:3306/banco"

# Zerar o banco (DROP de todas as tabelas) — reset completo
python limpar_banco.py

# Criar o schema do zero (+ admin default se DB_SEED_DEFAULT_USERS=true)
python criar_banco.py

# Rodar a aplicação → http://127.0.0.1:5000
python rotas.py

pip install -r requirements.txt
```

## Variáveis de Ambiente

| Variável | Obrigatória | Descrição |
|----------|-------------|-----------|
| `DATABASE_URL` | ✅ | `mysql://user:pass@host:3306/db` |
| `SECRET_KEY` | Recomendada | Chave Flask de sessão (fallback inseguro só em `FLASK_DEBUG`) |
| `DB_SEED_DEFAULT_USERS` | Não | Se `true`, cria o admin default (`admin@escola.com` / `admin123`) |
| `FLASK_DEBUG` | Não | `true` liga debug e reload de templates |

## Arquitetura

| Arquivo/Pasta | Responsabilidade |
|---------------|-----------------|
| `rotas.py` | Cria o app Flask, registra os módulos de rotas e o context processor `injetar_usuario` |
| `blueprints/` | Um módulo por área; cada um exporta `registrar(app)` que define as rotas diretamente no app (sem classe Blueprint) |
| `db.py` | `conectar()` → `_Conn` envolvendo PyMySQL com `DictCursor`; fecha no `__exit__` |
| `auth.py` | `usuario_logado()`, decorator `requer_login`; `requer_perfil(*_)` é apenas um alias de `requer_login` |
| `criar_banco.py` | Cria o schema MySQL (rodar uma vez) |
| `limpar_banco.py` | Reset completo: DROP de todas as tabelas (atuais + antigas) |
| `templates/` | Jinja2; herdam de `base.html` exceto `relatorio.html` (impressão standalone) e `login.html` |
| `static/css/style.css` | Folha de estilos global |

### Módulos de Rotas (`blueprints/`)

| Módulo | Conteúdo |
|--------|----------|
| `autenticacao.py` | `/` (dashboard com stats), `/login`, `/logout` |
| `professores.py` | CRUD de professor (nome, email, telefone, status) + paginação |
| `disciplinas.py` | CRUD de disciplina (nome, sigla, cor) + color picker + paginação |
| `turmas.py` | CRUD de turma (nome, série, turno como texto) |
| `horarios.py` | CRUD de horário de aula (com flag `eh_intervalo`) |
| `disponibilidade.py` | Disponibilidade do professor (dia × horário) + grade visual |
| `alocacao.py` | **Montagem manual da grade por turma** (núcleo do sistema) |
| `relatorio.py` | Relatório de horário **por turma** (1 página, impressão) |

## Modelo de Dados

Tabelas (todas em `criar_banco.py`):

```
usuario(id_usuario, nome, email UNIQUE, senha_hash)          -- login único de admin
professor(id_professor, nome, email, telefone, status)
disciplina(id_disciplina, nome UNIQUE, sigla UNIQUE, cor)
turma(id_turma, nome, serie, turno)  UNIQUE(nome, serie, turno)   -- turno é TEXTO (Matutino/Vespertino/Noturno)
horario_aula(id_horario, hora_inicio, hora_fim, eh_intervalo)
disponibilidade_professor(id_disponibilidade, id_professor, dia_semana, id_horario, disponivel)
    UNIQUE(id_professor, dia_semana, id_horario)
alocacao(id_alocacao, id_turma, id_disciplina, id_professor, dia_semana, id_horario)
    UNIQUE(id_professor, dia_semana, id_horario)   -- professor não em 2 lugares ao mesmo tempo
    UNIQUE(id_turma, dia_semana, id_horario)       -- turma tem 1 aula por slot
```

`dia_semana` ∈ {segunda, terca, quarta, quinta, sexta}. **Não há** tabelas de turno, local,
professor_disciplina, grade_curricular nem sugestões — foram removidas na reformulação para
manter só o essencial da montagem manual.

## Montagem Manual da Grade (núcleo)

`blueprints/alocacao.py` + `templates/montar_grade.html`:

- `GET /montar_grade` → lista turmas (com contagem de aulas) para escolher uma.
- `GET /montar_grade/<id_turma>` → grade visual: linhas = horários (sem intervalo), colunas = seg–sex.
  Passa ao template como JSON: `disciplinas_json`, `professores_json`,
  `disponibilidades_json` (`{pid:{dia:[id_horario]}}`), `ocupacao_json` (professores já alocados em
  qualquer turma naquele slot).
- Célula vazia → botão `+` abre um **modal** com `<select>` de disciplina (todas) e `<select>` de
  professor **filtrado por JS**: só professores com disponibilidade naquele dia+horário e não ocupados.
  O modal faz `POST /montar_grade/<id_turma>/alocar` (`{id_disciplina, id_professor, dia, id_horario}`).
- Célula preenchida → mostra sigla + primeiro nome do professor (fundo com a cor da disciplina) e um
  botão `✕` que faz `POST /montar_grade/<id_turma>/remover/<id_alocacao>`.
- `POST /montar_grade/<id_turma>/limpar` → apaga toda a grade da turma.
- Conflitos são barrados pelos `UNIQUE` da `alocacao` — o backend captura `pymysql.IntegrityError`
  e emite `flash` explicando (professor ocupado / turma ocupada). O filtro JS é só a camada de UX.

## Relatório (1 página, por turma)

`blueprints/relatorio.py` + `templates/relatorio.html` (standalone, não herda `base.html`):

- `GET /relatorio` → escolhe a turma; campos opcionais **nome da escola** e **data** (via query string).
- `GET /relatorio/<id_turma>?nome_escola=...&data_rel=...` → grade linhas = horários × colunas = seg–sex.
- `_montar_dados_relatorio(id_turma)` monta `grade[id_horario][dia] = {sigla, cor, nome_disciplina, professor_curto}`.
- Layout A4 landscape, células coloridas por disciplina, `print-color-adjust: exact`, botão Imprimir
  (Ctrl+P → Salvar como PDF). Linhas de intervalo (`eh_intervalo=1`) viram faixa "— INTERVALO —".

## Autenticação

Login único de administrador. `auth.usuario_logado()` retorna `{id, nome}` a partir da sessão.
Todas as rotas usam `@requer_login` (o antigo `requer_perfil(*perfis)` foi mantido como alias que
só exige login, para não reescrever decorators). `usuario_atual` fica disponível nos templates via
context processor. Senhas com `werkzeug.security` (`generate_password_hash` / `check_password_hash`).

Seed default (só se tabela `usuario` vazia **e** `DB_SEED_DEFAULT_USERS=true`):
`admin@escola.com` / `admin123`.

## Padrões de Código

### Acesso ao Banco (MySQL / PyMySQL)
```python
from db import conectar
with conectar() as conexao:
    cursor = conexao.cursor()
    cursor.execute("SELECT ... WHERE id = %s", (id,))   # SEMPRE %s, nunca ?
    conexao.commit()                                    # só em INSERT/UPDATE/DELETE
```
- Placeholder `%s`; erros de unicidade/FK → `pymysql.IntegrityError`.
- COUNT: `SELECT COUNT(*) AS total` + `fetchone()['total']` (DictCursor não indexa por número).
- Exclusões de professor/disciplina/turma/horário capturam `IntegrityError` e emitem `flash`
  amigável quando há dependências (não estouram 500).

### Rotas CRUD
`GET /cadastrar_<x>` (form) · `POST /salvar_<x>` · `GET /<x>s` (lista) ·
`GET /editar_<x>/<id>` (form inline na própria lista) · `POST /atualizar_<x>/<id>` · `POST /deletar_<x>/<id>`.

### Flash Messages
Erros e validações via `flask.flash(msg, 'erro')` + redirect (nunca `erro=` no template).
`base.html` renderiza `.alerta-<categoria>` automaticamente.

## Personalização Visual

Todo template (exceto `relatorio.html` e `login.html`) herda de `base.html`:
```html
{% extends "base.html" %}
{% block titulo %}...{% endblock %}
{% block conteudo %}...{% endblock %}
```
Blocos: `titulo`, `conteudo`, `estilos_extra`, `scripts_extra`.

### Tema — Academic Authority (claro, profissional)

Fundo claro, sem glassmorphism escuro. Fonte Inter (Google Fonts). Variáveis CSS principais:
`--cor-primaria #0F4C81`, `--cor-acento #B83222`, `--cor-fundo #f4f6f9`, `--cor-superficie #ffffff`,
`--cor-borda #e2e8f0`, `--cor-texto #1a1c1e`, `--cor-sucesso #16a34a`, `--cor-erro #dc2626`.

Cabeçalhos de tabela: `background:#f1f5f9` + `border:1px solid var(--cor-borda)`.
Cards/tabelas: fundo branco com borda leve e sombra sutil.

### Componentes-chave
`.cabecalho-pagina` (botão ← + h1) · `.layout-duplo` (form + lista lateral) · `.card` ·
`.btn-primario`/`.btn-secundario`/`.btn-perigo` · `.badge-ativo`/`.badge-inativo` ·
`.seletor-cor`/`.swatch` (color picker de disciplina) · `.dashboard-stats`/`.stat-card` ·
`.dashboard-modulos`/`.modulo-card`/`.acao-rapida` (dashboard).

### Botões de ação em tabelas
Envolver os botões num `<div class="flex-linha">`. Link "Editar" termina em `#form-edicao`
(scroll até o form inline, que tem `id="form-edicao"`). Excluir usa `.btn-perigo` com `confirm()`.

### Animações (Motion.dev via CDN)
`base.html` importa `motion@11.11.13/+esm` e anima header, cards, linhas de tabela e alertas na
entrada. Novos templates com listas ganham a cascata de `tbody tr` automaticamente.

## Entrega

**Demonstração local + código aberto.** O sistema roda localmente (`python rotas.py` →
<http://127.0.0.1:5000>) e é apresentado presencialmente; não há hospedagem online nem arquivos de
deploy (Procfile/wsgi/gunicorn foram removidos). O código-fonte fica publicado no GitHub sob licença
aberta para quem quiser instalar localmente.
