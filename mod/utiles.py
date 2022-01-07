from typing import List


def get_clean_display_name(display_name: str, team_tags: List) -> str:

    update_name = display_name

    for team_tag in team_tags:
        if team_tag in display_name:
            update_name = display_name.replace(team_tag, "")
            # display_name.removeprefix(team_tag, "")
            break

    return update_name


def get_relative_complement_list(main: List, sub: List) -> str:

    # cast to set
    main = set(main)
    sub = set(sub)

    relative = main - sub

    return list(relative)
