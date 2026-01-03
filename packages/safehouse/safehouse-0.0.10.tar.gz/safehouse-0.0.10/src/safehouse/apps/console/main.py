#!/usr/bin/env python
import logging
import sys

from safehouse.apps.console import commands
from safehouse.apps.console.commands.types import Runnable

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


supported_commands: dict[str, Runnable] = {
    'orgs': commands.orgs.run,
    'projects': commands.projects.run,
    'services': commands.services.run,
    'status': commands.status.run,
    'users': commands.users.run,
    'version': commands.version.run,
}

def run():
    #print(f"safehouse-{metadata.version('safehouse')}")
    args = [arg.lower() for arg in sys.argv[1:]]
    if len(args) > 0:
        command_name: str = args[0]
        try:
            command = supported_commands[command_name]
        except KeyError:
            logger.error(f"'safehouse {command_name}' not supported")
            logger.info(usage())
            sys.exit(-1)
        try:
            command(args[1:])
        except commands.exceptions.CommandError as e:
            logger.error(e)
            sys.exit(-1)
        except Exception as e:
            logger.exception(e)
            sys.exit(-1)
    else:
        print(usage())
        sys.exit(0)


def usage() -> str:
    return f"usage: safehouse <{'|'.join(supported_commands.keys())}>"

if __name__ == "__main__":
    run()
