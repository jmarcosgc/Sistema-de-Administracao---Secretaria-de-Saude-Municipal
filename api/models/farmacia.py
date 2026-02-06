from datetime import datetime
from extensions import db
from .base import BaseModel
from .enums import StatusLote, TipoEntrega
from sqlalchemy.orm import validates



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

class EntregaFarmacia(BaseModel):
    __tablename__ = 'entrega_farmacia'

    id = db.Column(db.BigInteger, primary_key=True)
    data_entrega = db.Column(db.DateTime, default=datetime.utcnow)
    tipo_entrega = db.Column(db.Enum(TipoEntrega), nullable=False)
    justificativa = db.Column(db.Text)

    fk_paciente = db.Column(db.BigInteger, db.ForeignKey('paciente.id'), nullable=False)
    fk_farmaceutico = db.Column(db.BigInteger, db.ForeignKey('farmaceutico.id'), nullable=False)
    fk_protocolo = db.Column(db.BigInteger, db.ForeignKey('protocolo.id'), unique=True)

    paciente = db.relationship("Paciente", backref="entregas")
    farmaceutico = db.relationship("Farmaceutico", backref="entregas")
    protocolo = db.relationship("Protocolo", backref="entrega", uselist=False)

    def __repr__(self):
        return f"<EntregaFarmacia id={self.id} tipo_entrega={self.tipo_entrega}>"
    
    @validates('fk_protocolo', 'tipo_entrega')
    def validate_entrega(self, key, value):
        if key == 'fk_protocolo':
            if self.tipo_entrega == TipoEntrega.PROTOCOLO and value is None:
                raise ValueError("PROTOCOLO exige fk_protocolo")
            if self.tipo_entrega == TipoEntrega.RECEITA_PARTICULAR and value is not None:
                raise ValueError("RECEITA_PARTICULAR não deve ter fk_protocolo")
        return value