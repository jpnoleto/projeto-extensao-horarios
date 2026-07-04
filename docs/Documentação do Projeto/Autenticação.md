# Autenticação

Arquivo: `auth.py`

Login **único de administrador**. Não há mais perfis (diretor/secretaria/professor), gestão de
usuários, primeiro-login nem máscara de CPF — tudo removido na reformulação.

## Funções de auth.py

| Função | Descrição |
|--------|-----------|
| `usuario_logado()` | Retorna `{id, nome}` a partir da sessão, ou `None` |
| `@requer_login` | Redireciona para `/login` se não autenticado |
| `requer_perfil(*_)` | **Alias de `requer_login`** — só exige login; mantido para não reescrever decorators |

## Uso nos blueprints

Todas as rotas exigem apenas login:

```python
from auth import requer_login

@app.route('/rota')
@requer_login
def view():
    ...
```

Alguns módulos ainda importam `requer_perfil('...')` por herança — como agora é um alias de
`requer_login`, o efeito é idêntico (só exige estar logado).

## Context processor (rotas.py)

```python
@app.context_processor
def injetar_usuario():
    return dict(usuario_atual=auth.usuario_logado())
```

`usuario_atual` fica disponível em todos os templates via `base.html`.

## Login

`autenticacao.login()` valida email + senha contra a tabela `usuario` com
`werkzeug.security.check_password_hash` e grava `usuario_id` / `usuario_nome` na sessão.
Sem lógica de primeiro-login ou perfil.

## Seed padrão (criar_banco.py)

Criado apenas se a tabela `usuario` estiver vazia **e** `DB_SEED_DEFAULT_USERS=true`:

| Email | Senha |
|-------|-------|
| `admin@escola.com` | `admin123` |

> ⚠️ Só para desenvolvimento — trocar a senha antes de qualquer uso real. Em produção, criar o admin
> via INSERT manual com hash gerado por `generate_password_hash`.

## Segurança de sessão

Cookies com `HttpOnly`, `SameSite=Lax` e `Secure` (HTTPS-only fora do modo debug). `SECRET_KEY`
obrigatória em produção (RuntimeError se ausente com `FLASK_DEBUG=0`).
