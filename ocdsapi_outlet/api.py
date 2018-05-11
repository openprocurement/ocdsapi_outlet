import logging

from flask import jsonify
from flask_restful import Resource

from apscheduler.schedulers.gevent import GeventScheduler
from apscheduler.executors.gevent import GeventExecutor


LOGGER = logging.getLogger('ocdsapi.outlet')
SCHEDULER = GeventScheduler(
    executors={"default": GeventExecutor()},
    logger=LOGGER
)


class Jobs(Resource):
        
    def get(self):
        return jsonify({
            "jobs": SCHEDULER.print_jobs()
        })


def include(api, **options):
    api.add_resource(
        Jobs,
        '/jobs',
        endpoint='jobs',
    )
    


