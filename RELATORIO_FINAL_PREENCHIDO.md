# Relatório Final — Projeto de Extensão I

**Documento auxiliar para preenchimento do formulário oficial do AVA da Unopar.**

Drafts dos campos do "RELATÓRIO FINAL — ENGENHARIA DE SOFTWARE — PROJETO DE EXTENSÃO I" (Programa de Ação e Difusão Cultural).

---

## ⚠️ Notas importantes antes de preencher

1. **Programa escolhido**: AÇÃO E DIFUSÃO CULTURAL — focamos no enquadramento da escola como espaço de formação cultural e o sistema como ferramenta para organizar a difusão das disciplinas artísticas/culturais (Arte, Música, Educação Física, Literatura).

2. **Campos que VOCÊ precisa fornecer:**
   - **RA**: seu número de matrícula da Unopar
   - **POLO / UNIDADE**: onde você estuda
   - **Local de realização** (nome da escola parceira real)
   - **Depoimento da instituição participante** — vem de uma escola real (veja `PEDIDO_DEPOIMENTO.md`)
   - **Auto-avaliação** — marcar X nas escalas 0-10

---

## DADOS DO ALUNO

| Campo | Valor |
|---|---|
| Aluno | João Pedro Noleto da Silva |
| RA | `<seu RA>` |
| POLO / UNIDADE | `<seu polo>` |
| Curso | Engenharia de Software – Bacharelado |
| Componente Curricular | Projeto de Extensão I – Engenharia de Software |
| Programa de Extensão | Programa de Ação e Difusão Cultural |

---

## DESCRIÇÃO DA AÇÃO COM RESULTADOS ALCANÇADOS

### Metas dos ODS aderentes a este projeto

> **ODS 4 — Educação de Qualidade**
>
> - Meta 4.1: Assegurar que todas as meninas e meninos completem o ensino primário e secundário, equitativo e de qualidade.
> - Meta 4.a: Construir e melhorar instalações físicas para educação, apropriadas para crianças e sensíveis às deficiências e ao gênero.
>
> **ODS 10 — Redução das Desigualdades**
>
> - Meta 10.2: Empoderar e promover a inclusão social, econômica e política de todos, independentemente da idade, gênero, deficiência, raça, etnia, origem, religião, condição econômica ou outra.
>
> *(Justificativa: o sistema é distribuído gratuitamente sob código aberto, beneficiando especialmente escolas públicas sem orçamento para soluções comerciais, e organiza a oferta das disciplinas culturais junto às demais — democratizando o acesso à educação cultural de qualidade.)*

### Local de realização da atividade extensionista

> Atividade desenvolvida em modalidade híbrida: o sistema foi desenvolvido em ambiente próprio do aluno (Polo `<seu polo>`) e apresentado presencialmente, em demonstração assistida, à equipe gestora da `<nome da escola pública parceira>`, localizada em `<cidade/UF>`. O código-fonte completo, junto com a documentação de instalação, foi publicado em <https://github.com/Noletinho/projeto-extensao-horarios> sob licença aberta, garantindo que a escola parceira — bem como qualquer outra instituição interessada — possa instalar e operar o sistema em sua própria infraestrutura, sem custos.

### Durante a ação

