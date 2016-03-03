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

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from schemas import ArchivedJob, init_db
from jobs import job_get, job_post
from serializers import validator_action_trigger, validator_action, validator_trigger 

# Configure tornado
PORT = 8888

# Configure DB
engine = create_engine('sqlite:///jobs.sqlite', echo=False)

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
    job_id = generate_id()
    kind = request['action'].get('kind')
    url = request['action'].get('url')
    headers = request['action'].get('headers', None)
    params = request['action'].get('params', None)
    body = request['action'].get('body', None)
    callback = request['action'].get('callback', None)
    
    if kind.lower() == 'get':
        job = scheduler.add_job(job_get,
                                'date', 
                                id=job_id,
                                run_date=request['trigger']['date']['time'], 
                                kwargs={
                                    'job_id': job_id,
                                    'url': url, 
                                    'headers': headers, 
                                    'params': params,
                                    'callback': callback
                                })
    
    elif kind.lower() == 'post':
        job = scheduler.add_job(job_post, 
                                'date',
                                id=job_id,
                                run_date=request['trigger']['date']['time'], 
                                kwargs={
                                    'job_id': job_id,
                                    'url': url, 
                                    'headers': headers, 
                                    'params': params,
                                    'callback': callback
                                })

    # Save the job in the db archives
    archived_job = ArchivedJob(id=job_id,
                               status=False,
                               response='',
                               action='http_' + kind,
                               trigger='date',
                               callback=callback,
                               
                               time_created = datetime.now())
    session.add(archived_job)
    session.commit()
    
    return job_id


class BaseHandler(tornado.web.RequestHandler):
    def prepare(self):
        if self.request.headers["Content-Type"].startswith("application/json"):
            self.json_args = json.loads( self.request.body )
        else:
            self.json_args = None


class JobsHandler(BaseHandler):
    """ """
    def get(self):
        """Retrieves a job given a job id"""
        response = {}
        job_id = self.get_argument("id", default=None)
        
        print "*"*50
        print str(datetime.now()) + " Got it mr GET"
        print "*"*50

        self.set_status(200)
        self.write( json.dumps(response) )

    def post(self):
        """Creates a job"""
        response = {}
        # Validate the request
        
        # Serialzie the request
        self.json_args['trigger']['date']['time'] = convert_isodate_to_dateobj(self.json_args['trigger']['date']['time'])
        
        # Create the job
        job_id = create_http_date_job( self.json_args, session=Session() )
        response['reason'] = 'Job created'
        response['job_id'] = job_id
        self.set_status(201)
        self.write( json.dumps(response) )


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
        
        # start the db
        init_db(engine)
        Session = sessionmaker(bind=engine)
        
        application.listen(PORT)
        tornado.ioloop.IOLoop.instance().start()
    except( KeyboardInterrupt, SystemExit ):
        print("Shutting Down")
        pass