"""
"""
import os
import json
from datetime import datetime

import tornado.ioloop
import tornado.web

import apscheduler.schedulers.tornado

import requests


PORT = 8888
scheduler = apscheduler.schedulers.tornado.TornadoScheduler()

def tick(x):
    print( 'Tick tock Mr %s, the time is %s' % (x, datetime.now() ) ) 


# Jobs
def job_get(url, headers=None, params=None):
    """ """
    requests.get(url, headers=headers, params=params)

def job_post(url, headers=None, body=None):
    """ """
    requests.post(url, headers=headers, body=body)


# Serializers


# Validators
def validator_action_trigger(request):
    if 'action' in request and 'trigger' in request:
        return True
    return False

def validator_action(request):
    if 'type' in request['action'] and 'url' in request['action'] and 'kind' in request['action']:
        return True
    return False

def validator_trigger(request):
    if 'date' in request['trigger'] or 'interval' in request['trigger'] or 'cron' in request['trigger']:
        return True
    return False


class JobsCtrl(tornado.web.RequestHandler):
    """ """
    def get(self):
        """ """
        response = {}
        print "Got it mr GET"
        
        # scheduler.add_job(lambda: tick("applesauce"), 'interval', seconds=5)
        
        self.set_status(200)
        self.write( json.dumps(response) )

    def post(self):
        """ """
        response = {}
        request = json.loads( self.request.body )
        
        if validator_action_trigger(request) and validator_action(request) and validator_trigger(request):
            
            if request['trigger'] == 'date':
                # Create a date job
                print "Creating a date job"
                
                if request['action']['type'].lower() == 'http':
                    kind = request['action'].get('kind')
                    url = request['action'].get('url')
                    headers = request['action'].get('headers', None)
                    params = request['action'].get('params', None)
                    body = request['action'].get('body', None)
                    
                    if kind.lower() == 'get':
                        job = scheduler.add_job(lambda: job_get(url=url, headers=headers, params=params), 'date', rundate=request['action']['time'])
                    elif kind.lower() == 'post':
                        job = scheduler.add_job(lambda: job_get(url=url, headers=headers, body=body), 'date', rundate=request['action']['time'])
                    
                    else:
                        response['reason'] = 'HTTP action of kind ' + kind + ' is not supported.'
                        self.set_status(400)
                        self.write( json.dumps(response) )
                
                else:
                    response['reason'] =  request['action']['type'] + ' action is not supported.'
                    self.set_status(400)
                    self.write( json.dumps(response) )
                
            elif request['trigger'] == 'interval':
                # Create an interval job
                pass
            elif request['trigger'] == 'cron':
                # Create a cron job
                pass
            response['reason'] = request['trigger'] + ' trigger is not supported.'
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