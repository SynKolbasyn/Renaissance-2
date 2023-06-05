import ujson
import os

import player_account


def get_dict_from_json(file_name: str) -> dict:
    with open(file_name, "r") as file:
        return ujson.load(file)


LOCATIONS = get_dict_from_json("../game_data/locations.json")
ACTIONS = get_dict_from_json("../game_data/actions.json")


def create_new_player(identification_number: int, login: str, name: str) -> player_account.Player:
    return player_account.Player(identification_number, login, name, "Forest", [], 100, 1)


def create_exist_player(identification_number: int) -> player_account.Player:
    player_data = get_dict_from_json(f"../players_data_base/{identification_number}.json")
    return player_account.Player(identification_number, player_data["login"], player_data["name"],
                                 player_data["location"], player_data["previous_locations"], player_data["hp"],
                                 player_data["damage"])


def except_new_player(identification_number: int, login: str, name: str) -> player_account.Player:
    if f"{identification_number}.json" in os.listdir("../players_data_base/"):
        return create_exist_player(identification_number)
    return create_new_player(identification_number, login, name)


def is_action_correct(action: str) -> int:
    return action in ACTIONS.keys()


def execute_action(action: str, identification_number: int, login: str, name: str) -> str:
    player = except_new_player(identification_number, login, name)
    if not is_action_correct(action):
        return "Unknown action"
    return player.perform_action(action)


def get_action_buttons(identification_number: int) -> list[str]:
    player = create_exist_player(identification_number)
    return player.get_action_buttons()