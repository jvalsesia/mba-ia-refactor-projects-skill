"""Layer 6 — Composition root (P-05). Loads config, constructs the single DB
connection, injects it into repositories, wires controllers and routes, and
registers the centralized error handler. Nothing self-instantiates a global
connection at import time."""
from flask import Flask
from flask_cors import CORS

from config import settings
from models.db import create_connection, init_schema, seed_if_empty
from models.produto import ProdutoRepository
from models.usuario import UsuarioRepository
from models.pedido import PedidoRepository
from models.system import SystemRepository
from controllers.produto_controller import ProdutoController
from controllers.usuario_controller import UsuarioController
from controllers.pedido_controller import PedidoController
from controllers.system_controller import SystemController
from routes.produto_routes import make_produto_blueprint
from routes.usuario_routes import make_usuario_blueprint
from routes.pedido_routes import make_pedido_blueprint
from routes.relatorio_routes import make_relatorio_blueprint
from routes.system_routes import make_system_blueprint
from middleware.errors import register_error_handlers
from middleware.auth import make_require_admin


def create_app(db=None):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG
    CORS(app)

    # Construct the connection here (composition root) and inject downward.
    if db is None:
        db = create_connection(settings.DATABASE_PATH)
    init_schema(db)
    seed_if_empty(db)

    produto_controller = ProdutoController(ProdutoRepository(db))
    usuario_controller = UsuarioController(UsuarioRepository(db))
    pedido_controller = PedidoController(PedidoRepository(db))
    system_controller = SystemController(SystemRepository(db))

    require_admin = make_require_admin(settings.ADMIN_TOKEN)

    app.register_blueprint(make_produto_blueprint(produto_controller))
    app.register_blueprint(make_usuario_blueprint(usuario_controller))
    app.register_blueprint(make_pedido_blueprint(pedido_controller))
    app.register_blueprint(make_relatorio_blueprint(pedido_controller))
    app.register_blueprint(make_system_blueprint(system_controller, require_admin))

    register_error_handlers(app)
    return app


app = create_app()


if __name__ == "__main__":
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print("Rodando em http://localhost:" + str(settings.PORT))
    print("=" * 50)
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG, use_reloader=False)
