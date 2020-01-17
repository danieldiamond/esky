import datetime
import os
import traceback
import uuid

from flask import (
    Flask,
    jsonify,
    request
)
from papermill.exceptions import PapermillExecutionError

import jobs
import settings
from settings import logger
from settings import huey  # noqa
from tasks import job_runner

app = Flask(__name__)


@app.errorhandler(Exception)
def handle_error(error):
    message = [str(x) for x in error.args]
    status_code = 500
    success = False
    response = {
        'ok': success,
        'error_type': 'Unhandled Exception',
        'error_class': error.__class__.__name__,
        'error_message': message,
        'traceback': traceback.format_exc()
    }

    return jsonify(response), status_code


@app.errorhandler(PapermillExecutionError)
def handle_papermill_error(error):
    message = [str(x) for x in error.args]
    status_code = 500
    success = False
    response = {
        'ok': success,
        'error_type': error.__class__.__name__,
        'error_class': error.__class__.__name__,
        'error_message': message,
        'traceback': traceback.format_exc()
    }

    return jsonify(response), status_code


@app.route('/run/', methods=['POST'])
def run():
    job_request = request.get_json()
    # logger.info('TESSTTTTTTTT', extra={
    #     'job_request IS IT JSON ++++': request.get_json()
    # })
    # return
    kernel_name = job_request.get('kernel_name')
    input_notebook = os.path.join(
        settings.AppConfig.EXAMPLES_DIR,
        job_request['input_notebook'])
    parameters = job_request['parameters']

    # job name and notebook name are the same
    jobname = os.path.basename(input_notebook)
    create_date = str(datetime.datetime.now())
    status = jobs.JobStatus.CREATED
    job_id = uuid.uuid4().hex

    parameters['job_info'] = dict(
        job_id=job_id,
        create_date=create_date,
        jobname=jobname
    )

    output_dir = os.path.join(
        settings.AppConfig.OUTPUT_DESTINATION,
        jobname,
        job_id
    )

    output_notebook = os.path.join(output_dir, jobname)

    logger.info('notebooks.trigger.job', extra={
        'request': job_request,
        'parameters': parameters
    })

    # trigger job run async
    x = job_runner(
        job_id, input_notebook,
        output_notebook, output_dir, parameters,
        kernel_name=kernel_name
    )

    job_request.update(
         dict(output_notebook=output_notebook, input_notebook=input_notebook))

    response = {
        'ok': True,
        'status': status,
        'job': job_request
    }

    [i for i in x]

    return jsonify(response)


@app.route('/examples/', methods=['GET'])
def get_example():
    return jsonify(settings.AppConfig.EXAMPLES_NOTEBOOKS)


if __name__ == '__main__':
    app.run(debug=True)
