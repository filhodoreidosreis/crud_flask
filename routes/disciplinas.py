from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_conn

disciplinas_bp = Blueprint("disciplinas", __name__, url_prefix="/disciplinas")


@disciplinas_bp.route("/")
def listar():
    conn = get_conn()
    disciplinas = conn.execute(
        """
        SELECT d.*, p.nome as professor_nome, p.foto as professor_foto
        FROM disciplinas d
        LEFT JOIN professores p ON p.id = d.professor_id
        ORDER BY d.nome
        """
    ).fetchall()
    conn.close()
    return render_template("disciplinas/list.html", disciplinas=disciplinas)


@disciplinas_bp.route("/novo", methods=["GET", "POST"])
def novo():
    conn = get_conn()
    professores = conn.execute("SELECT * FROM professores ORDER BY nome").fetchall()

    if request.method == "POST":
        nome = request.form["nome"].strip()
        carga_horaria = request.form["carga_horaria"].strip()
        professor_id = request.form.get("professor_id") or None

        if not nome or not carga_horaria:
            conn.close()
            flash("Preencha todos os campos obrigatórios!", "erro")
            return redirect(url_for("disciplinas.novo"))

        conn.execute(
            "INSERT INTO disciplinas (nome, carga_horaria, professor_id) VALUES (?, ?, ?)",
            (nome, carga_horaria, professor_id),
        )
        conn.commit()
        conn.close()
        flash("Disciplina cadastrada com sucesso!", "sucesso")
        return redirect(url_for("disciplinas.listar"))

    conn.close()
    return render_template(
        "disciplinas/form.html", disciplina=None, professores=professores, titulo="Nova Disciplina"
    )


@disciplinas_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conn = get_conn()
    disciplina = conn.execute("SELECT * FROM disciplinas WHERE id = ?", (id,)).fetchone()
    if disciplina is None:
        conn.close()
        flash("Disciplina não encontrada!", "erro")
        return redirect(url_for("disciplinas.listar"))

    professores = conn.execute("SELECT * FROM professores ORDER BY nome").fetchall()

    if request.method == "POST":
        nome = request.form["nome"].strip()
        carga_horaria = request.form["carga_horaria"].strip()
        professor_id = request.form.get("professor_id") or None

        conn.execute(
            "UPDATE disciplinas SET nome=?, carga_horaria=?, professor_id=? WHERE id=?",
            (nome, carga_horaria, professor_id, id),
        )
        conn.commit()
        conn.close()
        flash("Disciplina atualizada com sucesso!", "sucesso")
        return redirect(url_for("disciplinas.listar"))

    conn.close()
    return render_template(
        "disciplinas/form.html", disciplina=disciplina, professores=professores, titulo="Editar Disciplina"
    )


@disciplinas_bp.route("/excluir/<int:id>", methods=["POST"])
def excluir(id):
    conn = get_conn()
    conn.execute("DELETE FROM disciplinas WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Disciplina excluída com sucesso!", "sucesso")
    return redirect(url_for("disciplinas.listar"))
