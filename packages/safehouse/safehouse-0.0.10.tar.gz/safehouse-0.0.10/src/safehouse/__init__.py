import logging

from . import (
    events as events,
    mode as mode,
    projects as projects,
    services as services,
    users as users,
    utils as utils,
)


active_project = None
logger = logging.Logger(__name__)
runtime_mode = "local"
user = users.User()


projects.init(user.safehouse_directory, user.organizations_directory)


def activate_project(
    *,
    name: str,
    org_name: str,
    runtime_mode: str,
    user: users.User | None = None,
) -> projects.Project:
    global active_project
    active_project = projects.register_project(
        mode=runtime_mode,
        name=name,
        org_name=org_name,
        user=user,
    )
    try:
        services.organizations.register_active_project()
    except services.exceptions.ServicesError as e:
        logger.error(f"couldn't register {active_project} with safehouse services: '{e}'")
    return active_project
