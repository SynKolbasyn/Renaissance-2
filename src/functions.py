import ujson
import os

import player_account


def get_dict_from_json(file_name: str) -> dict:
    with open(file_name, "r") as file:
        return ujson.load(file)


LOCATIONS = get_dict_from_json("../game_data/locations.json")
ACTIONS = get_dict_from_json("../game_data/actions.json")
NPC_DATA = get_dict_from_json("../game_data/npc_data.json")
ITEMS = get_dict_from_json("../game_data/items.json")


def create_new_player(identification_number: int, login: str, name: str) -> player_account.Player:
    player = player_account.Player(identification_number, login, name, {"location": "Forest", "status": "Stay"}, [],
                                   {"cloths": "Rags", "weapon": "Stick"}, 100, 0, 0, LOCATIONS["Forest"]["actions"], {},
                                   {})
    player.update_data()
    return player


def create_exist_player(identification_number: int) -> player_account.Player:
    player_data = get_dict_from_json(f"../players_data_base/{identification_number}.json")
    return player_account.Player(identification_number, player_data["login"], player_data["name"],
                                 player_data["location"], player_data["previous_locations"], player_data["equipment"],
                                 player_data["hp"], player_data["experience"], player_data["money"],
                                 player_data["buttons"], player_data["enemies"], player_data["inventory"])


def except_new_player(identification_number: int, login: str, name: str) -> player_account.Player:
    if f"{identification_number}.json" in os.listdir("../players_data_base/"):
        return create_exist_player(identification_number)
    return create_new_player(identification_number, login, name)


def is_action_correct(action: str) -> bool:
    return action in ACTIONS.keys()


def execute_action(action: str, identification_number: int, login: str, name: str) -> str:
    player = except_new_player(identification_number, login, name)
    if not is_action_correct(action):
        return "Unknown action"
    return player.perform_action(action)


def get_action_buttons(identification_number: int) -> list[str]:
    player = create_exist_player(identification_number)
    return player.get_action_buttons()


def get_player_info(identification_number: int, login: str, name: str) -> str:
    player = except_new_player(identification_number, login, name)
    return player.info()


def get_player_inventory_info(identification_number: int, login: str, name: str) -> str:
    player = except_new_player(identification_number, login, name)
    return player.inventory_info()
