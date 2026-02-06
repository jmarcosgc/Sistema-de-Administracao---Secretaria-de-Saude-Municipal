from flask import Blueprint, render_template # jsonify, request
# from extensions import db
# from sqlalchemy import func

from api.models import Medicamento, TipoMedicamento, LoteMedicamento

entrega_bp = Blueprint('entrega', __name__, url_prefix='/entrega')

# --- ROTAS DE PÁGINAS ---