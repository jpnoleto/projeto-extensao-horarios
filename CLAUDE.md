# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Comandos Essenciais

```bash
# Configurar variável de ambiente obrigatória antes de qualquer comando
export DATABASE_URL="mysql://usuario:senha@host:3306/banco"

# Inicializar o banco de dados (apenas uma vez ou para recriar)
python criar_banco.py

# Executar a aplicação
python rotas.py
# Acesso em: http://127.0.0.1:5000

# Instalar dependências
pip install -r requirements.txt
```

## Variáveis de Ambiente

| Variável | Obrigatória | Descrição |
|----------|-------------|-----------|
| `DATABASE_URL` | ✅ Sim | URL de conexão MySQL: `mysql://user:pass@host:3306/db` |
| `SECRET_KEY` | Recomendada | Chave Flask para sessões (padrão hardcoded em dev) |
| `PORT` | Deploy | Porta HTTP para Railway/Heroku (padrão: 5000) |

## Arquitetura

Sistema de gerenciamento de horários escolares — Flask monolítico com renderização server-side via Jinja2 e banco **MySQL**.

### Camadas

| Arquivo/Pasta | Responsabilidade |
|---------------|-----------------|
| `rotas.py` | Ponto de entrada: cria o app Flask, registra todos os módulos de rotas e define a rota raiz `/` |
| `blueprints/` | Um módulo por entidade; cada módulo exporta `registrar(app)` que define as rotas diretamente no app |
| `db.py` | Único utilitário: `conectar()` retorna `_Conn` wrapping PyMySQL com `RealDictCursor` |
| `criar_banco.py` | Script de criação do schema MySQL (executar uma vez) |
| `templates/` | Templates Jinja2; todos herdam de `base.html` exceto `relatorio.html` (layout de impressão) |
| `static/css/style.css` | Folha de estilos global com variáveis CSS e componentes |
| `Procfile` | Entry point para deploy (Railway/Heroku): `web: python rotas.py` |

### Módulos de Rotas (`blueprints/`)

Cada arquivo define uma função `registrar(app)` que registra rotas diretamente no app Flask — sem Blueprint class, mantendo `url_for('nome_funcao')` sem namespace.

| Módulo | Entidade |
|--------|----------|
| `professores.py` | Professor |
| `disciplinas.py` | Disciplina |
| `turnos.py` | Turno |
| `turmas.py` | Turma |
| `locais.py` | Local |
| `horarios.py` | Horário de Aula |
| `professor_disciplina.py` | Relação Professor × Disciplina |
| `disponibilidade.py` | Disponibilidade do Professor + Grade |
| `grade_curricular.py` | Grade Curricular (compartilhada por turno + série) |
| `alocacao.py` | Alocação de Aulas |
| `relatorio.py` | Relatório de Grade Horária + Horário do Professor (`/meu_horario`) |
| `sugestao.py` | Sugestões Automáticas de Grade (`/sugestoes`) |

### Modelo de Dados (ordem de dependência)

```
turno → turma
disciplina
professor → professor_disciplina ← disciplina
professor → disponibilidade_professor ← horario_aula
(turno + serie) + disciplina → grade_curricular   ← compartilhada, sem duplicação por turma
grade_curricular + turma + professor + local + horario_aula → alocacao
```

Entidades base (sem dependências): `professor`, `disciplina`, `turno`, `local`, `horario_aula`.

### Padrão de Rotas

Cada entidade segue o mesmo padrão CRUD em seu módulo:
- `GET /cadastrar_<entidade>` → formulário de criação
- `POST /salvar_<entidade>` → validação + inserção; erros via `flash()` + redirect
- `GET /<entidades>` → listagem
- `GET /editar_<entidade>/<id>` → formulário inline de edição (mesma página da listagem)
- `POST /atualizar_<entidade>/<id>` → atualização
- `POST /deletar_<entidade>/<id>` → exclusão

