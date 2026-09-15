from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_conn

professores_bp = Blueprint("professores", __name__, url_prefix="/professores")


@professores_bp.route("/")
def listar():
    conn = get_conn()
    busca = request.args.get("busca", "").strip()
    if busca:
        professores = conn.execute(
            "SELECT * FROM professores WHERE nome LIKE ? OR especialidade LIKE ? ORDER BY nome",
            (f"%{busca}%", f"%{busca}%"),
        ).fetchall()
    else:
        professores = conn.execute("SELECT * FROM professores ORDER BY nome").fetchall()
    conn.close()
    return render_template("professores/list.html", professores=professores, busca=busca)


@professores_bp.route("/novo", methods=["GET", "POST"])
def novo():
    if request.method == "POST":
        nome = request.form["nome"].strip()
        email = request.form["email"].strip()
        especialidade = request.form["especialidade"].strip()
        foto = request.form.get("foto", "").strip() or f"https://i.pravatar.cc/150?u={email}"

        if not nome or not email or not especialidade:
            flash("Preencha todos os campos obrigatórios!", "erro")
            return redirect(url_for("professores.novo"))

        conn = get_conn()
        conn.execute(
            "INSERT INTO professores (nome, email, especialidade, foto) VALUES (?, ?, ?, ?)",
            (nome, email, especialidade, foto),
        )
        conn.commit()
        conn.close()
        flash("Professor cadastrado com sucesso!", "sucesso")
        return redirect(url_for("professores.listar"))

    return render_template("professores/form.html", professor=None, titulo="Novo Professor")


@professores_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conn = get_conn()
    professor = conn.execute("SELECT * FROM professores WHERE id = ?", (id,)).fetchone()
    if professor is None:
        conn.close()
        flash("Professor não encontrado!", "erro")
        return redirect(url_for("professores.listar"))

    if request.method == "POST":
        nome = request.form["nome"].strip()
        email = request.form["email"].strip()
        especialidade = request.form["especialidade"].strip()
        foto = request.form.get("foto", "").strip() or professor["foto"]

        conn.execute(
            "UPDATE professores SET nome=?, email=?, especialidade=?, foto=? WHERE id=?",
            (nome, email, especialidade, foto, id),
        )
        conn.commit()
        conn.close()
        flash("Professor atualizado com sucesso!", "sucesso")
        return redirect(url_for("professores.listar"))

    conn.close()
    return render_template("professores/form.html", professor=professor, titulo="Editar Professor")


@professores_bp.route("/excluir/<int:id>", methods=["POST"])
def excluir(id):
    conn = get_conn()
    conn.execute("DELETE FROM professores WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Professor excluído com sucesso!", "sucesso")
    return redirect(url_for("professores.listar"))


@professores_bp.route("/perfil/<int:id>")
def perfil(id):
    conn = get_conn()
    professor = conn.execute("SELECT * FROM professores WHERE id = ?", (id,)).fetchone()
    if professor is None:
        conn.close()
        flash("Professor não encontrado!", "erro")
        return redirect(url_for("professores.listar"))

    disciplinas = conn.execute(
        "SELECT * FROM disciplinas WHERE professor_id = ? ORDER BY nome", (id,)
    ).fetchall()
    conn.close()
    return render_template("professores/perfil.html", professor=professor, disciplinas=disciplinas)
