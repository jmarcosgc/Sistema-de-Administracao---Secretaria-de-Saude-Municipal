import os
from flask import Flask, render_template
from config import Config
from api.farmacia.routes import farmacia_bp

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)

    app.register_blueprint(farmacia_bp)

    return app
    
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
