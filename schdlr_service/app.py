"""
"""
import os
import json
import time
import random
import string
from datetime import datetime
from datetime import timedelta

from os.path import join, dirname
from dotenv import load_dotenv

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import apscheduler.schedulers.tornado
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import requests

import models
from jobs import job_get, job_post
from serializers import validator_action_trigger, validator_action, validator_trigger 

# Load the .env file
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


# Options
tornado.options.define('port', default=8888, help='run on the given port', type=int)
tornado.options.define('debug', default=True, type=bool)
tornado.options.define('db_path', default=os.environ.get('DB_PATH'), type=str)


# Configure APScheduler
JOBSTORES = {
    'default': SQLAlchemyJobStore(url=os.environ.get('DB_PATH'))
}
EXECUTORS = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}
JOB_DEFAULTS = {
    'coalesce': False,
    'max_instances': 3
}


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            tornado.web.url(r'/jobs', JobsHandler, name='jobs'),
        ]
        settings = dict(
            debug=tornado.options.options.debug
        )
        tornado.web.Application.__init__(self, handlers, **settings)
        
        # Configure the database
        engine = create_engine(tornado.options.options.db_path, convert_unicode=True, echo=tornado.options.options.debug)
        models.init_db(engine)
        self.db = scoped_session(sessionmaker(bind=engine))

        # Configure the scheduler
        scheduler = apscheduler.schedulers.tornado.TornadoScheduler(jobstores=JOBSTORES)
        # scheduler.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        scheduler.start()
        self.schdlr = scheduler


# Utility functions
def convert_isodate_to_dateobj(iso_str):
    return datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S.%f")

def generate_id(N=50):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))

def create_http_date_job(request, scheduler=None, session=None):
    http_jobs = {
        'get': job_get,
        'post': job_post
    }
    
    try:
        job_id = generate_id()

        job = scheduler.add_job(http_jobs[request['action'].get('kind').lower()],
                                'date', 
                                id=job_id,
                                run_date=request['trigger']['date']['time'], 
                                kwargs={
                                    'job_id': job_id,
                                    'url': request['action'].get('url'), 
                                    'headers': request['action'].get('headers', None), 
                                    'params': request['action'].get('params', None),
                                    'data': request['action'].get('data', None),
                                    'callback': request['action'].get('callback', None)
                                })
        

        # Save the job in the db archives
        archived_job = models.ArchivedJob(id=job_id,
                                          status=False,
                                          action='http_' + request['action'].get('kind').lower(),
                                          trigger='date',
                                          callback=request['action'].get('callback', None),
                                        
                                          time_created = datetime.now())
        session.add(archived_job)
        session.commit()
        
        return job_id
    except Exception as e:
        print "There was an error: " + str(e)
        return None
    
    


class BaseHandler(tornado.web.RequestHandler):
    def prepare(self):
        # This service will always return application/json
        self.set_header('Content-Type', 'application/json')
        
        # Load JSON data
        if 'Content-Type' in self.request.headers:
            if self.request.headers["Content-Type"].startswith("application/json"):
                request = self.request.body or '{}'
                self.json_args = json.loads( request )
            else:
                self.json_args = None
        else:
            self.json_args = None
    
    @property
    def db(self):
        return self.application.db
    
    @property
    def schdlr(self):
        return self.application.schdlr


class JobsHandler(BaseHandler):
    """Main handler that deals with creating and retrieving jobs"""
    def get(self):
        """Retrieves a job given a job id"""
        response = {}
        job_id = self.get_argument("id", default=None)
        
        if job_id:
            job = self.db.query(models.ArchivedJob).filter_by( id=job_id ).first()
            
            if job:
                response['job_id'] = job_id
                response['job'] = {
                    'status': job.status,
                    'action': job.action,
                    'trigger': job.trigger,
                    'callback': job.callback,
                    'time_created': job.time_created.isoformat(),
                    'time_completed': job.time_completed.isoformat() if job.time_completed else None
                } 
                self.set_status(200)
                self.write( json.dumps(response) )
            else:
                self.set_status(404)

        else:
            self.set_status(404)
         

    def post(self):
        """Creates a job"""
        response = {}
        # Validate the request
        # TODO
        
        # Serialzie the request
        # TODO
        self.json_args['trigger']['date']['time'] = convert_isodate_to_dateobj(self.json_args['trigger']['date']['time'])
        
        # Create the job
        job_id = create_http_date_job( self.json_args, scheduler=self.schdlr, session=self.db )
        if job_id:
            response['reason'] = 'Job created'
            response['job_id'] = job_id
            self.set_status(201)
            self.write( json.dumps(response) )
        else:
            self.set_status(400)
    
    def put(self):
        """Updates a job""" 
        job = self.db.query(models.ArchivedJob).filter_by( id=self.get_argument('job_id') ).first()
        if job:
            job.status = True
            job.status_code = self.get_argument('status_code')
            job.time_completed = datetime.now()
            
            self.db.commit()
            
            # if callback was provided, send a GET
            if job.callback:
                requests.get( job.callback )    
    

def main():
    """
    """
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer( Application() )
    http_server.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    print '[%s]: Serving on port %s' % ( str(datetime.now()), str(tornado.options.options.port) )    
    try:
        main()
    except( KeyboardInterrupt, SystemExit ):
        print '[%s]: Stopping tornado' % str(datetime.now())
        pass