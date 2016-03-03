"""
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import requests

from models import ArchivedJob, init_db

engine = create_engine('sqlite:///jobs.sqlite', echo=False)
init_db(engine)
Session = sessionmaker(bind=engine)

def job_get(**kwargs):
    """ """
    requests.get( kwargs.get('url'), headers=kwargs.get('headers', None), params=kwargs.get('params', None) )

def job_post(**kwargs):
    """ """
    requests.post( kwargs.get('url'), headers=kwargs.get('headers', None), body=kwargs.get('body', None) )
