from extensions import db
from .base import BaseModel
from .enums import StatusLote

# Tabela associativa (Many-to-Many)
protocolo_medicamento = db.Table('protocolo_medicamento',
    db.Column('fkProtocolo', db.BigInteger, db.ForeignKey('Protocolo.id'), primary_key=True),
    db.Column('fkMedicamento', db.BigInteger, db.ForeignKey('Medicamento.id'), primary_key=True)
)

class Medicamento(BaseModel):
    __tablename__ = 'Medicamento'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(255), unique=True)

    tipos = db.relationship("TipoMedicamento", back_populates="medicamento")
    # many-to-many com Protocolo
    protocolos = db.relationship("Protocolo", secondary=protocolo_medicamento, back_populates="medicamentos")

class TipoMedicamento(BaseModel):
    __tablename__ = 'TipoMedicamento'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    descricao = db.Column(db.String(255))
    tipo = db.Column(db.String(255))
    unidadeMedida = db.Column(db.String(255))
    quantidadeCaixa = db.Column(db.Integer, nullable=False)
    estoqueMinimo = db.Column(db.Integer, nullable=False)
    fkMedicamento = db.Column(db.BigInteger, db.ForeignKey('Medicamento.id'), nullable=False)

    medicamento = db.relationship("Medicamento", back_populates="tipos")
    lotes = db.relationship("LoteMedicamento", back_populates="tipo_medicamento")

class LoteMedicamento(BaseModel):
    __tablename__ = 'LoteMedicamento'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    quantidadeEntrada = db.Column(db.Integer, nullable=False)
    quantidadeEstoque = db.Column(db.Integer, nullable=False)
    dataFabricacao = db.Column(db.DateTime)
    dataValidade = db.Column(db.DateTime)
    status = db.Column(db.Enum(StatusLote))
    fkTipoMedicamento = db.Column(db.BigInteger, db.ForeignKey('TipoMedicamento.id'), nullable=False)

    tipo_medicamento = db.relationship("TipoMedicamento", back_populates="lotes")