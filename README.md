# Task Manager Web App

Aplicação web de gerenciamento de tarefas construída com Python e Flask, com foco em segurança, usabilidade e testes.

## 📋 Recursos Principais

### Autenticação e Segurança
- Cadastro e login seguro com hashing de senha via **bcrypt**
- Validação de email com verificação de domínio real
- Proteção CSRF baseada em token de sessão
- Sessões configuradas com **HttpOnly** e **SameSite=Lax**
- Cookies `Secure` habilitados quando `FLASK_FORCE_HTTPS=1`
- Redução de ataques de força bruta com bloqueio após 5 tentativas
- Cabeçalhos HTTP de segurança via **Flask-Talisman**

### Gestão de Tarefas
- CRUD completo de tarefas
- Título, descrição, prioridade, data de conclusão e status
- Validação de campos e rejeição de datas de conclusão no passado
- Filtros de lista por prioridade e status
- Cada usuário acessa somente suas próprias tarefas

### UX e Responsividade
- Interface limpa em HTML + CSS
- Layout responsivo para desktop e mobile
- Mensagens flash para feedback instantâneo
- Menu de perfil e ações rápidas intuitivas

## 🛠 Arquitetura do Projeto

- `app.py` — configuração do Flask, rotas e segurança
- `auth.py` — cadastro, login, bloqueio de tentativas e validações
- `database.py` — conexão SQLite e esquema de inicialização
- `models.py` — dataclass de tarefas e validações de dados
- `templates/` — frontend com Jinja2
- `static/style.css` — estilo e responsividade
- `tests/` — suíte de testes `unittest`

## 📦 Dependências

As dependências estão em `requirements.txt`:
- Flask>=2.3.0
- bcrypt>=4.0.0
- Flask-Talisman>=1.1.0

## ⚙️ Configuração do Ambiente

O projeto usa um arquivo `.env` para variáveis de configuração. Existe um modelo em `.env.example`.

### Variáveis suportadas
- `FLASK_SECRET_KEY` — chave secreta para sessões e CSRF (**obrigatório em produção**)
- `FLASK_ENV` — `development` ou `production`
- `FLASK_DEBUG` — `1` ou `0`
- `FLASK_FORCE_HTTPS` — `1` para forçar HTTPS em produção
- `FLASK_DATABASE_PATH` — caminho opcional para usar outro arquivo SQLite

### Exemplo `.env`
```env
FLASK_SECRET_KEY=troque_por_uma_chave_segura
FLASK_ENV=development
FLASK_DEBUG=1
```

## 🚀 Instalação e Execução

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Criar `.env`
```bash
copy .env.example .env
```

### 3. Executar o servidor
```bash
python app.py
```

Acesse: **http://127.0.0.1:5500**

## 🧪 Testes

O projeto agora possui uma suíte de testes em `tests/`.

Execute todos os testes com:
```bash
python -m unittest discover -s tests -p 'test_*.py'
```

### O que já está testado
- Esquema e inicialização do banco SQLite
- Validação de dados de tarefas
- Registro e login com bloqueio por tentativas falhas
- Rotas básicas do Flask e proteção CSRF

## 📁 Estrutura Atual do Repositório

```
.
├── app.py
├── auth.py
├── database.py
├── models.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── index.html
│   └── task_form.html
├── static/
│   └── style.css
└── tests/
    ├── test_app.py
    ├── test_auth.py
    ├── test_database.py
    └── test_models.py
```

## 🚢 Deploy em Produção

### Passos mínimos
1. Defina `FLASK_SECRET_KEY` forte e seguro
2. Configure `FLASK_ENV=production`
3. Defina `FLASK_DEBUG=0`
4. Use HTTPS e `FLASK_FORCE_HTTPS=1`

### Sugestão de execução
```bash
pip install gunicorn
gunicorn --workers 4 --bind 0.0.0.0:8000 app:app
```

### Exemplo básico com Nginx
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

## ✅ Mudanças recentes refletidas no README

- Inclusão da suíte de testes e instruções de execução
- Documentação do `FLASK_DATABASE_PATH`
- Descrição da geração de chave temporária em desenvolvimento
- Atualização da arquitetura e dos arquivos do projeto
- Registro das melhorias de segurança e responsividade
