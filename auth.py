# Lógica de autenticação e validação de usuários.
# Este módulo cuida de registros, login, hashing de senha e proteção contra ataques de força bruta.
import re
import socket
import sqlite3
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import session, redirect, url_for, flash, g

EMAIL_PATTERN = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,}$"
)
MAX_FAILED_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


def hash_password(password: str) -> str:
    # Gera hash seguro para a senha usando bcrypt.
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password: str, hashed: str | bytes) -> bool:
    # Verifica se a senha informada corresponde ao hash armazenado.
    if isinstance(hashed, str):
        hashed = hashed.encode("utf-8")
    return bcrypt.checkpw(password.encode("utf-8"), hashed)


def has_valid_email_domain(domain: str) -> bool:
    # Verifica se o domínio do email resolve para um host válido.
    try:
        socket.getaddrinfo(domain, None)
        return True
    except socket.gaierror:
        return False


def validate_email(email: str) -> bool:
    # Valida o formato do email e verifica se o domínio existe.
    address = email.strip().lower()
    if not address or len(address) > 254:
        return False
    if not EMAIL_PATTERN.fullmatch(address):
        return False

    domain = address.split("@", 1)[1]
    return has_valid_email_domain(domain)


def get_login_attempt_row(db, email: str):
    # Retorna a linha de tentativas de login para controle de bloqueio.
    return db.execute(
        "SELECT attempts, last_attempt FROM login_attempts WHERE email = ?",
        (email.strip().lower(),),
    ).fetchone()


def is_login_allowed(db, email: str) -> bool:
    # Verifica se o usuário ainda pode tentar login ou se está temporariamente bloqueado.
    row = get_login_attempt_row(db, email)
    if row is None:
        return True

    if row["attempts"] < MAX_FAILED_LOGIN_ATTEMPTS:
        return True

    last_attempt = datetime.fromisoformat(row["last_attempt"])
    return datetime.utcnow() - last_attempt >= timedelta(minutes=LOCKOUT_MINUTES)


def get_login_block_message(db, email: str) -> str | None:
    # Retorna a mensagem de bloqueio se o usuário excedeu tentativas de login.
    row = get_login_attempt_row(db, email)
    if row is None or row["attempts"] < MAX_FAILED_LOGIN_ATTEMPTS:
        return None

    last_attempt = datetime.fromisoformat(row["last_attempt"])
    delta = datetime.utcnow() - last_attempt
    if delta >= timedelta(minutes=LOCKOUT_MINUTES):
        return None

    remaining_minutes = max(1, LOCKOUT_MINUTES - int(delta.total_seconds() // 60))
    return f"Conta bloqueada temporariamente. Tente novamente em {remaining_minutes} minuto(s)."


def record_login_attempt(db, email: str, success: bool) -> None:
    # Registra uma tentativa de login, resetando no sucesso e acumulando no erro.
    email = email.strip().lower()
    row = get_login_attempt_row(db, email)
    if success:
        if row is not None:
            db.execute("DELETE FROM login_attempts WHERE email = ?", (email,))
            db.commit()
        return

    now = datetime.utcnow().isoformat()
    if row is None:
        db.execute(
            "INSERT INTO login_attempts (email, attempts, last_attempt) VALUES (?, ?, ?)",
            (email, 1, now),
        )
    else:
        attempts = row["attempts"] + 1
        db.execute(
            "UPDATE login_attempts SET attempts = ?, last_attempt = ? WHERE email = ?",
            (attempts, now, email),
        )
    db.commit()


def register_user(db, email: str, password: str) -> bool:
    # Cadastra um novo usuário no banco, retornando True se bem-sucedido.
    email = email.strip().lower()
    if not email or not password or len(password) < 6 or not validate_email(email):
        return False

    password_hash = hash_password(password)
    created_at = datetime.utcnow().isoformat()

    try:
        db.execute(
            "INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)",
            (email, password_hash, created_at),
        )
        db.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception:
        return False


def authenticate_user(db, email: str, password: str):
    # Autentica usuário verificando email, senha e proteção contra bloqueio.
    email = email.strip().lower()
    if not is_login_allowed(db, email):
        return None

    row = db.execute(
        "SELECT id, email, password_hash FROM users WHERE email = ?",
        (email,),
    ).fetchone()

    if row is None:
        record_login_attempt(db, email, False)
        return None

    password_hash = row["password_hash"]
    if isinstance(password_hash, str):
        password_hash = password_hash.encode("utf-8")

    if check_password(password, password_hash):
        record_login_attempt(db, email, True)
        return {"id": row["id"], "email": row["email"]}

    record_login_attempt(db, email, False)
    return None


def login_required(view):
    # Decorator que exige autenticação para acessar uma rota.
    @wraps(view)
    def wrapped_view(**kwargs):
        if "user_id" not in session:
            flash("É preciso fazer login para acessar esta página.", "warning")
            return redirect(url_for("login"))

        if get_current_user() is None:
            session.clear()
            flash("Sessão inválida. Faça login novamente.", "warning")
            return redirect(url_for("login"))

        return view(**kwargs)

    return wrapped_view


def login_user(user_id: int):
    # Inicia a sessão do usuário armazenando seu ID.
    session.clear()
    session["user_id"] = user_id


def logout_user():
    # Remove dados de sessão para efetuar logout.
    session.clear()


def get_current_user():
    # Retorna os dados do usuário atualmente autenticado.
    user_id = session.get("user_id")
    if user_id is None:
        return None

    db = getattr(g, "db", None)
    if db is None:
        return None

    row = db.execute("SELECT id, email FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None:
        return None
    return {"id": row["id"], "email": row["email"]}
