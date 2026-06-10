# Visão Geral do Projeto

Sistema de gerenciamento de horários escolares desenvolvido como **projeto de extensão universitária**.

## Identificação acadêmica

| Campo | Informação |
|---|---|
| **Autor** | João Pedro Noleto da Silva |
| **Instituição** | Unopar - Anhanguera |
| **Curso** | Engenharia de Software |
| **Atividade** | Projeto de Extensão |
| **Período** | 2° Período |
| **Repositório** | <https://github.com/Noletinho/projeto-extensao-horarios> |

Documento acadêmico completo (resumo, objetivos, metodologia, resultados): **[[../../DOCUMENTACAO_PROJETO|DOCUMENTACAO_PROJETO.md]]** (raiz do projeto).

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python + Flask (server-side rendering) |
| Banco de dados | MySQL via PyMySQL |
| Templates | Jinja2 (herdam de `base.html`) |
| Animações | Motion.dev v11.11.13 (CDN) |
| Servidor de produção | Gunicorn (WSGI multi-worker) |
| Hospedagem recomendada | Render.com (Web Service Free) + freedb.tech (MySQL gratuito) |

## Como rodar localmente

```bash
# 1. Cria o .env (copie de .env.example) com:
#    DATABASE_URL=mysql://root:senha@localhost:3306/escola_horarios
#    FLASK_DEBUG=1
#    DB_SEED_DEFAULT_USERS=true  (cria diretor/secretaria default)

pip install -r requirements.txt
python criar_banco.py   # apenas na primeira vez
python rotas.py         # http://127.0.0.1:5000
```

## Variáveis de ambiente

| Variável | Obrigatória | Descrição |
|----------|-------------|-----------|
| `DATABASE_URL` | ✅ | `mysql://user:pass@host:3306/db` |
| `SECRET_KEY` | ✅ em produção | Falha ao iniciar se ausente quando `FLASK_DEBUG=0` |
| `FLASK_DEBUG` | Não (default `0`) | `1` apenas em dev local |
| `DB_SEED_DEFAULT_USERS` | Não (default `false`) | Cria usuários `diretor@escola.com / diretor123` e `secretaria@escola.com / secretaria123`. **NUNCA em produção.** |
| `PORT` | Auto | Porta HTTP (Railway/Heroku preenchem) |

Detalhamento completo em `.env.example` (raiz do projeto).

## Estrutura de pastas

```
rotas.py                  ← ponto de entrada Flask
wsgi.py                   ← entrypoint para PythonAnywhere
Procfile                  ← entrypoint para Railway/Render (gunicorn)
blueprints/               ← um módulo por entidade
db.py                     ← conectar() com RealDictCursor
auth.py                   ← usuario_logado(), requer_login, requer_perfil
criar_banco.py            ← script de criação do schema
templates/                ← Jinja2, herdam de base.html
static/css/style.css      ← design system global
.env.example              ← documenta variáveis de ambiente
DEPLOY.md                 ← guia de deploy (PythonAnywhere/Railway/Render)
DOCUMENTACAO_PROJETO.md   ← documento acadêmico de extensão
```

## Segurança (hardening de produção)

- `SECRET_KEY` obrigatória — RuntimeError se ausente em produção
- `FLASK_DEBUG=0` por default — sem traceback exposto
- Cookies de sessão com `HttpOnly`, `SameSite=Lax`, `Secure` (HTTPS-only)
- Senhas hasheadas com `werkzeug.security` (PBKDF2 600k iterações + salt)
- Servidor de produção via Gunicorn (não o dev server do Flask)
- Usuários default só com `DB_SEED_DEFAULT_USERS=true` (off em produção)
- `.env` no `.gitignore` — credenciais nunca commitadas

## Links rápidos

- [[Banco de Dados]] — schema e modelo de dados
- [[Módulos (Blueprints)]] — rotas por entidade
- [[Alocação e Sugestões]] — algoritmo MCV de alocação automática
- [[Visual e Tema]] — design system Academic Authority
- [[Autenticação]] — perfis, primeiro_login, controle de acesso
- [[Deploy]] — PythonAnywhere (recomendado), Railway, Render
- [[Restrições e Especificações]] — regras de negócio
