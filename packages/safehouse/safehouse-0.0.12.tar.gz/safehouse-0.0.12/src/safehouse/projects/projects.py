import json
from pathlib import Path

from safehouse.events.event_manager import EventManager
from safehouse import mode
from safehouse.services import local
from safehouse.types import JsonBlob
from . import exceptions


MODES = (
    'live',
    'local',
    'standalone',
)


class Project:
    def __init__(
        self,
        *,
        event_type_definitions: list[JsonBlob]=list(),
        filepath: Path,
        in_development: bool=False,
        mode: str='local',
        name: str,
        organization_name: str,
    ):
        self.event_type_definitions: list[JsonBlob] = event_type_definitions
        self._events_manager: EventManager | None = None
        self.filepath = filepath
        self.in_development = bool(in_development)
        self.mode = mode.lower()
        self.name = name.lower()
        self.organization_name = organization_name.lower()
        self.validate()

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"{self.organization_name}.{self.name} ({self.filepath})"

    @property
    def events(self) -> EventManager:
        if self._events_manager is None:
            self._events_manager = EventManager(self.event_type_definitions)
            self._events_manager.register_event_types()
        return self._events_manager

    @property
    def is_local(self) -> bool:
        return self.mode == 'local'

    @property
    def json(self) -> JsonBlob:
        return {
            'events': self.event_type_definitions,
            'mode': self.mode,
            'name': self.name,
            'organization': self.organization_name,
        }

    @property
    def json_file(self) -> Path:
        return self.filepath / 'project.json'

    def save(self):
        with open(self.json_file, 'w') as f:
            json.dump(self.json, f, indent=4)

    @property
    def services_url(self) ->str:
        # use inversion of control here: services or actions (for standalone) interrogate for mode
        # and then "to the right thing"
        return mode.services_url()

    def validate(self):
        if self.in_development:
            assert self.filepath is not None
        assert self.name is not None
        assert self.organization_name is not None
        if self.mode not in MODES:
            raise Exception(f"unsupported mode: '{self.mode}'")
        #if self.is_local and not local.is_running():
        #    raise exceptions.ProjectError(f"{self} needs safehouse services to be running locally")


def from_safehouse_dir(safehouse_dir: Path, in_development: bool=False) -> Project:
    project_json_file = str(safehouse_dir / "project.json")
    with open(project_json_file, 'r', encoding='utf-8') as f:
        project_dict: JsonBlob = json.load(f)
        events = project_dict.get('events', {})
        mode = project_dict.get('mode', 'local')
        name = project_dict.get('name')
        org_name = project_dict.get('organization')
        return Project(
            event_type_definitions=events,
            filepath=safehouse_dir,
            in_development=in_development,
            mode=mode,
            name=name,
            organization_name=org_name,
        )


def from_settings(
        *,
        filepath: Path,
        mode: str,
        name: str,
        org_name: str,
) -> Project:
    return Project(
        filepath=filepath,
        mode=mode,
        name=name,
        organization_name=org_name,
    )
