from app.extensions import db
from app.models.api_key import ApiKey


class ApiKeyRepository:
    def create(self, **kwargs) -> ApiKey:
        record = ApiKey(**kwargs)
        db.session.add(record)
        db.session.commit()
        return record
