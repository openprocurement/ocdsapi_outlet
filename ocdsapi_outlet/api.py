
from gevent import monkey
monkey.patch_all()

import logging
import sys
import click
import yaml
import os.path
from logging.config import dictConfig
from flask import Flask
from flask import jsonify
from flask import send_from_directory
from flask_restful import Resource, Api
from waitress import serve
from datetime import datetime, timedelta
from apscheduler.schedulers.gevent import GeventScheduler
from apscheduler.executors.gevent import GeventExecutor
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from gevent import spawn
from .utils import dump
from . import constants as C


LOGGER = logging.getLogger('ocdsapi_dumptool')
logging.getLogger('waitress').setLevel(logging.INFO)
SCHEDULER = GeventScheduler(
    executors={"default": GeventExecutor()},
    logger=LOGGER
)
APP = Flask(__name__)
API = Api(APP)


class Health(Resource):

    def get(self):
        """
        Route for health checks
        """
        return jsonify({"status": "ok"})


class Jobs(Resource):
    """
    Simple API over current scheduler status
    """
    def get(self):
        jobs = SCHEDULER.get_jobs()
        LOGGER.info("Current jobs {}".format(jobs))
        return jsonify({
            "jobs": jobs
        })

    def post(self):
        """ Start dumping """
        try:
            run_at = datetime.now()  + timedelta(seconds=10)
            SCHEDULER.add_job(
                func=dump,
                args=(APP, LOGGER),
                trigger=DateTrigger(run_date=run_at)
            )
            return jsonify({
                "result": "success",
                "reason": {
                    "next_run": run_at
                }
            })
        except Exception as e:
            return jsonify({
                "result": "error",
                "reason": str(e)

            })


class StaticContent(Resource):

    def get(self): 
        """
        Download all tender as zip file
        """
        path = APP.config['backend']['fs']['file_path']
        if not path.startswith('/'):
            root_dir = os.path.dirname(os.getcwd())
            path = os.path.join(root_dir, path)
        LOGGER.info('Sending file {}'.format(os.path.join(path, C.ZIP_NAME)))
        return send_from_directory(
            path,
            C.ZIP_NAME,
            mimetype='application/zip',
            as_attachment=True,
            attachment_filename=C.ZIP_NAME
        )


def main(cfg):
    with open(cfg) as _in:
        config = yaml.load(_in)

    server_cfg = config.pop('server')
    for section in ('db', 'dump', 'backend'):
        APP.config[section] = config.get(section)
    dictConfig(config)
    SCHEDULER.start()

    if 'cron' in APP.config['dump']:
        SCHEDULER.add_job(
            func=dump,
            args=(APP, LOGGER),
            trigger=CronTrigger.from_crontab(APP.config['dump']['cron']),
            id="cron_dumper"
        )
    # For now serving is available only for fs backand due to
    # serving public files from s3 makes no sense
    API.add_resource(Jobs, '/jobs', endpoint='jobs')
    API.add_resource(Health, '/health', endpoint='health')
    API.add_resource(StaticContent, "/{}".format(C.ZIP_NAME), endpoint='Json')
    return serve(APP, **server_cfg)


@click.command()
@click.option(
    '--config',
    help='path to configuration file',
    required=True
)
def run(config):
    """
    Main script entry point
    """
    sys.exit(main(config))
