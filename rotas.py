import os
from dotenv import load_dotenv
load_dotenv()
from flask import Flask
import auth

from blueprints import (
    autenticacao, professores, disciplinas, turnos, turmas, locais,
    horarios, professor_disciplina, disponibilidade,
    grade_curricular, alocacao, relatorio, usuarios, sugestao
)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'escola_horarios_chave_secreta_2024')
app.config['TEMPLATES_AUTO_RELOAD'] = True

autenticacao.registrar(app)
professores.registrar(app)
disciplinas.registrar(app)
turnos.registrar(app)
turmas.registrar(app)
locais.registrar(app)
horarios.registrar(app)
professor_disciplina.registrar(app)
disponibilidade.registrar(app)
grade_curricular.registrar(app)
alocacao.registrar(app)
relatorio.registrar(app)
usuarios.registrar(app)
sugestao.registrar(app)


@app.context_processor
def injetar_usuario():
    return dict(usuario_atual=auth.usuario_logado())


@app.template_filter('formatar_cpf')
def formatar_cpf(cpf):
    if not cpf:
        return '—'
    c = str(cpf)
    if len(c) == 11:
        return f'{c[:3]}.{c[3:6]}.{c[6:9]}-{c[9:]}'
    return c


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
