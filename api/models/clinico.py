from extensions import db
from .base import BaseModel
from .enums import StatusConsulta
from .farmacia import protocolo_medicamento 

class Paciente(BaseModel):
    __tablename__ = 'Paciente'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    numeroSus = db.Column(db.String(255), nullable=False, unique=True)
    fkPessoa = db.Column(db.BigInteger, db.ForeignKey('Pessoa.id'), unique=True)

    pessoa = db.relationship("Pessoa", back_populates="paciente")
    consultas = db.relationship("Consulta", back_populates="paciente")

class Protocolo(BaseModel):
    __tablename__ = 'Protocolo'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    codigo = db.Column(db.String(255))
    status = db.Column(db.Boolean) # Mapeado bit(1) como Boolean
    dataGerada = db.Column(db.DateTime)
    dataEntrega = db.Column(db.DateTime)
    fkFarmaceutico = db.Column(db.BigInteger, db.ForeignKey('Farmaceutico.id'))

    farmaceutico = db.relationship("Farmaceutico", back_populates="protocolos")
    consulta = db.relationship("Consulta", back_populates="protocolo", uselist=False)
    medicamentos = db.relationship("Medicamento", secondary=protocolo_medicamento, back_populates="protocolos")

class Consulta(BaseModel):
    __tablename__ = 'Consulta'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    dataConsulta = db.Column(db.DateTime)
    descricao = db.Column(db.String(255))
    tipoConsulta = db.Column(db.String(255))
    status = db.Column(db.Enum(StatusConsulta))
    
    fkMedico = db.Column(db.BigInteger, db.ForeignKey('Medico.id'), nullable=False)
    fkPaciente = db.Column(db.BigInteger, db.ForeignKey('Paciente.id'), nullable=False)
    fkProtocolo = db.Column(db.BigInteger, db.ForeignKey('Protocolo.id'), unique=True)

    medico = db.relationship("Medico", back_populates="consultas")
    paciente = db.relationship("Paciente", back_populates="consultas")
    protocolo = db.relationship("Protocolo", back_populates="consulta")