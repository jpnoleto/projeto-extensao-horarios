# Autenticação

Arquivo: `auth.py`

## Perfis e permissões

| Funcionalidade | diretor | secretaria | professor |
|---|---|---|---|
| Login / logout | ✅ | ✅ | ✅ |
| Editar próprio perfil | ✅ | ✅ | ✅ |
| Ver relatório de horários | ✅ | ✅ | ✅ |
| CRUD de entidades | ✅ | ✅ | ❌ |
| Gerenciar usuários | ✅ | ❌ | ❌ |

## Funções de auth.py

| Função | Descrição |
|--------|-----------|
| `usuario_logado()` | Retorna `{id, nome, perfil, id_professor, primeiro_login}` ou `None` |
| `@requer_login` | Redireciona para `/login` se não autenticado |
| `@requer_perfil(*perfis)` | Verifica `session['usuario_perfil']` |

## Uso nos blueprints

```python
from auth import requer_perfil

@app.route('/rota')
@requer_perfil('diretor', 'secretaria')
def view():
    ...
```

- Todos os blueprints usam `@requer_perfil('diretor', 'secretaria')`
- `relatorio.py` usa apenas `@requer_login`
- `usuarios.py` usa `@requer_perfil('diretor')` em todas as rotas

## Context processor (rotas.py)

```python
@app.context_processor
def injetar_usuario():
    return dict(usuario_atual=auth.usuario_logado())
```

`usuario_atual` disponível em todos os templates via `base.html`.

## Primeiro login

Quando `usuario['primeiro_login'] == 1`: redirect automático para `/meu_perfil` após login.
Ao salvar nova senha, `primeiro_login` é zerado.

## Seeds padrão (criar_banco.py)

Criados apenas se a tabela `usuario` estiver vazia:

| Email | Senha | Perfil |
|-------|-------|--------|
| `diretor@escola.com` | `diretor123` | diretor |
| `secretaria@escola.com` | `secretaria123` | secretaria |

> ⚠️ Trocar as senhas após o primeiro login!

## Máscara de CPF

- **Diretor**: vê CPF formatado `XXX.XXX.XXX-XX` via filtro Jinja2 `{{ cpf|formatar_cpf }}`
- **Secretaria**: vê `***.***.***-**`
- Filtro definido em `rotas.py` com `@app.template_filter`
