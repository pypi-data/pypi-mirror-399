import logging
import uuid

import safehouse
from safehouse.users import NULL_UUID
from ..exceptions import CommandError


logger = logging.Logger(__name__)


def run(args: list[str]):
    if len(args) != 1:
        raise CommandError(usage())
    command_tokens = args[0].split('=')
    if len(command_tokens) != 2:
        raise CommandError(usage())
    value = command_tokens[-1]
    attribute_tokens = command_tokens[0].split('.')
    if len(attribute_tokens) != 2:
        raise CommandError(usage())
    attribute, mode = attribute_tokens
    if attribute != 'id':
        raise CommandError(usage())
    try:
        if value == 'null':
            id = NULL_UUID
        else:
            id = uuid.UUID(value)
    except ValueError as e:
        raise CommandError(str(e))
    if (id != NULL_UUID) and (id.version != 4):
        raise CommandError(f"'{value}' is not a valid uuid4")
    if not safehouse.user.set_id_for(mode, id):
        logger.error(f"failed to set user id for mode {mode} to {id}")


def usage() -> str:
    return "safehouse users set id.<mode>=<value|null>"
