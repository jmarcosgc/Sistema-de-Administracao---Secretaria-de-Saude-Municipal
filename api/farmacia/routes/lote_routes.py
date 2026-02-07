from flask import Blueprint, render_template


lote_bp = Blueprint('lote', __name__, url_prefix='/lote')


@lote_bp.route('/')
def page_lote_medicamento():
    return render_template('pages/farmacia_lote.html')