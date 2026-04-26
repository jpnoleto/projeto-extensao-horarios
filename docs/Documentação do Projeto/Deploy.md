# Deploy

Plataforma: **Railway**

## Passos

1. Criar projeto no Railway e adicionar plugin MySQL
2. Definir variáveis de ambiente:
   - `DATABASE_URL` — preenchida automaticamente pelo plugin MySQL
   - `SECRET_KEY` — gerar uma chave segura
3. Conectar ao repositório GitHub — Railway detecta o `Procfile` automaticamente
4. Após o primeiro deploy, rodar no terminal do Railway:
   ```bash
   python criar_banco.py
   ```

## Procfile

```
web: python rotas.py
```

## Exportação de relatório em PDF

Não há geração automática de PDF no servidor.
WeasyPrint foi removido — não funciona no Windows sem GTK runtime.

**Fluxo atual:** Rota `GET /baixar_relatorio_pdf/<id_turno>` redireciona para o relatório HTML.
O usuário usa `Ctrl+P → Salvar como PDF` no navegador.
