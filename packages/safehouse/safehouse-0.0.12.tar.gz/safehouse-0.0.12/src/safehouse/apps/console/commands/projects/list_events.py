from safehouse.services import events
from ..exceptions import CommandError


def run(args: list[str]):
    if len(args) != 1:
        raise CommandError(usage())
    tokens = args[0].split('.')
    if len(tokens) != 2:
        raise CommandError(usage())
    organization, project = tokens
    events_list = events.get_event_types(organization, project)
    events_list = sorted(events_list, key=lambda e: e['name'])
    print(f"Registered events for {organization}.{project}:")
    for e in events_list:
        name = e['name']
        attributes: dict[str, str] = e['attributes'] # ty: ignore
        s = f"\t{name}: "
        s += ', '.join([f"{k}:{v}" for k, v in attributes.items()])
        print(s)


def usage() -> str:
    return "usage: safehouse projects list_events <organization.project>"
