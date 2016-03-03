"""
"""
import os
import json
from datetime import datetime
from os.path import join, dirname
from dotenv import load_dotenv

import requests

# Load the .env file
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

UPDATE_ENDPOINT = os.environ.get("JOB_UPDATE_PATH")

def update_callback(url, data):
    requests.put( url, data=data )

def job_get(**kwargs):
    """ """
    r = requests.get( kwargs.get('url'), headers=kwargs.get('headers', None), params=kwargs.get('params', None) )
    update_callback( UPDATE_ENDPOINT, 
                     data={ 
                            'job_id': kwargs.get('job_id'), 
                            'status_code': r.status_code 
                          } )    

def job_post(**kwargs):
    """ """
    r = requests.post( kwargs.get('url'), headers=kwargs.get('headers', None), data=kwargs.get('data', None) )
    update_callback( UPDATE_ENDPOINT, 
                     data={ 
                            'job_id': kwargs.get('job_id'), 
                            'status_code': r.status_code 
                          } )

def my_listener(event):
    if event.exception:
        print('The job crashed :(')
    else:
        print('The job worked :)')
