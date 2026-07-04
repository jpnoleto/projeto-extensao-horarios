# Gestor de Horários Escolares

Documentação do projeto de extensão universitária. Painel de **montagem manual** de horários:
o administrador associa professor + disciplina à mão em cada célula da grade da turma, respeitando
a disponibilidade, e imprime um relatório de 1 página.

## Índice

- [[Visão Geral]] — stack, como rodar, estrutura de pastas
- [[Banco de Dados]] — schema (7 tabelas), modelo de dependências, padrões de acesso
- [[Módulos (Blueprints)]] — rotas por área, padrão CRUD, fluxos especiais
- [[Montagem da Grade]] — montagem manual do horário por turma (núcleo do sistema)
- [[Visual e Tema]] — design system Academic Authority, classes CSS, animações
- [[Autenticação]] — login único de administrador
- [[Deploy]] — demonstração local (padrão), Render, Oracle Cloud, PDF por impressão
- [[Restrições e Especificações]] — regras estruturais (unicidade, disponibilidade, formatos)
