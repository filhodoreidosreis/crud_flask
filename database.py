import sqlite3

DB_NAME = "escola.db"


def get_conn():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(seed=False):
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS professores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL,
            especialidade TEXT NOT NULL,
            foto TEXT
        );

        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            idade INTEGER NOT NULL,
            email TEXT NOT NULL,
            turma TEXT NOT NULL,
            foto TEXT
        );

        CREATE TABLE IF NOT EXISTS disciplinas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            carga_horaria INTEGER NOT NULL,
            professor_id INTEGER,
            FOREIGN KEY (professor_id) REFERENCES professores(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS horarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disciplina_id INTEGER NOT NULL,
            dia_semana TEXT NOT NULL,
            hora_inicio TEXT NOT NULL,
            hora_fim TEXT NOT NULL,
            sala TEXT NOT NULL,
            FOREIGN KEY (disciplina_id) REFERENCES disciplinas(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS matriculas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id INTEGER NOT NULL,
            disciplina_id INTEGER NOT NULL,
            data_matricula TEXT DEFAULT CURRENT_DATE,
            FOREIGN KEY (aluno_id) REFERENCES alunos(id) ON DELETE CASCADE,
            FOREIGN KEY (disciplina_id) REFERENCES disciplinas(id) ON DELETE CASCADE,
            UNIQUE(aluno_id, disciplina_id)
        );
    """)
    conn.commit()

    if seed:
        _seed_data(conn)
    conn.close()


def _seed_data(conn):
    existentes = conn.execute("SELECT COUNT(*) c FROM professores").fetchone()["c"]
    if existentes > 0:
        return

    professores = [
        ("Carlos Mendes", "carlos.mendes@escola.com", "Matemática", "https://i.pravatar.cc/150?img=12"),
        ("Ana Ferreira", "ana.ferreira@escola.com", "Português", "https://i.pravatar.cc/150?img=47"),
        ("Roberto Alves", "roberto.alves@escola.com", "História", "https://i.pravatar.cc/150?img=33"),
        ("Juliana Costa", "juliana.costa@escola.com", "Programação", "https://i.pravatar.cc/150?img=45"),
    ]
    conn.executemany(
        "INSERT INTO professores (nome, email, especialidade, foto) VALUES (?, ?, ?, ?)",
        professores,
    )

    alunos = [
        ("Pedro Souza", 19, "pedro.souza@aluno.com", "ADS-2A", "https://i.pravatar.cc/150?img=51"),
        ("Mariana Lima", 20, "mariana.lima@aluno.com", "ADS-2A", "https://i.pravatar.cc/150?img=25"),
        ("Lucas Oliveira", 22, "lucas.oliveira@aluno.com", "ADS-3B", "https://i.pravatar.cc/150?img=14"),
        ("Beatriz Santos", 18, "beatriz.santos@aluno.com", "ADS-1A", "https://i.pravatar.cc/150?img=32"),
    ]
    conn.executemany(
        "INSERT INTO alunos (nome, idade, email, turma, foto) VALUES (?, ?, ?, ?, ?)",
        alunos,
    )
    conn.commit()

    disciplinas = [
        ("Cálculo I", 80, 1),
        ("Redação e Comunicação", 60, 2),
        ("História da Tecnologia", 40, 3),
        ("Programação Web", 100, 4),
        ("Banco de Dados", 80, 4),
    ]
    conn.executemany(
        "INSERT INTO disciplinas (nome, carga_horaria, professor_id) VALUES (?, ?, ?)",
        disciplinas,
    )
    conn.commit()

    horarios = [
        (1, "Segunda", "08:00", "10:00", "Sala 101"),
        (2, "Terça", "10:00", "12:00", "Sala 102"),
        (3, "Quarta", "14:00", "16:00", "Sala 103"),
        (4, "Quinta", "19:00", "21:00", "Lab 01"),
        (5, "Sexta", "19:00", "21:00", "Lab 02"),
    ]
    conn.executemany(
        "INSERT INTO horarios (disciplina_id, dia_semana, hora_inicio, hora_fim, sala) VALUES (?, ?, ?, ?, ?)",
        horarios,
    )
    conn.commit()

    matriculas = [(1, 1), (1, 4), (2, 1), (2, 2), (3, 4), (3, 5), (4, 2), (4, 3)]
    conn.executemany(
        "INSERT INTO matriculas (aluno_id, disciplina_id) VALUES (?, ?)",
        matriculas,
    )
    conn.commit()
