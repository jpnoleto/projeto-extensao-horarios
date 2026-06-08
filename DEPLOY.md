# Deploy em Produção

Guia para subir o sistema em hospedagem cloud de forma segura.

## Pré-requisitos de Segurança

Antes de fazer qualquer deploy, certifique-se:

- [x] `.env` está no `.gitignore` (credenciais nunca commitadas)
- [x] `SECRET_KEY` é obrigatória em produção (erro se ausente quando `FLASK_DEBUG=0`)
- [x] `FLASK_DEBUG=0` (default) — não vaza tracebacks em erros
- [x] Cookies de sessão com `HttpOnly`, `SameSite=Lax`, `Secure` (em HTTPS)
- [x] Senhas hasheadas com `werkzeug.security`
- [x] Servidor de produção via `gunicorn` (não o dev server do Flask)
- [x] Usuários default só se `DB_SEED_DEFAULT_USERS=true` (off em produção)

## Plataformas Recomendadas

### Railway (recomendado)

1. Crie conta em <https://railway.app>
2. **New Project → Deploy from GitHub repo** → escolha `Noletinho/projeto-extensao-horarios`
3. Adicione plugin **MySQL**: **+ New → Database → MySQL**
4. Configure variáveis de ambiente do app (aba **Variables**):

   | Variável | Valor |
   |---|---|
   | `DATABASE_URL` | `${{ MySQL.DATABASE_URL }}` (referência automática) |
   | `SECRET_KEY` | (gere com `openssl rand -hex 32`) |
   | `FLASK_DEBUG` | `0` |

5. Após primeiro deploy, abra o **shell do Railway** e rode uma vez:
   ```bash
   python criar_banco.py
   ```
6. Crie o primeiro usuário diretor via console MySQL do Railway:
   ```sql
   INSERT INTO usuario (nome, email, senha_hash, perfil, primeiro_login)
   VALUES ('Seu Nome', 'voce@dominio.com', '<hash>', 'diretor', 1);
   ```
   O hash pode ser gerado localmente:
   ```bash
   python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('SUA_SENHA_FORTE'))"
   ```

### Render

1. Crie conta em <https://render.com>
2. **New + → Web Service** → conecte o repositório
3. Build: `pip install -r requirements.txt`
4. Start: (vem do `Procfile`)
5. Adicione MySQL externo (PlanetScale free ou Railway DB)
6. Variáveis de ambiente: mesmas do Railway

## Variáveis de Ambiente

| Variável | Obrigatória | Descrição |
|---|---|---|
| `DATABASE_URL` | **Sim** | `mysql://user:pass@host:3306/db` |
| `SECRET_KEY` | **Sim em produção** | 32 bytes aleatórios (`openssl rand -hex 32`) |
| `FLASK_DEBUG` | Não (default `0`) | `1` apenas em dev local |
| `DB_SEED_DEFAULT_USERS` | Não (default `false`) | **NUNCA habilite em produção** |
| `PORT` | Auto (Railway/Heroku) | Porta HTTP |

## Após o Deploy

1. **Acesse a URL** fornecida pelo Railway/Render
2. **Faça login** com o usuário diretor que você inseriu manualmente
3. **Confirme o HTTPS** está ativo (cadeado verde no browser)
4. **Crie os usuários de secretaria/professores** pelo `/usuarios`
5. **Configure horários, turnos, turmas, etc.** pelos respectivos cadastros

## Rollback

Se algo der errado:

```bash
git log --oneline
git revert <commit-hash>
git push origin master
```

Railway/Render fazem redeploy automaticamente no push.

## Monitoramento

- **Railway**: logs em tempo real na aba **Deployments → View Logs**
- **Render**: aba **Logs** do serviço
- Erros 500: confira logs do gunicorn (formato `--access-logfile - --error-logfile -` no Procfile envia para stdout/stderr)

## Restrições de Acesso (opcional, recomendado para escolas)

Para limitar acesso por IP, use Cloudflare Tunnel ou Railway IP whitelist (paid plan).

Para autenticação extra (2FA), considere integrar [Flask-Security-Too](https://flask-security-too.readthedocs.io/).
