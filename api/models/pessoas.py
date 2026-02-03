from extensions import db
from .base import BaseModel
from .enums import TipoUsuario

class Pessoa(BaseModel):
    __tablename__ = 'Pessoa'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(255))
    cpf = db.Column(db.String(255), unique=True)
    email = db.Column(db.String(255))
    telefone = db.Column(db.String(255))
    sexo = db.Column(db.String(1))
    dataNascimento = db.Column(db.DateTime)
    endereco = db.Column(db.String(255))

    # uselist=False para indicar 1-para-1
    funcionario = db.relationship("Funcionario", back_populates="pessoa", uselist=False)
    paciente = db.relationship("Paciente", back_populates="pessoa", uselist=False)

class Funcionario(BaseModel):
    __tablename__ = 'Funcionario'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    matricula = db.Column(db.Integer, unique=True, nullable=False)
    dataAdimissao = db.Column(db.DateTime)
    fkPessoa = db.Column(db.BigInteger, db.ForeignKey('Pessoa.id'), unique=True)

    pessoa = db.relationship("Pessoa", back_populates="funcionario")
    usuario_sistema = db.relationship("UsuarioSistema", back_populates="funcionario", uselist=False)
    
    # Subtipos (Associações 1:1 simulando herança)
    medico = db.relationship("Medico", back_populates="funcionario", uselist=False)
    farmaceutico = db.relationship("Farmaceutico", back_populates="funcionario", uselist=False)
    recepcionista = db.relationship("Recepcionista", back_populates="funcionario", uselist=False)
    administrador = db.relationship("Administrador", back_populates="funcionario", uselist=False)

class UsuarioSistema(BaseModel):
    __tablename__ = 'UsuarioSistema'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    login = db.Column(db.String(255))
    senha = db.Column(db.String(255))
    ativo = db.Column(db.Boolean, nullable=False)
    tipoUser = db.Column(db.Enum(TipoUsuario))
    fkUsuario = db.Column(db.BigInteger, db.ForeignKey('Funcionario.id'), unique=True)

    funcionario = db.relationship("Funcionario", back_populates="usuario_sistema")
