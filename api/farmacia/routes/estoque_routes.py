from flask import Blueprint, render_template, jsonify, request
from extensions import db
from sqlalchemy import func

from api.models.farmacia import Medicamento, TipoMedicamento, LoteMedicamento

estoque_bp = Blueprint('estoque', __name__, url_prefix='/estoque')


# --- ROTAS DE PÁGINAS ---

@estoque_bp.route('/')
def page_lista():
    return render_template('pages/farmacia_estoque.html')

@estoque_bp.route('/novo')
def page_novo():
    return render_template('pages/farmacia_estoque_novoMedicamento.html', mode='novo')

@estoque_bp.route('/editar/<int:id>')
def page_editar(id):
    return render_template('pages/farmacia_estoque_novoMedicamento.html', mode='editar', id=id)


# --- ROTAS DA API (JSON) ---

@estoque_bp.route('/api/listar', methods=['GET'])
def api_listar():
    termo = request.args.get('q', '').lower()

    query = db.session.query(
        TipoMedicamento.id,
        Medicamento.nome,
        TipoMedicamento.tipo,
        TipoMedicamento.estoqueMinimo,
        func.coalesce(func.sum(LoteMedicamento.quantidadeEstoque), 0).label('total_estoque'),
        func.min(LoteMedicamento.dataValidade).label('prox_validade')
    ).join(Medicamento, TipoMedicamento.fkMedicamento == Medicamento.id)\
     .outerjoin(LoteMedicamento, LoteMedicamento.fkTipoMedicamento == TipoMedicamento.id)

    if termo:
        query = query.filter(Medicamento.nome.ilike(f'%{termo}%'))

    resultados = query.group_by(
        TipoMedicamento.id, 
        Medicamento.nome, 
        TipoMedicamento.tipo, 
        TipoMedicamento.estoqueMinimo
    ).all()

    lista = []
    for row in resultados:
        lista.append({
            "id": row.id,
            "nome": row.nome,
            "tipo": row.tipo,
            "qtde": int(row.total_estoque),
            "min": row.estoqueMinimo,
            "validade": row.prox_validade.strftime('%d/%m/%Y') if row.prox_validade else "-"
        })

    return jsonify(lista)

@estoque_bp.route('/api/obter/<int:id>', methods=['GET'])
def api_obter_unico(id):
    tipo = TipoMedicamento.query.get_or_404(id)
    medicamento = Medicamento.query.get(tipo.fkMedicamento)
    
    nome_medicamento = medicamento.nome if medicamento is not None else ""
    
    dados = {
        "id": tipo.id,
        "nome": nome_medicamento,
        "tipo": tipo.tipo,
        "unidade": tipo.unidadeMedida,
        "min": tipo.estoqueMinimo,
        "caixa": tipo.quantidadeCaixa,
        "descricao": tipo.descricao
    }
    return jsonify(dados)

@estoque_bp.route('/api/salvar', methods=['POST'])
def api_salvar():
    data = request.json
    
    med = Medicamento.query.filter_by(nome=data['nome']).first()
    if not med:
        med = Medicamento()
        med.nome = data['nome']
        db.session.add(med)
        db.session.flush()

    novo_tipo = TipoMedicamento()
    
    novo_tipo.descricao = data.get('descricao', '')
    novo_tipo.tipo = data['tipo']
    novo_tipo.unidadeMedida = data['unidade']
    novo_tipo.quantidadeCaixa = data['qtd_por_caixa']
    novo_tipo.estoqueMinimo = data['qtd_minima']
    novo_tipo.fkMedicamento = med.id
    
    db.session.add(novo_tipo)
    db.session.commit()
    
    return jsonify({"msg": "Cadastrado com sucesso!"}), 201

@estoque_bp.route('/api/atualizar/<int:id>', methods=['PUT'])
def api_atualizar(id):
    data = request.json
    tipo = TipoMedicamento.query.get_or_404(id)
    
    tipo.tipo = data['tipo']
    tipo.unidadeMedida = data['unidade']
    tipo.estoqueMinimo = data['qtd_minima']
    tipo.quantidadeCaixa = data['qtd_por_caixa']
    tipo.descricao = data.get('descricao', '') 
    
    med = Medicamento.query.get(tipo.fkMedicamento)
    if med:
        med.nome = data['nome']

    db.session.commit()
    return jsonify({"msg": "Atualizado com sucesso!"})

@estoque_bp.route('/api/remover/<int:id>', methods=['DELETE'])
def api_remover(id):
    tipo = TipoMedicamento.query.get_or_404(id)
    db.session.delete(tipo)
    db.session.commit()
    return jsonify({"msg": "Removido com sucesso!"})