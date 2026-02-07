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
    return render_template(
        'pages/farmacia_estoque_novoMedicamento.html',
        mode='novo'
    )

@estoque_bp.route('/editar/<int:id>')
def page_editar(id):
    return render_template(
        'pages/farmacia_estoque_novoMedicamento.html',
        mode='editar',
        id=id
    )


# --- ROTAS DA API (JSON) ---

@estoque_bp.route('/api/listar', methods=['GET'])
def api_listar():
    termo = request.args.get('q', '').lower()

    query = db.session.query(
        TipoMedicamento.id,
        Medicamento.nome,
        TipoMedicamento.tipo,
        TipoMedicamento.estoque_minimo,
        func.coalesce(
            func.sum(LoteMedicamento.quantidade_estoque), 0
        ).label('total_estoque'),
        func.min(LoteMedicamento.data_validade).label('prox_validade')
    ).join(
        Medicamento,
        TipoMedicamento.fk_medicamento == Medicamento.id
    ).outerjoin(
        LoteMedicamento,
        LoteMedicamento.fk_tipo_medicamento == TipoMedicamento.id
    )

    if termo:
        query = query.filter(Medicamento.nome.ilike(f'%{termo}%'))

    resultados = query.group_by(
        TipoMedicamento.id,
        Medicamento.nome,
        TipoMedicamento.tipo,
        TipoMedicamento.estoque_minimo
    ).all()

    lista = []
    for row in resultados:
        lista.append({
            "id": row.id,
            "nome": row.nome,
            "tipo": row.tipo,
            "qtde": int(row.total_estoque),
            "min": row.estoque_minimo,
            "validade": (
                row.prox_validade.strftime('%d/%m/%Y')
                if row.prox_validade else "-"
            )
        })

    return jsonify(lista)


@estoque_bp.route('/api/obter/<int:id>', methods=['GET'])
def api_obter_unico(id):
    tipo = TipoMedicamento.query.get_or_404(id)
    medicamento = Medicamento.query.get(tipo.fk_medicamento)

    nome_medicamento = medicamento.nome if medicamento else ""

    dados = {
        "id": tipo.id,
        "nome": nome_medicamento,
        "tipo": tipo.tipo,
        "unidade": tipo.unidade_medida,
        "min": tipo.estoque_minimo,
        "caixa": tipo.quantidade_caixa,
        "descricao": tipo.descricao
    }

    return jsonify(dados)


@estoque_bp.route('/api/salvar', methods=['POST'])
def api_salvar():
    data = data = request.get_json(force=True)


    med = Medicamento.query.filter_by(nome=data['nome']).first()
    if not med:
        med = Medicamento(nome=data['nome']) # type: ignore
        db.session.add(med)
        db.session.flush()

    novo_tipo = TipoMedicamento(
        descricao=data.get('descricao', ''), # type: ignore
        tipo=data['tipo'], # type: ignore
        unidade_medida=data['unidade'], # type: ignore
        quantidade_caixa=data['qtd_por_caixa'], # type: ignore
        estoque_minimo=data['qtd_minima'], # type: ignore
        fk_medicamento=med.id # type: ignore
    ) 

    db.session.add(novo_tipo)
    db.session.commit()

    return jsonify({"msg": "Cadastrado com sucesso!"}), 201


@estoque_bp.route('/api/atualizar/<int:id>', methods=['PUT'])
def api_atualizar(id):
    data = request.get_json(force=True)
    tipo = TipoMedicamento.query.get_or_404(id)

    tipo.tipo = data['tipo']
    tipo.unidade_medida = data['unidade']
    tipo.estoque_minimo = data['qtd_minima']
    tipo.quantidade_caixa = data['qtd_por_caixa']
    tipo.descricao = data.get('descricao', '')

    med = Medicamento.query.get(tipo.fk_medicamento)
    if med:
        med.nome = data['nome']

    db.session.commit()
    return jsonify({"msg": "Atualizado com sucesso!"})

@estoque_bp.route('/api/remover/<int:id>', methods=['DELETE'])
def api_remover(id):
    tipo = TipoMedicamento.query.get_or_404(id)

    lotes = LoteMedicamento.query.filter_by(fk_tipo_medicamento=tipo.id).count()
    if lotes > 0:
        return jsonify({"error": "Não é possível remover este tipo de medicamento enquanto houver lotes associados."}), 400

    db.session.delete(tipo)
    db.session.commit()
    return jsonify({"msg": "Removido com sucesso!"})

