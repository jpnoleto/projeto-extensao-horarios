# Restrições e Especificações do Sistema

Este documento descreve as regras estruturais que governam o sistema. Algumas são técnicas (banco de dados, algoritmo), outras são pedagógicas (carga horária escolar). Violá-las causa erros silenciosos ou falhas de alocação.

---

## 1. Capacidade semanal por turma

**Regra:** cada turma tem exatamente **6 horários de aula por dia × 5 dias = 30 slots por semana**.

O intervalo **não conta** como horário de aula — ele existe na tabela `horario_aula` com `eh_intervalo = 1` e é filtrado em todas as queries de alocação.

**Consequência:** a soma de `aulas_semanais` de todas as disciplinas na grade curricular de uma série **deve ser exatamente 30**. Se for menor, sobram slots vazios. Se for maior, o algoritmo nunca consegue alocar tudo independentemente da quantidade de professores.

```sql
-- Verificar se a grade fecha em 30 por série/turno
SELECT id_turno, serie, SUM(aulas_semanais) AS total
FROM grade_curricular
GROUP BY id_turno, serie;
-- Todos os resultados devem ser 30
```

---

## 2. Capacidade máxima de um professor

**Regra:** um professor pode dar no máximo **30 aulas por semana** (1 por slot, sem presença simultânea em duas turmas).

A carga real de um professor é calculada como:

```
carga = Σ (aulas_semanais × número de turmas que ele atende por disciplina)
```

Se `carga > 30`, o professor está sobrecarregado e o algoritmo vai deixar aulas sem alocar.

**Exemplo de sobrecarga:**
- Professor A ensina Matemática (3 aulas) para 13 turmas → 39 slots necessários > 30 disponíveis ❌

**Solução:** dividir as turmas entre 2+ professores da mesma disciplina. O sistema suporta múltiplos professores por disciplina — o algoritmo distribui automaticamente.

```sql
-- Verificar carga por professor (com divisão por co-professores)
SELECT p.nome,
       SUM(gc.aulas_semanais * cnt.qtd / co.total) AS carga_estimada
FROM professor p
JOIN professor_disciplina pd ON pd.id_professor = p.id_professor
JOIN grade_curricular gc ON gc.id_disciplina = pd.id_disciplina
JOIN (SELECT id_turno, serie, COUNT(*) AS qtd FROM turma GROUP BY id_turno, serie) cnt
    ON cnt.id_turno = gc.id_turno AND cnt.serie = gc.serie
JOIN (SELECT id_disciplina, COUNT(*) AS total FROM professor_disciplina GROUP BY id_disciplina) co
    ON co.id_disciplina = pd.id_disciplina
WHERE p.status = 'ativo'
GROUP BY p.id_professor, p.nome
ORDER BY carga_estimada DESC;
-- carga_estimada deve ser <= 30 para todos
```

---

## 3. O problema da folga zero (por que 1 slot extra importa)

Com **30 aulas = 30 slots** por turma, não existe margem de erro. O algoritmo de alocação usa a heurística **MCV (Most Constrained Variable)** — a cada passo, agenda a demanda com menos slots disponíveis primeiro — mas qualquer sequência de atribuições que crie um beco sem saída deixa 1–2 aulas sem slot.

**Analogia:** imagine 30 cadeiras e 30 pessoas, onde cada pessoa só pode sentar em certas cadeiras. Mesmo que a conta feche (30 = 30), pode ser impossível sentar todos se as preferências conflitarem no último lugar.

**Solução permanente:** cadastrar **31 horários de aula** (ou seja, um 7º horário por dia ou um horário extra em algum dia). Com 1 slot de folga, o algoritmo sempre tem uma saída.

---

## 4. Ordenação dos horários

Os horários são armazenados como `VARCHAR` (ex: `'07:10'`) e ordenados com `ORDER BY hora_inicio`. Isso funciona corretamente para strings no formato `HH:MM`.

**Restrição:** o campo `hora_inicio` **nunca pode ser texto livre** (ex: `'Intervalo'`). Se um intervalo for cadastrado sem horário, ele vai aparecer no final da lista porque a letra `'I'` tem valor ASCII maior que `'9'`.

**Regra:** todo horário — incluindo intervalos — deve ter `hora_inicio` e `hora_fim` no formato `HH:MM`. O campo `eh_intervalo = 1` distingue o intervalo das aulas normais na exibição.

---

## 5. Unicidade das alocações (restrições do banco)

A tabela `alocacao` possui três constraints `UNIQUE` que impedem conflitos físicos:

| Constraint | Significado |
|---|---|
| `(id_professor, dia_semana, id_horario)` | Professor não pode estar em dois lugares ao mesmo tempo |
| `(id_turma, dia_semana, id_horario)` | Turma não pode ter duas aulas simultâneas |
| `(id_local, dia_semana, id_horario)` | Sala/local não pode ter duas turmas ao mesmo tempo |

Tentativas de inserir conflitos são capturadas via `SAVEPOINT` + `ROLLBACK TO SAVEPOINT` e ignoradas silenciosamente (o slot é pulado e contado como conflito).

---

## 6. Grade curricular × turmas

A `grade_curricular` é definida por **turno + série**, não por turma individual. Isso significa que todas as turmas de uma série dentro do mesmo turno compartilham a mesma grade.

**Consequência:** alterar `aulas_semanais` de uma disciplina na grade de "1° ano Matutino" afeta **todas** as turmas do 1° ano matutino (A, B, C, D...).

Para ter grades diferentes por turma, seria necessário refatorar o modelo de dados — algo fora do escopo atual.

---

## 7. Professores sem vínculo ou sem disponibilidade

O algoritmo trata professores **sem disponibilidade cadastrada** como disponíveis em todos os slots (comportamento permissivo). Isso é intencional para o modo de sugestão ideal.

Porém, ao **aplicar** uma sugestão ou alocação automática, a constraint do banco é que vale — um professor sem disponibilidade pode ser alocado em qualquer horário sem restrição de sistema.

**Boas práticas:**
- Todo professor ativo deve ter pelo menos 1 disciplina vinculada (caso contrário nunca será considerado pelo algoritmo)
- Cadastrar disponibilidade é opcional, mas recomendado para refletir a realidade

As telas de **Vincular Professor × Disciplina** e **Cadastrar Disponibilidade** exibem alertas com os professores que ainda não foram configurados.

---

## 8. Palavra reservada `local`

A tabela `local` usa uma palavra reservada do MySQL. **Toda query** que referencia essa tabela deve usar backticks:

```sql
SELECT * FROM `local` WHERE status = 'ativo'
```

Esquecer os backticks causa `SyntaxError` no MySQL mesmo que o Python não reclame na hora da construção da string.

---

## 9. Perfil professor — restrições de acesso

Professores com perfil `'professor'` no sistema:
- **Não veem** menus de cadastro, alocação ou sugestões
- **Veem apenas** "Meu Horário" (`/meu_horario`) e "Relatório por Turno"
- O `id_professor` do usuário deve estar vinculado a um registro da tabela `professor` para que o horário pessoal funcione

Se `id_professor` for `NULL` no registro do usuário, a rota `/meu_horario` redireciona com flash de erro.

---

## 10. Paginação nas listagens

Professores e disciplinas são paginados (20 por página, parâmetro `?pagina=N`).

As rotas de **edição** (`editar_professor`, `editar_disciplina`) **não paginam** — exibem todos os registros para garantir que o formulário inline apareça na tela independente da página em que o item estaria.
