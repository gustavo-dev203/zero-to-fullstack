# Task Manager Web App

Um sistema CRUD completo e seguro para gerenciamento de tarefas, desenvolvido em Python com Flask. Permite que usuários se registrem, façam login seguro com proteção contra força bruta e gerenciem suas tarefas pessoais. Ideal para aprender desenvolvimento web seguro e melhores práticas em Python.

## 📋 Funcionalidades

### Autenticação e Segurança
- **Registro e Login Seguros**: Autenticação com bcrypt, proteção contra força bruta (bloqueio temporário após 5 tentativas).
- **Validação de Email**: Verifica formato e domínio real (DNS lookup).
- **Proteção CSRF**: Token gerado por sessão para formulários.
- **Sessões Seguras**: HttpOnly, SameSite, Secure (em produção).

### Gerenciamento de Tarefas (CRUD)
- **Create**: Adicionar nova tarefa com título, descrição, prioridade (baixa/média/alta) e data de conclusão.
- **Read**: Listar tarefas do usuário com filtros por prioridade ou status.
- **Update**: Editar todas as propriedades de uma tarefa existente.
- **Delete**: Remover tarefas com confirmação.
- **Isolamento por Usuário**: Cada usuário vê apenas suas tarefas.

### Interface e UX
- Templates HTML5 com CSS responsivo.
- Mensagens flash para feedback de ações.
- Filtros e ordenação de tarefas.
- Design limpo e intuitivo.

## 🔐 Segurança

- **Hashing de Senhas**: bcrypt com salt aleatório.
- **Proteção contra SQL Injection**: Queries parametrizadas (SQLite).
- **Proteção contra XSS**: Jinja2 auto-escapes HTML por padrão.
- **CSRF Protection**: Token único por sessão.
- **Bloqueio por Tentativas Falhas**: 5 tentativas = 15 minutos bloqueado.
- **Headers HTTP Seguros**: CSP, X-Frame-Options, X-Content-Type-Options (Flask-Talisman).
- **Chave Secreta Configurável**: Via `FLASK_SECRET_KEY` em `.env`.

## 🛠 Tecnologias

- **Backend**: Python 3.x + Flask 2.3+
- **Banco de Dados**: SQLite com foreign keys habilitadas
- **Autenticação**: bcrypt (password hashing)
- **Segurança HTTP**: Flask-Talisman
- **Frontend**: HTML5 + CSS3 (sem frameworks JavaScript)
- **Gerenciamento de Ambientes**: `.env` com variáveis de configuração

## 📦 Pré-requisitos

- Python 3.8+ instalado
- Pip (gerenciador de pacotes)
- Git (opcional, para clonar o repositório)

## 🚀 Instalação

