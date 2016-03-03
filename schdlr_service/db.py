from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import init_db

engine = create_engine('sqlite:///jobs.sqlite', echo=False)
Session = sessionmaker(bind=engine)

def get_session(engine):
    return sessionmaker(bind=engine)