Entidades especiais com fluxo de dois passos (seleção de turno antes de listar): `alocacao`, `grade_curricular`, `relatorio`.

### Flash Messages

Erros e validações usam `flask.flash(mensagem, 'erro')` + redirect. O `base.html` renderiza automaticamente as mensagens com a classe `.alerta-<categoria>`. Não passar `erro=` para templates — usar sempre flash.

### Acesso ao Banco

Padrão obrigatório em todas as rotas:
```python
from db import conectar

with conectar() as conexao:
    cursor = conexao.cursor()
    cursor.execute("SELECT ... WHERE id = %s", (id,))  # SEMPRE %s, nunca ?
    conexao.commit()  # apenas em INSERT/UPDATE/DELETE
```

**Regras MySQL obrigatórias:**
- Placeholder: `%s` (nunca `?` — isso é SQLite)
- Erros de unicidade: capturar `pymysql.IntegrityError` (não `sqlite3.IntegrityError`)
- Tabela `local` é palavra reservada MySQL — usar backticks `` `local` `` em todas as queries
- COUNT queries: usar alias `SELECT COUNT(*) AS total` + `fetchone()['total']` (RealDictCursor não suporta índice numérico)
- Multi-insert com conflito tolerado: usar `SAVEPOINT` + `ROLLBACK TO SAVEPOINT` dentro do loop (MySQL aborta a transação inteira em qualquer erro sem rollback)
- Conexão fechada automaticamente pelo `_Conn.__exit__` ao sair do bloco `with`

## Personalização Visual

### Template Base

Todo template herda de `base.html`:
```html
{% extends "base.html" %}
{% block titulo %}Nome da Página{% endblock %}
{% block conteudo %}
  <!-- conteúdo aqui -->
{% endblock %}
```

Blocos disponíveis: `titulo`, `conteudo`, `estilos_extra` (CSS no `<head>`), `scripts_extra` (JS antes do `</body>`).

### Tema Atual — Academic Authority (Profissional Claro)

Design system baseado no projeto Stitch "Gestor de Horários Pro". Fundo claro, sem glassmorphism, sem imagem de fundo. Fonte Inter via Google Fonts.

| Variável | Valor | Uso |
|----------|-------|-----|
| `--cor-primaria` | `#0F4C81` | Azul institucional — headers, botões, links |
| `--cor-secundaria` | `#1a6fb5` | Azul hover |
| `--cor-acento` | `#B83222` | Crimson — ações de destaque |
| `--cor-fundo` | `#f4f6f9` | Background da página |
| `--cor-superficie` | `#ffffff` | Cards, tabelas |
| `--cor-superficie-alt` | `#f8fafc` | Hover de linhas, inputs |
| `--cor-borda` | `#e2e8f0` | Bordas leves |
| `--cor-borda-forte` | `#cbd5e1` | Bordas com mais contraste |
| `--cor-texto` | `#1a1c1e` | Texto principal (escuro) |
| `--cor-texto-claro` | `#64748b` | Texto secundário |
| `--cor-sucesso` | `#16a34a` | Verde |
| `--cor-erro` | `#dc2626` | Vermelho |

**Fonte:** `'Inter', 'Segoe UI', Arial, sans-serif` — carregada via `<link>` no `base.html`.

