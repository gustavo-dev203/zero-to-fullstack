# Configuração do banco SQLite e inicialização de esquema.
import sqlite3
from pathlib import Path


def get_db(db_path: str) -> sqlite3.Connection:
    # Abre conexão SQLite reutilizando row_factory para acesso por nome de coluna.
    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: str) -> None:
    # Cria o diretório do banco se necessário e inicializa o esquema.
    database_path = Path(db_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)

    connection = get_db(db_path)
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            priority TEXT NOT NULL,
            due_date TEXT,
            status TEXT NOT NULL DEFAULT 'pendente',
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS login_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            attempts INTEGER NOT NULL DEFAULT 0,
            last_attempt TEXT NOT NULL
        )
        """
    )

    # Confirma todas as alterações e fecha a conexão.
    connection.commit()
    connection.close()


if __name__ == "__main__":
    import os

    # Executa a inicialização do banco quando o arquivo é chamado diretamente.
    path = os.path.join(os.path.dirname(__file__), "app.db")
    init_db(path)
    print("Banco inicializado em", path)
