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
    return render_template('pages/entrega_lista.html')


@entrega_bp.route('/nova')
def page_nova():
    return render_template('pages/entrega_nova.html')


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


@entrega_bp.route('/api/confirmar', methods=['POST'])
def api_confirmar_entrega():
    data = request.get_json(force=True)

    # validações básicas
    tipo_entrega = data.get("tipo_entrega")
    fk_protocolo = data.get("fk_protocolo")
    if tipo_entrega == "PROTOCOLO" and not fk_protocolo:
        return jsonify({"error": "PROTOCOLO exige fk_protocolo"}), 400
    if tipo_entrega == "RECEITA_PARTICULAR" and fk_protocolo:
        return jsonify({"error": "RECEITA_PARTICULAR não deve ter fk_protocolo"}), 400

    entrega = EntregaFarmacia(
        tipo_entrega=tipo_entrega,
        justificativa=data.get("justificativa"),
        fk_paciente=data["fk_paciente"],
        fk_farmaceutico=data["fk_farmaceutico"],
        fk_protocolo=fk_protocolo
    )

    db.session.add(entrega)
    db.session.commit()

    # TODO: atualizar estoque dos medicamentos se necessário
    # Exemplo: se tipo_entrega == "PROTOCOLO", percorrer os medicamentos do protocolo
    # e reduzir quantidade_estoque nos lotes disponíveis.

    return jsonify({"msg": "Entrega registrada com sucesso!"}), 201
