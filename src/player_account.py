import ujson
import random


def get_dict_from_json(file_name: str) -> dict:
    with open(file_name, "r") as file:
        return ujson.load(file)


LOCATIONS = get_dict_from_json("../game_data/locations.json")
STATUSES = get_dict_from_json("../game_data/statuses.json")
ACTIONS = get_dict_from_json("../game_data/actions.json")
NPC_DATA = get_dict_from_json("../game_data/npc_data.json")
ITEMS = get_dict_from_json("../game_data/items.json")
SHOPS = get_dict_from_json("../game_data/shops.json")


class Player:
    def __init__(self, identification_number: int, login: str, name: str, location: dict, previous_locations: list,
                 equipment: dict, hp: int, experience: int, money: int, buttons: list, enemies: dict,
                 inventory: dict):
        self.identification_number = identification_number
        self.login = login
        self.name = name
        self.location = location
        self.previous_locations = previous_locations
        self.equipment = equipment
        self.hp = hp
        self.experience = experience
        self.money = money
        self.buttons = buttons
        self.enemies = enemies
        self.inventory = inventory
    
    def damage(self) -> int:
        return ITEMS[self.equipment["weapon"]]["damage"]

    def get_dict_format_data(self) -> dict:
        return {
            "identification_number": self.identification_number,
            "login": self.login,
            "name": self.name,
            "location": self.location,
            "previous_locations": self.previous_locations,
            "equipment": self.equipment,
            "hp": self.hp,
            "experience": self.experience,
            "money": self.money,
            "buttons": self.buttons,
            "enemies": self.enemies,
            "inventory": self.inventory
        }

    def info(self) -> str:
        return f"ID: {self.identification_number}\n" \
               f"Name: {self.name}\n" \
               f"Location: {self.location['location']}\n" \
               f"Status: {self.location['status']}\n" \
               f"Cloths: {self.equipment['cloths']}\n" \
               f"Weapon: {self.equipment['weapon']}\n" \
               f"HP: {self.hp}\n" \
               f"Damage: {self.damage()}\n" \
               f"Experience: {self.experience}\n" \
               f"Money: {self.money}"

    def inventory_info(self) -> str:
        info = ""
        for item_name in self.inventory:
            info += f"{item_name} -> {self.inventory[item_name]}\n"
        return info

    def update_data(self):
        with open(f"../players_data_base/{self.identification_number}.json", "w") as file:
            file.write(ujson.dumps(self.get_dict_format_data(), indent=2))

    def sell_buttons(self) -> list:
        items_to_sell = []
        for item_name in self.inventory:
            if "sell" in ITEMS[item_name]["types"]:
                items_to_sell.append(item_name)
        items_to_sell.append("Leave")
        return items_to_sell

    def buy_buttons(self) -> list:
        items_to_buy = []
        for item_name in SHOPS[self.location["location"]]["items"]:
            items_to_buy.append(item_name)
        items_to_buy.append("Leave")
        return items_to_buy

    def info_buttons(self) -> list:
        info_items = []
        for item_name in self.inventory:
            if "info" in ITEMS[item_name]["types"]:
                info_items.append(item_name)
        info_items.append("Leave")
        return info_items

    def equip_buttons(self) -> list:
        eqip_items = []
        for item_name in self.inventory:
            if ("equipment_cloths" in ITEMS[item_name]["types"]) or ("equipment_weapon" in ITEMS[item_name]["types"]):
                eqip_items.append(item_name)
        eqip_items.append("Leave")
        return eqip_items

    def use_buttons(self) -> list:
        use_items = []
        for item_name in self.inventory:
            if "use" in ITEMS[item_name]["types"]:
                use_items.append(item_name)
        use_items.append("Leave")
        return use_items

    def dynamic_buttons(self) -> list:
        if self.location["status"] == "Sell":
            return self.sell_buttons()
        if self.location["status"] == "Buy":
            return self.buy_buttons()
        if self.location["status"] == "Read":
            return self.info_buttons()
        if self.location["status"] == "Equip":
            return self.equip_buttons()
        if self.location["status"] == "Use":
            return self.use_buttons()

    def update_buttons(self):
        if STATUSES[self.location["status"]]["type"] == "new actions":
            self.buttons = STATUSES[self.location["status"]]["actions"].copy()
        elif STATUSES[self.location["status"]]["type"] == "dynamic actions":
            self.buttons = self.dynamic_buttons()
        else:
            self.buttons = LOCATIONS[self.location["location"]]["actions"].copy()
        if self.location["location"] != "Inventory":
            self.buttons.append("Inventory")

    def check_location(self, location: dict) -> bool:
        return location == self.location

    def action_movement(self, action: str) -> str:
        if action == "Leave":
            self.location = self.previous_locations[-1]
            self.previous_locations.pop(-1)
            return ACTIONS[action]["description"]
        if self.check_location(ACTIONS[action]["location_arrive"]):
            return "You are already here or you can't go there"
        self.previous_locations.append(self.location)
        self.location = ACTIONS[action]["location_arrive"]
        return ACTIONS[action]["description"]

    def check_enemy(self, enemy_name: str):
        if enemy_name not in self.enemies.keys():
            self.enemies[enemy_name] = NPC_DATA[enemy_name].copy()

    def add_to_inventory(self, item_name: str):
        if item_name not in self.inventory.keys():
            self.inventory[item_name] = 0
        self.inventory[item_name] += 1

    def remove_from_inventory(self, item_name, count) -> bool:
        if item_name not in self.inventory.keys():
            return False
        self.inventory[item_name] -= count
        if self.inventory[item_name] < 0:
            self.inventory[item_name] += count
            return False
        if self.inventory[item_name] == 0:
            del self.inventory[item_name]
        return True

    def get_drop_from_enemy(self, enemy_name: str):
        self.experience += self.enemies[enemy_name]["experience"]
        drop = random.choice(self.enemies[enemy_name]["drop"])
        self.add_to_inventory(drop)

    def beat_enemy(self, enemy_name: str) -> str:
        self.enemies[enemy_name]["hp"] -= self.damage()
        if self.enemies[enemy_name]["hp"] <= 0:
            self.get_drop_from_enemy(enemy_name)
            del self.enemies[enemy_name]
            return f"You killed a {enemy_name}. You have gained {NPC_DATA[enemy_name]['experience']} experience\n"
        return f"You attacked a {enemy_name}, {enemy_name} took {self.damage()} damage. " \
               f"The {enemy_name} has {self.enemies[enemy_name]['hp']} hp left\n"

    def constrain_damage(self, enemy_name: str) -> int:
        damage = self.enemies[enemy_name]["damage"]
        damage -= ITEMS[self.equipment["cloths"]]["defence"]
        if damage <= 0:
            return 1
        return damage

    def get_enemies_damage(self) -> str:
        answer = ""
        for enemy_name in self.enemies:
            self.hp -= self.constrain_damage(enemy_name)
            answer += f"{enemy_name} is attacked you, you took {self.enemies[enemy_name]['damage']} damage. " \
                      f"You have {self.hp} hp left\n"
        return answer

    def is_dead(self) -> bool:
        return self.hp <= 0

    def dead_script(self) -> str:
        self.location = {"location": "Forest", "status": "Stay"}
        self.previous_locations = []
        self.equipment = {"cloths": "Rags", "weapon": "Stick"}
        self.hp = 100
        self.enemies = 0
        self.money = 0
        self.enemies = {}
        self.inventory = {}
        return "You're dead"

    def action_attack(self, action: str) -> str:
        answer = ""
        self.check_enemy(ACTIONS[action]["enemy_name"])
        answer += self.beat_enemy(ACTIONS[action]["enemy_name"])
        return answer

    def action_sell(self, item_name: str) -> str:
        if item_name in self.inventory.keys():
            self.money += ITEMS[item_name]["price"]
            if not self.remove_from_inventory(item_name, 1):
                return f"You can't sold {item_name}"
            return f"You sold {item_name}"
        return f"You haven't got {item_name}"

    def action_buy(self, item_name: str) -> str:
        if item_name not in SHOPS[self.location["location"]]["items"].keys():
            return f"You can't buy {item_name} here"
        if self.money < SHOPS[self.location["location"]]["items"][item_name]:
            return f"You can't buy {item_name} because you don't have enough money"
        self.money -= SHOPS[self.location["location"]]["items"][item_name]
        self.add_to_inventory(item_name)
        return f"You bought {item_name}"

    def action_info(self, item_name: str) -> str:
        if item_name not in self.inventory.keys():
            return f"You haven't got {item_name}"
        return ITEMS[item_name]["description"]

    def equip_equipment(self, item_name: str) -> str:
        answer = ""
        if "equipment_cloths" in ITEMS[item_name]["types"]:
            self.add_to_inventory(self.equipment["cloths"])
            self.equipment["cloths"] = item_name
            answer += f"You're wearing {item_name}"
        if "equipment_weapon" in ITEMS[item_name]["types"]:
            self.add_to_inventory(self.equipment["weapon"])
            self.equipment["weapon"] = item_name
            answer += f"You have equipped {item_name}"
        if answer != "":
            self.remove_from_inventory(item_name, 1)
        else:
            answer += "Unknown equipment type"
        return answer

    def action_equip(self, item_name: str) -> str:
        if item_name not in self.inventory.keys():
            return f"You haven't got {item_name}"
        return self.equip_equipment(item_name)

    def use_item(self, item_name: str) -> str:
        answer = ""
        if "hp_regeneration" in ITEMS[item_name].keys():
            self.hp += ITEMS[item_name]["hp_regeneration"]
            answer += f"You have replenished {ITEMS[item_name]['hp_regeneration']} hp\n"
        if answer != "":
            self.remove_from_inventory(item_name, 1)
        return answer

    def action_use(self, item_name: str) -> str:
        if item_name not in self.inventory.keys():
            return f"You haven't got {item_name}"
        return self.use_item(item_name)

    def perform_action(self, action: str) -> str:
        answer = ""
        if ACTIONS[action]["type"] == "movement":
            answer += self.action_movement(action) + "\n"
        if ACTIONS[action]["type"] == "attack":
            answer += self.action_attack(action) + "\n"
        if ACTIONS[action]["type"] == "item" and self.location["status"] == "Sell":
            answer += self.action_sell(action) + "\n"
        if ACTIONS[action]["type"] == "item" and self.location["status"] == "Buy":
            answer += self.action_buy(action) + "\n"
        if ACTIONS[action]["type"] == "item" and self.location["status"] == "Read":
            answer += self.action_info(action) + "\n"
        if ACTIONS[action]["type"] == "item" and self.location["status"] == "Equip":
            answer += self.action_equip(action) + "\n"
        if ACTIONS[action]["type"] == "item" and self.location["status"] == "Use":
            answer += self.action_use(action) + "\n"
        answer += self.get_enemies_damage()
        if self.is_dead():
            answer += self.dead_script()
        self.update_buttons()
        self.update_data()
        return answer

    def get_action_buttons(self) -> list:
        return self.buttons
