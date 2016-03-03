from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import init_db

engine = create_engine('sqlite:///jobs.sqlite', echo=False)
Session = Session = sessionmaker(bind=engine)
    
if __name__ == '__main__':
    print "yo"
    init_db(engine)
