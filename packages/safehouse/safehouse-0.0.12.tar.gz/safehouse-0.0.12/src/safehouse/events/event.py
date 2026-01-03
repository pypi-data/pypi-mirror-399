import datetime
import logging
import uuid

from .exceptions import FieldError
from safehouse.services import events as events_service
from safehouse.types import JsonBlob


FIELD_TYPES = int|float|str # Datetime is handled as a special case
logger = logging.Logger(__name__)


class FieldType:
    def __init__(self, data_type: FIELD_TYPES):
        self.data_type: FIELD_TYPES = data_type

    def cast(self, value: object) -> FIELD_TYPES:
        try:
            return self.data_type(value) # ty: ignore
        except ValueError:
            raise FieldError(f"couldn't convert '{value}' to data type {self.data_type}")


class DatetimeFieldType:
    def __init__(self):
        pass

    def cast(self, value: datetime.datetime) -> str:
        try:
            return value.isoformat()
        except Exception:
            raise FieldError(f"couldn't convert '{value}' to a stringified datetime") 


class UUIDFieldType:
    def __init__(self):
        pass

    def cast(self, value: uuid.UUID) -> str:
        try:
            return str(value)
        except Exception:
            raise FieldError(f"couldn't convert '{value}' to a UUID")


DATA_TYPE_NAME_TO_FIELD_TYPE = {
    'datetime': DatetimeFieldType(),
    'int': FieldType(int), # ty: ignore
    'float': FieldType(float), # ty: ignore
    'str': FieldType(str), # ty: ignore
    'uuid': UUIDFieldType(),
}


class EventType:
    def __init__(
        self,
        *,
        fields: dict[str, str]={},
        name: str,
        organization_name: str,
        project_name: str,
        services_url: str,
        version: int,
    ):
        self.fields = {}
        for field_name, field_type_name in fields.items():
            field_type = DATA_TYPE_NAME_TO_FIELD_TYPE.get(field_type_name)
            if not field_type:
                raise FieldError(f"unknown field type '{field_type_name}'")
            self.fields[field_name] = field_type
        self.name = name
        self.organization_name= organization_name
        self.project_name = project_name
        self.services_url = services_url
        self.version = version

    def __str_(self) -> str:
        return self.name


class Event:
    def __init__(
            self,
            *,
            event_type: EventType,
            origin: str,
    ):
        self.event_type = event_type
        self.origin = origin

    def __str__(self) -> str:
        return f"{self.event_type} event"

    def format_attributes(self, attributes: JsonBlob) -> JsonBlob:
        formatted_attributes = {}
        for name, value in attributes.items():
            field_type = self.event_type.fields.get(name)
            if not field_type:
                raise Exception(f"attempting to send unknown field '{name}={attributes[name]}'")
            formatted_attributes[name] = field_type.cast(value)
        return formatted_attributes

    def send(self, *args, **kwargs) -> bool:
        '''
        send event with supplied arguments; returns True if sent and False otherwise.
        '''
        try:
            event_attributes = self.format_attributes(kwargs)
            return events_service.send_event(
                attributes=event_attributes,
                name=self.event_type.name,
                origin=self.origin,
                sent_at=datetime.datetime.now(datetime.timezone.utc),
                version=self.event_type.version,
            )
        except FieldError as e:
            logger.error(f"couldn't send {self}: {e}")
            return False


class UnknownEvent:
    def __init__(
            self,
            *,
            event_type_name: str,
            origin: str,
    ):
        self.event_type_name = event_type_name
        self.origin = origin

    def send(self, *args, **kwargs) -> bool:
        logger.error(f"unknown event type: '{self.event_type_name}'")
        return False
