import datetime
import json
import logging

from safehouse.services import client
from safehouse.types import JsonBlob


logger = logging.Logger(__name__)


def get_event_types(organization_name: str, project_name: str) -> list[JsonBlob]:
    response = client.get(
        endpoint='/events/types/registry/',
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-ORGANIZATION": organization_name,
            "X-PROJECT": project_name,
        }
    )
    return response.json()


def register_event_types(
    *,
    event_types: list[JsonBlob],
) -> list[JsonBlob]:
    response = client.post(
        data=json.dumps(event_types),
        endpoint='/events/types/registry/',
    )
    return response.json()


def send_event(
    *,
    attributes: JsonBlob,
    name: str,
    origin: str,
    sent_at: datetime.datetime,
    version: int,
) -> bool:
    try:
        client.post(
            data=json.dumps(
                {
                    'attributes': attributes,
                    'name': name,
                    'origin': origin,
                    'sent_at': sent_at.isoformat(),
                    'version': version,
                }
            ),
            endpoint='/events/',
        )
    except client.ClientError as e:
        logger.error(f"couldn't send event type '{name}.{version}': {e}")
        return False
    return True
