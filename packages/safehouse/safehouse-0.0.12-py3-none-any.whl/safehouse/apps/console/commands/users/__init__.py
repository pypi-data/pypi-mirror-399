from ..exceptions import CommandError
from . import set_attribute


def run(args: list[str]):
    if len(args) < 1:
        raise CommandError(usage())
    command = args[0]
    if command == 'set':
        set_attribute.run(args[1:])


def usage() -> str:
    return "safehouse users set <attribute.mode=value>"
