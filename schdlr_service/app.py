"""
"""
import os
import json
import time
import random
import string
from datetime import datetime
from datetime import timedelta
from pytz import utc

import tornado.options
import tornado.ioloop
import tornado.web

import apscheduler.schedulers.tornado
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

from db import Session
from models import ArchivedJob, init_db
from jobs import job_get, job_post
from serializers import validator_action_trigger, validator_action, validator_trigger 

# Configure tornado
PORT = 8888

# Configure APScheduler
JOBSTORES = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}
EXECUTORS = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}
JOB_DEFAULTS = {
    'coalesce': False,
    'max_instances': 3
}
scheduler = apscheduler.schedulers.tornado.TornadoScheduler(jobstores=JOBSTORES)


# Utility functions
def convert_isodate_to_dateobj(iso_str):
    return datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S.%f")

def generate_id(N=50):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))

def create_http_date_job(request, session=None):
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
                                    'body': request['action'].get('body', None),
                                    'callback': request['action'].get('callback', None)
                                })
        

        # Save the job in the db archives
        archived_job = ArchivedJob(id=job_id,
                                status=False,
                                response='',
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
        if 'Content-Type' in self.request.headers:
            if self.request.headers["Content-Type"].startswith("application/json"):
                request = self.request.body or '{}'
                self.json_args = json.loads( request )
            else:
                self.json_args = None
        else:
            self.json_args = None


class JobsHandler(BaseHandler):
    """Main handler that deals with creating and retrieving jobs"""
    def get(self):
        """Retrieves a job given a job id"""
        response = {}
        job_id = self.get_argument("id", default=None)
        
        if job_id:
            session = Session()
            job = session.query(ArchivedJob).filter_by( id=job_id ).first()
            
            if job:
                response['job_id'] = job_id
                response['job'] = {
                    'status': job.status,
                    'response': job.response,
                    'action': job.action,
                    'trigger': job.trigger,
                    'callback': job.callback,
                    'time_created': job.time_created.isoformat(),
                    'time_completed': job.time_completed.isoformat() if job.time_completed else None
                }
                
                self.set_header('Content-Type', 'application/json') 
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
        job_id = create_http_date_job( self.json_args, session=Session() )
        if job_id:
            response['reason'] = 'Job created'
            response['job_id'] = job_id
            self.set_status(201)
            self.write( json.dumps(response) )
        else:
            self.set_status(400)

# Define the routes
routes = [
    tornado.web.url(r'/jobs', JobsHandler, name='jobs'),
]

# Define the application
application = tornado.web.Application(routes, debug=True)

if __name__ == '__main__':
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        # Start the scheduler
        scheduler.start()
        
        # Start the application
        application.listen(PORT)
        tornado.ioloop.IOLoop.instance().start()
    except( KeyboardInterrupt, SystemExit ):
        print("Shutting Down")
        pass