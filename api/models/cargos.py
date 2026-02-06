from extensions import db
from .base import BaseModel


class Administrador(BaseModel):
    __tablename__ = 'administrador'

    id = db.Column(
        db.BigInteger,
        db.ForeignKey('funcionario.id'),
        primary_key=True
    )

    setor = db.Column(db.String(255))

    funcionario = db.relationship(
        "Funcionario",
        back_populates="administrador",
        uselist=False
    )


class Medico(BaseModel):
    __tablename__ = 'medico'

    id = db.Column(
        db.BigInteger,
        db.ForeignKey('funcionario.id'),
        primary_key=True
    )

    crm = db.Column(db.String(255), nullable=False, unique=True)
    especialidade = db.Column(db.String(255))
    nomeFantasia = db.Column(db.String(255))

    funcionario = db.relationship(
        "Funcionario",
        back_populates="medico",
        uselist=False
    )

    consultas = db.relationship("Consulta", back_populates="medico")


class Farmaceutico(BaseModel):
    __tablename__ = 'farmaceutico'

    id = db.Column(
        db.BigInteger,
        db.ForeignKey('funcionario.id'),
        primary_key=True
    )

    crf = db.Column(db.String(255), nullable=False, unique=True)

    funcionario = db.relationship(
        "Funcionario",
        back_populates="farmaceutico",
        uselist=False
    )

    protocolos = db.relationship("Protocolo", back_populates="farmaceutico")


class Recepcionista(BaseModel):
    __tablename__ = 'recepcionista'

    id = db.Column(
        db.BigInteger,
        db.ForeignKey('funcionario.id'),
        primary_key=True
    )

    setor = db.Column(db.String(255))

    funcionario = db.relationship(
        "Funcionario",
        back_populates="recepcionista",
        uselist=False
    )
