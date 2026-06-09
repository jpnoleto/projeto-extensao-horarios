# Sistema de Gerenciamento de Horários Escolares

**Projeto de Extensão Universitária**

---

## Identificação

| Campo | Informação |
|---|---|
| **Título do projeto** | Sistema de Gerenciamento de Horários Escolares |
| **Autor** | João Pedro Noleto da Silva |
| **Instituição** | Unopar - Anhanguera |
| **Curso** | Engenharia de Software |
| **Disciplina / Atividade de Extensão** | Projeto de Extensão |
| **Orientador(a)** | Unopar |
| **Período** | 2° Período |
| **Repositório** | <https://github.com/Noletinho/projeto-extensao-horarios> |

---

## Resumo

Este projeto consiste no desenvolvimento de um sistema web para a gestão de horários escolares, voltado à realidade de escolas públicas brasileiras de Ensino Médio. A aplicação permite o cadastro estruturado de professores, disciplinas, turnos, turmas, locais e horários de aula, além de oferecer rotinas automatizadas para alocação de aulas com base em uma grade curricular previamente definida, geração de sugestões de distribuição (usando o heurístico *Most Constrained Variable*), produção de relatórios de impressão em A4 paisagem e controle de acesso por perfis (diretor, secretaria e professor). O sistema foi desenvolvido em Python com o microframework Flask, banco de dados MySQL e templates Jinja2 renderizados no servidor, sendo distribuído gratuitamente sob código aberto para uso por qualquer instituição interessada.

**Palavras-chave:** gestão escolar; horários; alocação automática; Flask; código aberto; extensão universitária.

---

## 1. Introdução

A organização de horários é uma das tarefas mais críticas e demoradas do início de cada semestre letivo em escolas de Ensino Médio. Diretores e equipes pedagógicas dedicam, em média, semanas para distribuir manualmente professores, disciplinas e turmas em uma matriz de horários respeitando a grade curricular, a carga horária de cada disciplina, a disponibilidade individual dos professores e os locais físicos disponíveis (salas regulares, laboratórios, quadras, etc.). Esse trabalho, quando realizado em planilhas ou no papel, é propenso a erros: conflitos de professor em dois lugares ao mesmo tempo, sub ou superalocação de carga horária, falta de transparência para quem precisa consultar.

Este projeto de extensão nasce justamente para mitigar esse problema: oferecer, sem custo, uma ferramenta computacional simples, instalável em qualquer servidor gratuito (incluindo PythonAnywhere e Render), capaz de centralizar todos os cadastros, detectar conflitos automaticamente e gerar relatórios prontos para impressão. O sistema foi desenhado com foco em escolas públicas, que muitas vezes não dispõem de orçamento para soluções comerciais.

## 2. Justificativa

A escolha do tema decorre de três fatores principais:

1. **Demanda real e recorrente** — Toda escola enfrenta o problema da elaboração da grade horária todo semestre. A literatura em pesquisa operacional já demonstra que o *School Timetabling Problem* é NP-difícil, o que justifica o uso de heurísticas em vez de tentativas manuais exaustivas.

2. **Acessibilidade** — Sistemas comerciais existentes têm custo elevado e dependem de licenças anuais, o que torna o acesso inviável para escolas públicas com orçamento limitado. A licença aberta deste projeto remove essa barreira.

3. **Contribuição extensionista** — Como projeto de extensão, o sistema retorna o conhecimento técnico adquirido no curso universitário diretamente à comunidade externa, beneficiando estudantes, professores e gestores da rede pública.

## 3. Objetivos

### 3.1. Objetivo Geral

Desenvolver e disponibilizar gratuitamente um sistema web completo para a gestão de horários escolares, com algoritmo automatizado de alocação de aulas, voltado ao uso por escolas públicas de Ensino Médio.

### 3.2. Objetivos Específicos

