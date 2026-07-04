"""
Reset COMPLETO do banco: remove todas as tabelas (esquema atual e antigo) para
permitir recriar o schema do zero com `python criar_banco.py`.

Como a reformulação mudou o modelo de dados (removeu turno, local,
professor_disciplina, grade_curricular, sugestao_grade e a coluna cpf/perfil),
este script derruba tanto as tabelas atuais quanto as antigas que possam ter
sobrado de versões anteriores.

Uso:
    python limpar_banco.py     # apaga tudo (inclui logins)
    python criar_banco.py      # recria o schema + admin default (se DB_SEED_DEFAULT_USERS)
"""
import os
from dotenv import load_dotenv
load_dotenv()

from db import conectar

# União do esquema atual + tabelas antigas removidas na reformulação.
TABELAS = [
    'alocacao',
    'disponibilidade_professor',
    'sugestao_grade',
    'grade_curricular',
    'professor_disciplina',
    'turma',
    'disciplina',
    'professor',
    '`local`',
    'horario_aula',
    'turno',
    'usuario',
]

with conectar() as conexao:
    cursor = conexao.cursor()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    for tabela in TABELAS:
        cursor.execute(f"DROP TABLE IF EXISTS {tabela}")
        print(f"  Removida: {tabela}")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    conexao.commit()

print("\nBanco zerado. Agora rode: python criar_banco.py")
