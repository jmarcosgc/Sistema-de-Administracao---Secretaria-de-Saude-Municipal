from extensions import db
from .base import BaseModel


class Medico(BaseModel):
    __tablename__ = 'medico'

    id = db.Column(
        db.BigInteger,
        db.ForeignKey('funcionario.id'),
        primary_key=True
    )

    crm = db.Column(db.String(255), unique=True, nullable=False)
    especialidade = db.Column(db.String(255))
    nome_fantasia = db.Column(db.String(255))

    funcionario = db.relationship(
        "Funcionario",
        back_populates="medico"
    )

    consultas = db.relationship(
        "Consulta",
        back_populates="medico"
    )
