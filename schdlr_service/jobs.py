"""
"""
import json
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import requests

from db import Session
from models import ArchivedJob, init_db

def http_callback(url):
    requests.get( url )

def job_get(**kwargs):
    """ """
    r = requests.get( kwargs.get('url'), headers=kwargs.get('headers', None), params=kwargs.get('params', None) )
    
    # update the archived job object
    session = Session()
    job = session.query(ArchivedJob).filter_by( id=kwargs.get('job_id') ).first()
    if job:
        job.status = True
        job.response = json.dumps({
            'status_code': r.status_code,
            'content': r.text
        })
        job.time_completed = datetime.now()
        session.commit()
        
        # if callback was provided, send a GET
        if job.callback:
            http_callback(job.callback)    

def job_post(**kwargs):
    """ """
    r = requests.post( kwargs.get('url'), headers=kwargs.get('headers', None), body=kwargs.get('body', None) )
    
    # update the archived job object
    session = Session()
    job = session.query(ArchivedJob).filter_by( id=kwargs.get('job_id') ).first()
    if job:
        job.status = True
        job.response = json.dumps({
            'status_code': r.status_code,
            'content': r.text
        })
        job.time_completed = datetime.now()
        session.commit()
        
        # if callback was provided, send a GET
        if job.callback:
            http_callback(job.callback)