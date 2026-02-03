from extensions import db
from .base import BaseModel

class Medico(BaseModel):
    __tablename__ = "Medico"

    crm = db.Column(db.String(255), unique=True, nullable=False)
    especialidade = db.Column(db.String(255))
    nome_fantasia = db.Column(db.String(255))

    id = db.Column(
        db.BigInteger,
        db.ForeignKey("Funcionario.id"),
        primary_key=True
    )

    funcionario = db.relationship("Funcionario", backref="medico")
