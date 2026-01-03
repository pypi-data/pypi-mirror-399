import safehouse


def run(args: list[str]):
    mode = safehouse.runtime_mode
    print(f"mode: {mode}, user_id: {safehouse.user.id_for(mode)}")
    projects = safehouse.projects.list_projects()
    if projects:
        print("registered projects:")
        for p in projects:
            s = f"\t{p}"
            if p.in_development:
                s += " (in development)"
            print(s)