@estoque_bp.route('/api/listar_lotes', methods=['GET'])
def api_listar_lotes():
    lotes = db.session.query(
        LoteMedicamento.id,
        TipoMedicamento.id.label('tipo_id'),
        Medicamento.nome.label('nome_medicamento'),
        TipoMedicamento.tipo,
        LoteMedicamento.quantidade_estoque,
        TipoMedicamento.unidade_medida,  # pegar a unidade do tipo, não do lote
        LoteMedicamento.data_validade
    ).join(
        TipoMedicamento, LoteMedicamento.fk_tipo_medicamento == TipoMedicamento.id
    ).join(
        Medicamento, TipoMedicamento.fk_medicamento == Medicamento.id
    ).all()

    lista = []
    for l in lotes:
        lista.append({
            "id": l.id,
            "fk_tipo_medicamento": l.tipo_id,
            "nome_medicamento": l.nome_medicamento,
            "tipo": l.tipo,
            "quantidade_estoque": l.quantidade_estoque,
            "unidade_medida": l.unidade_medida,  # agora vem do tipo
            "data_validade": l.data_validade.strftime('%Y-%m-%d') if l.data_validade else ""
        })

    return jsonify(lista)

@estoque_bp.route('/api/obter_lote/<int:id>', methods=['GET'])
def api_obter_lote(id):
    lote = LoteMedicamento.query.get_or_404(id)
    tipo = TipoMedicamento.query.get(lote.fk_tipo_medicamento)
    med = Medicamento.query.get(tipo.fk_medicamento)

    dados = {
        "id": lote.id,
        "fk_tipo_medicamento": tipo.id,
        "nome_medicamento": med.nome,
        "tipo": tipo.tipo,
        "quantidade_estoque": lote.quantidade_estoque,
        "unidade_medida": lote.unidade_medida,
        "data_validade": lote.data_validade.strftime('%Y-%m-%d') if lote.data_validade else ""
    }
    return jsonify(dados)

@estoque_bp.route('/api/salvar_lote', methods=['POST'])
def api_salvar_lote():
    data = request.get_json(force=True)

    # Pega o tipo do medicamento
    tipo = TipoMedicamento.query.get_or_404(data['fk_tipo_medicamento'])

    # Preenche os campos obrigatórios
    novo_lote = LoteMedicamento(
        fk_tipo_medicamento=tipo.id,
        quantidade_entrada=int(data.get('quantidade_entrada', 0)),  # obrigatório
        quantidade_estoque=int(data.get('quantidade_estoque', 0)),  # obrigatório
        data_fabricacao=data.get('data_fabricacao'),                # opcional, pode ser None
        data_validade=data.get('data_validade'),                    # opcional
        status=data.get('status', 'DISPONIVEL')                     # default para não nulo
    )

    db.session.add(novo_lote)
    db.session.commit()

    return jsonify({"msg": "Lote cadastrado com sucesso!"}), 201



@estoque_bp.route('/api/remover_lote/<int:id>', methods=['DELETE'])
def api_remover_lote(id):
    lote = LoteMedicamento.query.get_or_404(id)
    db.session.delete(lote)
    db.session.commit()
    return jsonify({"msg": "Lote removido com sucesso!"})

@estoque_bp.route('/api/medicamentos_com_lotes', methods=['GET'])
def api_medicamentos_com_lotes():
    medicamentos = []

    tipos = db.session.query(
        TipoMedicamento.id.label('tipo_id'),
        TipoMedicamento.tipo,
        TipoMedicamento.quantidade_caixa,
        TipoMedicamento.fk_medicamento,
        Medicamento.nome.label('nome_medicamento')
    ).join(Medicamento, TipoMedicamento.fk_medicamento == Medicamento.id).all()

    # Lotes
    for t in tipos:
        lotes = LoteMedicamento.query.filter_by(fk_tipo_medicamento=t.tipo_id).all()
        lista_lotes = []
        for l in lotes:
            lista_lotes.append({
                "id": l.id,
                "quantidade_estoque": l.quantidade_estoque,
                "data_validade": l.data_validade.strftime('%Y-%m-%d')
            })

        # Verifica se já existe o medicamento
        med = next((m for m in medicamentos if m['id'] == t.fk_medicamento), None)
        tipo_dict = {
            "id": t.tipo_id,
            "tipo": t.tipo,
            "quantidade_caixa": t.quantidade_caixa,
            "lotes": lista_lotes
        }

        if med:
            med['tipo_medicamento'].append(tipo_dict)
        else:
            medicamentos.append({
                "id": t.fk_medicamento,
                "nome_medicamento": t.nome_medicamento,
                "tipo_medicamento": [tipo_dict]
            })

    return jsonify(medicamentos)
