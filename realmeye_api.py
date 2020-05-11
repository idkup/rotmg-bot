from requests import get


def get_desc(player: dict) -> str:
    """Returns the player's description on their Realmeye profile."""
    return "\n".join(player["description"])


def get_player(name: str) -> dict:
    """Returns the JSON object representing the player named from the API."""
    player = get('http://tiffit.net/RealmInfo/api/user?u={}'.format(name)).json()
    try:
        if player['error']:
            raise RuntimeError("User not found!")
    except KeyError:
        pass
    return player


def get_total_fame(player: dict) -> int:
    """Returns the total amount of fame the player has."""
    return player['fame']


def get_total_maxed_stats(player: dict) -> int:
    """Returns the total amount of maxed stats the player has."""
    total_stats = 0
    for c in player['characters']:
        maxed = int(c['stats_maxed'][0])
        total_stats += maxed
    return total_stats
