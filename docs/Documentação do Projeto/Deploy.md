# Deploy

Guia resumido. Versão completa em `DEPLOY.md` (raiz do projeto).

## Modo padrão: demonstração local

Para a entrega acadêmica (apresentação à escola parceira + banca), **não é necessário** hospedar online. Basta rodar localmente:

```bash
pip install -r requirements.txt
python criar_banco.py   # primeira vez
python rotas.py         # http://127.0.0.1:5000
```

Demonstra-se presencialmente com o notebook; o código fica publicado em código aberto no GitHub para a escola (ou qualquer outra interessada) instalar quando desejar.

## Hospedagem online (opcional)

Caso a escola decida operar o sistema em produção:

| Plataforma | Status | Observação |
|---|---|---|
| **Oracle Cloud Free Tier** | ✅ Forever free | VM ARM 24 GB RAM. MySQL local. Setup Linux ~1h. |
| **TiDB Cloud Serverless + Render** | ✅ Forever free | TiDB: 5 GB MySQL-compatível. Render Web Service Free. |
| Render + freedb.tech | ⚠️ DB auto-exclui em 24h ociosas | Só viável com uso diário |
| PythonAnywhere | ⚠️ MySQL agora exige plano pago | — |
| Railway | 🔴 Sem free tier permanente | — |

## Render + freedb.tech (recomendado)

Hospedagem em duas camadas, ambas gratuitas:

- **freedb.tech** — banco MySQL gratuito (200 MB, sem cartão)
- **Render Web Service Free** — aplicação Flask (dorme após 15 min ociosa; perfeito para uso esporádico)

### Passo a passo resumido

1. **freedb.tech** → criar conta → **Create New Database** → anotar host/user/pass/dbname
2. **Render** → login com GitHub → **New + → Web Service** → conectar `Noletinho/projeto-extensao-horarios`
3. Configurar:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: (vazio — vem do `Procfile`)
   - Instance Type: **Free**
4. Adicionar Environment Variables:
   ```ini
   DATABASE_URL=mysql://freedb_user:senha@sql.freedb.tech:3306/freedb_escola
   SECRET_KEY=<gere com python -c "import secrets; print(secrets.token_hex(32))">
   FLASK_DEBUG=0
   PYTHON_VERSION=3.11.9
   ```
5. **Create Web Service** → após deploy, no Shell do Render:
   ```bash
   python criar_banco.py
   # depois insira o usuário diretor (passos completos em DEPLOY.md)
   ```

Detalhe completo + criação do diretor em [`DEPLOY.md`](../../DEPLOY.md) na raiz do projeto.

## Entrypoints

- `Procfile` (`web: gunicorn rotas:app --workers 2 --timeout 120 ...`) — usado por Render/Railway
- `wsgi.py` — entrypoint WSGI alternativo (usado caso o deploy seja em servidores que procuram `application`)

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
