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
from tasks import job_runner, task_write_nb_to_html, fake_quick_task, fake_long_task

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
    parameters = job_request['parameters']
    kernel_name = job_request.get('kernel_name')
    create_date = str(datetime.datetime.now())
    status = jobs.JobStatus.CREATED
    job_id = uuid.uuid4().hex

    input_notebook = os.path.join(
        settings.AppConfig.NOTEBOOKS_DIR,
        job_request['input_notebook'])
    base_name = os.path.basename(input_notebook)
    jobname = job_request.get('jobname', os.path.splitext(base_name)[0])

    if not os.path.exists(input_notebook):
        response = {
            'ok': False,
            'error_message': 'Notebook does not exist',
            'job': job_request
        }
        return jsonify(response)

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
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    output_notebook = os.path.join(output_dir, jobname)
    if not output_notebook.endswith('.ipynb'):
        output_notebook = output_notebook + '.ipynb'

    logger.info('notebooks.trigger.job', extra={
        'request': job_request,
        'parameters': parameters
    })

    run_nb_task = job_runner(
        job_id, input_notebook,
        output_notebook, output_dir, parameters,
        kernel_name=kernel_name, cwd=output_dir
    )
    write_nb_task = task_write_nb_to_html(output_notebook)

    job_request.update(
         dict(output_notebook=output_notebook, input_notebook=input_notebook))

    response = {
        'ok': True,
        'status': status,
        'job': job_request,
        'run_nb_result': run_nb_task.task.id,
        'write_nb_result': write_nb_task.task.id
    }
    return jsonify(response)


@app.route('/examples/')
def get_example():
    return jsonify(settings.AppConfig.EXAMPLES_NOTEBOOKS)


@app.route('/pending/')
def get_pending():
    return jsonify(str(huey.pending()))


@app.route('/scheduled/')
def get_scheduled():
    return jsonify(str(huey.scheduled()))


@app.route('/results/')
def get_results():
    return jsonify(list(huey.all_results().keys()))


@app.route('/how_many/')
def get_how_many():
    return jsonify(huey.__len__())


@app.route('/add_fake_quick/')
def add_fake_quick():
    result = fake_quick_task()
    return jsonify(f'Add fake quick {result.task.id}')


@app.route('/add_fake_long/')
def add_fake_long():
    result = fake_long_task()
    return jsonify(f'Add fake long {result.task.id}')


@app.route('/check_task/<task_id>')
def check_task(task_id):
    return jsonify(huey.get(task_id, peek=True))


@app.route('/')
def index():
    return jsonify("Welcome")


if __name__ == '__main__':
    app.run(debug=True)
