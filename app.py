# Flask application entry point and route definitions.
# Este arquivo configura o app, a segurança e define as rotas da aplicação.
import os
import secrets
from datetime import datetime, timedelta, timezone
from flask import (
    Flask,
    g,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    abort,
)
from flask_talisman import Talisman
from auth import (
    authenticate_user,
    get_current_user,
    get_login_block_message,
    is_login_allowed,
    login_required,
    login_user,
    logout_user,
    register_user,
    validate_email,
)
from database import get_db, init_db
from models import Task, validate_task_data, validate_task_status


def load_env_file(path: str = ".env") -> None:
    """Carrega variáveis de ambiente a partir de um arquivo .env local."""
    if not os.path.exists(path):
        return

    with open(path, "r", encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


load_env_file()

# Cria a aplicação Flask e aplica configurações básicas de sessão e ambiente.
app = Flask(__name__, template_folder="templates", static_folder="static")
# Configura ENV e DEBUG antes de usar na validação de chave secreta.
app.config["ENV"] = os.environ.get("FLASK_ENV", "development").lower()
app.config["DEBUG"] = app.config["ENV"] == "development" or os.environ.get("FLASK_DEBUG", "0") == "1"
# Chave secreta usada para sessões, cookies assinados e proteção CSRF.
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
if not app.secret_key:
    if app.config["ENV"] == "production":
        raise ValueError("FLASK_SECRET_KEY deve estar definida em produção.")
    app.secret_key = secrets.token_urlsafe(32)
    print("[WARN] FLASK_SECRET_KEY não definido; usando chave temporária apenas para desenvolvimento.")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# O comportamento padrão de produção exige HTTPS explícito via FLASK_FORCE_HTTPS.
# Isso evita que testes locais em modo production que usem HTTP falhem com cookies seguros.
force_https = os.environ.get("FLASK_FORCE_HTTPS", "0").lower() in ("1", "true", "yes")
if app.config["ENV"] == "production" and not app.config["DEBUG"] and not force_https:
    print("[WARN] Modo production detectado, mas HTTPS não está ativado. Defina FLASK_FORCE_HTTPS=1 em produção real.")

app.config["SESSION_COOKIE_SECURE"] = force_https
# Define o esquema de URL preferido como HTTP para uso local.
app.config["PREFERRED_URL_SCHEME"] = "http"

# Configuração de segurança HTTP usando Flask-Talisman.
# Em ambiente de desenvolvimento, não redirecionamos para HTTPS automaticamente.
force_https = force_https

if app.config["DEBUG"]:
    print("[INFO] Rodando em modo de desenvolvimento. HTTPS não será forçado.")

# Define políticas de segurança de conteúdo e cabeçalhos HTTP.
talisman = Talisman(
    app,
    content_security_policy={
        "default-src": "'self'",
        "script-src": "'self'",
        "style-src": "'self'",
    },
    force_https=force_https,
    strict_transport_security=False,
    frame_options="DENY",
    x_content_type_options="nosniff",
    referrer_policy="strict-origin-when-cross-origin",
)

# Caminho para o arquivo SQLite local.
DEFAULT_DATABASE_PATH = os.path.join(os.path.dirname(__file__), "app.db")
app.config["DATABASE_PATH"] = os.environ.get("FLASK_DATABASE_PATH", DEFAULT_DATABASE_PATH)

RATE_LIMIT_MAX = 18
RATE_LIMIT_WINDOW_SECONDS = 300
RATE_LIMIT_BLOCK_SECONDS = 900
_rate_limit_store = {}


def create_app(test_config=None):
    if test_config:
        app.config.update(test_config)
    return app

def enforce_login_rate_limit():
    ip = request.remote_addr or "unknown"
    now = datetime.now(timezone.utc)
    state = _rate_limit_store.get(ip, {
        "count": 0,
        "first_request": now,
        "blocked_until": None,
    })

    if state["blocked_until"] and now < state["blocked_until"]:
        abort(429, "Muitas solicitações de login. Tente novamente em alguns minutos.")

    if (now - state["first_request"]).total_seconds() > RATE_LIMIT_WINDOW_SECONDS:
        state = {"count": 0, "first_request": now, "blocked_until": None}

    state["count"] += 1

    if state["count"] > RATE_LIMIT_MAX:
        state["blocked_until"] = now + timedelta(seconds=RATE_LIMIT_BLOCK_SECONDS)
        _rate_limit_store[ip] = state
        abort(429, "Muitas solicitações de login. Tente novamente em alguns minutos.")

    _rate_limit_store[ip] = state


@app.before_request
def before_request():
    # Abre conexão com o banco antes de cada requisição.
    g.db = get_db(app.config["DATABASE_PATH"])
    # Limita tentativas de login por IP para reduzir ataques de força bruta.
    if request.endpoint == "login" and request.method == "POST":
        enforce_login_rate_limit()

    # Garante que exista um token CSRF para formulários.
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(24)

    # Valida CSRF para todas as requisições POST.
    if request.method == "POST":
        token = request.form.get("csrf_token", "")
        if not token or token != session.get("csrf_token"):
            abort(400, "CSRF token inválido.")


@app.context_processor
def inject_csrf_token():
    # Disponibiliza o token CSRF em todos os templates.
    return {"csrf_token": session.get("csrf_token", "")}


@app.context_processor
def inject_current_user():
    # Disponibiliza o usuário atual em todos os templates.
    return {"user": get_current_user()}


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "db", None)
    if db is not None:
        db.close()


