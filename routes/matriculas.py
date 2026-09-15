from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_conn
import sqlite3

matriculas_bp = Blueprint("matriculas", __name__, url_prefix="/matriculas")


@matriculas_bp.route("/")
def listar():
    conn = get_conn()
    matriculas = conn.execute(
        """
        SELECT m.id, a.id as aluno_id, a.nome as aluno_nome, a.foto as aluno_foto,
               d.id as disciplina_id, d.nome as disciplina_nome, m.data_matricula
        FROM matriculas m
        JOIN alunos a ON a.id = m.aluno_id
        JOIN disciplinas d ON d.id = m.disciplina_id
        ORDER BY a.nome, d.nome
        """
    ).fetchall()
    conn.close()
    return render_template("matriculas/list.html", matriculas=matriculas)


@matriculas_bp.route("/nova", methods=["GET", "POST"])
def nova():
    conn = get_conn()
    alunos = conn.execute("SELECT * FROM alunos ORDER BY nome").fetchall()
    disciplinas = conn.execute("SELECT * FROM disciplinas ORDER BY nome").fetchall()

    if request.method == "POST":
        aluno_id = request.form["aluno_id"]
        disciplina_id = request.form["disciplina_id"]

        try:
            conn.execute(
                "INSERT INTO matriculas (aluno_id, disciplina_id) VALUES (?, ?)",
                (aluno_id, disciplina_id),
            )
            conn.commit()
            flash("Matrícula realizada com sucesso!", "sucesso")
        except sqlite3.IntegrityError:
            flash("Este aluno já está matriculado nessa disciplina!", "erro")

        conn.close()
        return redirect(url_for("matriculas.listar"))

    conn.close()
    return render_template("matriculas/form.html", alunos=alunos, disciplinas=disciplinas)


@matriculas_bp.route("/excluir/<int:id>", methods=["POST"])
def excluir(id):
    conn = get_conn()
    conn.execute("DELETE FROM matriculas WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Matrícula cancelada com sucesso!", "sucesso")
    return redirect(url_for("matriculas.listar"))
