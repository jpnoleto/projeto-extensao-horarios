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

### PythonAnywhere (grátis para sempre — recomendado)

PythonAnywhere é o melhor para projetos de escola: MySQL incluso, não dorme, e é feito para Flask.

**Passo a passo:**

1. **Crie conta grátis** em <https://www.pythonanywhere.com/registration/register/beginner/>
   - Escolha um username (vai virar parte da URL: `seuuser.pythonanywhere.com`)

2. **Crie o banco MySQL** (aba **Databases**):
   - Defina uma senha forte para o usuário MySQL
   - Crie o banco: nome `seuuser$escola` (o prefixo `seuuser$` é obrigatório)
   - **Anote os dados** que aparecem:
     - Host: `seuuser.mysql.pythonanywhere-services.com`
     - User: `seuuser`
     - Banco: `seuuser$escola`

3. **Clone o repositório** (aba **Consoles → Bash**):
   ```bash
   git clone https://github.com/Noletinho/projeto-extensao-horarios.git
   cd projeto-extensao-horarios
   ```

4. **Crie o virtualenv** e instale dependências:
   ```bash
   mkvirtualenv --python=python3.10 mvenv
   pip install -r requirements.txt
   ```

5. **Crie o `.env`** no diretório do projeto:
   ```bash
   nano .env
   ```
   Cole (substitua `seuuser` e `SUASENHA` pelos seus valores):

   ```ini
   DATABASE_URL=mysql://seuuser:SUASENHA@seuuser.mysql.pythonanywhere-services.com:3306/seuuser$escola
   SECRET_KEY=cole-aqui-32-bytes-aleatorios
   FLASK_DEBUG=0
   ```
   Gere a `SECRET_KEY` com: `python -c "import secrets; print(secrets.token_hex(32))"`

6. **Crie o schema do banco**:
   ```bash
   python criar_banco.py
   ```

7. **Crie seu usuário diretor** (gere o hash da senha primeiro):
   ```bash
   python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('SUA_SENHA_FORTE'))"
   ```
   Copie o hash gerado. Abra a aba **Databases → Consoles → Start a console** e rode:
   ```sql
   USE seuuser$escola;
   INSERT INTO usuario (nome, email, senha_hash, perfil, primeiro_login)
   VALUES ('Seu Nome', 'voce@dominio.com', '<hash_copiado>', 'diretor', 1);
   ```

8. **Configure o web app** (aba **Web**):
   - **Add a new web app**
   - Escolha **Manual configuration** (NÃO use "Flask quickstart")
   - Selecione **Python 3.10**
   - Na seção **Code**:
     - **Source code**: `/home/seuuser/projeto-extensao-horarios`
     - **Working directory**: `/home/seuuser/projeto-extensao-horarios`
     - **WSGI configuration file**: clique no link e substitua todo o conteúdo por:

       ```python
       import sys
       sys.path.insert(0, '/home/seuuser/projeto-extensao-horarios')
       from dotenv import load_dotenv
       load_dotenv('/home/seuuser/projeto-extensao-horarios/.env')
       from rotas import app as application
       ```
   - Na seção **Virtualenv**: cole `/home/seuuser/.virtualenvs/mvenv`
   - Na seção **Static files**:
     - URL: `/static/`
     - Directory: `/home/seuuser/projeto-extensao-horarios/static`

9. **Recarregue** clicando no botão verde **Reload seuuser.pythonanywhere.com**

10. Acesse **<https://seuuser.pythonanywhere.com>** e faça login com o diretor criado

**Para atualizar o código depois:**

```bash
cd ~/projeto-extensao-horarios
git pull
# se mudou requirements.txt:
pip install -r requirements.txt
# Recarregar app via aba Web > botão Reload
```

### Railway (não-grátis — ~$5/mês)

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
