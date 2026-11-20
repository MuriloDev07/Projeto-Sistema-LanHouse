from flask_sqlalchemy import SQLAlchemy
from contextlib import contextmanager

db = SQLAlchemy()

@contextmanager
def atomic_transaction():
    try:
        yield 
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise