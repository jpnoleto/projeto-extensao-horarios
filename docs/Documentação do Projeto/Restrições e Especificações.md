# Restrições e Especificações do Sistema

Regras estruturais que governam o sistema após a reformulação (montagem manual). Como não há mais
algoritmo automático, grade curricular nem locais, as regras ficaram bem mais simples.

---

## 1. Unicidade das alocações (constraints do banco)

A tabela `alocacao` tem duas constraints `UNIQUE` que impedem conflitos físicos:

| Constraint | Significado |
|---|---|
| `(id_professor, dia_semana, id_horario)` | Professor não pode estar em duas turmas ao mesmo tempo |
| `(id_turma, dia_semana, id_horario)` | Turma não pode ter duas aulas simultâneas |

Ao alocar, o backend captura `pymysql.IntegrityError` e emite um `flash` explicando o conflito.
Nada é inserido quando há conflito — não existe mais o "pular slot silenciosamente".

> A antiga constraint de local `(id_local, dia_semana, id_horario)` foi removida junto com a tabela `local`.

---

## 2. Disponibilidade do professor

Na [[Montagem da Grade]], o `<select>` de professor de cada célula só oferece professores que:

1. Têm **disponibilidade cadastrada** para aquele dia + horário (`disponibilidade_professor.disponivel = 1`), e
2. **Não estão ocupados** nesse mesmo slot em outra turma.

Consequência: um professor **sem nenhuma disponibilidade cadastrada nunca aparece** para alocação.
Se o administrador não encontra o professor esperado numa célula, o passo que faltou é cadastrar a
disponibilidade dele. O filtro é só UX — a garantia final continua sendo o `UNIQUE` do banco.

---

## 3. Formato e ordenação dos horários

`hora_inicio` / `hora_fim` são `VARCHAR` no formato `HH:MM` (ex: `'07:10'`), ordenados por
`ORDER BY hora_inicio` (funciona para strings `HH:MM`).

**Regra:** todo horário — inclusive intervalos — deve ter `hora_inicio`/`hora_fim` no formato `HH:MM`.
O campo `eh_intervalo = 1` marca o intervalo. Intervalos são **filtrados** na montagem da grade e
aparecem no relatório como uma faixa "— INTERVALO —" ocupando as colunas dos dias.

---

## 4. Turno como texto

`turma.turno` é uma coluna de texto (`Matutino` / `Vespertino` / `Noturno`), validada no backend
contra a lista `TURNOS` em `blueprints/turmas.py`. Não há tabela `turno` nem FK — o agrupamento por
turno nas listagens é feito com `groupby('turno')` no Jinja2.

---

## 5. Associação livre professor × disciplina

Professores e disciplinas são cadastrados de forma **independente**. Não existe tabela de vínculo:
na montagem da grade o administrador escolhe **qualquer** disciplina e **qualquer** professor
disponível para a célula. A responsabilidade pedagógica da combinação é do administrador.

---

## 6. Exclusão de itens em uso

Excluir professor, disciplina, turma ou horário que já esteja referenciado em `alocacao` ou
`disponibilidade_professor` dispara `IntegrityError` de FK. O sistema captura e mostra um `flash`
amigável ("remova as aulas antes" / "marque o professor como inativo"), sem estourar erro 500.

---

## 7. Paginação nas listagens

Professores e disciplinas são paginados (20 por página, `?pagina=N`). As rotas de **edição**
(`editar_professor`, `editar_disciplina`) não paginam — exibem todos os registros para o formulário
inline aparecer independentemente da página.

---

## 8. Relatório em uma página

O relatório por turma (`relatorio.html`) é otimizado para caber em **1 página A4 paisagem**. Usa
`print-color-adjust: exact` para preservar as cores das disciplinas ao imprimir/salvar em PDF
(`Ctrl+P → Salvar como PDF`). Não há geração de PDF no servidor.