1. Modelar o domínio de horários escolares (professores, disciplinas, turnos, turmas, locais, horários de aula, grade curricular e alocações) em uma base de dados relacional MySQL.
2. Implementar interfaces web (formulários CRUD) para cadastro e manutenção de todas as entidades, com validação no servidor.
3. Desenvolver um algoritmo de alocação automática baseado no heurístico *Most Constrained Variable* (MCV), capaz de gerar sugestões respeitando a grade curricular e a disponibilidade dos professores.
4. Construir um relatório de impressão em formato A4 paisagem, otimizado para uma única página por turno, com identificação visual por disciplina (cores).
5. Implementar controle de acesso por perfis (diretor, secretaria, professor) com senhas hasheadas e mecanismo de troca obrigatória no primeiro login.
6. Publicar o código sob licença aberta no GitHub, com documentação de deploy gratuita em PythonAnywhere.

## 4. Público-alvo

O sistema é direcionado a **escolas públicas de Ensino Médio** das redes estaduais e municipais brasileiras. Os usuários finais são:

- **Diretores escolares** — responsáveis pela visão geral do sistema, criação de usuários e validação das grades;
- **Equipe da secretaria** — responsáveis pelos cadastros do dia a dia (professores, disciplinas, alocações);
- **Professores** — usuários consultivos, com acesso à sua própria grade de horários e à edição do seu perfil.

Embora o foco seja o Ensino Médio público, o sistema funciona, sem adaptações, para escolas de Ensino Fundamental, técnicas ou privadas que adotem o modelo de turnos com aulas regulares.

## 5. Metodologia

O desenvolvimento seguiu um modelo iterativo e incremental, com ciclos curtos de implementação e validação. As etapas foram:

1. **Levantamento de requisitos** — análise do problema real de elaboração de grade horária em escolas públicas, levantamento das entidades envolvidas e dos fluxos de uso.
2. **Modelagem de dados** — construção do diagrama relacional do banco MySQL, com tabelas para todas as entidades e seus relacionamentos.
3. **Prototipação da interface** — definição de uma identidade visual sóbria e institucional (paleta "Academic Authority", azul institucional + crimson + laranja, fonte Inter).
4. **Implementação iterativa por entidade** — cada blueprint Flask foi desenvolvido isoladamente: cadastro → listagem → edição inline → exclusão, com tratamento de erros via mensagens *flash*.
5. **Implementação do algoritmo de alocação** — heurístico MCV (*Most Constrained Variable*): a cada iteração, agenda primeiro a demanda com menos slots disponíveis, evitando *deadlocks* característicos de algoritmos *greedy*.
6. **Implementação do relatório de impressão** — otimização para uma única página A4 paisagem, com cálculo dinâmico de *zoom* via Jinja2 para qualquer número de turmas.
7. **Hardening de segurança** — auditoria de pontos críticos (chave secreta, cookies de sessão, modo debug, credenciais default) antes do deploy.
8. **Documentação e publicação** — versionamento em Git, repositório público no GitHub e guia de deploy para PythonAnywhere.

## 6. Tecnologias Utilizadas

| Categoria | Tecnologia | Versão | Uso |
|---|---|---|---|
| **Linguagem** | Python | 3.10+ | Backend |
| **Microframework web** | Flask | ≥ 3.0 | Roteamento, sessões, templates |
| **Templates** | Jinja2 | (incluso no Flask) | Renderização HTML server-side |
| **Banco de dados** | MySQL | 8.0+ | Persistência relacional |
| **Driver MySQL** | PyMySQL | ≥ 1.1 | Conexão MySQL via Python puro |
| **Hashing de senhas** | Werkzeug Security | ≥ 3.0 | `generate_password_hash` / `check_password_hash` |
| **Variáveis de ambiente** | python-dotenv | ≥ 1.0 | Carga de `.env` para dev local |
| **Servidor de produção** | Gunicorn | ≥ 21.0 | WSGI multi-worker |
| **Autenticação criptográfica** | cryptography | ≥ 42.0 | Suporte ao `caching_sha2_password` do MySQL 8.0+ |
| **Hospedagem alvo** | PythonAnywhere | (free tier) | Deploy gratuito com MySQL incluso |
| **Versionamento** | Git + GitHub | — | Código aberto |
| **Frontend** | HTML + CSS + JavaScript puro | — | Sem frameworks pesados; animações via biblioteca Motion.dev |

