# Montagem da Grade

Módulos: `blueprints/alocacao.py` + `templates/montar_grade.html`

O núcleo do sistema. O administrador monta a grade de cada turma **manualmente**, associando
professor + disciplina em cada célula (dia × horário). Não há algoritmo automático — a associação é
livre, limitada apenas pela **disponibilidade** cadastrada e pelas restrições de conflito do banco.

> A antiga alocação automática (algoritmo MCV/greedy) e as sugestões salvas em `sugestao_grade`
> foram **removidas** na reformulação. Hoje tudo é feito à mão pelo administrador.

## Rotas (`alocacao.py`)

| Rota | Método | Descrição |
|------|--------|-----------|
| `/montar_grade` | GET | Lista turmas (com contagem de aulas) para escolher uma |
| `/montar_grade/<id_turma>` | GET | Grade visual da turma (linhas = horários, colunas = seg–sex) |
| `/montar_grade/<id_turma>/alocar` | POST | Insere uma aula: `{id_disciplina, id_professor, dia, id_horario}` |
| `/montar_grade/<id_turma>/remover/<id_alocacao>` | POST | Remove uma aula |
| `/montar_grade/<id_turma>/limpar` | POST | Apaga toda a grade da turma |

## Fluxo de montagem

1. **Selecionar turma** em `/montar_grade`.
2. A grade aparece: linhas = horários de aula (intervalos são filtrados), colunas = segunda a sexta.
3. **Célula vazia** → botão `+` abre um **modal** com:
   - `<select>` de disciplina (todas as disciplinas cadastradas — associação livre)
   - `<select>` de professor **filtrado por JavaScript**: só aparecem professores que têm
     disponibilidade cadastrada naquele dia+horário **e** não estão ocupados nesse slot em outra turma.
   - Se não houver professor disponível, exibe aviso e desabilita o botão de salvar.
4. **Célula preenchida** → mostra a sigla + primeiro nome do professor, com o fundo na cor da
   disciplina, e um botão `✕` para remover.

## Dados passados ao template

`montar_grade` envia estes JSONs para o filtro client-side:

| Variável | Formato | Uso |
|----------|---------|-----|
| `disciplinas_json` | `[{id, nome, sigla, cor}]` | Preencher o select de disciplina |
| `professores_json` | `[{id, nome}]` | Base do select de professor |
| `disponibilidades_json` | `{pid: {dia: [id_horario, ...]}}` | Filtrar professores disponíveis |
| `ocupacao_json` | `{pid: {dia: [id_horario, ...]}}` | Excluir professores já ocupados no slot |

## Validação de conflitos

O filtro JS é apenas conforto de UX. A **garantia real** vem das constraints `UNIQUE` da tabela
`alocacao`:

- `(id_professor, dia_semana, id_horario)` — professor em duas turmas ao mesmo tempo
- `(id_turma, dia_semana, id_horario)` — turma com duas aulas simultâneas

Ao inserir, `alocar_slot` captura `pymysql.IntegrityError` e emite um `flash` explicando o conflito
(professor ocupado / turma ocupada). Nada é inserido em caso de conflito.

## Relacionado

- [[Banco de Dados]] — tabela `alocacao` e `disponibilidade_professor`
- [[Módulos (Blueprints)]] — visão geral dos módulos
- O relatório final por turma é gerado em `relatorio.py` (ver [[Módulos (Blueprints)]]).
