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
| **Repositório** | <https://github.com/jpnoleto/projeto-extensao-horarios> |

---

## Resumo

Este projeto consiste no desenvolvimento de um sistema web para a **montagem manual de horários escolares**, voltado à realidade de escolas públicas brasileiras de Ensino Médio. A aplicação permite o cadastro estruturado e independente de professores, disciplinas, turmas e horários de aula, o registro da disponibilidade de cada professor e a montagem da grade de cada turma **à mão pelo administrador**, célula a célula, associando livremente professor e disciplina. O sistema atua como um "guarda de trilhos": ao montar a grade, oferece apenas professores disponíveis no horário escolhido e impede automaticamente conflitos (mesmo professor em duas turmas ou turma com duas aulas no mesmo horário). Ao final, gera um relatório de impressão em A4 paisagem, com uma única página por turma e identificação visual por disciplina. O sistema foi desenvolvido em Python com o microframework Flask, banco de dados MySQL e templates Jinja2 renderizados no servidor, sendo distribuído gratuitamente sob código aberto para uso por qualquer instituição interessada.

**Palavras-chave:** gestão escolar; horários; montagem manual; Flask; código aberto; extensão universitária.

---

## 1. Introdução

A organização de horários é uma das tarefas mais críticas e demoradas do início de cada semestre letivo em escolas de Ensino Médio. Diretores e equipes pedagógicas dedicam, em média, semanas para distribuir manualmente professores, disciplinas e turmas em uma matriz de horários respeitando a disponibilidade individual dos professores. Esse trabalho, quando realizado em planilhas ou no papel, é propenso a erros: conflitos de professor em dois lugares ao mesmo tempo, turmas com duas aulas no mesmo horário e falta de transparência para quem precisa consultar.

Este projeto de extensão nasce justamente para mitigar esse problema: oferecer, sem custo, uma ferramenta computacional simples que preserva a autonomia do gestor sobre a montagem da grade, ao mesmo tempo em que impede conflitos e respeita a disponibilidade dos professores, e gera relatórios prontos para impressão. O sistema foi desenhado com foco em escolas públicas, que muitas vezes não dispõem de orçamento para soluções comerciais.

## 2. Justificativa

A escolha do tema decorre de três fatores principais:

1. **Demanda real e recorrente** — Toda escola enfrenta o problema da elaboração da grade horária todo semestre. O processo manual em planilhas é lento e sujeito a erros que só são percebidos tarde demais.

2. **Acessibilidade** — Sistemas comerciais existentes têm custo elevado e dependem de licenças anuais, o que torna o acesso inviável para escolas públicas com orçamento limitado. A licença aberta deste projeto remove essa barreira.

3. **Contribuição extensionista** — Como projeto de extensão, o sistema retorna o conhecimento técnico adquirido no curso universitário diretamente à comunidade externa, beneficiando estudantes, professores e gestores da rede pública.

## 3. Objetivos

### 3.1. Objetivo Geral

Desenvolver e disponibilizar gratuitamente um sistema web para a **montagem manual assistida** de horários escolares, no qual o administrador tem controle total sobre a distribuição das aulas e o sistema garante o respeito à disponibilidade dos professores e a ausência de conflitos, voltado ao uso por escolas públicas de Ensino Médio.

### 3.2. Objetivos Específicos

1. Modelar o domínio de horários escolares (professores, disciplinas, turmas, horários de aula, disponibilidade e alocações) em uma base de dados relacional MySQL.
2. Implementar interfaces web (formulários CRUD) para cadastro e manutenção de todas as entidades, com validação no servidor.
3. Permitir o cadastro **independente** de professores e disciplinas, com a associação entre eles feita manualmente pelo administrador no momento da montagem da grade.
4. Construir uma tela de **montagem visual da grade por turma**, na qual cada célula (dia × horário) oferece apenas professores disponíveis e livres, prevenindo conflitos.
5. Construir um relatório de impressão em formato A4 paisagem, otimizado para uma única página por turma, com identificação visual por disciplina (cores).
6. Implementar controle de acesso por login de administrador, com senhas hasheadas.
7. Publicar o código sob licença aberta no GitHub, com documentação de instalação local.

## 4. Público-alvo

O sistema é direcionado a **escolas públicas de Ensino Médio** das redes estaduais e municipais brasileiras. É operado pela **administração da escola** (direção/secretaria), que realiza os cadastros e monta as grades. Os professores e a comunidade escolar são beneficiados pelos relatórios impressos de horário por turma.

Embora o foco seja o Ensino Médio público, o sistema funciona, sem adaptações, para escolas de Ensino Fundamental, técnicas ou privadas que adotem o modelo de turnos com aulas regulares.

## 5. Metodologia

O desenvolvimento seguiu um modelo iterativo e incremental, com ciclos curtos de implementação e validação. As etapas foram:

