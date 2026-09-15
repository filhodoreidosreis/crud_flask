from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_conn

horarios_bp = Blueprint("horarios", __name__, url_prefix="/horarios")

DIAS_SEMANA = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"]


@horarios_bp.route("/")
def listar():
    conn = get_conn()
    horarios = conn.execute(
        """
        SELECT h.*, d.nome as disciplina_nome, p.nome as professor_nome
        FROM horarios h
        JOIN disciplinas d ON d.id = h.disciplina_id
        LEFT JOIN professores p ON p.id = d.professor_id
        ORDER BY
            CASE h.dia_semana
                WHEN 'Segunda' THEN 1 WHEN 'Terça' THEN 2 WHEN 'Quarta' THEN 3
                WHEN 'Quinta' THEN 4 WHEN 'Sexta' THEN 5 ELSE 6
            END, h.hora_inicio
        """
    ).fetchall()
    conn.close()
    return render_template("horarios/list.html", horarios=horarios)


@horarios_bp.route("/grade")
def grade():
    conn = get_conn()
    horarios = conn.execute(
        """
        SELECT h.*, d.nome as disciplina_nome, p.nome as professor_nome
        FROM horarios h
        JOIN disciplinas d ON d.id = h.disciplina_id
        LEFT JOIN professores p ON p.id = d.professor_id
        ORDER BY h.hora_inicio
        """
    ).fetchall()
    conn.close()

    grade_dados = {dia: [] for dia in DIAS_SEMANA}
    for h in horarios:
        if h["dia_semana"] in grade_dados:
            grade_dados[h["dia_semana"]].append(h)

    return render_template("horarios/grade.html", grade_dados=grade_dados, dias=DIAS_SEMANA)


@horarios_bp.route("/novo", methods=["GET", "POST"])
def novo():
    conn = get_conn()
    disciplinas = conn.execute("SELECT * FROM disciplinas ORDER BY nome").fetchall()

    if request.method == "POST":
        disciplina_id = request.form["disciplina_id"]
        dia_semana = request.form["dia_semana"]
        hora_inicio = request.form["hora_inicio"]
        hora_fim = request.form["hora_fim"]
        sala = request.form["sala"].strip()

        if not disciplina_id or not dia_semana or not hora_inicio or not hora_fim or not sala:
            conn.close()
            flash("Preencha todos os campos!", "erro")
            return redirect(url_for("horarios.novo"))

        conn.execute(
            "INSERT INTO horarios (disciplina_id, dia_semana, hora_inicio, hora_fim, sala) VALUES (?, ?, ?, ?, ?)",
            (disciplina_id, dia_semana, hora_inicio, hora_fim, sala),
        )
        conn.commit()
        conn.close()
        flash("Horário cadastrado com sucesso!", "sucesso")
        return redirect(url_for("horarios.listar"))

    conn.close()
    return render_template(
        "horarios/form.html", horario=None, disciplinas=disciplinas, dias=DIAS_SEMANA, titulo="Novo Horário"
    )


@horarios_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conn = get_conn()
    horario = conn.execute("SELECT * FROM horarios WHERE id = ?", (id,)).fetchone()
    if horario is None:
        conn.close()
        flash("Horário não encontrado!", "erro")
        return redirect(url_for("horarios.listar"))

    disciplinas = conn.execute("SELECT * FROM disciplinas ORDER BY nome").fetchall()

    if request.method == "POST":
        disciplina_id = request.form["disciplina_id"]
        dia_semana = request.form["dia_semana"]
        hora_inicio = request.form["hora_inicio"]
        hora_fim = request.form["hora_fim"]
        sala = request.form["sala"].strip()

        conn.execute(
            "UPDATE horarios SET disciplina_id=?, dia_semana=?, hora_inicio=?, hora_fim=?, sala=? WHERE id=?",
            (disciplina_id, dia_semana, hora_inicio, hora_fim, sala, id),
        )
        conn.commit()
        conn.close()
        flash("Horário atualizado com sucesso!", "sucesso")
        return redirect(url_for("horarios.listar"))

    conn.close()
    return render_template(
        "horarios/form.html", horario=horario, disciplinas=disciplinas, dias=DIAS_SEMANA, titulo="Editar Horário"
    )


@horarios_bp.route("/excluir/<int:id>", methods=["POST"])
def excluir(id):
    conn = get_conn()
    conn.execute("DELETE FROM horarios WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Horário excluído com sucesso!", "sucesso")
    return redirect(url_for("horarios.listar"))
