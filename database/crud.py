from sqlalchemy.orm import Session
from database.models import User


def get_user_by_username(db: Session, username: str):
    """
    Fetch a user from DB using username/email.
    Returns User object or None.
    """
    return db.query(User).filter(User.username == username).first()
