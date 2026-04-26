# Visual e Tema

Tema: **Academic Authority** — profissional claro, sem glassmorphism, sem fundo escuro.
Fonte: Inter via Google Fonts.

## Paleta de cores

| Variável CSS | Valor | Uso |
|---|---|---|
| `--cor-primaria` | `#0F4C81` | Azul institucional — headers, botões, links |
| `--cor-secundaria` | `#1a6fb5` | Hover |
| `--cor-acento` | `#B83222` | Crimson — ações de destaque |
| `--cor-fundo` | `#f4f6f9` | Background da página |
| `--cor-superficie` | `#ffffff` | Cards, tabelas |
| `--cor-superficie-alt` | `#f8fafc` | Hover de linhas, inputs |
| `--cor-borda` | `#e2e8f0` | Bordas leves |
| `--cor-borda-forte` | `#cbd5e1` | Bordas com contraste |
| `--cor-texto` | `#1a1c1e` | Texto principal |
| `--cor-texto-claro` | `#64748b` | Texto secundário |
| `--cor-sucesso` | `#16a34a` | Verde |
| `--cor-erro` | `#dc2626` | Vermelho |

## Badges e indicadores

| Tipo | Background | Border | Texto |
|------|-----------|--------|-------|
| Sucesso | `#f0fdf4` | `#bbf7d0` | `var(--cor-sucesso)` |
| Alerta | `#fef3c7` | `#fde68a` | `#92400e` |
| Erro | `#fef2f2` | `#fecaca` | `var(--cor-erro)` |
| Info | `#eff6ff` | `#bfdbfe` | `var(--cor-primaria)` |
| Neutro | `var(--cor-superficie-alt)` | `var(--cor-borda)` | `var(--cor-texto-claro)` |

## Templates especiais (não herdam base.html)

- `login.html` — fundo escuro estrelado
- `relatorio.html` — standalone de impressão, header crimson
- `meu_horario.html` — standalone, tema claro próprio

## Classes de componentes

| Classe | Uso |
|--------|-----|
| `.card` | Card com borda e sombra |
| `.cabecalho-pagina` | Flex row com botão ← e h1 |
| `.layout-duplo` | Grid 2 colunas: form + lista lateral |
| `.tabela-lateral` | Tabela compacta para coluna direita |
| `.btn-primario` / `.btn-secundario` / `.btn-perigo` / `.btn-acento` | Variantes de botão |
| `.badge-ativo` / `.badge-inativo` | Status inline |
| `.flex-linha` | Linha flexível com gap |
| `.form-grupo` | Espaçamento entre campos |
| `.paginacao` / `.pag-info` | Paginação (professores, disciplinas) |

## Regras fixas

- Cabeçalhos de tabela: `background: #f1f5f9` com `border: 1px solid var(--cor-borda)`
- Cards e tabelas: fundo `#ffffff`, sem `backdrop-filter`, sem `rgba()` em superfícies
- Botão Excluir: sempre `.btn-perigo` (o CSS usa `:not(.btn-perigo)` para especificidade)
- Link Editar: sempre termina com `#form-edicao` para scroll automático
- Formulário de edição inline: sempre `id="form-edicao"`

## Animações (Motion.dev)

CDN: `https://cdn.jsdelivr.net/npm/motion@11.11.13/+esm`

Aplicadas automaticamente em `base.html`:
- Header: slide de cima
- Linhas de tabela (`tbody tr`): entrada em cascata da esquerda
- Cards (`.card`): fade + slide de baixo
- Alertas: fade + scale

Cada template de listagem pode adicionar partículas flutuantes no hover via `spawnParticulas()`.
