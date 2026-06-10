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

### Render + freedb.tech (grátis para sempre — recomendado)

Combinação ideal para projetos de extensão com **uso esporádico**: Render hospeda o app Flask grátis e freedb.tech fornece um MySQL grátis (200 MB). Sem cartão de crédito em nenhum dos dois.

**Observação:** O Render Free Web Service **dorme após 15 minutos** sem requisições e demora ~30s para acordar. Para uso ocasional (apresentação à banca, demonstrações pontuais) isso é irrelevante.

#### Parte 1 — Criar o banco MySQL no freedb.tech (~5 min)

1. Acesse <https://freedb.tech/> → **Sign Up** (só email + senha, sem cartão)
2. Confirme o email
3. No painel → **Create New Database**
4. Anote os dados que aparecem:

   | Campo | Exemplo |
   |---|---|
   | Host | `sql.freedb.tech` |
   | Port | `3306` |
   | User | `freedb_seuuser` |
   | Password | (a que você definiu) |
   | Database name | `freedb_escola` |

#### Parte 2 — Criar conta no Render (~3 min)

1. Acesse <https://render.com> → **Get Started** (login com GitHub é o mais simples)
2. Autorize o Render a acessar seu repositório `Noletinho/projeto-extensao-horarios`

#### Parte 3 — Deploy do Web Service (~10 min)

1. No dashboard do Render → **New + → Web Service**
2. Selecione o repositório `projeto-extensao-horarios` → **Connect**
3. Configure:

   | Campo | Valor |
   |---|---|
   | Name | `projeto-extensao-horarios` (ou outro) |
   | Region | `Oregon (US West)` (mais rápido pro freedb.tech) |
   | Branch | `master` |
   | Runtime | `Python 3` |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | (deixe vazio — vem do `Procfile`) |
   | Instance Type | **Free** |

4. Em **Environment Variables** clique **Add Environment Variable** e adicione:

   | Key | Value |
   |---|---|
   | `DATABASE_URL` | `mysql://freedb_seuuser:SUASENHA@sql.freedb.tech:3306/freedb_escola` |
   | `SECRET_KEY` | (gere com `python -c "import secrets; print(secrets.token_hex(32))"`) |
   | `FLASK_DEBUG` | `0` |
   | `PYTHON_VERSION` | `3.11.9` |

5. Clique **Create Web Service** → o Render começa o primeiro build (~3 min)

#### Parte 4 — Inicializar o banco e criar diretor (~5 min)

1. Quando o deploy terminar, no dashboard do serviço → aba **Shell** (à esquerda)
2. Rode:

   ```bash
   python criar_banco.py
   ```

   Isso cria o schema no MySQL do freedb.tech (sem usuários default — `DB_SEED_DEFAULT_USERS` está off).

3. Gere o hash da senha do diretor:

   ```bash
   python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('SUA_SENHA_FORTE'))"
   ```

   Copie o hash inteiro (começa com `pbkdf2:sha256:...` ou `scrypt:...`).

4. Ainda no shell do Render, conecte no MySQL:

   ```bash
   python -c "
   from db import conectar
   with conectar() as c:
       cur = c.cursor()
       cur.execute('INSERT INTO usuario (nome, email, senha_hash, perfil, primeiro_login) VALUES (%s, %s, %s, %s, %s)',
                   ('Seu Nome', 'voce@dominio.com', 'COLE_O_HASH_AQUI', 'diretor', 1))
       c.commit()
       print('OK')
   "
   ```

5. Acesse a URL fornecida (algo como `https://projeto-extensao-horarios.onrender.com`) → login com email/senha do diretor criado.

#### Atualizar código depois

```bash
# Localmente:
git push origin master
```

O Render detecta o push e faz redeploy automaticamente (~3 min).

### Alternativas

#### Oracle Cloud Free Tier (forever free, mais poderoso)

Para uso intenso ou portfolio mais robusto: VM ARM com 24 GB RAM **forever free**, MySQL local, sem cold start. Setup ~1h de Linux. Requer cartão para verificação (não cobra).

#### Railway (pago — ~$5/mês de crédito de trial)

1. Crie conta em <https://railway.app>
2. **New Project → Deploy from GitHub repo** → escolha o repositório
3. **+ New → Database → MySQL**
4. Variáveis de ambiente:

   | Variável | Valor |
   |---|---|
   | `DATABASE_URL` | `${{ MySQL.DATABASE_URL }}` |
   | `SECRET_KEY` | (gere com `openssl rand -hex 32`) |
   | `FLASK_DEBUG` | `0` |

5. Após deploy, no shell: `python criar_banco.py`
6. Crie o diretor no MySQL console do Railway (mesmo SQL da seção freedb.tech)

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
