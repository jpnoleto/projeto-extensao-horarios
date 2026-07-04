# Visão Geral do Projeto

Sistema de gerenciamento de horários escolares desenvolvido como **projeto de extensão universitária**.

Painel onde um **administrador** monta os horários **manualmente**: professores e disciplinas são
cadastrados independentemente e associados à mão em cada célula da grade da turma, respeitando a
disponibilidade dos professores. No fim, gera um **relatório de 1 página** por turma. Não há mais
alocação automática, sugestões, grade curricular, turnos/locais como tabelas nem perfis de usuário.

## Identificação acadêmica

| Campo | Informação |
|---|---|
| **Autor** | João Pedro Noleto da Silva |
| **Instituição** | Unopar - Anhanguera |
| **Curso** | Engenharia de Software |
| **Atividade** | Projeto de Extensão |
| **Período** | 2° Período |
| **Repositório** | <https://github.com/jpnoleto/projeto-extensao-horarios> |

Documento acadêmico completo (resumo, objetivos, metodologia, resultados): **[[../../DOCUMENTACAO_PROJETO|DOCUMENTACAO_PROJETO.md]]** (raiz do projeto).

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python + Flask (server-side rendering) |
| Banco de dados | MySQL via PyMySQL |
| Templates | Jinja2 (herdam de `base.html`) |
| Animações | Motion.dev v11.11.13 (CDN) |
| Servidor | Servidor de desenvolvimento do Flask (uso local) |
| Modo de entrega | Demonstração local + código aberto no GitHub (sem hospedagem online) |

## Como rodar localmente

```bash
# 1. Cria o .env (copie de .env.example) com:
#    DATABASE_URL=mysql://root:senha@localhost:3306/escola_horarios
#    FLASK_DEBUG=1
#    DB_SEED_DEFAULT_USERS=true  (cria o admin default)

pip install -r requirements.txt
python limpar_banco.py  # opcional: reset completo (DROP de todas as tabelas)
python criar_banco.py   # cria o schema (e o admin default se DB_SEED_DEFAULT_USERS=true)
python rotas.py         # http://127.0.0.1:5000
```

## Variáveis de ambiente

| Variável | Obrigatória | Descrição |
|----------|-------------|-----------|
| `DATABASE_URL` | ✅ | `mysql://user:pass@host:3306/db` |
| `SECRET_KEY` | ✅ em produção | Falha ao iniciar se ausente quando `FLASK_DEBUG=0` |
| `FLASK_DEBUG` | Não (default `0`) | `1` apenas em dev local |
| `DB_SEED_DEFAULT_USERS` | Não (default `false`) | Cria o admin `admin@escola.com / admin123` (só em dev) |

Detalhamento completo em `.env.example` (raiz do projeto).

## Estrutura de pastas

```
rotas.py                  ← ponto de entrada Flask
blueprints/               ← um módulo por área (cadastros, disponibilidade, montagem, relatório)
db.py                     ← conectar() com DictCursor
auth.py                   ← usuario_logado(), requer_login (requer_perfil é alias)
criar_banco.py            ← script de criação do schema
limpar_banco.py           ← reset completo (DROP de todas as tabelas)
templates/                ← Jinja2, herdam de base.html
static/css/style.css      ← design system global
.env.example              ← documenta variáveis de ambiente
DOCUMENTACAO_PROJETO.md   ← documento acadêmico de extensão
```

## Segurança

- `SECRET_KEY` obrigatória fora do modo debug — RuntimeError se ausente
- Cookies de sessão com `HttpOnly`, `SameSite=Lax`, `Secure` (fora do debug)
- Senhas hasheadas com `werkzeug.security` (PBKDF2 + salt)
- Admin default só com `DB_SEED_DEFAULT_USERS=true`
- `.env` no `.gitignore` — credenciais nunca commitadas

## Links rápidos

- [[Banco de Dados]] — schema e modelo de dados
- [[Módulos (Blueprints)]] — rotas por área
- [[Montagem da Grade]] — montagem manual do horário por turma
- [[Visual e Tema]] — design system Academic Authority
- [[Autenticação]] — login único de administrador
- [[Restrições e Especificações]] — regras de negócio
