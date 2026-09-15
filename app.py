from flask import Flask, render_template
from database import init_db, get_conn
from routes.alunos import alunos_bp
from routes.professores import professores_bp
from routes.disciplinas import disciplinas_bp
from routes.horarios import horarios_bp
from routes.matriculas import matriculas_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = "escola-secret-key-2026"

    app.register_blueprint(alunos_bp)
    app.register_blueprint(professores_bp)
    app.register_blueprint(disciplinas_bp)
    app.register_blueprint(horarios_bp)
    app.register_blueprint(matriculas_bp)

    @app.route("/")
    def dashboard():
        conn = get_conn()

        total_alunos = conn.execute("SELECT COUNT(*) c FROM alunos").fetchone()["c"]
        total_professores = conn.execute("SELECT COUNT(*) c FROM professores").fetchone()["c"]
        total_disciplinas = conn.execute("SELECT COUNT(*) c FROM disciplinas").fetchone()["c"]
        total_matriculas = conn.execute("SELECT COUNT(*) c FROM matriculas").fetchone()["c"]

        alunos_por_turma = conn.execute(
            "SELECT turma, COUNT(*) qtd FROM alunos GROUP BY turma ORDER BY turma"
        ).fetchall()

        disciplinas_carga = conn.execute(
            "SELECT nome, carga_horaria FROM disciplinas ORDER BY carga_horaria DESC LIMIT 6"
        ).fetchall()

        ultimos_alunos = conn.execute(
            "SELECT * FROM alunos ORDER BY id DESC LIMIT 5"
        ).fetchall()

        proximos_horarios = conn.execute(
            """
            SELECT h.*, d.nome as disciplina_nome
            FROM horarios h JOIN disciplinas d ON d.id = h.disciplina_id
            ORDER BY
                CASE h.dia_semana
                    WHEN 'Segunda' THEN 1 WHEN 'Terça' THEN 2 WHEN 'Quarta' THEN 3
                    WHEN 'Quinta' THEN 4 WHEN 'Sexta' THEN 5 ELSE 6
                END, h.hora_inicio
            LIMIT 5
            """
        ).fetchall()

        conn.close()

        return render_template(
            "dashboard.html",
            total_alunos=total_alunos,
            total_professores=total_professores,
            total_disciplinas=total_disciplinas,
            total_matriculas=total_matriculas,
            alunos_por_turma=alunos_por_turma,
            disciplinas_carga=disciplinas_carga,
            ultimos_alunos=ultimos_alunos,
            proximos_horarios=proximos_horarios,
        )

    return app


app = create_app()

if __name__ == "__main__":
    init_db(seed=True)
    app.run(debug=True)
