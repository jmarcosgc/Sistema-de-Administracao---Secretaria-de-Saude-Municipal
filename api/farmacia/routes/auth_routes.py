from flask import Blueprint, render_template, jsonify, request

farmacia_bp = Blueprint('farmacia', __name__)

@farmacia_bp.route('/login')
def login_page():
    return render_template('pages/login.html')

@farmacia_bp.route('/auth/autenticar', methods=['POST'])
def autenticar():
    dados = request.get_json()
    usuario = dados.get('usuario')
    senha = dados.get('senha')

    print(f"Tentativa de login: {usuario} com senha {senha}")

    if usuario == 'admin' and senha == '1234':
        return jsonify({"sucesso": True, "redirect": "/estoque"})
    else:
        return jsonify({"sucesso": False, "mensagem": "Usuário ou senha errados"}), 401