### 1. Clone ou baixe o projeto
```bash
git clone https://github.com/gustavo-dev203/zero-to-fullstack.git
cd zero-to-fullstack
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Configure o arquivo `.env` (IMPORTANTE)
Crie um arquivo `.env` na raiz do projeto:

```bash
cp .env.example .env
```

Edite `.env` e defina uma chave secreta segura:
```env
FLASK_SECRET_KEY=sua_chave_aleatoria_de_50_caracteres_aqui
FLASK_ENV=development
FLASK_DEBUG=1
```

**Como gerar uma chave segura:**

Python:
```python
import secrets
print(secrets.token_urlsafe(50))
```

PowerShell:
```powershell
$bytes = [System.Text.Encoding]::UTF8.GetBytes($(Get-Random -Minimum 100000 -Maximum 999999))
$key = [Convert]::ToBase64String($bytes)
Write-Host $key
```

### 4. Execute o servidor de desenvolvimento
```bash
python app.py
```

O app estará disponível em: **http://127.0.0.1:5500**

## 📖 Como Usar

### Primeiro Acesso
1. Clique em **"Registrar"** no navegador
2. Insira um email válido (com domínio real)
3. Crie uma senha com 6+ caracteres
4. Confirme a senha
5. Clique em **"Criar conta"**

### Login
1. Vá para a página de login
2. Insira email e senha
3. Clique em **"Entrar"**

### Gerenciar Tarefas
1. **Adicionar**: Clique em **"Nova Tarefa"**
   - Título (mín. 3 caracteres)
   - Descrição (mín. 5 caracteres)
   - Prioridade (baixa/média/alta)
   - Data de conclusão (opcional)

2. **Visualizar**: Lista principal mostra todas suas tarefas
   - Use filtros por prioridade ou status

3. **Editar**: Clique na tarefa para abrir o formulário de edição
   - Altere qualquer campo
   - Mude o status (pendente/concluída)

4. **Excluir**: Clique em "Remover" na tarefa desejada

5. **Logout**: Clique em **"Sair"** para encerrar sessão

## 📁 Estrutura do Projeto

```
task-manager/
├── app.py                  # Aplicação Flask - rotas e configuração
├── auth.py                 # Autenticação, hashing, validação
├── database.py             # Inicialização e conexão SQLite
├── models.py               # Classes e validação de dados
├── requirements.txt        # Dependências do projeto
│
├── templates/              # Templates HTML (Jinja2)
│   ├── base.html          # Template base (header, nav, footer)
│   ├── login.html         # Página de login
│   ├── register.html      # Página de registro
│   ├── index.html         # Lista de tarefas
│   └── task_form.html     # Formulário de criar/editar tarefa
│
├── static/                 # Arquivos estáticos
│   └── style.css          # CSS responsivo
│
├── .env                    # Variáveis de ambiente (gitignored)
├── .env.example           # Exemplo de variáveis (commitado)
├── .gitignore             # Arquivos ignorados pelo Git
│
└── README.md              # Este arquivo
```

## 🔧 Variáveis de Ambiente

### `.env.example` (modelo para versionar)
```env
FLASK_SECRET_KEY=troque_por_uma_chave_segura
FLASK_ENV=development
FLASK_DEBUG=1
```

### `.env` (seu arquivo local, nunca commitar)
```env
FLASK_SECRET_KEY=3:********************************
FLASK_ENV=development
FLASK_DEBUG=1
```

**Variáveis disponíveis:**
- `FLASK_SECRET_KEY`: Chave para assinar cookies e tokens CSRF (**OBRIGATÓRIO em produção**)
- `FLASK_ENV`: `development` ou `production` (define o modo)
- `FLASK_DEBUG`: `1` para ativar debug mode, `0` para desativar

## 🧪 Testes e Debugging

### Testar Manualmente
1. Abra http://127.0.0.1:5500
2. Registre uma conta com email válido
3. Faça login
4. Crie, edite e delete tarefas
5. Teste os filtros

### Verificar Erros
Erros aparecerão:
- No terminal (Flask dev server)
- No navegador (página de erro com stack trace)

### Testar Proteção contra Força Bruta
1. Tente login com senha incorreta 5 vezes
2. Receberá mensagem: "Conta bloqueada temporariamente. Tente novamente em 15 minuto(s)."
3. Após 15 minutos, poderá tentar novamente

### Inspecionar Banco de Dados
```bash
python
>>> import sqlite3
>>> conn = sqlite3.connect("app.db")
>>> conn.row_factory = sqlite3.Row
>>> cursor = conn.cursor()
>>> cursor.execute("SELECT email FROM users").fetchall()
```

## 🚢 Deploy em Produção

### Preparação
1. Defina um `FLASK_SECRET_KEY` forte (mínimo 50 caracteres aleatórios)
2. Mude `FLASK_ENV` para `production`
3. Mude `FLASK_DEBUG` para `0`
4. Configure HTTPS (certificado SSL/TLS)

### Servidor Recomendado: Gunicorn
```bash
pip install gunicorn
gunicorn --workers 4 --bind 0.0.0.0:8000 app:app
```

### Com Nginx (reverse proxy)
```nginx
server {
    listen 80;
    server_name seu-dominio.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Variáveis de Produção (.env)
```env
FLASK_SECRET_KEY=sua_chave_aleatoria_de_produção
FLASK_ENV=production
FLASK_DEBUG=0
```

## 📝 Arquivos Principais Explicados

### `app.py`
- Configura a aplicação Flask
- Carrega variáveis de `.env`
- Define rotas (login, registro, CRUD de tarefas)
- Implementa proteção CSRF e sessões
- Gerencia requests/responses

### `auth.py`
- `hash_password()`: Cria hash bcrypt
- `check_password()`: Verifica senha contra hash
- `validate_email()`: Valida formato e domínio (DNS)
- `register_user()`: Cadastra novo usuário
- `authenticate_user()`: Faz login com proteção contra força bruta
- `login_required`: Decorator para rotas protegidas

### `database.py`
- `get_db()`: Abre conexão SQLite
- `init_db()`: Cria tabelas (users, tasks, login_attempts)
- Habilita foreign keys automaticamente

### `models.py`
- Classe `Task`: Dataclass para representar tarefas
- `validate_task_data()`: Valida título, descrição, prioridade
- `validate_task_status()`: Valida status (pendente/concluída)

## 🛡️ Checklist de Segurança

- [x] Senhas hashed com bcrypt
- [x] Proteção contra SQL injection (queries parametrizadas)
- [x] Proteção contra XSS (Jinja2 auto-escape)
- [x] CSRF token em todos os formulários
- [x] Sessões HttpOnly e SameSite
- [x] Bloqueio por tentativas falhas
- [x] Validação de email (DNS)
- [x] Chave secreta configurável
- [x] Isolamento de dados por usuário
- [x] Headers HTTP seguro (CSP, X-Frame-Options)
- [x] Sem segredos hardcoded no código
- [x] `.env` no `.gitignore`

## 🐛 Troubleshooting

### Erro: "Chave FLASK_SECRET_KEY não definida"
**Solução**: Defina `FLASK_SECRET_KEY` em `.env` ou no terminal

### Erro: "Banco de dados 'app.db' não encontrado"
**Solução**: Execute `python app.py` uma vez para criar o banco

### Erro: "Email inválido ou domínio não existe"
**Solução**: Use um email com domínio real (gmail.com, hotmail.com, etc)

### Página não carrega em http://127.0.0.1:5500
**Solução**: Verifique se o servidor está rodando no terminal

### Não consigo fazer login mesmo com senha correta
**Solução**: Pode estar bloqueado por 5 tentativas falhas anteriores. Aguarde 15 minutos.

## 📞 Suporte e Contribuições

- **Issues**: Reporte bugs no GitHub
- **Pull Requests**: Contribuições são bem-vindas
- **Manutenção**: Este projeto foi desenvolvido com foco educacional

## 📄 Licença

Este projeto é fornecido como está para fins educacionais. Use sob sua responsabilidade.

## ✨ Agradecimentos

Desenvolvido com Python, Flask, SQLite e melhores práticas de segurança web.

---

**Última atualização**: 30 de Abril de 2026  
**Status**: ✅ Funcional e seguro para educação e prototipagem


Este projeto é para fins educacionais. Use sob sua responsabilidade.

## Suporte

Se encontrar erros, verifique os logs no terminal ou em `audit.log`. Para dúvidas, revise o código comentado.
