from app.extensions import db
from app.models.session import Session


class SessionRepository:
    def create(self, **kwargs) -> Session:
        session = Session(**kwargs)
        db.session.add(session)
        db.session.commit()
        return session

    def get_active_by_jti(self, jti: str) -> Session | None:
        return Session.query.filter_by(jti=jti, is_active=True).first()

    def revoke(self, session: Session) -> None:
        session.is_active = False
        db.session.commit()
