"""
"""
import json
from datetime import datetime

import requests

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from db import DB_PATH
from models import ArchivedJob

# engine = create_engine(DB_PATH, echo=False)

def http_callback(url):
    requests.get( url )

def job_get(**kwargs):
    """ """
    r = requests.get( kwargs.get('url'), headers=kwargs.get('headers', None), params=kwargs.get('params', None) )
    
    # update the archived job object
    # Session = sessionmaker(bind=engine)
    # session = Session()
    # job = session.query(ArchivedJob).filter_by( id=kwargs.get('job_id') ).first()
    # if job:
    #     job.status = True
    #     job.status_code = r.status_code
    #     job.time_completed = datetime.now()
    #     session.commit()
        
    #     # if callback was provided, send a GET
    #     if job.callback:
    #         http_callback(job.callback)    

def job_post(**kwargs):
    """ """
    r = requests.post( kwargs.get('url'), headers=kwargs.get('headers', None), body=kwargs.get('body', None) )
    
    # update the archived job object
    # Session = sessionmaker(bind=engine)
    # session = Session()
    # job = session.query(ArchivedJob).filter_by( id=kwargs.get('job_id') ).first()
    # if job:
    #     job.status = True
    #     job.status_code = r.status_code
    #     job.time_completed = datetime.now()
    #     session.commit()
        
    #     # if callback was provided, send a GET
    #     if job.callback:
    #         http_callback(job.callback)


def my_listener(event):
    if event.exception:
        print('The job crashed :(')
    else:
        print('The job worked :)')
