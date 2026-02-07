from flask import Blueprint, render_template, jsonify, request
from extensions import db
from api.models import (
    EntregaFarmacia,
    Paciente,
    Farmaceutico,
    Protocolo,
    Medicamento,
    Consulta
)

entrega_bp = Blueprint('entrega', __name__, url_prefix='/entrega')

# =========================
# ROTAS DE PÁGINAS
# =========================

@entrega_bp.route('/')
def page_lista():
    return render_template('pages/farmacia_estoque_novoMedicamento.html')


@entrega_bp.route('/nova')
def page_nova():
    return render_template('pages/login.html')


# =========================
# ROTAS DE API
# =========================

@entrega_bp.route('/api/listar', methods=['GET'])
def api_listar():
    entregas = db.session.query(
        EntregaFarmacia.id,
        EntregaFarmacia.data_entrega,
        EntregaFarmacia.tipo_entrega,
        Paciente.id.label('paciente_id'),
        Protocolo.codigo
    ).join(
        Paciente, EntregaFarmacia.fk_paciente == Paciente.id
    ).outerjoin(
        Protocolo, EntregaFarmacia.fk_protocolo == Protocolo.id
    ).order_by(
        EntregaFarmacia.data_entrega.desc()
    ).all()

    lista = []
    for e in entregas:
        lista.append({
            "id": e.id,
            "data": e.data_entrega.strftime('%d/%m/%Y'),
            "tipo": e.tipo_entrega,
            "paciente_id": e.paciente_id,
            "protocolo": e.codigo or "-"
        })

    return jsonify(lista)


@entrega_bp.route('/api/dados', methods=['GET'])
def api_dados():
    pacientes = Paciente.query.all()
    farmaceuticos = Farmaceutico.query.all()
    protocolos = Protocolo.query.filter_by(status=True).all()

    return jsonify({
        "pacientes": [
            {"id": p.id, "nome": p.pessoa.nome} for p in pacientes
        ],
        "farmaceuticos": [
            {"id": f.id, "nome": f.funcionario.pessoa.nome} for f in farmaceuticos
        ],
        "protocolos": [
            {"id": pr.id, "codigo": pr.codigo} for pr in protocolos
        ]
    })


@entrega_bp.route('/api/protocolos/<int:paciente_id>', methods=['GET'])
def api_protocolos_paciente(paciente_id):
    # Buscar protocolos do paciente via consulta
    protocolos = db.session.query(Protocolo).join(Consulta).filter(
        Consulta.fk_paciente == paciente_id
    ).all()

    lista = [{"id": p.id, "codigo": p.codigo} for p in protocolos]
    return jsonify(lista)




@entrega_bp.route('/api/protocolo/<int:protocolo_id>/medicamentos', methods=['GET'])
def api_medicamentos_protocolo(protocolo_id):
    protocolo = Protocolo.query.get_or_404(protocolo_id)
    meds = [{"id": m.id, "nome": m.nome} for m in protocolo.medicamentos]
    return jsonify(meds)


@entrega_bp.route('/api/medicamentos', methods=['GET'])
def api_medicamentos_com_lotes():
    """
    Retorna todos os medicamentos com seus tipos e lotes válidos
    para o front-end na tela de entrega.
    """
    from datetime import datetime
    from api.models.farmacia import Medicamento, TipoMedicamento, LoteMedicamento

    hoje = datetime.utcnow()
    lista = []

    medicamentos = Medicamento.query.all()
    for med in medicamentos:
        tipos_lista = []
        for tipo in med.tipos:  # relação Medicamento.tipos
            lotes_validos = [
                {
                    "id": lote.id,
                    "quantidade_estoque": lote.quantidade_estoque,
                    "data_validade": lote.data_validade.strftime('%d/%m/%Y') if lote.data_validade else None,
                    # aqui pode adicionar todos os atributos do lote
                }
                for lote in tipo.lotes
                if lote.quantidade_estoque > 0 and (not lote.data_validade or lote.data_validade >= hoje)
            ]

            tipos_lista.append({
                "id": tipo.id,
                "tipo": tipo.tipo,
                "unidade_medida": tipo.unidade_medida,
                "quantidade_caixa": tipo.quantidade_caixa,
                "estoque_minimo": tipo.estoque_minimo,
                "descricao": tipo.descricao,
                "lotes": lotes_validos
            })

        lista.append({
            "id": med.id,
            "nome_medicamento": med.nome,
            "tipo_medicamento": tipos_lista
        })

    return jsonify(lista)

@entrega_bp.route('/api/confirmar', methods=['POST'])
def api_confirmar_entrega():
    """
    Confirma uma entrega, registra no banco e atualiza o estoque dos lotes.
    Espera receber JSON com:
    {
        "tipo_entrega": "PROTOCOLO" ou "RECEITA_PARTICULAR",
        "fk_paciente": 1,
        "fk_farmaceutico": 2,
        "fk_protocolo": 3,        # se for PROTOCOLO
        "justificativa": "...",
        "itens": [
            {"tipo_id": 1, "lote_id": 10, "quantidade": 2},
            {"tipo_id": 1, "lote_id": 11, "quantidade": 3}
        ]
    }
    """
    from api.models.farmacia import LoteMedicamento

    data = request.get_json(force=True)

    # --- Validações básicas ---
    tipo_entrega = data.get("tipo_entrega")
    fk_protocolo = data.get("fk_protocolo")

    if tipo_entrega == "PROTOCOLO" and not fk_protocolo:
        return jsonify({"error": "PROTOCOLO exige fk_protocolo"}), 400
    if tipo_entrega == "RECEITA_PARTICULAR" and fk_protocolo:
        return jsonify({"error": "RECEITA_PARTICULAR não deve ter fk_protocolo"}), 400

    # --- Criar registro de entrega ---
    entrega = EntregaFarmacia(
        tipo_entrega=tipo_entrega,
        justificativa=data.get("justificativa"),
        fk_paciente=data["fk_paciente"],
        fk_farmaceutico=data["fk_farmaceutico"],
        fk_protocolo=fk_protocolo
    )
    db.session.add(entrega)
    db.session.flush()  # ainda não confirma, mas permite usar o ID se necessário

    # --- Atualizar estoque dos lotes ---
    itens = data.get("itens", [])
    for item in itens:
        lote = LoteMedicamento.query.get(item["lote_id"])
        if not lote:
            db.session.rollback()
            return jsonify({"error": f"Lote {item['lote_id']} não encontrado"}), 400
        if lote.quantidade_estoque < item["quantidade"]:
            db.session.rollback()
            return jsonify({"error": f"Estoque insuficiente no lote {lote.id}"}), 400

        lote.quantidade_estoque -= item["quantidade"]

    db.session.commit()
    return jsonify({"msg": "Entrega registrada e estoque atualizado com sucesso!"}), 201
