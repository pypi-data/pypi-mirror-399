import logging

from safehouse.services import client
from safehouse.types import JsonBlob


logger = logging.Logger(__name__)


def get_local_user() -> JsonBlob:
    response = client.get(
        endpoint='/users/local/',
    )
    return response.json()
