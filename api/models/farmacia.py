from extensions import db
from .base import BaseModel
from .enums import StatusLote


protocolo_medicamento = db.Table(
    'protocolo_medicamento',
    db.Column(
        'fk_protocolo',
        db.BigInteger,
        db.ForeignKey('protocolo.id'),
        primary_key=True
    ),
    db.Column(
        'fk_medicamento',
        db.BigInteger,
        db.ForeignKey('medicamento.id'),
        primary_key=True
    )
)


class Medicamento(BaseModel):
    __tablename__ = 'medicamento'

    id = db.Column(db.BigInteger, primary_key=True)
    nome = db.Column(db.String(255), unique=True)

    tipos = db.relationship("TipoMedicamento", back_populates="medicamento")
    protocolos = db.relationship(
        "Protocolo",
        secondary=protocolo_medicamento,
        back_populates="medicamentos"
    )


class TipoMedicamento(BaseModel):
    __tablename__ = 'tipo_medicamento'

    id = db.Column(db.BigInteger, primary_key=True)
    descricao = db.Column(db.String(255))
    tipo = db.Column(db.String(255))
    unidade_medida = db.Column(db.String(255))
    quantidade_caixa = db.Column(db.Integer, nullable=False)
    estoque_minimo = db.Column(db.Integer, nullable=False)

    fk_medicamento = db.Column(
        db.BigInteger,
        db.ForeignKey('medicamento.id'),
        nullable=False
    )

    medicamento = db.relationship("Medicamento", back_populates="tipos")
    lotes = db.relationship("LoteMedicamento", back_populates="tipo_medicamento")


class LoteMedicamento(BaseModel):
    __tablename__ = 'lote_medicamento'

    id = db.Column(db.BigInteger, primary_key=True)
    quantidade_entrada = db.Column(db.Integer, nullable=False)
    quantidade_estoque = db.Column(db.Integer, nullable=False)
    data_fabricacao = db.Column(db.DateTime)
    data_validade = db.Column(db.DateTime)
    status = db.Column(db.Enum(StatusLote))

    fk_tipo_medicamento = db.Column(
        db.BigInteger,
        db.ForeignKey('tipo_medicamento.id'),
        nullable=False
    )

    tipo_medicamento = db.relationship("TipoMedicamento", back_populates="lotes")
