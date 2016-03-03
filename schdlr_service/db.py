from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import init_db

engine = create_engine('sqlite:///jobs.sqlite', echo=False)

def get_session( ):
    return sessionmaker(bind=engine)