**Regra:** Cards e tabelas usam fundo branco (#ffffff) com borda `#e2e8f0` e sombra sutil. Sem `backdrop-filter`, sem `rgba()` para superfícies.

**Exceções que mantêm estilo próprio:**
- `login.html`: fundo escuro estrelado (campo estelar) para contraste com o card branco
- `relatorio.html`: standalone de impressão sem header — turno aparece como label discreta no canto superior-esquerdo da tabela (`.th-turno-label` com `colspan=3` cobrindo as colunas de dia/número/horário)
- `meu_horario.html`: standalone com tema claro próprio

Logo da escola: `static/img/logo.png` — exibida no header do `base.html` (o relatório de impressão não usa mais a logo para otimizar espaço vertical).

Paleta do relatório de impressão (cores da logo):
- Crimson escuro `#7B1818` → `--crim` (label do turno, coluna dia, separadores entre dias)
- Crimson médio `#9B2020` → `--crim2` (cabeçalho de turmas)
- Laranja `#C8601A` → `--laranja` (bordas da coluna do dia, filete nos separadores)

### Dashboard (index.html)

A rota `/` agora carrega estatísticas do banco e passa ao template:
- `total_professores`, `total_turmas`, `total_disciplinas`, `total_alocacoes`, `total_sugestoes`
- Exibidos em `.stat-card` no `.dashboard-stats`
- Módulos de navegação em `.dashboard-modulos` com `.modulo-card` + `.acao-rapida`

### Padrão de Cores para Badges e Indicadores

Usar sempre tons semânticos consistentes com o tema claro:

| Tipo | Background | Border | Texto |
|------|-----------|--------|-------|
| Sucesso / ok | `#f0fdf4` | `#bbf7d0` | `var(--cor-sucesso)` |
| Alerta / médio | `#fef3c7` | `#fde68a` | `#92400e` |
| Erro / baixo | `#fef2f2` | `#fecaca` | `var(--cor-erro)` |
| Primário / info | `#eff6ff` | `#bfdbfe` | `var(--cor-primaria)` |
| Neutro | `var(--cor-superficie-alt)` | `var(--cor-borda)` | `var(--cor-texto-claro)` |

**Regra para cabeçalhos de tabela:** usar `background: #f1f5f9` com `border: 1px solid var(--cor-borda)`. Nunca `rgba(106,110,121,.18)` (era da paleta do tema escuro).

### Classes de Componentes

- **`.card`** — card com borda e sombra (tema escuro)
- **`.cabecalho-pagina`** — flex row com botão ← e h1 no topo de cada página
- **`.layout-duplo`** — grid 2 colunas: formulário + lista lateral (colapsa em mobile)
- **`.tabela-lateral`** — tabela compacta para uso na coluna direita do layout duplo
- **`.seletor-cor`** + **`.btn-cor-preview`** + **`.swatch`** — color picker personalizado para disciplinas
- **`.btn-primario`** / **`.btn-secundario`** / **`.btn-perigo`** / **`.btn-acento`** — variantes de botão
- **`.alerta-erro`** / **`.alerta-sucesso`** — mensagens de feedback (semi-transparentes no dark)
- **`.badge-ativo`** / **`.badge-inativo`** — indicador de status inline
- **`.flex-linha`** — linha flexível com gap
- **`.form-grupo`** — espaçamento padrão entre campos

### Padrão de Navegação

- Todo template tem `<div class="cabecalho-pagina">` com botão ← no topo, antes do `h1`.
- Templates de cadastro usam `class="layout-duplo"` com o formulário à esquerda e a lista existente à direita.
- Para CPF: validação backend exige exatamente 11 dígitos (ou vazio). `cpf or None` para salvar NULL quando vazio.

### Seletor de Cores (Disciplinas)

`cadastro_disciplina.html` e o formulário de edição em `disciplinas.html` usam um color picker customizado:
- `.btn-cor-preview` — círculo clicável que abre o `<input type="color">` nativo
- `.swatch` — paleta de 16 cores predefinidas para disciplinas
- JS em `{% block scripts_extra %}` sincroniza cor entre clique nas swatches e o picker nativo

### Padrão dos Botões de Ação nas Tabelas

O `<td>` de ações **não recebe** `class="flex-linha"` diretamente. Envolva os botões num `<div>` interno:
```html
<td>
    <div class="flex-linha">
        <a href="{{ url_for('editar_X', id=item['id']) }}#form-edicao" class="btn btn-secundario">Editar</a>
        <form action="{{ url_for('deletar_X', id=item['id']) }}" method="POST">
            <button type="submit" class="btn-perigo" onclick="return confirm('...')">Excluir</button>
        </form>
    </div>
</td>
```

- O link "Editar" **sempre** termina com `#form-edicao` para scroll automático até o formulário.
- O formulário de edição inline **sempre** tem `id="form-edicao"` no `<div class="card mt-2">`.
- Botão de excluir **sempre** usa `.btn-perigo` — o CSS usa `:not(.btn-perigo)` para evitar conflito de especificidade.

### Relatório de Impressão

`templates/relatorio.html` é standalone (não herda `base.html`). Requisitos:
- `.celula` deve ter `print-color-adjust: exact` para preservar cores ao imprimir.
- A tabela deve usar `<thead>` para repetição de cabeçalho em múltiplas páginas.
- Botões de ação usam `class="no-print"` para sumir na impressão.

## Animações e Elementos Visuais (Motion.dev)

A aplicação usa **Motion.dev v11.11.13** via CDN ES module para animações. Não requer instalação — carregado em `base.html`.

### Animações Globais (`base.html`)

Aplicadas automaticamente em todas as páginas:
- Header: slide de cima (`y: [-10, 0]`)
- Linhas de tabela (`tbody tr`): entrada em cascata da esquerda (`stagger(0.04)`)
- Cards (`.card`): fade + slide de baixo (`stagger(0.07)`)
- Título da página (`.cabecalho-pagina h1`): slide da esquerda
- Alertas: fade + scale

CDN import:
```javascript
import { animate, stagger } from "https://cdn.jsdelivr.net/npm/motion@11.11.13/+esm";
```

### Fundo Decorativo

`<div id="fundo-escola">` em `base.html` (classe `no-print`) recebe ícones escolares gerados via JS puro que sobem lentamente com opacidade ~6%. Não interfere com impressão.

### Ícones e Partículas por Entidade

Cada template de listagem adiciona um `.icone-linha` na primeira célula e spawna **partículas flutuantes** ao hover (usando `animate()` do Motion). Timeout de 120ms evita spam.

| Template | Lógica do ícone |
|----------|-----------------|
| `disciplinas.html` | Mapeamento por nome/sigla → 17 categorias (📐 Mat, ⚡ Fís, ⚗️ Qui, 🧬 Bio…) + borda lateral com a cor da disciplina |
| `professores.html` | Sempre 👨‍🏫 + partículas acadêmicas |
| `turmas.html` | `data-turno` → ☀️ matutino / 🌅 vespertino / 🌙 noturno |
| `locais.html` | `data-tipo` → 🔬 lab / 💻 informática / 📚 biblioteca / ⚽ quadra / 🏫 padrão |
| `horarios_aula.html` | `data-inicio` → ícone por faixa de hora (manhã/tarde/noite) |
| `turnos.html` | `data-nome` → ☀️ / 🌅 / 🌙 por nome do turno |

### Classes CSS de Animação

- **`.fundo-escola`** — container fixo z-index:-1, não captura eventos
- **`.item-fundo`** — ícone flutuante; usa `@keyframes flutuar-fundo`
- **`.icone-linha`** — inline em `td:first-child`; escala 1.4× ao hover
- **`.particula-hover`** — `position:fixed`, z-index:9999, removida após animação

## Design Visual — Campo Estelar e Animações

### Fundo (`#fundo-estrelas`)

`#fundo-estrelas` em `base.html` gera um campo de estrelas suave via JS puro:
- Fundo preto `#000` fixo em toda a viewport
- N estrelas (`.estrela`) calculadas por área da tela: `Math.round(W*H/5800)`, min 60, max 220
- Cada estrela tem tamanho aleatório (0.8–2.4px), opacidade variável e animação `estrela-deriva`
- `@keyframes estrela-deriva`: drift suave com `--dx`/`--dy` (±9px) e fade de `--op-a` → `--op-b`
- Duração por estrela: 22–50 s com `animation-delay` negativo aleatório (sem "flash" inicial)

### Botões Flutuantes (`.btn-float`)

Usado na página inicial (`index.html`) para dar vida aos botões de cadastro:
- `.btn-float.btn-primario`: `@keyframes flutuar-suave` — sobe/desce 4px, 3.4 s
- `.btn-float.btn-secundario`: mesma animação, 3.8 s com delay 0.3 s
- `.btn-float.btn-acento`: `@keyframes flutuar-acento` (glow âmbar), 3.2 s
- `animation-play-state: paused` no hover — botão congela ao passar o mouse

### Seções do Index (`.secao-flutuante`)

`index.html` não usa `.card` — usa `.secao-flutuante` e `.secao-titulo` para layout limpo:
```html
<div class="secao-flutuante">
    <h2 class="secao-titulo">🗂️ Cadastros Base</h2>
    <div class="flex-linha mt-1">
        <a href="..." class="btn btn-primario btn-float">Cadastrar X</a>
    </div>
</div>
```

### Botões gerais — Efeito Shine

Todos os botões têm shine sweep no hover via `::after`:
- Gradiente diagonal `rgba(255,255,255,0.1)` percorre o botão (`left: -110% → 160%`)
- Transição `cubic-bezier(0.175, 0.885, 0.32, 1.275)` em `background-color` e `box-shadow`
- **Sem** `transform` no hover (mantém fluido, sem "pulo")

### Padrão para novos templates com ícones

```html
{% block scripts_extra %}
<script type="module">
import { animate } from "https://cdn.jsdelivr.net/npm/motion@11.11.13/+esm";

function spawnParticulas(particulas, rect) {
    for (let i = 0; i < 5; i++) {
        const el = document.createElement('span');
        el.textContent = particulas[Math.floor(Math.random() * particulas.length)];
        el.className = 'particula-hover';
        el.style.left = (rect.left + Math.random() * rect.width) + 'px';
        el.style.top  = (rect.top  + rect.height / 2) + 'px';
        el.style.fontSize = (12 + Math.random() * 8) + 'px';
        document.body.appendChild(el);
        animate(el,
            { y:[0, -(40 + Math.random() * 45)], opacity:[0.9, 0], scale:[1, 0.5] },
            { duration: 0.85 + Math.random() * 0.4, delay: i * 0.08, ease:'easeOut' }
        ).then(() => el.remove());
    }
}

document.querySelectorAll('tbody tr[data-X]').forEach(tr => {
    /* injetar icone-linha + registrar hover com spawnParticulas */
});
</script>
{% endblock %}
```

Adicionar `data-*` aos `<tr>` no Jinja2: `<tr data-X="{{ item['campo'] }}">`.

## Autenticação e Controle de Acesso

### Perfis e Permissões

| Funcionalidade | diretor | secretaria | professor |
|---|---|---|---|
| Login / logout | ✅ | ✅ | ✅ |
| Editar próprio perfil | ✅ | ✅ | ✅ |
| Ver relatório de horários | ✅ | ✅ | ✅ |
| Listar / CRUD entidades | ✅ | ✅ | ❌ |
| Gerenciar usuários | ✅ | ❌ | ❌ |

### Tabela `usuario`
```sql
CREATE TABLE IF NOT EXISTS usuario (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    perfil TEXT NOT NULL CHECK (perfil IN ('diretor', 'secretaria', 'professor')),
    id_professor INTEGER,
    primeiro_login INTEGER DEFAULT 1 CHECK (primeiro_login IN (0, 1)),
    ativo INTEGER DEFAULT 1 CHECK (ativo IN (0, 1)),
    FOREIGN KEY (id_professor) REFERENCES professor(id_professor)
);
```

### Arquivo `auth.py`
- `usuario_logado()` → dict `{id, nome, perfil, id_professor, primeiro_login}` ou `None`
- `requer_login` → decorator; redireciona para `/login` se não autenticado
- `requer_perfil(*perfis)` → decorator; verifica se `session['usuario_perfil']` está nos perfis permitidos
- Senhas: `werkzeug.security.generate_password_hash` / `check_password_hash`

### Decorators nos blueprints
```python
from auth import requer_perfil   # ou requer_login para relatorio

@app.route('/rota')
@requer_perfil('diretor', 'secretaria')  # todos blueprints exceto relatorio
def view():
    ...
```
- `relatorio.py` usa apenas `@requer_login`
- `blueprints/usuarios.py` usa `@requer_perfil('diretor')` em todas as rotas

### Context Processor (rotas.py)
```python
@app.context_processor
def injetar_usuario():
    return dict(usuario_atual=auth.usuario_logado())
```
`usuario_atual` disponível em todos os templates (usado em `base.html` para nav dinâmica).

### Primeiro Login
Quando `usuario['primeiro_login'] == 1`: redirect automático para `/meu_perfil` após login.
Ao salvar nova senha em `/meu_perfil`, campo `primeiro_login` é zerado.

### Seeds padrão (criar_banco.py)
Inseridos somente se tabela `usuario` estiver vazia:
- `diretor@escola.com` / `diretor123` → perfil diretor
- `secretaria@escola.com` / `secretaria123` → perfil secretaria

### Rotas de auth (rotas.py)
- `GET/POST /login` → login
- `POST /logout` → limpa sessão
- `GET/POST /meu_perfil` → editar próprio perfil (requer_login)
- `GET / ` → index (requer_login)

## Paginação nas Listagens

Implementada em `professores` e `disciplinas`: 20 itens por página, via `?pagina=N`.

- Rotas: `LIMIT %s OFFSET %s` com `COUNT(*) AS total` para calcular `total_paginas`
- Templates: bloco `{% if total_paginas is defined and total_paginas > 1 %}` com botões Anterior/Próxima
- CSS: `.paginacao` + `.pag-info` em `style.css`
- Modo edição (editar_professor / editar_disciplina) não pagina — exibe todos para o formulário inline

## Relatório de Grade Horária — Layout Visual

O relatório (`templates/relatorio.html`) usa layout de impressão otimizado para uma única página A4 landscape, com fundo branco e células coloridas por disciplina.

**Estrutura:**

- `relatorio.html` é standalone (não herda `base.html`), `@page size: 297mm 210mm`
- **Sem header com logo** (otimização de espaço vertical) — turno aparece como label discreta no canto superior-esquerdo via `<th colspan="3" class="th-turno-label">`
- **Linhas de intervalo removidas** — filtradas via `{% set horarios_aula = horarios | rejectattr('eh_intervalo') | list %}`; só horários de aula são renderizados
- **Separador entre dias** com 5px de altura (`.tr-separador`), crimson com filete laranja via box-shadow
- Células mostram `sigla` (12px bold) + `professor_curto` (10px) com `background-color` da disciplina
- `print-color-adjust: exact` garante que as cores aparecem ao imprimir/salvar PDF

**Margem 2mm uniforme em todos os lados:**

- `@page margin: 0` (Chrome headless ignora @page margin de forma confiável)
- `body { padding: 2mm; width: 297mm; height: 210mm; box-sizing: border-box }` — padding fixo FORA do escalonamento
- Zoom aplicado apenas no `.relatorio-wrapper` (não no `html`), com largura/altura infladas (`293/zoom mm` e `206/zoom mm`) para preencher a área útil após o escalonamento
- `.relatorio-wrapper table { height: 100%; width: 100% }` — tabela estica para preencher o wrapper, eliminando espaço vazio no rodapé

**Garantia de 1 página independente do número de turmas:**

- Fórmula Jinja `_th = 45 + (_nd - 1) * 5 + _nd * _na * 24` calcula altura estimada usando dias e aulas (NÃO turmas)
- `_rz = 900 / _th` capado em 1.0 → zoom adapta dinamicamente
- `white-space: nowrap + text-overflow: ellipsis` em `.sigla`, `.prof`, `.th-turma`, `.th-turno-label`, `.td-hora`, `.td-num` — previne wrap em colunas estreitas (que causaria células altas e overflow para 2 páginas)
- `table-layout: fixed` + `<colgroup>` com `col.col-dia` (12px), `col.col-num` (14px), `col.col-hora` (30px) — as N colunas de turma dividem o restante automaticamente
- Testado com 5, 13, 20 e 30 turmas — todos resultam em 1 página

**Tela de seleção e parâmetros (preservados):**

- `selecionar_turno_relatorio.html` tem campos opcionais: **nome da escola** e **data do relatório** — enviados via GET para a rota
- Parâmetros `nome_escola` e `data_rel` são query strings em `/relatorio_horario_turno/<id_turno>`
- `_montar_dados_relatorio` inclui `professor_curto` (primeiro nome) além de `professor` (nome completo)

## Sugestões de Alocação

- Renomeado de "Sugestões de Grade" para "Sugestões de Alocação" (a grade já existe; o que se sugere é a distribuição de aulas nos horários)
- Tabela `sugestao_grade` criada em `criar_banco.py` (não mais em `sugestao.py`)
- Algoritmo: pré-atribui professor fixo por demand (load balancing) + MCV (Most Constrained Variable)
- MCV: a cada iteração agenda a demanda com menos slots disponíveis primeiro — evita deadlocks greedy com zero folga (30 aulas = 30 slots)
- Passa `{}` como disponibilidades → horário ideal irrestrito; conflitos reais só são detectados ao aplicar
- Geração por turno completo: todas as turmas de todas as séries do turno
- Rotas: `GET /sugestoes`, `POST /gerar_sugestoes`, `GET /sugestao/<id>`, `POST /sugestao/<id>/excluir`, `POST /sugestao/<id>/aplicar`
- Aplicar tudo ou por turma individual; editar via `alocar_turma_completa?sugestao_id=X`
- `alocar_turma.html` inicializa `pendentes` com `sugestaoPendentes` quando `sugestao_id` é passado

## Alocação Automática

- Rotas em `blueprints/sugestao.py`: `GET /alocacao_automatica` e `POST /executar_alocacao_automatica`
- Lê a grade curricular do turno selecionado e chama `_gerar_sugestao(..., seed=42)` com disponibilidades vazias
- Insere slots diretamente na tabela `alocacao` via SAVEPOINT (conflitos com alocações existentes são ignorados)
- Template: `templates/alocacao_automatica.html` — seleção de turno com radio buttons + confirmação
- Link no dashboard (index.html) no módulo Planejamento, acima de "Alocar por Turma"
- Redireciona para `listar_alocacoes_turno` após execução com flash de resultado (inseridos / conflitos / sem slots)

## Exportação de Relatório em PDF

Rota `GET /baixar_relatorio_pdf/<id_turno>` redireciona para o relatório com instrução de usar a impressão do navegador (Ctrl+P → Salvar como PDF). WeasyPrint foi removido — não funciona no Windows sem GTK runtime.

## Máscara de CPF

- **Diretor**: vê CPF formatado (`XXX.XXX.XXX-XX`) via filtro Jinja2 `{{ cpf|formatar_cpf }}`
- **Secretaria**: vê `***.***.***-**` (mascarado)
- Filtro `formatar_cpf` definido em `rotas.py` com `@app.template_filter`
- Rotas `listar_professores` e `editar_professor` passam `pode_ver_cpf` (bool) ao template
- No formulário de edição: secretaria vê campo desabilitado + `<input type="hidden">` para preservar o valor

## Intervalo nos Horários

- Coluna `eh_intervalo INTEGER DEFAULT 0` incluída diretamente na tabela `horario_aula` em `criar_banco.py`
- Formulário de cadastro/edição tem checkbox "É um intervalo?" — quando marcado, oculta campos de hora via JS
- Relatório: horários com `eh_intervalo=1` renderizam linha `<td colspan="dias×turmas">— INTERVALO —</td>` em vez de células por turma
- Horários de intervalo não aparecem no select de alocação

## Alocação — Grade Visual de Disponibilidade

O formulário `cadastro_alocacao.html` usa uma grade visual interativa gerada por JavaScript:

**Fluxo:**
1. Usuário seleciona Turma + Disciplina + Professor
2. A grade aparece automaticamente: linhas = horários, colunas = dias da semana
3. Cada célula mostra o status:
   - Verde: professor disponível e turma livre → checkbox + seletor de local
   - Âmbar: professor disponível mas turma já tem outra alocação nesse slot → aviso + permite alocar
   - Vermelho: professor já está alocado nesse slot (outro lugar) → bloqueado
   - Cinza: professor sem disponibilidade cadastrada → bloqueado
4. Cada célula selecionada tem seu **próprio seletor de local** — permite locais diferentes por dia (ex: Ed. Física na Quadra na segunda e Sala na quarta)
5. Se houver apenas 1 local cadastrado, é pré-selecionado automaticamente

**Backend (`blueprints/alocacao.py`):**
- Passa ao template: `disponibilidades_json`, `alocacoes_existentes_json`, `ocupacao_professor_json`, `horarios_json`, `locais_json`
- POST recebe `slots_json`: array JSON `[{dia, id_horario, id_local}, ...]`
- Insere uma alocação por slot, usando SAVEPOINT para conflitos individuais

## Horário do Professor (view-only)

- Rota `GET /meu_horario` em `blueprints/relatorio.py`, decorator `@requer_login`
- Apenas acessível para perfil `professor` com `id_professor` vinculado; outros perfis são redirecionados
- Função helper `_montar_dados_professor(id_professor)` retorna grade filtrada por professor
- Template standalone `templates/meu_horario.html` (não herda `base.html`), com botão imprimir
- Link "Meu Horário" adicionado na nav do `base.html` para perfil professor

## Entrega e Deploy

**Modo padrão: demonstração local + código aberto no GitHub.**

Para o uso previsto (projeto de extensão, apresentação à escola parceira e à banca), **não há necessidade de hospedagem online**. O sistema roda localmente no notebook (`python rotas.py` → <http://127.0.0.1:5000>) e é demonstrado presencialmente. O código-fonte fica publicado em <https://github.com/jpnoleto/projeto-extensao-horarios> sob licença aberta, com `DEPLOY.md` documentando instalação para que qualquer escola interessada possa adotá-lo.

**Por que não hospedar online por default:** durante o desenvolvimento, sucessivas plataformas mudaram suas políticas — Railway encerrou o plano gratuito permanente, PythonAnywhere passou a cobrar pelo MySQL e freedb.tech auto-exclui o banco após 24h ociosas. Manter o discurso de "demonstração local + open source" elimina dependência de provedor externo e preserva a confiabilidade da entrega.

### Hospedagem online (opcional, para uso permanente pela escola)

Caso a escola decida operar o sistema em produção, opções avaliadas:

| Plataforma | Status | Observação |
|---|---|---|
| **Oracle Cloud Free Tier** | ✅ Forever free | VM ARM 24 GB RAM. MySQL local. Setup Linux ~1h. Cartão pra verificação. |
| **TiDB Cloud Serverless + Render** | ✅ Forever free | TiDB: 5 GB MySQL-compatível. Render Free hospeda Flask (dorme após 15 min). Cartão pra verificação. |
| Render + freedb.tech | ⚠️ DB auto-exclui em 24h ociosas | Só viável com uso diário |
| PythonAnywhere | ⚠️ MySQL exige plano pago | Mudou em 2026 |
| Railway | 🔴 Sem free tier permanente | Crédito de avaliação apenas |

Passo a passo detalhado em `DEPLOY.md` na raiz.

**Entrypoints coexistentes:**

- `Procfile` (`web: gunicorn rotas:app ...`) — usado por Render/Railway
- `wsgi.py` — entrypoint WSGI alternativo (servidores que procuram `application`)

## Contexto do Projeto

Projeto de extensão universitária. Interface totalmente em Português.
