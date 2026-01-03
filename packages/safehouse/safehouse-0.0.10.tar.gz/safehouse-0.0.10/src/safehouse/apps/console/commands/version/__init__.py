from importlib import metadata


def run(args: list[str]):
    print(f"safehouse-{metadata.version('safehouse')}")
