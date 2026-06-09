# Deploy

Guia resumido. Versão completa em `DEPLOY.md` (raiz do projeto).

## Opções de hospedagem

| Plataforma | Custo | MySQL | Cold start | Recomendação |
|---|---|---|---|---|
| **PythonAnywhere** | 🟢 Grátis pra sempre | ✅ Incluso (512 MB) | ❌ Sempre online | ⭐ Padrão deste projeto |
| Render | 🟡 Grátis (web) | ❌ DB externo | ⚠️ Dorme em 15 min | Alternativa |
| Fly.io | 🟡 Grátis (3 VMs) | ❌ DB externo | ✅ Não dorme | Mais complexo |
| Railway | ❌ ~$5/mês (sem free tier) | ✅ Plugin | ✅ Não dorme | Pago |

## PythonAnywhere (recomendado)

1. Criar conta em <https://www.pythonanywhere.com>
2. **Databases** → criar MySQL `seuuser$escola` com senha forte
3. **Consoles → Bash**:
   ```bash
   git clone https://github.com/Noletinho/projeto-extensao-horarios.git
   cd projeto-extensao-horarios
   mkvirtualenv --python=python3.10 mvenv
   pip install -r requirements.txt
   ```
4. Criar `.env` no projeto:
   ```ini
   DATABASE_URL=mysql://seuuser:SENHA@seuuser.mysql.pythonanywhere-services.com:3306/seuuser$escola
   SECRET_KEY=<gere com python -c "import secrets; print(secrets.token_hex(32))">
   FLASK_DEBUG=0
   ```
5. `python criar_banco.py` (cria schema sem usuários default)
6. Inserir usuário diretor manualmente (instruções no `DEPLOY.md`)
7. **Web → Add a new web app → Manual configuration → Python 3.10**, configurar paths conforme `DEPLOY.md`
8. Botão verde **Reload**

## Entrypoints

- `wsgi.py` — usado pelo PythonAnywhere (uWSGI procura `application`)
- `Procfile` (`web: gunicorn rotas:app --workers 2 --timeout 120 ...`) — usado por Railway/Render

Os dois coexistem sem conflito; cada plataforma usa o que precisa.

## Variáveis de ambiente em produção

| Variável | Valor |
|---|---|
| `DATABASE_URL` | URL MySQL completa |
| `SECRET_KEY` | 32 bytes aleatórios (`openssl rand -hex 32`) |
| `FLASK_DEBUG` | `0` (sempre em produção) |
| `DB_SEED_DEFAULT_USERS` | **NÃO definir** (default false) — produção não tem usuários default |

## Exportação de relatório em PDF

Não há geração automática de PDF no servidor.

**Fluxo atual:** o relatório (`templates/relatorio.html`) é HTML otimizado para impressão A4 paisagem em uma única página (margem 2mm, fórmula de zoom Jinja2). O usuário usa `Ctrl+P → Salvar como PDF` no navegador.

WeasyPrint foi descartado — não funciona no Windows sem GTK runtime.

## Atualizar código em produção (PythonAnywhere)

```bash
cd ~/projeto-extensao-horarios
git pull
# se mudou requirements.txt:
pip install -r requirements.txt
# Aba Web → botão Reload
```
