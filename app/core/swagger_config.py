from flasgger import Swagger

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "API Taciana Lan House",
        "description": "Documentação oficial dos endpoints REST do sistema de gestão da Lan House Taciana Variedades. Inclui autenticação JWT via Cookies HTTP-Only, persistência PostgreSQL e cache em memória com Redis.",
        "version": "3.0.0",
        "contact": {
            "name": "Murilo Costa Nascimento",
            "email": "murilodev07@gmail.com"
        }
    },
    "securityDefinitions": {
        "CookieAuth": {
            "type": "apiKey",
            "name": "access_token_cookie",  # Nome exato da chave do Flask-JWT-Extended
            "in": "cookie",
            "description": (
                "Esta API utiliza autenticação baseada em Cookies HTTP-Only para proteção contra XSS.\n\n"
                "**Como autenticar no Swagger UI:**\n"
                "1. Execute a rota `POST /auth/login` diretamente nesta documentação com credenciais válidas.\n"
                "2. O seu navegador armazenará o cookie de acesso automaticamente.\n"
                "3. Todas as rotas protegidas (com ícone de cadeado) passarão a funcionar nativamente.\n\n"
                "*Nota: O campo 'Value:' desta janela é gerado pelo padrão OpenAPI 2.0 e pode ser deixado em branco durante os testes no navegador.*"
            )
        }
    }
}

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda rule: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_router": "/apidocs/"
}

def init_swagger(app):
    """
    Inicializa a extensão Flasgger na instância da aplicação Flask.
    """
    return Swagger(app, template=swagger_template, config=swagger_config)