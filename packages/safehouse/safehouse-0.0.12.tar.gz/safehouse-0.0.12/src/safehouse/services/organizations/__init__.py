import json
import logging

import safehouse
from safehouse.services import client
from safehouse.types import JsonBlob


logger = logging.Logger(__name__)


def register_active_project() -> JsonBlob:
    assert safehouse.active_project is not None
    response = client.post(
        data=json.dumps({'name': safehouse.active_project.name}),
        endpoint='/organizations/projects/register/',
    )
    return response.json()
    