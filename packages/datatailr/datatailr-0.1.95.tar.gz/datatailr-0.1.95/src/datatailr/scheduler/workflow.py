import os
from typing import Callable, Optional, Dict, Union
import functools
from datatailr.logging import DatatailrLogger
from datatailr.scheduler import Batch, Schedule, Resources
from datatailr import Environment, Image, ACL, User

logger = DatatailrLogger(__name__).get_logger()


def workflow(
    name: Optional[str] = None,
    schedule: Optional[Schedule] = None,
    image: Optional[Image] = None,
    run_as: Optional[Union[str, User]] = None,
    resources: Resources = Resources(memory="100m", cpu=1),
    acl: Optional[ACL] = None,
    python_version: str = "auto",
    python_requirements: str = "",
    build_script_pre: str = "",
    build_script_post: str = "",
    env_vars: Dict[str, str | int | float | bool] = {},
):
    _name = name
    _schedule = schedule
    _image = image
    _run_as = run_as
    _resources = resources
    _acl = acl
    _python_version = python_version
    _python_requirements = python_requirements
    _build_script_pre = build_script_pre
    _build_script_post = build_script_post
    _env_vars = env_vars

    def decorator(func) -> Callable:
        @functools.wraps(func)
        def wrapper(
            *args,
            local_run: bool = False,
            schedule: Optional[Schedule] = None,
            image: Optional[Image] = None,
            run_as: Optional[Union[str, User]] = None,
            resources: Optional[Resources] = None,
            acl: Optional[ACL] = None,
            python_version: Optional[str] = None,
            python_requirements: Optional[str] = None,
            build_script_pre: Optional[str] = None,
            build_script_post: Optional[str] = None,
            env_vars: Optional[Dict[str, str | int | float | bool]] = None,
            **kwargs,
        ):
            workflow_file_path = func.__code__.co_filename
            # If the workflow is being invoked from a package installed in the container then raise a warning and return
            if (
                workflow_file_path.startswith(
                    "/opt/datatailr/usr/lib/python/site-packages/"
                )
                and os.getenv("DATATAILR_JOB_TYPE") == "batch"
            ) or os.getenv("DATATAILR_BATCH_DONT_RUN_WORKFLOW") == "true":
                return
            __schedule = schedule or _schedule
            __image = image or _image
            __run_as = run_as or _run_as
            __resources = resources or _resources
            __acl = acl or _acl
            __python_version = python_version or _python_version
            __python_requirements = python_requirements or _python_requirements
            __build_script_pre = build_script_pre or _build_script_pre
            __build_script_post = build_script_post or _build_script_post
            __env_vars = env_vars or _env_vars

            if local_run and (__schedule is not None):
                raise ValueError("Cannot set schedule for local run.")

            dag = Batch(
                name=_name or func.__name__.replace("_", " ").title(),
                environment=Environment.DEV,
                schedule=__schedule,
                image=__image,
                run_as=__run_as,
                resources=__resources,
                acl=__acl,
                local_run=local_run,
                python_version=__python_version,
                python_requirements=__python_requirements,
                build_script_pre=__build_script_pre,
                build_script_post=__build_script_post,
                env_vars=__env_vars,
            )
            dag.set_autorun(False)
            with dag:
                func(*args, **kwargs)

        return wrapper

    return decorator
