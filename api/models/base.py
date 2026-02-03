from extensions import db
from flask_sqlalchemy import inspect
from datetime import datetime, date
# from sqlalchemy import MetaData

# Convenção de nomenclatura para constraints (importante para migrações futuras com Alembic)
# convention = {
#     "ix": 'ix_%(column_0_label)s',
#     "uq": "uq_%(table_name)s_%(column_0_name)s",
#     "ck": "ck_%(table_name)s_%(constraint_name)s",
#     "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
#     "pk": "pk_%(table_name)s"
# }

# metadata = MetaData(naming_convention=convention)
# db = SQLAlchemy(metadata=metadata)

class BaseModel(db.Model):
    __abstract__ = True

    def to_dict(self):
        result = {}

        mapper = db.inspect(self.__class__)
        for column in mapper.columns:
            column_name = column.key
            value = getattr(self, column_name)

            if isinstance(value, (datetime, date)):
                value = value.isoformat()

            result[column_name] = value

        return result
