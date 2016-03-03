"""
"""
import json
from datetime import datetime
import requests

def update_callback(url, data):
    requests.put( url, data=data )

def job_get(**kwargs):
    """ """
    r = requests.get( kwargs.get('url'), headers=kwargs.get('headers', None), params=kwargs.get('params', None) )
    update_callback( 'https://5379926d.ngrok.com/jobs', 
                     data={ 
                            'job_id': kwargs.get('job_id'), 
                            'status_code': r.status_code 
                          } )    

def job_post(**kwargs):
    """ """
    r = requests.post( kwargs.get('url'), headers=kwargs.get('headers', None), data=kwargs.get('data', None) )

def my_listener(event):
    if event.exception:
        print('The job crashed :(')
    else:
        print('The job worked :)')
