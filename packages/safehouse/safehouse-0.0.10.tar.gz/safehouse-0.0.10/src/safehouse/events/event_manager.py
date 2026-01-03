import logging

import safehouse
from safehouse import assertions
from safehouse.services import events as events_service
from safehouse.types import JsonBlob

from .event import Event, EventType, UnknownEvent


logger = logging.Logger(__name__)


class EventManager:
    def __init__(self, event_type_definitions: list[JsonBlob], origin: str=''):
        self.event_types: dict[str, EventType] = {}
        self.event_type_definitions = event_type_definitions
        self.origin = origin

    def __getattr__(self, name):
        event_type = self.event_types.get(name)
        if event_type:
            return Event(event_type=event_type, origin=self.origin)
        return UnknownEvent(event_type_name=name, origin=self.origin)

    def register_event_types(self):
        assertions.active_project()
        event_types_data: list[JsonBlob] = []
        event_types_data= events_service.register_event_types(
            event_types=self.event_type_definitions,
        )
        self.event_types = {
            str(e['name']): EventType(
                fields=e['attributes'], # ty: ignore
                name=e['name'], #ty: ignore
                organization_name=self.organization_name,
                project_name=self.project_name,
                services_url=self.services_url,
                version=e['version'], # ty: ignore
            ) # ty: ignore
            for e in event_types_data
        }
        if not self.event_types:
            logger.warning(f"There are no event types available for use in {safehouse.active_project}")
