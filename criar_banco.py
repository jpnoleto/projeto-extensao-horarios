import pymysql
import os
from urllib.parse import urlparse
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
load_dotenv()

url = urlparse(os.environ['DATABASE_URL'])
conn = pymysql.connect(
    host=url.hostname,
    user=url.username,
    password=url.password or '',
    database=url.path.lstrip('/'),
    port=url.port or 3306,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor,
)
cursor = conn.cursor()

comandos_sql = [
    """
    CREATE TABLE IF NOT EXISTS professor (
        id_professor INT AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(255) NOT NULL,
        cpf VARCHAR(14) UNIQUE,
        email VARCHAR(255),
        telefone VARCHAR(20),
        status VARCHAR(10) DEFAULT 'ativo' CHECK (status IN ('ativo', 'inativo'))
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS turno (
        id_turno INT AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(100) NOT NULL UNIQUE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS turma (
        id_turma INT AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(100) NOT NULL,
        serie VARCHAR(50) NOT NULL,
        id_turno INT NOT NULL,
        FOREIGN KEY (id_turno) REFERENCES turno(id_turno),
        UNIQUE (nome, serie, id_turno)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS disciplina (
        id_disciplina INT AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(255) NOT NULL UNIQUE,
        sigla VARCHAR(20) NOT NULL UNIQUE,
        cor VARCHAR(20) NOT NULL,
        carga_horaria_semanal INT NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS professor_disciplina (
        id_professor INT NOT NULL,
        id_disciplina INT NOT NULL,
        PRIMARY KEY (id_professor, id_disciplina),
        FOREIGN KEY (id_professor) REFERENCES professor(id_professor),
        FOREIGN KEY (id_disciplina) REFERENCES disciplina(id_disciplina)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS `local` (
        id_local INT AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(255) NOT NULL UNIQUE,
        tipo VARCHAR(50) NOT NULL,
        status VARCHAR(10) DEFAULT 'ativo' CHECK (status IN ('ativo', 'inativo'))
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS horario_aula (
        id_horario INT AUTO_INCREMENT PRIMARY KEY,
        hora_inicio VARCHAR(10) NOT NULL,
        hora_fim VARCHAR(10) NOT NULL,
        eh_intervalo INT DEFAULT 0,
        UNIQUE(hora_inicio, hora_fim)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS disponibilidade_professor (
        id_disponibilidade INT AUTO_INCREMENT PRIMARY KEY,
        id_professor INT NOT NULL,
        dia_semana VARCHAR(10) NOT NULL CHECK (dia_semana IN ('segunda', 'terca', 'quarta', 'quinta', 'sexta')),
        id_horario INT NOT NULL,
        disponivel INT DEFAULT 1 CHECK (disponivel IN (0, 1)),
        FOREIGN KEY (id_professor) REFERENCES professor(id_professor),
        FOREIGN KEY (id_horario) REFERENCES horario_aula(id_horario),
        UNIQUE (id_professor, dia_semana, id_horario)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS grade_curricular (
        id_grade INT AUTO_INCREMENT PRIMARY KEY,
        id_turno INT NOT NULL,
        serie VARCHAR(50) NOT NULL,
        id_disciplina INT NOT NULL,
        aulas_semanais INT NOT NULL,
        FOREIGN KEY (id_turno) REFERENCES turno(id_turno),
        FOREIGN KEY (id_disciplina) REFERENCES disciplina(id_disciplina),
        UNIQUE (id_turno, serie, id_disciplina)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS alocacao (
        id_alocacao INT AUTO_INCREMENT PRIMARY KEY,
        id_turma INT NOT NULL,
        id_disciplina INT NOT NULL,
        id_professor INT NOT NULL,
        id_local INT NOT NULL,
        dia_semana VARCHAR(10) NOT NULL CHECK (dia_semana IN ('segunda', 'terca', 'quarta', 'quinta', 'sexta')),
        id_horario INT NOT NULL,
        FOREIGN KEY (id_turma) REFERENCES turma(id_turma),
        FOREIGN KEY (id_disciplina) REFERENCES disciplina(id_disciplina),
        FOREIGN KEY (id_professor) REFERENCES professor(id_professor),
        FOREIGN KEY (id_local) REFERENCES `local`(id_local),
        FOREIGN KEY (id_horario) REFERENCES horario_aula(id_horario),
        UNIQUE (id_professor, dia_semana, id_horario),
        UNIQUE (id_turma, dia_semana, id_horario),
        UNIQUE (id_local, dia_semana, id_horario)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS usuario (
        id_usuario INT AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL UNIQUE,
        senha_hash VARCHAR(512) NOT NULL,
        perfil VARCHAR(20) NOT NULL CHECK (perfil IN ('diretor', 'secretaria', 'professor')),
        id_professor INT,
        primeiro_login INT DEFAULT 1 CHECK (primeiro_login IN (0, 1)),
        ativo INT DEFAULT 1 CHECK (ativo IN (0, 1)),
        FOREIGN KEY (id_professor) REFERENCES professor(id_professor)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS sugestao_grade (
        id_sugestao INT AUTO_INCREMENT PRIMARY KEY,
        id_turno INT NOT NULL,
        nome VARCHAR(100) NOT NULL,
        dados_json LONGTEXT NOT NULL,
        cobertura_pct INT DEFAULT 0,
        nao_alocados INT DEFAULT 0,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_turno) REFERENCES turno(id_turno)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
]

for comando in comandos_sql:
    cursor.execute(comando)

cursor.execute("SELECT COUNT(*) AS total FROM usuario")
if cursor.fetchone()['total'] == 0:
    seed_default = os.environ.get('DB_SEED_DEFAULT_USERS', '').lower() in ('1', 'true', 'yes')
    if seed_default:
        seeds = [
            ('Diretor', 'diretor@escola.com', generate_password_hash('diretor123'), 'diretor', None),
            ('Secretaria', 'secretaria@escola.com', generate_password_hash('secretaria123'), 'secretaria', None),
        ]
        cursor.executemany("""
            INSERT INTO usuario (nome, email, senha_hash, perfil, id_professor, primeiro_login)
            VALUES (%s, %s, %s, %s, %s, 1)
        """, seeds)
        print("\n[AVISO] Usuarios padrao criados (somente para desenvolvimento):")
        print("  diretor@escola.com    / diretor123")
        print("  secretaria@escola.com / secretaria123")
        print("  TROQUE AS SENHAS no primeiro login (primeiro_login=1 forca redirecionamento).\n")
    else:
        print("\n[INFO] Nenhum usuario criado.")
        print("  Para popular usuários default em DEV: DB_SEED_DEFAULT_USERS=true python criar_banco.py")
        print("  Em PRODUÇÃO: crie o primeiro diretor via INSERT manual:")
        print("    INSERT INTO usuario (nome, email, senha_hash, perfil, primeiro_login)")
        print("    VALUES ('Seu Nome', 'voce@dominio.com', '<hash gerado>', 'diretor', 1);")
        print("  (gere o hash com: python -c \"from werkzeug.security import generate_password_hash; print(generate_password_hash('SUA_SENHA'))\")\n")

conn.commit()
conn.close()

print("Banco MySQL criado com sucesso!")
