from extensions import db
from sqlalchemy import inspect
from datetime import datetime, date

class BaseModel(db.Model):
    __abstract__ = True

    def to_dict(self):
        result = {}
        
        mapper = inspect(self.__class__)
        
        if mapper is not None:
            for column in mapper.columns:
                column_name = column.key
                value = getattr(self, column_name)

                if isinstance(value, (datetime, date)):
                    value = value.isoformat()

                result[column_name] = value

        return result