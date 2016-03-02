"""
"""
import os
import json
import time
from datetime import datetime
from datetime import timedelta
from pytz import utc

import tornado.ioloop
import tornado.web

import apscheduler.schedulers.tornado
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

from sqlalchemy import create_engine

from schemas import ArchivedJob
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


class BaseHandler(tornado.web.RequestHandler):
  @property
  def db(self):
    return self.application.db


class JobsCtrl(tornado.web.RequestHandler):
    """ """
    def get(self):
        """ """
        response = {}
        print "*"*50
        print str(datetime.now()) + " Got it mr GET"
        print "*"*50

        self.set_status(200)
        self.write( json.dumps(response) )

    def post(self):
        """ """
        response = {}
        request = json.loads( self.request.body )

        if validator_action_trigger(request) and validator_action(request) and validator_trigger(request):

            if 'date' in request['trigger']:
                # Create a date job
                request['trigger']['date']['time'] = convert_isodate_to_dateobj(request['trigger']['date']['time'])

                print "Sending job at this time: " + str(request['trigger']['date']['time'])

                if request['action']['type'].lower() == 'http':
                    kind = request['action'].get('kind')
                    url = request['action'].get('url')
                    headers = request['action'].get('headers', None)
                    params = request['action'].get('params', None)
                    body = request['action'].get('body', None)

                    if kind.lower() == 'get':
                        # should generate an explicit job id here and pass it as a kwarg
                        # so that the job can then update the DB store with the appropriate response
                        job = scheduler.add_job(job_get, 'date', run_date=request['trigger']['date']['time'], kwargs={'url': url, 'headers': headers, 'params': params})
                        response['reason'] = 'Job created'
                        response['job_id'] = job.id
                        self.set_status(201)
                        self.write( json.dumps(response) )


                    elif kind.lower() == 'post':
                        job = scheduler.add_job(lambda: job_get(url=url, headers=headers, body=body), 'date', run_date=request['trigger']['date']['time'])
                        response['reason'] = 'Job created'
                        response['job_id'] = job.id
                        self.set_status(201)
                        self.write( json.dumps(response) )

                    else:
                        response['reason'] = 'HTTP action of kind ' + kind + ' is not supported.'
                        self.set_status(400)
                        self.write( json.dumps(response) )


                else:
                    response['reason'] =  request['action']['type'] + ' action is not supported.'
                    self.set_status(400)
                    self.write( json.dumps(response) )


            elif 'interval' in request['trigger']:
                # Create an interval job
                pass
            elif 'cron' in request['trigger']:
                # Create a cron job
                pass
            else:
                response['reason'] = 'Trigger is not supported.'
                self.set_status(400)
                self.write( json.dumps(response) )


        else:
            response['reason'] = "Improperly configured request body."
            self.set_status(400)
            self.write( json.dumps(response) )


routes = [
    (r'/jobs', JobsCtrl),
]

application = tornado.web.Application(routes, debug=True)


if __name__ == '__main__':
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        scheduler.start()
        application.listen(PORT)
        tornado.ioloop.IOLoop.current().start()
    except( KeyboardInterrupt, SystemExit ):
        print("Shutting Down")
        pass