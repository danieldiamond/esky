import time

import papermill
from papermill.exceptions import PapermillExecutionError

import jobs
from settings import huey
from settings import logger
from utils import write_nb_to_html


@huey.task()
def job_runner(job_id, input_notebook, output_notebook,
               output_dir, parameters, **papermill_args):
    """
    Task to execute notebooks.

    Parameters
    ----------
    job_id: str, uuid4
        the job id
    input_notebook: str
        location of input notebook to run
    output_notebook: str
        location to put output_notebook
    parameters: dict
        notebook parameters
    papermill_args: **kwargs
        extra parameters to pass too papermill execution
    """
    log_context = dict(
        parameters=parameters, input_notebook=input_notebook,
        output_notebook=output_notebook, output_dir=output_dir,
        papermill_args=papermill_args
    )

    job_status = jobs.JobStatus.RUNNING

    # Execute Notebook
    try:
        logger.info('notebooks.executing.started', extra=log_context)

        papermill.execute_notebook(
            input_notebook,
            output_notebook,
            parameters=parameters,
            **papermill_args
        )

        job_status = jobs.JobStatus.SUCCESS
        log_context.update(dict(job_status=job_status))
        logger.info('notebooks.executing.finished', extra=log_context)

    except PapermillExecutionError as e:
        job_status = jobs.JobStatus.FAILED
        log_context.update(dict(job_status=job_status))
        logger.exception('notebooks.executing.error', extra=log_context)
        raise e

    return {
        "job_status": job_status,
        "output_notebook": output_notebook
    }


@huey.task()
def task_write_nb_to_html(filename):
    write_nb_to_html(filename)


@huey.task()
def fake_quick_task():
    logger.info('Consumer Logging fake quick task')
    return {
        "fake": "task",
        "task_length": "quick"
    }


@huey.task()
def fake_long_task():
    logger.info('Consumer Logging fake long task: wait 10 seconds')
    time.sleep(10)
    logger.info('End of fake long task')
    return {
        "fake": "task",
        "task_length": "10 seconds"
    }
