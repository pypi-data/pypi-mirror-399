import logging
from pathlib import Path
from typing import List

from safehouse import projects
from ..exceptions import CommandError


logger = logging.getLogger()


def run(args: List[str]) -> projects.Project:
    if projects.current_development_project():
        raise CommandError(f"project already exists: {projects.current_development_project()}")
    if len(args) != 1:
        raise CommandError(usage())
    tokens = args[0].split('.')
    if len(tokens) != 2:
        raise CommandError(usage())
    organization, project = tokens
    project_dir: Path = Path.cwd()
    config_dir = project_dir / '.safehouse'
    try:
        project = projects.from_settings(
            filepath=config_dir,
            name=project,
            org_name=organization,
            mode='local',
        )
    except projects.exceptions.ProjectError as e:
        raise CommandError(str(e))
    Path.mkdir(config_dir, exist_ok=True)
    project.save()
    logger.info(f"succesfully initialized {project}")
    return project


def usage() -> str:
    return "usage: safehouse init <organization.project>"
