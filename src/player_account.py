import ujson


def get_dict_from_json(file_name: str) -> dict:
    with open(file_name, "r") as file:
        return ujson.load(file)


LOCATIONS = get_dict_from_json("../game_data/locations.json")
ACTIONS = get_dict_from_json("../game_data/actions.json")


class Player:
    def __init__(self, identification_number: int, login: str, name: str, location: str, previous_locations: list,
                 hp: int, damage: int):
        self.identification_number = identification_number
        self.login = login
        self.name = name
        self.location = location
        self.previous_locations = previous_locations
        self.hp = hp
        self.damage = damage

    def get_dict_format_data(self) -> dict:
        return {
            "identification_number": self.identification_number,
            "login": self.login,
            "name": self.name,
            "location": self.location,
            "previous_locations": self.previous_locations,
            "hp": self.hp,
            "damage": self.damage
        }

    def update_data(self):
        with open(f"../players_data_base/{self.identification_number}.json", "w") as file:
            file.write(ujson.dumps(self.get_dict_format_data(), indent=2))

    def check_location(self, location: str) -> bool:
        return location == self.location

    def action_movement(self, action) -> str:
        if self.check_location(ACTIONS[action]["location_arrive"]):
            return "You are already here or you can't go there"
        self.previous_locations.append(self.location)
        self.location = ACTIONS[action]["location_arrive"]
        return ACTIONS[action]["description"]

    def perform_action(self, action: str) -> str:
        answer = ""
        if ACTIONS[action]["type"] == "movement":
            answer += self.action_movement(action)
        self.update_data()
        return answer

    def get_action_buttons(self) -> list[str]:
        return LOCATIONS[self.location]["actions"]
