"""
"""
import requests

def job_get(**kwargs):
    """ """
    requests.get( kwargs.get('url'), headers=kwargs.get('headers', None), params=kwargs.get('params', None) )

def job_post(**kwargs):
    """ """
    requests.post( kwargs.get('url'), headers=kwargs.get('headers', None), body=kwargs.get('body', None) )
