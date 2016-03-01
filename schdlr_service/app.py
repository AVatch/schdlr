"""
"""

from datetime import datetime
import os

import tornado.ioloop
import tornado.web
from apscheduler.schedulers.tornado import TornadoScheduler

PORT = 8888
scheduler = TornadoScheduler()

def tick():
    print( 'Tick tock, the time is %s' % datetime.now() ) 


class TaskViewCtrl(tornado.web.RequestHandler):
    def get(self):
        scheduler.add_job(tick, 'interval', seconds=5)
        print "GET IT"
        self.write("Hello World")

routes = [
    (r'/task', TaskViewCtrl),
]

application = tornado.web.Application(routes, debug=True)


if __name__ == '__main__':
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        scheduler.start()
        application.listen(PORT)
        tornado.ioloop.IOLoop.current().start()
    except( KeyboardInterrupt, SystemExit ):
        pass
