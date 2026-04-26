# Banco de Dados

Script de criação: `criar_banco.py`
Banco: **MySQL** — charset `utf8mb4`, engine `InnoDB`

## Modelo de dependências

```
turno → turma
disciplina
professor → professor_disciplina ← disciplina
professor → disponibilidade_professor ← horario_aula
(turno + serie) + disciplina → grade_curricular
grade_curricular + turma + professor + local + horario_aula → alocacao
sugestao_grade → turno
```

Entidades base (sem dependências): `professor`, `disciplina`, `turno`, `local`, `horario_aula`

## Tabelas

### professor
| Campo | Tipo | Notas |
|-------|------|-------|
| id_professor | INT PK AUTO | |
| nome | VARCHAR(255) | NOT NULL |
| cpf | VARCHAR(14) | UNIQUE, nullable |
| email | VARCHAR(255) | |
| telefone | VARCHAR(20) | |
| status | VARCHAR(10) | `'ativo'` \| `'inativo'` |

### turno
| Campo | Tipo |
|-------|------|
| id_turno | INT PK AUTO |
| nome | VARCHAR(100) UNIQUE NOT NULL |

### turma
| Campo | Tipo | Notas |
|-------|------|-------|
| id_turma | INT PK AUTO | |
| nome | VARCHAR(100) | |
| serie | VARCHAR(50) | |
| id_turno | FK → turno | |

UNIQUE: `(nome, serie, id_turno)`

### disciplina
| Campo | Tipo |
|-------|------|
| id_disciplina | INT PK AUTO |
| nome | VARCHAR(255) UNIQUE |
| sigla | VARCHAR(20) UNIQUE |
| cor | VARCHAR(20) |
| carga_horaria_semanal | INT |

### professor_disciplina
Relação N:N entre professor e disciplina.
PK composta: `(id_professor, id_disciplina)`

### local
> ⚠️ Palavra reservada MySQL — usar backticks em toda query: `` `local` ``

| Campo | Tipo |
|-------|------|
| id_local | INT PK AUTO |
| nome | VARCHAR(255) UNIQUE |
| tipo | VARCHAR(50) |
| status | `'ativo'` \| `'inativo'` |

### horario_aula
| Campo | Tipo | Notas |
|-------|------|-------|
| id_horario | INT PK AUTO | |
| hora_inicio | VARCHAR(10) | ex: `'07:30'` |
| hora_fim | VARCHAR(10) | |
| eh_intervalo | INT | `0` = aula, `1` = intervalo |

UNIQUE: `(hora_inicio, hora_fim)`
> Intervalos aparecem no relatório como linha spanning; **não** aparecem no select de alocação.

### disponibilidade_professor
| Campo | Tipo |
|-------|------|
| id_disponibilidade | INT PK AUTO |
| id_professor | FK → professor |
| dia_semana | `'segunda'`\|`'terca'`\|`'quarta'`\|`'quinta'`\|`'sexta'` |
| id_horario | FK → horario_aula |
| disponivel | `0` ou `1` |

UNIQUE: `(id_professor, dia_semana, id_horario)`

### grade_curricular
Compartilhada por turno + série — sem duplicação por turma.

| Campo | Tipo |
|-------|------|
| id_grade | INT PK AUTO |
| id_turno | FK → turno |
| serie | VARCHAR(50) |
| id_disciplina | FK → disciplina |
| aulas_semanais | INT |

UNIQUE: `(id_turno, serie, id_disciplina)`

### alocacao
| Campo | Tipo |
|-------|------|
| id_alocacao | INT PK AUTO |
| id_turma | FK → turma |
| id_disciplina | FK → disciplina |
| id_professor | FK → professor |
| id_local | FK → local |
| dia_semana | `'segunda'`…`'sexta'` |
| id_horario | FK → horario_aula |

Restrições de unicidade (evitam conflito):
- `(id_professor, dia_semana, id_horario)` — professor em dois lugares
- `(id_turma, dia_semana, id_horario)` — turma com duas aulas simultâneas
- `(id_local, dia_semana, id_horario)` — local ocupado duas vezes

### sugestao_grade
| Campo | Tipo |
|-------|------|
| id_sugestao | INT PK AUTO |
| id_turno | FK → turno |
| nome | VARCHAR(100) |
| dados_json | LONGTEXT |
| cobertura_pct | INT |
| nao_alocados | INT |
| criado_em | TIMESTAMP |

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
- Multi-insert com tolerância a conflito → usar `SAVEPOINT` + `ROLLBACK TO SAVEPOINT`
