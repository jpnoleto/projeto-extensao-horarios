# Visão Geral do Projeto

Sistema de gerenciamento de horários escolares desenvolvido como **projeto de extensão universitária**.

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python + Flask (server-side rendering) |
| Banco de dados | MySQL via PyMySQL |
| Templates | Jinja2 (herdam de `base.html`) |
| Animações | Motion.dev v11.11.13 (CDN) |
| Deploy | Railway (Procfile) |

## Como rodar localmente

```bash
export DATABASE_URL="mysql://usuario:senha@host:3306/banco"
pip install -r requirements.txt
python criar_banco.py   # apenas na primeira vez
python rotas.py         # http://127.0.0.1:5000
```

## Variáveis de ambiente

| Variável | Obrigatória | Descrição |
|----------|-------------|-----------|
| `DATABASE_URL` | ✅ | `mysql://user:pass@host:3306/db` |
| `SECRET_KEY` | Recomendada | Chave Flask para sessões |
| `PORT` | Deploy | Porta para Railway/Heroku |

## Estrutura de pastas

```
rotas.py              ← ponto de entrada Flask
blueprints/           ← um módulo por entidade
db.py                 ← conectar() com RealDictCursor
criar_banco.py        ← script de criação do schema
templates/            ← Jinja2, herdam de base.html
static/css/style.css  ← design system global
```

## Links rápidos

- [[Banco de Dados]] — schema e modelo de dados
- [[Módulos (Blueprints)]] — rotas por entidade
- [[Alocação e Sugestões]] — algoritmo de alocação automática
- [[Visual e Tema]] — design system Academic Authority
- [[Autenticação]] — perfis e controle de acesso
- [[Deploy]] — Railway