1. **Levantamento de requisitos** — análise do problema real de elaboração de grade horária em escolas públicas, levantamento das entidades envolvidas e dos fluxos de uso.
2. **Modelagem de dados** — construção do modelo relacional do banco MySQL, com tabelas para todas as entidades e seus relacionamentos.
3. **Prototipação da interface** — definição de uma identidade visual sóbria e institucional (paleta "Academic Authority", azul institucional + crimson, fonte Inter).
4. **Implementação iterativa por entidade** — cada blueprint Flask foi desenvolvido isoladamente: cadastro → listagem → edição inline → exclusão, com tratamento de erros via mensagens *flash*.
5. **Prototipação de alocação automática e decisão de projeto** — durante o desenvolvimento, chegou-se a implementar um protótipo de alocação automática baseado no heurístico *Most Constrained Variable* (MCV), estudado em Inteligência Artificial. Após testes, optou-se por **não** incluí-lo na versão final: a geração automática mostrou-se rígida diante das preferências pedagógicas reais e retirava do gestor o controle sobre decisões que são, por natureza, humanas. A versão entregue adota **montagem manual assistida**, na qual o computador atua como validador (disponibilidade e conflitos), e não como decisor.
6. **Implementação da montagem visual da grade** — tela por turma em que cada célula abre um seletor de disciplina e professor, filtrando os professores por disponibilidade e ocupação.
7. **Implementação do relatório de impressão** — otimização para uma única página A4 paisagem por turma, com cores por disciplina preservadas na impressão.
8. **Boas práticas de segurança** — proteção da chave secreta, cookies de sessão seguros, senhas com hash e ausência de credenciais reais no código aberto.
9. **Documentação e publicação** — versionamento em Git, repositório público no GitHub e documentação técnica (`CLAUDE.md`) e acadêmica.

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
| **Autenticação criptográfica** | cryptography | ≥ 42.0 | Suporte ao `caching_sha2_password` do MySQL 8.0+ |
| **Versionamento** | Git + GitHub | — | Código aberto |
| **Frontend** | HTML + CSS + JavaScript puro | — | Sem frameworks pesados; animações via biblioteca Motion.dev |
| **Execução** | Servidor local (`python rotas.py`) | — | Uso presencial; sem hospedagem online |

## 7. Funcionalidades Implementadas

### 7.1. Cadastros Base (independentes)

- **Professores** — nome, e-mail, telefone, status ativo/inativo.
- **Disciplinas** — nome, sigla e cor de identificação (com paleta de 16 cores predefinidas).
- **Turmas** — nome, série e turno (Matutino/Vespertino/Noturno).
- **Horários de aula** — janelas de tempo (`hora_início` / `hora_fim`), com marcação opcional de intervalo.

Professores e disciplinas são cadastrados de forma **independente**; a associação entre eles não é pré-definida — é feita à mão pelo administrador na montagem da grade.

### 7.2. Disponibilidade do Professor

Grade visual de disponibilidade por dia da semana × horário. É o insumo que o sistema usa para oferecer, na montagem, apenas os professores realmente disponíveis em cada horário.

### 7.3. Montagem Manual da Grade

Tela por turma com uma matriz dias × horários. Cada célula vazia abre um seletor no qual o administrador escolhe **qualquer** disciplina e **qualquer** professor disponível para aquele dia e horário. O sistema:

- oferece somente professores com disponibilidade cadastrada no horário e que não estejam ocupados em outra turma;
- impede, no banco de dados, conflitos de professor (dois lugares ao mesmo tempo) e de turma (duas aulas simultâneas);
- permite remover e reatribuir aulas livremente, e limpar a grade inteira de uma turma.

> Nota de projeto: uma alocação automática por heurística (MCV) chegou a ser prototipada, mas foi retirada da versão final em favor do controle manual do gestor (ver seção 5).

### 7.4. Relatório de Grade Horária

- Layout otimizado para impressão em A4 paisagem, **uma única página por turma**.
- Identificação visual por disciplina via cores, preservadas na impressão (`print-color-adjust: exact`).
- Campos opcionais de nome da escola e data no cabeçalho.
- Exportação em PDF pelo próprio navegador (`Ctrl+P → Salvar como PDF`).

### 7.5. Autenticação e Controle de Acesso

- Login **único de administrador**.
- Senhas hasheadas com `werkzeug.security` (PBKDF2 com salt).
- Cookies de sessão protegidos: `HttpOnly`, `SameSite=Lax`, `Secure` (fora do modo de desenvolvimento).

## 8. Arquitetura do Sistema

### 8.1. Visão Geral

A aplicação segue arquitetura monolítica com renderização server-side, modelo clássico de aplicação Flask + templates Jinja2 + banco relacional MySQL. Optou-se intencionalmente por não usar frameworks frontend (React, Vue, etc.) para manter a simplicidade e reduzir a barreira de manutenção por outras pessoas.

### 8.2. Camadas

