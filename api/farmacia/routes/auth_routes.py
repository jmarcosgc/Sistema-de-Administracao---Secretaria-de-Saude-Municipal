from flask import Blueprint, render_template, jsonify, request, session
from werkzeug.security import check_password_hash


from api.models.pessoas import UsuarioSistema 

farmacia_bp = Blueprint('farmacia', __name__)

@farmacia_bp.route('/login')
def login_page():
    return render_template('pages/login.html')

@farmacia_bp.route('/auth/autenticar', methods=['POST'])
def autenticar():
    dados = request.get_json()
    usuario_input = dados.get('usuario')
    senha_input = dados.get('senha')

    if not usuario_input or not senha_input:
        return jsonify({"sucesso": False, "mensagem": "Preencha todos os campos"}), 400


    usuario_db = UsuarioSistema.query.filter_by(login=usuario_input).first()

    if not usuario_db:
        return jsonify({"sucesso": False, "mensagem": "Usuário não encontrado"}), 401

    if not usuario_db.ativo:
        return jsonify({"sucesso": False, "mensagem": "Usuário inativo. Contate o suporte."}), 403

    if check_password_hash(usuario_db.senha, senha_input):
        
        session['user_id'] = usuario_db.id
        
        session['tipo'] = usuario_db.tipo_user.name if hasattr(usuario_db.tipo_user, 'name') else usuario_db.tipo_user

        return jsonify({"sucesso": True, "redirect": "/estoque"})
    
    else:
        return jsonify({"sucesso": False, "mensagem": "Senha incorreta"}), 401