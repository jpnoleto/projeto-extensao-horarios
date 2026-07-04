# Banco de Dados

Script de criação: `criar_banco.py`
Reset completo (DROP de todas as tabelas): `limpar_banco.py`
Banco: **MySQL** — charset `utf8mb4`, engine `InnoDB`

## Modelo de dependências

```
turma
disciplina
professor → disponibilidade_professor ← horario_aula
turma + disciplina + professor + horario_aula → alocacao
usuario (login único de admin, isolado)
```

Entidades base (sem dependências): `professor`, `disciplina`, `turma`, `horario_aula`.

> **Removidas na reformulação:** `turno`, `local`, `professor_disciplina`, `grade_curricular` e
> `sugestao_grade`. O turno virou uma **coluna de texto** em `turma`; a associação professor×disciplina
> passou a ser feita à mão na [[Montagem da Grade]].

## Tabelas

### usuario
Login único de administrador.

| Campo | Tipo | Notas |
|-------|------|-------|
| id_usuario | INT PK AUTO | |
| nome | VARCHAR(255) | NOT NULL |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| senha_hash | VARCHAR(512) | `werkzeug.security` |

### professor
| Campo | Tipo | Notas |
|-------|------|-------|
| id_professor | INT PK AUTO | |
| nome | VARCHAR(255) | NOT NULL |
| email | VARCHAR(255) | nullable |
| telefone | VARCHAR(20) | nullable |
| status | VARCHAR(10) | `'ativo'` \| `'inativo'` |

### disciplina
| Campo | Tipo |
|-------|------|
| id_disciplina | INT PK AUTO |
| nome | VARCHAR(255) UNIQUE |
| sigla | VARCHAR(20) UNIQUE |
| cor | VARCHAR(20) |

### turma
| Campo | Tipo | Notas |
|-------|------|-------|
| id_turma | INT PK AUTO | |
| nome | VARCHAR(100) | ex: `'1A'` |
| serie | VARCHAR(50) | ex: `'1º Ano'` |
| turno | VARCHAR(20) | texto: `Matutino` \| `Vespertino` \| `Noturno` |

UNIQUE: `(nome, serie, turno)`

### horario_aula
| Campo | Tipo | Notas |
|-------|------|-------|
| id_horario | INT PK AUTO | |
| hora_inicio | VARCHAR(10) | ex: `'07:30'` |
| hora_fim | VARCHAR(10) | |
| eh_intervalo | INT | `0` = aula, `1` = intervalo |

UNIQUE: `(hora_inicio, hora_fim)`
> Intervalos aparecem no relatório como linha spanning; **não** entram na montagem da grade.

### disponibilidade_professor
| Campo | Tipo |
|-------|------|
| id_disponibilidade | INT PK AUTO |
| id_professor | FK → professor |
| dia_semana | `'segunda'`\|`'terca'`\|`'quarta'`\|`'quinta'`\|`'sexta'` |
| id_horario | FK → horario_aula |
| disponivel | `0` ou `1` |

UNIQUE: `(id_professor, dia_semana, id_horario)`

### alocacao
Cada linha = uma aula de uma turma num dia/horário.

| Campo | Tipo |
|-------|------|
| id_alocacao | INT PK AUTO |
| id_turma | FK → turma |
| id_disciplina | FK → disciplina |
| id_professor | FK → professor |
| dia_semana | `'segunda'`…`'sexta'` |
| id_horario | FK → horario_aula |

Restrições de unicidade (evitam conflito físico):
- `(id_professor, dia_semana, id_horario)` — professor em dois lugares ao mesmo tempo
- `(id_turma, dia_semana, id_horario)` — turma com duas aulas simultâneas

> Não há mais constraint de local — a coluna `id_local` foi removida.

## Padrão de acesso

```python
from db import conectar

with conectar() as conexao:
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM professor WHERE id_professor = %s", (id,))
    # %s sempre (nunca ?)
    conexao.commit()  # só em INSERT/UPDATE/DELETE
```

- `COUNT(*)` → sempre com alias: `SELECT COUNT(*) AS total` + `fetchone()['total']`
- Conflitos de unicidade/FK → capturar `pymysql.IntegrityError` e emitir `flash` amigável
  (exclusões de professor/disciplina/turma/horário em uso não estouram 500)