- **`rotas.py`** — ponto de entrada da aplicação Flask; registra todos os blueprints e configura a sessão.
- **`blueprints/`** — um módulo Python por área do domínio (professores, disciplinas, turmas, horários, disponibilidade, montagem da grade e relatório); cada um expõe `registrar(app)`.
- **`db.py`** — utilitário único de conexão ao MySQL (`conectar()`), com `DictCursor` do PyMySQL.
- **`auth.py`** — funções de autenticação (`usuario_logado()`) e o decorator `requer_login`.
- **`templates/`** — templates Jinja2; quase todos herdam de `base.html` (exceto o relatório de impressão e a tela de login, que são standalone).
- **`static/`** — CSS, imagens e JavaScript estático.
- **`criar_banco.py`** — script de criação do schema MySQL e *seed* opcional do administrador; **`limpar_banco.py`** faz o reset completo.

### 8.3. Modelo de Dados (entidades e dependências)

```
turma
disciplina
professor → disponibilidade_professor ← horario_aula
turma + disciplina + professor + horario_aula → alocacao
usuario (login único de administrador)
```

Entidades base, cadastradas independentemente: `professor`, `disciplina`, `turma`, `horario_aula`. A tabela `alocacao` representa cada aula montada na grade e possui restrições de unicidade que impedem conflitos de professor e de turma.

## 9. Decisão de Projeto: Montagem Manual em vez de Automática

Durante o desenvolvimento, implementou-se um protótipo de **alocação automática** baseado no heurístico *Most Constrained Variable* (MCV), estudado na disciplina de Inteligência Artificial. A ideia inicial era gerar a grade completa automaticamente, respeitando disponibilidade e demanda.

Os testes, porém, evidenciaram limitações práticas: a distribuição de aulas envolve decisões pedagógicas (afinidade professor-turma, preferências de horário, equilíbrio ao longo da semana) que uma heurística genérica não captura, e o resultado automático frequentemente precisava ser refeito manualmente. Além disso, o gestor perdia a sensação de controle sobre uma tarefa que é, por natureza, humana.

Optou-se, portanto, por uma abordagem de **montagem manual assistida**: o administrador decide cada aula, e o papel do computador é ser um **validador confiável** — oferecer apenas professores disponíveis, impedir conflitos e produzir o relatório final. Essa decisão privilegia a usabilidade e a confiança do usuário sobre a automação, e alinha-se ao princípio de projetar sistemas que *apoiam* o julgamento humano em vez de substituí-lo. O estudo do algoritmo MCV, ainda assim, foi valioso para compreender a complexidade do *School Timetabling Problem* e fundamentar a escolha.

## 10. Resultados Esperados

- **Para a escola usuária**: uma ferramenta gratuita que centraliza os cadastros, agiliza a montagem da grade, impede conflitos automaticamente e produz relatórios padronizados por turma, prontos para impressão e fixação em murais.
- **Para a comunidade extensionista**: disponibilização gratuita de um software completo e funcional, publicado sob código aberto, com documentação de instalação para qualquer escola interessada.
- **Para o autor**: aprofundamento em desenvolvimento web full-stack (backend Flask, frontend Jinja2, banco MySQL), estudo de algoritmos heurísticos (MCV) e das razões para preferir montagem manual assistida, e boas práticas de segurança em aplicações web.

## 11. Considerações Finais

O sistema demonstra que ferramentas de gestão escolar de qualidade podem ser desenvolvidas e disponibilizadas sem custo para a comunidade. A arquitetura simples, o uso de templates server-side e a operação puramente local (sem dependência de hospedagem online) permitem que a aplicação seja instalada e mantida por qualquer pessoa com conhecimento básico em Python, no próprio computador da escola.

A opção pela montagem manual assistida — em vez da geração automática — reforça um princípio importante: a tecnologia deve apoiar as decisões dos profissionais da educação, não tomá-las por eles.

Como trabalhos futuros, sugere-se:

- Exportação dos relatórios em PDF nativo (sem depender do navegador).
- Visão consolidada do horário individual de cada professor (a partir das grades montadas).
- Detecção de sugestões *opcionais* de preenchimento, sempre sujeitas à confirmação do gestor.
- Estudo comparativo de técnicas de programação por restrições (CSP) para um modo automático opcional futuro.

## 12. Referências Técnicas

- **Flask** — Pallets Projects. <https://flask.palletsprojects.com/>
- **Jinja2** — Pallets Projects. <https://jinja.palletsprojects.com/>
- **MySQL 8.0** — Oracle. <https://dev.mysql.com/doc/refman/8.0/en/>
- **Werkzeug Security** — Pallets Projects. <https://werkzeug.palletsprojects.com/>
- **Most Constrained Variable** — Russell, Stuart; Norvig, Peter. *Artificial Intelligence: A Modern Approach*. 4. ed. Pearson, 2020. Cap. 6 (Constraint Satisfaction Problems).
- **OWASP Top 10** — Open Web Application Security Project. <https://owasp.org/Top10/>

---

**Código-fonte:** <https://github.com/jpnoleto/projeto-extensao-horarios>
**Execução:** local, via `python rotas.py` → <http://127.0.0.1:5000> (sem hospedagem online).
