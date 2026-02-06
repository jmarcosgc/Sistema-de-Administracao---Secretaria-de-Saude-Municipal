from extensions import db
from .base import BaseModel
from .enums import StatusConsulta
from .farmacia import protocolo_medicamento


class Paciente(BaseModel):
    __tablename__ = 'paciente'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    numero_sus = db.Column(db.String(255), nullable=False, unique=True)

    fk_pessoa = db.Column(
        db.BigInteger,
        db.ForeignKey('pessoa.id'),
        unique=True
    )

    pessoa = db.relationship("Pessoa", back_populates="paciente")
    consultas = db.relationship("Consulta", back_populates="paciente")


class Protocolo(BaseModel):
    __tablename__ = 'protocolo'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    codigo = db.Column(db.String(255))
    status = db.Column(db.Boolean, default=True)
    data_gerada = db.Column(db.DateTime, server_default=db.func.now())
    data_entrega = db.Column(db.DateTime)

    fk_farmaceutico = db.Column(
        db.BigInteger,
        db.ForeignKey('farmaceutico.id'),
        nullable=True
    )

    farmaceutico = db.relationship("Farmaceutico", back_populates="protocolos")
    consulta = db.relationship("Consulta", back_populates="protocolo", uselist=False)

    medicamentos = db.relationship(
        "Medicamento",
        secondary=protocolo_medicamento,
        back_populates="protocolos"
    )



class Consulta(BaseModel):
    __tablename__ = 'consulta'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    data_consulta = db.Column(db.DateTime)
    descricao = db.Column(db.String(255))
    tipo_consulta = db.Column(db.String(255))

    status = db.Column(
        db.Enum(
            StatusConsulta,
            name='status_consulta',
            native_enum=True,
            create_type=False
        )
    )

    fk_medico = db.Column(
        db.BigInteger,
        db.ForeignKey('medico.id'),
        nullable=False
    )

    fk_paciente = db.Column(
        db.BigInteger,
        db.ForeignKey('paciente.id'),
        nullable=False
    )

    fk_protocolo = db.Column(
        db.BigInteger,
        db.ForeignKey('protocolo.id'),
        unique=True
    )

    medico = db.relationship("Medico", back_populates="consultas")
    paciente = db.relationship("Paciente", back_populates="consultas")
    protocolo = db.relationship("Protocolo", back_populates="consulta", uselist=False)
