from sqlalchemy import Column, Boolean, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def init_db(engine):
    Base.metadata.create_all(bind=engine)

class ArchivedJob(Base):
     __tablename__ = 'jobs'

     id = Column(String, primary_key=True)
     status = Column(Boolean)
     status_code = Column(Integer)
     
     action = Column(String)
     trigger = Column(String)
     
     callback = Column(String)
     
     time_created = Column(DateTime)
     time_completed = Column(DateTime)

     def __repr__(self):
        return "<Job(id='%s', status='%s')>" % (
                             self.id, self.status )

