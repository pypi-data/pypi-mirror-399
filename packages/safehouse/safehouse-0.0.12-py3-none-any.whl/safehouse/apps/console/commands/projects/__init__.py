from ..exceptions import CommandError
from . import (
    init as init,
    list_events as list_events,
)


def run(args: list[str]):
    if len(args) != 2:
        raise CommandError(usage())
    command = args[0]
    if command == 'init':
        init.run(args[1:])
    elif command == 'list_events':
        list_events.run(args[1:])
    else:
        raise CommandError(f"unsupported projects command '{command}'")


def usage() -> str:
    return "safehouse projects init <organization.project>"
 