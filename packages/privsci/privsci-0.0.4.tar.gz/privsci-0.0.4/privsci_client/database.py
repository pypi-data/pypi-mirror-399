from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from .config_store import load_config, DB_URL
from .base import Base

def get_engine(db_path=None):
    if db_path is None:
        config = load_config()
        db_path = config.get("DB_URL", DB_URL)
        
    return create_engine(db_path, echo=False)

def init_db(db_path=None, reset=False):
    """
    Explicit function to create the database.
    Users run this once.
    """
    engine = get_engine(db_path)
    
    from .models import Structure, Action, LeafType, Leaf, Packet

    if reset:
        print("Dropping all existing tables...")
        Base.metadata.drop_all(engine)
    
    # Now create the tables
    Base.metadata.create_all(engine)
    print(f"Database initialized at {db_path}")

@contextmanager
def get_db_session():
    """Provide a transactional scope around a series of operations."""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()