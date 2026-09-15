from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_conn

alunos_bp = Blueprint("alunos", __name__, url_prefix="/alunos")


@alunos_bp.route("/")
def listar():
    conn = get_conn()
    busca = request.args.get("busca", "").strip()
    if busca:
        alunos = conn.execute(
            "SELECT * FROM alunos WHERE nome LIKE ? OR turma LIKE ? ORDER BY nome",
            (f"%{busca}%", f"%{busca}%"),
        ).fetchall()
    else:
        alunos = conn.execute("SELECT * FROM alunos ORDER BY nome").fetchall()
    conn.close()
    return render_template("alunos/list.html", alunos=alunos, busca=busca)


@alunos_bp.route("/novo", methods=["GET", "POST"])
def novo():
    if request.method == "POST":
        nome = request.form["nome"].strip()
        idade = request.form["idade"].strip()
        email = request.form["email"].strip()
        turma = request.form["turma"].strip()
        foto = request.form.get("foto", "").strip() or f"https://i.pravatar.cc/150?u={email}"

        if not nome or not idade or not email or not turma:
            flash("Preencha todos os campos obrigatórios!", "erro")
            return redirect(url_for("alunos.novo"))

        conn = get_conn()
        conn.execute(
            "INSERT INTO alunos (nome, idade, email, turma, foto) VALUES (?, ?, ?, ?, ?)",
            (nome, idade, email, turma, foto),
        )
        conn.commit()
        conn.close()
        flash("Aluno cadastrado com sucesso!", "sucesso")
        return redirect(url_for("alunos.listar"))

    return render_template("alunos/form.html", aluno=None, titulo="Novo Aluno")


@alunos_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conn = get_conn()
    aluno = conn.execute("SELECT * FROM alunos WHERE id = ?", (id,)).fetchone()
    if aluno is None:
        conn.close()
        flash("Aluno não encontrado!", "erro")
        return redirect(url_for("alunos.listar"))

    if request.method == "POST":
        nome = request.form["nome"].strip()
        idade = request.form["idade"].strip()
        email = request.form["email"].strip()
        turma = request.form["turma"].strip()
        foto = request.form.get("foto", "").strip() or aluno["foto"]

        conn.execute(
            "UPDATE alunos SET nome=?, idade=?, email=?, turma=?, foto=? WHERE id=?",
            (nome, idade, email, turma, foto, id),
        )
        conn.commit()
        conn.close()
        flash("Aluno atualizado com sucesso!", "sucesso")
        return redirect(url_for("alunos.listar"))

    conn.close()
    return render_template("alunos/form.html", aluno=aluno, titulo="Editar Aluno")


@alunos_bp.route("/excluir/<int:id>", methods=["POST"])
def excluir(id):
    conn = get_conn()
    conn.execute("DELETE FROM alunos WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Aluno excluído com sucesso!", "sucesso")
    return redirect(url_for("alunos.listar"))


@alunos_bp.route("/perfil/<int:id>")
def perfil(id):
    conn = get_conn()
    aluno = conn.execute("SELECT * FROM alunos WHERE id = ?", (id,)).fetchone()
    if aluno is None:
        conn.close()
        flash("Aluno não encontrado!", "erro")
        return redirect(url_for("alunos.listar"))

    disciplinas = conn.execute(
        """
        SELECT d.*, p.nome as professor_nome
        FROM disciplinas d
        JOIN matriculas m ON m.disciplina_id = d.id
        LEFT JOIN professores p ON p.id = d.professor_id
        WHERE m.aluno_id = ?
        ORDER BY d.nome
        """,
        (id,),
    ).fetchall()
    conn.close()
    return render_template("alunos/perfil.html", aluno=aluno, disciplinas=disciplinas)