## 7. Funcionalidades Implementadas

### 7.1. Cadastros Base

- **Professores** — nome, e-mail, CPF (visível apenas para perfil diretor, mascarado para secretaria), status ativo/inativo.
- **Disciplinas** — nome, sigla, carga horária, cor de identificação (com paleta de 16 cores predefinidas).
- **Turnos** — manhã, tarde, noite (configuráveis).
- **Turmas** — vinculadas a um turno e a uma série (1ª, 2ª, 3ª ano, etc.).
- **Locais** — salas, laboratórios, biblioteca, quadras.
- **Horários de aula** — janelas de tempo (`hora_início` / `hora_fim`), com marcação opcional de intervalo.

### 7.2. Relacionamentos

- **Professor × Disciplina** — quais disciplinas cada professor está habilitado a lecionar.
- **Disponibilidade do Professor** — grade visual de disponibilidade por dia da semana × horário.
- **Grade Curricular** — quais disciplinas devem ser dadas em cada turno × série, com a respectiva carga horária semanal.

### 7.3. Alocação de Aulas

- **Manual** — formulário com grade visual interativa: ao escolher turma, disciplina e professor, o sistema mostra automaticamente a disponibilidade do docente, conflitos de turma e ocupação do professor em outros lugares.
- **Automática** — algoritmo MCV gera uma proposta completa de grade respeitando demanda e disponibilidade; pode ser aplicada integralmente ou por turma.

### 7.4. Sugestões Automáticas (algoritmo MCV)

- Geração de sugestões persistidas em banco (`sugestao_grade`).
- Cada sugestão pode ser visualizada, editada, excluída ou aplicada (parcialmente por turma ou integralmente).
- Detecção automática de conflitos no momento da aplicação.

### 7.5. Relatório de Grade Horária

- Layout otimizado para impressão em A4 paisagem.
- Garante exibição em **uma única página** independentemente do número de turmas (testado com 5, 13, 20 e 30 turmas).
- Identificação visual por disciplina via cores.
- Separação visual entre dias da semana.
- Margem 2 mm uniforme nos quatro lados.

### 7.6. Horário Individual do Professor

- Cada professor com acesso ao sistema visualiza somente a sua grade, na rota `/meu_horario`.

### 7.7. Autenticação e Controle de Acesso

- Três perfis: **diretor**, **secretaria**, **professor**.
- Senhas hasheadas com `werkzeug.security` (PBKDF2 com 600k iterações + salt).
- Cookies de sessão protegidos: `HttpOnly`, `SameSite=Lax`, `Secure` (HTTPS-only em produção).
- Mecanismo de "primeiro login": força troca de senha no primeiro acesso para usuários recém-criados.
- Mascaramento de CPF para perfis sem permissão de visualização.

## 8. Arquitetura do Sistema

### 8.1. Visão Geral

A aplicação segue arquitetura monolítica com renderização server-side (server-side rendering), modelo clássico de aplicação Flask + templates Jinja2 + banco relacional MySQL. Optou-se intencionalmente por não usar frameworks frontend (React, Vue, etc.) para manter a simplicidade do deploy e reduzir a barreira de manutenção por outras pessoas.

### 8.2. Camadas

- **`rotas.py`** — ponto de entrada da aplicação Flask; registra todos os blueprints e configura a sessão.
- **`blueprints/`** — um módulo Python por entidade do domínio (professores, disciplinas, turmas, etc.); cada um expõe uma função `registrar(app)` que define as rotas no app Flask.
- **`db.py`** — utilitário único de conexão ao MySQL (`conectar()`), retornando um objeto compatível com `RealDictCursor` do PyMySQL.
- **`auth.py`** — funções de autenticação (`usuario_logado()`) e decorators (`requer_login`, `requer_perfil`).
- **`templates/`** — templates Jinja2; quase todos herdam de `base.html` (exceto o relatório de impressão e a tela do horário individual do professor, que são standalone).
- **`static/`** — CSS, imagens e JavaScript estático.
- **`criar_banco.py`** — script idempotente de criação do schema MySQL e *seed* opcional de usuários.