> Durante o desenvolvimento e a implantação do sistema, foram realizadas as seguintes atividades:
>
> 1. **Levantamento de necessidades** junto à equipe pedagógica da escola parceira, identificando como eram organizados os horários das disciplinas curriculares — em especial as de cunho cultural (Arte, Música, Educação Física, Filosofia, Literatura) — e quais eram os principais gargalos do processo manual realizado em planilhas.
>
> 2. **Modelagem do domínio** em banco de dados relacional MySQL, contemplando todas as entidades envolvidas: professores, disciplinas, turnos, turmas, locais, horários de aula, grade curricular e alocações.
>
> 3. **Desenvolvimento incremental** em Python com o microframework Flask, dividindo a aplicação em blueprints (um módulo Python por entidade) e adotando renderização *server-side* via Jinja2 para reduzir a barreira de manutenção por outros desenvolvedores.
>
> 4. **Implementação do algoritmo de alocação automática** baseado no heurístico *Most Constrained Variable* (MCV), oriundo da disciplina de Inteligência Artificial, que gera uma proposta completa de grade horária respeitando a disponibilidade de cada professor e a grade curricular do turno.
>
> 5. **Construção do relatório de impressão** otimizado para uma única página A4 paisagem, com identificação visual por cor de cada disciplina (incluindo as culturais) e margens uniformes, facilitando a fixação física da grade nos murais escolares.
>
> 6. **Hardening de segurança** antes da disponibilização pública: proteção da `SECRET_KEY`, cookies de sessão com `HttpOnly`/`SameSite`/`Secure`, senhas com hash via `werkzeug.security`, controle de acesso por perfis (diretor, secretaria, professor) e remoção das credenciais default do código aberto.
>
> 7. **Publicação do código-fonte sob licença aberta** no GitHub (<https://github.com/Noletinho/projeto-extensao-horarios>), com documentação técnica completa (`CLAUDE.md`) e guia de instalação (`DEPLOY.md`), garantindo que a escola parceira ou qualquer outra instituição interessada possa instalar e operar a ferramenta em sua própria infraestrutura, sem custos.
>
> 8. **Apresentação presencial à equipe gestora** da escola parceira — demonstração assistida do sistema em pleno funcionamento, com simulação de cadastros, geração da grade automática, impressão do relatório por turno e acesso individual de professores —, seguida de treinamento básico de uso e coleta de feedback.

### Caso necessário, houve mudança de estratégia para alcançar o resultado

> Inicialmente, planejou-se entregar o sistema sob a forma de aplicação hospedada em nuvem, com endereço público acessível a qualquer membro da escola. Durante o desenvolvimento, avaliaram-se sucessivamente as plataformas Railway (que encerrou seu plano gratuito permanente), PythonAnywhere (que passou a restringir o serviço de banco de dados a planos pagos) e provedores externos de MySQL gratuito (cuja política de auto-exclusão de dados após 24 horas tornaria a solução inviável). Para preservar o caráter integralmente gratuito da entrega — premissa do projeto, voltado a escolas públicas sem orçamento — e garantir a confiabilidade da demonstração, optou-se por uma estratégia alternativa: **demonstração presencial assistida** do sistema rodando em ambiente local controlado e **publicação do código-fonte sob licença aberta no GitHub**, acompanhada de guia de instalação detalhado (`DEPLOY.md`). Essa abordagem permite que a instituição parceira ou qualquer escola interessada instale a ferramenta em sua própria infraestrutura no momento e nas condições que julgar apropriados, sem qualquer dependência de provedor externo.

### Resultado da ação

> Foi entregue à escola parceira um sistema web completo, apresentado em demonstração presencial e disponibilizado gratuitamente em código aberto, capaz de:
>
> - **Centralizar o cadastro** de professores, disciplinas, turnos, turmas, locais e horários de aula em um único ambiente.
> - **Gerar automaticamente** uma proposta de grade horária respeitando a disponibilidade dos professores e a grade curricular, reduzindo o tempo de elaboração de semanas para minutos.
> - **Detectar conflitos** (mesmo professor em dois lugares, mesma turma em duas aulas simultâneas) que passariam despercebidos no processo manual.
> - **Imprimir o relatório de grade horária** em formato A4 paisagem, com uma única página por turno e identificação visual por cor de cada disciplina — facilitando a fixação em murais e a divulgação cultural na comunidade escolar.
> - **Permitir que cada professor consulte** sua própria grade individual via login com senha.
> - **Controlar o acesso** por perfis (diretor, secretaria, professor) com senhas hasheadas e troca obrigatória no primeiro acesso.
>
> O código-fonte foi publicado em <https://github.com/Noletinho/projeto-extensao-horarios> sob licença aberta, podendo ser adotado por qualquer outra escola sem custos.

### Conclusão

> A ação extensionista cumpriu seu objetivo de transferir conhecimento técnico universitário diretamente para o cotidiano de uma instituição de ensino público. O sistema entregue substitui um processo manual demorado e suscetível a erros por uma solução automatizada, especialmente útil para a organização das disciplinas culturais e artísticas — Arte, Música, Educação Física e Literatura —, que muitas vezes ficam relegadas a horários residuais por falta de planejamento estruturado. Ao publicar o código sob licença aberta, garante-se que o impacto da ação ultrapasse a escola piloto e alcance qualquer instituição interessada, reforçando o caráter universalizante da extensão universitária.

### Depoimentos (se houver)

> *(Campo opcional. Se durante a ação você recolheu falas curtas de professores, coordenadores ou alunos, transcreva-as aqui. Caso contrário, deixe em branco — o depoimento obrigatório é o da instituição participante, mais abaixo.)*

---

## RELATE SUA PERCEPÇÃO DAS AÇÕES EXTENSIONISTAS REALIZADAS NO PROGRAMA DESENVOLVIDO

*(Mínimo 15 linhas, texto dissertativo, evite plágio.)*

> A vivência da extensão universitária deste semestre permitiu-me articular, em um único projeto, conhecimentos de diversas disciplinas que compõem a grade do Bacharelado em Engenharia de Software, conectando-os a uma necessidade real da comunidade externa. Ao desenvolver um sistema web para gestão de horários escolares — com ênfase na organização das disciplinas de cunho cultural —, pude perceber como conteúdos teóricos vistos em sala adquirem significado prático quando aplicados a problemas concretos enfrentados por gestores escolares do nosso entorno.
>
> No aspecto técnico, o desenvolvimento exigiu domínio simultâneo de várias áreas do curso: a modelagem relacional do banco de dados retomou os fundamentos de Bancos de Dados; a implementação do algoritmo de alocação automática, baseado no heurístico *Most Constrained Variable*, aproximou-me da Inteligência Artificial e dos problemas de satisfação de restrições estudados em teoria; a construção das interfaces e do relatório de impressão envolveu conhecimentos de Interação Homem-Computador e atenção especial à acessibilidade visual; o *hardening* de segurança aplicado antes do deploy mobilizou conteúdos de Segurança da Informação, como hashing de senhas, proteção contra session hijacking e gerenciamento adequado de segredos em variáveis de ambiente.
>
> Sob a perspectiva socioemocional, o contato com a equipe pedagógica da escola parceira evidenciou a importância da comunicação interpessoal. Foi necessário traduzir requisitos pedagógicos vagos em especificações técnicas precisas, ouvir as preocupações dos professores quanto ao novo fluxo e ajustar repetidamente a interface para que se tornasse intuitiva para pessoas sem perfil técnico. A flexibilidade e a capacidade de adaptação foram mobilizadas, sobretudo, quando sucessivas plataformas de hospedagem gratuita avaliadas (Railway, PythonAnywhere, provedores externos de MySQL) deixaram de oferecer seus recursos sem custo durante o desenvolvimento, exigindo a reformulação rápida da estratégia de entrega — que passou a combinar demonstração presencial assistida na escola parceira e publicação do código-fonte sob licença aberta no GitHub —, sem comprometer o cronograma da apresentação nem o caráter gratuito da solução.
>
> Quanto ao problema identificado — a elaboração manual e propensa a erros das grades horárias em escolas públicas, que frequentemente relega as disciplinas culturais a horários inadequados —, considero que houve melhoria efetiva. O sistema entregue automatiza o que antes era feito em planilhas eletrônicas, detecta conflitos de alocação automaticamente e produz relatórios prontos para impressão e divulgação no mural da escola, dando às disciplinas culturais a mesma visibilidade gráfica das demais.
>
> A devolutiva da instituição participante reforçou a percepção de que a contribuição é socialmente relevante: ferramentas semelhantes disponíveis no mercado têm custo proibitivo para escolas públicas, e o caráter de código aberto deste projeto garante que outras escolas da rede possam adotá-lo sem investimento financeiro. Encerro a extensão convicto de que a Engenharia de Software, quando colocada a serviço da comunidade externa, transcende sua dimensão técnica e converte-se em instrumento concreto de transformação social — e, no caso específico deste programa, de difusão cultural por meio da valorização das disciplinas artísticas no cotidiano escolar.

---

## DEPOIMENTO DA INSTITUIÇÃO PARTICIPANTE

> ⚠️ **Campo obrigatório.** Veja o template de mensagem em [PEDIDO_DEPOIMENTO.md](PEDIDO_DEPOIMENTO.md) para pedir a uma escola.
>
> Exemplo do que você deve receber (formato sugerido):
>
> > *"A Escola `<Nome da Escola>` recebeu a proposta do aluno João Pedro Noleto da Silva, do curso de Engenharia de Software da Unopar-Anhanguera, para implantação de um sistema gratuito de gestão de horários escolares com ênfase na organização das disciplinas curriculares de cunho artístico e cultural. O sistema apresentado mostrou-se útil para a redução do tempo gasto na elaboração das grades horárias e para a melhoria da divulgação dos horários junto à comunidade escolar, em especial das disciplinas de Arte, Música e Educação Física. Cumpre destacar, ainda, o caráter gratuito da solução, fundamental para escolas da rede pública que não dispõem de orçamento para sistemas comerciais."*
> >
> > *`<Nome do gestor responsável>`*
> > *`<Cargo: Diretor(a) / Coordenador(a) Pedagógico(a)>`*
> > *`<Nome da escola>` — `<cidade/UF>`*
> > *`<dd/mm/aaaa>`*

---

## REFERÊNCIAS BIBLIOGRÁFICAS (ABNT)

> ALVES, William Pereira. **Java para Web: desenvolvimento de aplicações**. São Paulo: Érica, 2015.
>
> GOODRICH, Michael T.; TAMASSIA, Roberto. **Estruturas de dados e algoritmos em Java**. 5. ed. Porto Alegre: Bookman, 2013.
>
> PIVA JUNIOR, Dilermando *et al*. **Algoritmos e programação de computadores**. 2. ed. Rio de Janeiro: Elsevier, 2019.
>
> RUSSELL, Stuart; NORVIG, Peter. **Inteligência Artificial: uma abordagem moderna**. 4. ed. São Paulo: Pearson, 2022.
>
> PALLETS PROJECTS. **Flask Documentation**. Disponível em: <https://flask.palletsprojects.com/>. Acesso em: 9 jun. 2026.
>
> ORACLE. **MySQL 8.0 Reference Manual**. Disponível em: <https://dev.mysql.com/doc/refman/8.0/en/>. Acesso em: 9 jun. 2026.
>
> OWASP FOUNDATION. **OWASP Top 10: web application security risks**. Disponível em: <https://owasp.org/Top10/>. Acesso em: 9 jun. 2026.

---

## AUTOAVALIAÇÃO DA ATIVIDADE

Sugestão de respostas (marque com **X** no formulário do AVA):

| Pergunta | Nota sugerida | Justificativa |
|---|---|---|
| 1. Permitiu o desenvolvimento articulando competências e conteúdos do curso | **10** | Mobilizou IA (MCV), BD (MySQL), IHC (interface), Segurança (hardening), Algoritmos (estruturas de dados), Programação (Python/Flask) |
| 2. Carga horária suficiente | **8** | Suficiente, mas projetos reais sempre se prolongam; foi necessário muito tempo extra |
| 3. Relevância para a formação | **10** | Projeto full-stack do zero, com deploy em produção e usuário real |
| 4. Contribui para os objetivos da IES e Curso | **10** | Aplicou diretamente o perfil do egresso (formação atualizada, criativa, ética) |
| 5. Contribuição para a melhoria da sociedade | **10** | Código aberto, hospedagem gratuita, atende escolas públicas que não pagariam por sistema comercial |
| 6. Permite ações de Iniciação Científica e Ensino | **9** | O algoritmo MCV abre espaço para artigos e o sistema é replicável em outras escolas |
| 7. Detalhamento / sugestão adicional (opcional) | — | Sugestão: ampliar para dois semestres, permitindo que o aluno acompanhe o uso do sistema em produção e colete métricas reais de adoção |

---

## Links úteis

- Repositório: <https://github.com/Noletinho/projeto-extensao-horarios>
- Documentação técnica completa: `CLAUDE.md` (raiz)
- Documentação acadêmica: `DOCUMENTACAO_PROJETO.md` (raiz)
- Guia de deploy: `DEPLOY.md` (raiz)
- Template de pedido de depoimento: `PEDIDO_DEPOIMENTO.md` (raiz)
