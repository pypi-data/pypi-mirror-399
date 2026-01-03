from pathlib import Path

import safehouse
from safehouse import users, utils


from .projects import (
    from_safehouse_dir as from_safehouse_dir,
    from_settings as from_settings,
    Project as Project,
)
from . import exceptions as exceptions


_projects_registry: dict[str, dict[str, Project]] = {}


def current_development_project() -> Project | None:
    for p in list_projects():
        if p.in_development:
            return p
    return None

        
def init(user_safehouse_directory, user_organizations_directory):
    development_safehouse_directory = utils.find_directory_in_parent_dirs('.safehouse')
    if development_safehouse_directory and development_safehouse_directory != user_safehouse_directory:
        load_project(from_safehouse_dir(development_safehouse_directory, in_development=True))
    load_projects(user_organizations_directory)


def load_project(project: Project):
    if project.organization_name not in _projects_registry:
        _projects_registry[project.organization_name] = { project.name: project }
    else:
        _projects_registry[project.organization_name][project.name] = project


def load_projects(organizations_root: Path):
    organization_dirs = [item for item in organizations_root.iterdir() if item.is_dir()]
    for organization_dir in organization_dirs:
        projects_dirs = [item for item in organization_dir.iterdir() if item.is_dir()]
        for project_dir in projects_dirs:
            if not registered_project(organization_dir.name, project_dir.name):
                load_project(from_safehouse_dir(project_dir))


def list_projects() -> list[Project]:
    projects_list = []
    for org_projects in _projects_registry.values():
        projects_list += org_projects.values()
    return projects_list


def register_project(
    *,
    mode: str,
    name: str,
    org_name: str,
    user: users.User | None = None,
) -> Project:
    project = registered_project(org_name, name)
    if project:
        return project
    if user is None:
        user = safehouse.user
    filepath = user.organizations_directory / org_name / name
    filepath.mkdir(parents=True, exist_ok=True)
    project = from_settings(filepath=filepath, mode=mode, org_name=org_name, name=name)
    project.save()
    return project


def registered_project(org_name: str, name: str) -> Project | None:
    org_dict = _projects_registry.get(org_name)
    if org_dict:
        return org_dict.get(name)
    return None
