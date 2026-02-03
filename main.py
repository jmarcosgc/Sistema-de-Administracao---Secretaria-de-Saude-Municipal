import os
from flask import Flask, render_template
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)


    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route("/health")
    def health():
        return {"status": "ok"}

    return app
    
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
