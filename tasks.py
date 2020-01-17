import functools
import os

import papermill
from papermill.exceptions import PapermillExecutionError

import jobs
from settings import huey
from settings import logger


def preserve_cwd(func):
    """To support artifacts notebooks might generate we run them in a directory.
    To run them in a directory we chdir into it and back after executing
    this function automates that process"""
    # FROM: https://stackoverflow.com/a/170174
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        cwd = os.getcwd()
        try:
            yield func(*args, **kwargs)
        finally:
            os.chdir(cwd)

    return decorator


def _assert_path_notexist(path):
    if os.path.exists(path):
        raise FileExistsError(f'{path} already exists')


@preserve_cwd
@huey.task()
def job_runner(job_id, input_notebook, output_notebook,
               output_dir, parameters, **papermill_args):
    """
    Task to execute notebooks. This task changes the working directory to
    {output_dir} and back to origin after function exists.
    Hence the @preserve_cwd

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

    try:
        logger.info('notebooks.executing.started', extra=log_context)

        _assert_path_notexist(output_dir)
        os.makedirs(output_dir)

        os.chdir(output_dir)

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