### 8.3. Modelo de Dados (entidades e dependências)

```
turno → turma
disciplina
professor → professor_disciplina ← disciplina
professor → disponibilidade_professor ← horario_aula
(turno + série) + disciplina → grade_curricular
grade_curricular + turma + professor + local + horario_aula → alocacao
```

## 9. Algoritmo de Alocação Automática (MCV)

A heurística *Most Constrained Variable* é aplicada da seguinte forma:

1. **Pré-atribuição de professores** — para cada par (disciplina × série), o sistema balanceia a carga entre os professores habilitados, distribuindo as turmas de forma equilibrada.
2. **Computação de slots disponíveis** — para cada par (turma × disciplina), conta-se quantos slots de horário ainda estão livres na grade.
3. **Iteração MCV** — a cada passo, agenda-se primeiro a demanda com **menos slots disponíveis** (a mais constrangida), evitando que demandas críticas fiquem sem opção quando se chega ao fim.
4. **Detecção de conflitos** — no momento de aplicar, o sistema verifica conflitos reais de professor (mesmo professor em dois lugares) e de turma (mesma turma em duas aulas simultâneas), preservando alocações pré-existentes.

Essa abordagem evita os *deadlocks* clássicos de algoritmos *greedy* puros, especialmente em cenários de alta densidade (carga horária semanal igual ao número total de slots).

## 10. Resultados Esperados

- **Para a escola usuária**: redução do tempo de elaboração da grade horária de várias semanas para algumas horas; eliminação de conflitos manuais; impressão de relatórios padronizados; histórico digital das grades aplicadas.
- **Para a comunidade extensionista**: disponibilização gratuita de um software completo e funcional, publicado sob código aberto, com documentação de instalação para qualquer escola interessada.
- **Para o autor**: aprofundamento em desenvolvimento web full-stack (backend Flask, frontend Jinja2, banco MySQL), aplicação prática de algoritmos heurísticos e estudo de boas práticas de segurança em aplicações web.

## 11. Considerações Finais

O sistema demonstra que ferramentas de gestão escolar de qualidade podem ser desenvolvidas e disponibilizadas sem custo para a comunidade, aproveitando exclusivamente plataformas gratuitas (PythonAnywhere para hospedagem, GitHub para versionamento, MySQL como banco). A arquitetura simples e o uso de templates server-side permitem que a aplicação seja mantida e estendida por outros desenvolvedores com conhecimento básico em Python.

Como trabalhos futuros, sugere-se:

- Integração com sistemas oficiais de gestão escolar (ex.: SIGEAM, SED-SP).
- Exportação dos relatórios em PDF nativo (sem depender do navegador).
- Aplicativo móvel complementar para consulta de horário pelos professores.
- Estudo comparativo do algoritmo MCV com técnicas de programação por restrições (CSP) ou metaheurísticas (algoritmos genéticos, têmpera simulada).

## 12. Referências Técnicas

- **Flask** — Pallets Projects. <https://flask.palletsprojects.com/>
- **Jinja2** — Pallets Projects. <https://jinja.palletsprojects.com/>
- **MySQL 8.0** — Oracle. <https://dev.mysql.com/doc/refman/8.0/en/>
- **Werkzeug Security** — Pallets Projects. <https://werkzeug.palletsprojects.com/>
- **Most Constrained Variable** — Russell, Stuart; Norvig, Peter. *Artificial Intelligence: A Modern Approach*. 4. ed. Pearson, 2020. Cap. 6 (Constraint Satisfaction Problems).
- **OWASP Top 10** — Open Web Application Security Project. <https://owasp.org/Top10/>

---

**Código-fonte:** <https://github.com/Noletinho/projeto-extensao-horarios>
**Demonstração online:** `<PREENCHA: URL do PythonAnywhere após o deploy, ex: https://seuuser.pythonanywhere.com>`