@app.cli.command("init-db")
def init_db_command():
    # Comando CLI para inicializar o banco de dados local.
    init_db(app.config["DATABASE_PATH"])
    print("Banco de dados inicializado.")


@app.route("/")
@login_required
def index():
    # Página inicial que lista as tarefas do usuário autenticado.
    user = get_current_user()
    if user is None:
        session.clear()
        flash("Sessão inválida. Faça login novamente.", "warning")
        return redirect(url_for("login"))

    search_query = request.args.get("query", "").strip()
    priority_filter = request.args.get("priority")
    status_filter = request.args.get("status")

    sql = "SELECT * FROM tasks WHERE user_id = ?"
    params = [user["id"]]

    if search_query:
        sql += " AND title LIKE ?"
        params.append(f"%{search_query}%")

    if priority_filter in ("baixa", "media", "alta"):
        sql += " AND priority = ?"
        params.append(priority_filter)

    if status_filter in ("pendente", "concluida"):
        sql += " AND status = ?"
        params.append(status_filter)

    sql += " ORDER BY due_date IS NULL, due_date ASC, created_at DESC"
    rows = g.db.execute(sql, params).fetchall()
    tasks = [Task.from_row(row).to_dict() for row in rows]

    return render_template(
        "index.html",
        user=user,
        tasks=tasks,
        search_query=search_query,
        priority_filter=priority_filter,
        status_filter=status_filter,
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    # Página de registro de usuário.
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        password_confirm = request.form.get("password_confirm", "")

        if not name or not email or not password:
            flash("Nome, email e senha são obrigatórios.", "danger")
        elif not validate_email(email):
            flash("Email inválido ou domínio não existe.", "danger")
        elif password != password_confirm:
            flash("As senhas não coincidem.", "danger")
        elif register_user(g.db, name, email, password):
            flash("Conta criada com sucesso. Faça login.", "success")
            return redirect(url_for("login"))
        else:
            flash("Não foi possível registrar. O email já existe ou os dados são inválidos.", "danger")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Página de login para autenticar o usuário.
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not is_login_allowed(g.db, email):
            message = get_login_block_message(g.db, email)
            flash(message or "Conta bloqueada temporariamente.", "danger")
        else:
            user = authenticate_user(g.db, email, password)
            if user:
                login_user(user["id"])
                flash("Login realizado com sucesso.", "success")
                return redirect(url_for("index"))

            if get_login_block_message(g.db, email):
                flash(get_login_block_message(g.db, email), "danger")
            else:
                flash("Email ou senha incorretos.", "danger")

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    # Encerra a sessão do usuário atual.
    logout_user()
    flash("Você saiu da sessão.", "info")
    return redirect(url_for("login"))


@app.route("/task/new", methods=["GET", "POST"])
@login_required
def task_create():
    # Rota de criação de nova tarefa para o usuário logado.
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        priority = request.form.get("priority", "baixa")
        due_date = request.form.get("due_date", None)

        if due_date:
            try:
                due_date_obj = datetime.strptime(due_date, "%Y-%m-%d").date()
            except ValueError:
                flash("Data de conclusão inválida.", "danger")
                return render_template("task_form.html", form_action=url_for("task_create"), task=None)

            if due_date_obj < datetime.utcnow().date():
                flash("Não é possível criar uma tarefa com data de conclusão no passado.", "danger")
                return render_template("task_form.html", form_action=url_for("task_create"), task=None)

        if not validate_task_data(title, description, priority):
            flash("Dados da tarefa inválidos. Verifique os campos e tente novamente.", "danger")
            return render_template("task_form.html", form_action=url_for("task_create"), task=None)

        created_at = datetime.now(timezone.utc).isoformat()
        user = get_current_user()

        g.db.execute(
            "INSERT INTO tasks (user_id, title, description, priority, due_date, status, created_at) VALUES (?, ?, ?, ?, ?, 'pendente', ?)",
            (user["id"], title, description, priority, due_date if due_date else None, created_at),
        )
        g.db.commit()
        flash("Tarefa criada com sucesso.", "success")
        return redirect(url_for("index"))

    return render_template("task_form.html", form_action=url_for("task_create"), task=None)


@app.route("/task/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def task_edit(task_id):
    # Rota para editar uma tarefa existente.
    user = get_current_user()
    row = g.db.execute(
        "SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, user["id"])
    ).fetchone()

    if row is None:
        flash("Tarefa não encontrada.", "warning")
        return redirect(url_for("index"))

    task = Task.from_row(row)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        priority = request.form.get("priority", "baixa")
        due_date = request.form.get("due_date", None)
        status = request.form.get("status", "pendente")

        if due_date:
            try:
                due_date_obj = datetime.strptime(due_date, "%Y-%m-%d").date()
            except ValueError:
                flash("Data de conclusão inválida.", "danger")
                return render_template("task_form.html", form_action=url_for("task_edit", task_id=task_id), task=task)

            if due_date_obj < datetime.utcnow().date():
                flash("Não é possível definir uma data de conclusão no passado.", "danger")
                return render_template("task_form.html", form_action=url_for("task_edit", task_id=task_id), task=task)

        if not validate_task_data(title, description, priority) or not validate_task_status(status):
            flash("Dados da tarefa inválidos. Verifique os campos e tente novamente.", "danger")
            return render_template("task_form.html", form_action=url_for("task_edit", task_id=task_id), task=task)

        g.db.execute(
            "UPDATE tasks SET title = ?, description = ?, priority = ?, due_date = ?, status = ? WHERE id = ? AND user_id = ?",
            (title, description, priority, due_date if due_date else None, status, task_id, user["id"]),
        )
        g.db.commit()
        flash("Tarefa atualizada com sucesso.", "success")
        return redirect(url_for("index"))

    return render_template("task_form.html", form_action=url_for("task_edit", task_id=task_id), task=task)


@app.route("/task/<int:task_id>/delete", methods=["POST"])
@login_required
def task_delete(task_id):
    # Rota para excluir uma tarefa do usuário autenticado.
    user = get_current_user()
    g.db.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user["id"]))
    g.db.commit()
    flash("Tarefa removida.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    # Inicializa o banco local caso ainda não exista, e executa o servidor.
    if not os.path.exists(app.config["DATABASE_PATH"]):
        init_db(app.config["DATABASE_PATH"])
    app.run(debug=app.config["DEBUG"], host="127.0.0.1", port=5500)
