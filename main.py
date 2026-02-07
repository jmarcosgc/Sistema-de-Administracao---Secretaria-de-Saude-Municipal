import os
from flask import Flask, render_template
from config import Config
from extensions import db

from api.farmacia.routes.auth_routes import farmacia_bp
from api.farmacia.routes.estoque_routes import estoque_bp
from api.farmacia.routes.entrega_routes import entrega_bp
from api.farmacia.routes.lote_routes import lote_bp


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)

    db.init_app(app)

    app.register_blueprint(farmacia_bp)
    app.register_blueprint(estoque_bp)
    app.register_blueprint(entrega_bp)
    app.register_blueprint(lote_bp)

    with app.app_context():
        try:
            db.create_all()
            print("--- BANCO DE DADOS CONECTADO E TABELAS CRIADAS COM SUCESSO ---")
        except Exception as e:
            print(f"--- ERRO AO CONECTAR NO BANCO: {e} ---")
            print("Dica: Verifique se o banco 'dbsistemasaude' existe no seu PostgreSQL.")

    return app
    
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
