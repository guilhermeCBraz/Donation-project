# 🍎 Donation Project - Sistema de Doação de Alimentos

Sistema completo de troca e doação de alimentos conectando doadores com ONGs que necessitam de ajuda.

## 🎯 Funcionalidades

### Para Clientes (Doadores)
- ✅ Cadastro e login
- ✅ Visualização de ONGs cadastradas
- ✅ Visualização das necessidades de alimentos de cada ONG
- ✅ Sistema de prioridades (Urgente, Alta, Média, Baixa)
- ✅ Realização de doações
- ✅ Acompanhamento de doações realizadas
- ✅ Filtros por categoria e busca

### Para ONGs
- ✅ Cadastro e login
- ✅ Dashboard com estatísticas
- ✅ Gerenciamento de necessidades de alimentos
- ✅ Acompanhamento de doações recebidas
- ✅ Controle de quantidade necessária vs recebida
- ✅ Sistema de prioridades para alimentos

### Administração
- ✅ Painel administrativo completo
- ✅ Gerenciamento de usuários, ONGs, alimentos
- ✅ Controle de doações e necessidades
- ✅ Categorização de alimentos

## 🚀 Características Técnicas

- **Django 5.2.8** - Framework web Python moderno
- **Django REST Framework** - API REST completa
- **CORS Headers** - Suporte para requisições cross-origin
- **Pillow** - Processamento de imagens
- **Python Decouple** - Gerenciamento de variáveis de ambiente
- **Modelo de Usuário Customizado** - Diferenciação entre Clientes e ONGs
- **SQLite** - Banco de dados (desenvolvimento)

## 📋 Pré-requisitos

- Python 3.10+
- pip

## ⚙️ Instalação

1. Clone o repositório
```bash
cd /home/guilherme/Documentos/programacao/Donation-project
```

2. Crie e ative o ambiente virtual (já criado)
```bash
source .venv/bin/activate
```

3. Instale as dependências
```bash
pip install -r requirements.txt
```

4. Execute as migrações
```bash
python manage.py migrate
```

5. Popule o banco com dados de exemplo
```bash
python manage.py popular_bd
```

6. Inicie o servidor de desenvolvimento
```bash
python manage.py runserver
```

## 🌐 Acessos

- **Home**: http://127.0.0.1:8000/
- **Login**: http://127.0.0.1:8000/login/
- **Cadastro**: http://127.0.0.1:8000/register/
- **Admin**: http://127.0.0.1:8000/admin/
- **API Status**: http://127.0.0.1:8000/api/status/

## 👥 Contas de Teste

Após rodar `python manage.py popular_bd`:

### Administrador
- **Usuário**: admin
- **Senha**: admin123

### Cliente (Doador)
- **Usuário**: joao
- **Senha**: senha123

### ONGs
- **ONG Esperança**
  - Usuário: ong_esperanca
  - Senha: senha123
  
- **Instituto Solidariedade**
  - Usuário: ong_solidaria
  - Senha: senha123

## 📁 Estrutura do Projeto

```
donation_project/
├── core/                      # App principal
│   ├── management/           # Comandos personalizados
│   │   └── commands/
│   │       └── popular_bd.py # Popula banco com dados
│   ├── migrations/           # Migrações do banco
│   ├── templates/            # Templates HTML
│   │   └── core/
│   │       ├── base.html
│   │       ├── home.html
│   │       ├── login.html
│   │       ├── register.html
│   │       ├── dashboard_cliente.html
│   │       ├── dashboard_ong.html
│   │       ├── doar_alimento.html
│   │       ├── minhas_doacoes.html
│   │       └── ong_detalhes.html
│   ├── admin.py             # Configuração admin
│   ├── models.py            # Modelos de dados
│   ├── views.py             # Views
│   └── urls.py              # URLs do app
├── donation_project/         # Configurações do projeto
│   ├── settings.py          # Configurações
│   ├── urls.py              # URLs principais
│   └── wsgi.py              # WSGI config
├── manage.py                # Gerenciador Django
├── requirements.txt         # Dependências
└── README.md               # Este arquivo
```

## 🗃️ Modelos de Dados

### User (Usuário Customizado)
- username, email, senha
- user_type: 'cliente' ou 'ong'
- telefone, endereço

### ONG
- user (OneToOne com User)
- nome, cnpj, descrição
- endereço completo
- telefone, email, responsável
- foto, status ativa

### CategoriaAlimento
- nome, descrição

### Alimento
- nome, categoria
- descrição
- unidade_medida (kg, g, l, ml, un, cx, pct)

### NecessidadeAlimento
- ong, alimento
- quantidade_necessaria, quantidade_recebida
- prioridade (baixa, media, alta, urgente)
- observações, status ativa

### Doacao
- doador, ong, alimento
- quantidade
- status (pendente, confirmada, em_transito, entregue, cancelada)
- mensagem, datas

## 🛠️ Comandos Úteis

```bash
# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Popular banco com dados de exemplo
python manage.py popular_bd

# Coletar arquivos estáticos
python manage.py collectstatic

# Iniciar servidor
python manage.py runserver

# Shell interativo
python manage.py shell
```

## 🎨 Fluxo de Uso

### Cliente
1. Cadastra-se como "Cliente"
2. Faz login
3. Visualiza ONGs e suas necessidades
4. Seleciona um alimento para doar
5. Informa quantidade e mensagem (opcional)
6. Confirma doação
7. Acompanha status no histórico

### ONG
1. Cadastra-se como "ONG"
2. Administrador cria perfil de ONG no admin
3. Faz login
4. Adiciona necessidades de alimentos via admin
5. Visualiza doações recebidas
6. Atualiza status das doações

## 📊 Dados de Exemplo

O comando `popular_bd` cria:
- 1 superusuário
- 1 cliente
- 2 ONGs com perfis completos
- 5 categorias de alimentos
- 16 tipos de alimentos
- 10 necessidades de alimentos (distribuídas entre as ONGs)

## 🔒 Segurança

- Autenticação Django completa
- Proteção CSRF
- Separação de permissões entre clientes e ONGs
- Validações de dados
- User model customizado

## 🌟 Próximos Passos Sugeridos

- [ ] Sistema de notificações por email
- [ ] Upload de fotos para ONGs
- [ ] Sistema de avaliação de ONGs
- [ ] Dashboard com gráficos
- [ ] Exportação de relatórios
- [ ] API REST completa
- [ ] Aplicativo mobile

## 📝 Licença

Este projeto está sob a licença MIT.

---

**Desenvolvido com ❤️ para ajudar quem precisa**
