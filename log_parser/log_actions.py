import json
import sys
from abc import ABC, abstractmethod
from typing import Dict

from log_parser.utils import parse_arg_val

PLAYER_CONNECT = "PLAYER_CONNECT"
PLAYER_DISCONNECT = "PLAYER_DISCONNECT"
PLAYER_TERMINATED = "PLAYER_TERMINATED"
PLAYER_TEAM_CHANGE = "PLAYER_TEAM_CHANGE"
ITEM_PURCHASE = "ITEM_PURCHASE"
ITEM_ASSEMBLE = "ITEM_ASSEMBLE"
ITEM_SELL = "ITEM_SELL"
GOLD_EARNED = "GOLD_EARNED"
GOLD_LOST = "GOLD_LOST"
GAME_END = "GAME_END"
GAME_CONCEDE = "GAME_CONCEDE"


def parse_log_entry(line: str):
    args = line.split()
    if args[0] == PLAYER_CONNECT:
        if args[1].startswith("time"):
            return None
        return PlayerConnectAction(line)
    if args[0] == PLAYER_TERMINATED:
        return PlayerTerminateAction(line)
    if args[0] == PLAYER_TEAM_CHANGE:
        return PlayerTeamChangeAction(line)
    if args[0] == ITEM_PURCHASE:
        return ItemPurchaseAction(line)
    if args[0] == ITEM_SELL:
        return ItemSellAction(line)
    if args[0] == GOLD_EARNED:
        if args[4].startswith("gold"):
            return None
        return GoldEarnedAction(line)
    if args[0] == GOLD_LOST:
        return GoldLostAction(line)
    if args[0] == GAME_END or args[0] == GAME_CONCEDE:
        return GameEndAction(line)
    else:
        return None


class LogAction(ABC):
    @abstractmethod
    def apply(self, match_data):
        pass


def get_passive_gold_at_time(time: int):
    return round(time / 1000 / 60.0 * 69)


class GoldChange:
    def __init__(self, time, value):
        super().__init__()
        self.time = time
        self.value = value


class ItemData:
    def __init__(self, time, code, value, consumable):
        super().__init__()
        self.code = code
        self.value = value
        self.consumable = consumable
        self.time = time


def is_consumable(item_code):
    consumables = [
        "Item_HomecomingStone",
        "Item_RunesOfTheBlight",
        "Item_Bottle",
        "Item_VeiledRot",
        "Item_FlamingEye",
        "Item_ManaEye",
        "Item_ManaPotion",
        "Item_HealthPotion",
        "Item_DustOfRevelation",
    ]
    return item_code in consumables


class PlayerData:

    def __init__(self, account_id, player_num):
        super().__init__()
        self.account_id = account_id
        self.player_num = player_num
        self.team = None
        self.gold_changes = []
        self.items = []

    # helper functions
    def get_gold_at_time(self, time=None):
        if time is None:
            time = sys.maxsize

        total = 600
        for gold_change in self.gold_changes:
            if gold_change.time > time:
                break
            total += gold_change.value
        return total + get_passive_gold_at_time(time)

    def get_networth_at_time(self, time=None):
        gold = self.get_gold_at_time(time=time)
        for item in self.items:
            if item.time > time:
                break

            if not item.consumable:
                gold += item.value
        return gold

    # modifying functions
    def sell_item(self, time, item_code, value):
        self.gold_changes.append(GoldChange(time, value))

        for item in self.items:
            if item.code == item_code:
                self.items.remove(item)
                return

    def buy_item(self, time, item_code, value):
        self.gold_changes.append(GoldChange(time, -value))
        self.items.append(ItemData(time, item_code, value, is_consumable(item_code)))

    def earn_gold(self, time, value):
        self.gold_changes.append(GoldChange(time, value))

    def lose_gold(self, time, value):
        self.gold_changes.append(GoldChange(time, -value))


class MatchData:
    def __init__(self):
        self.player_datas: Dict[int, PlayerData] = {}
        self.end_time = 0

    # main function
    def dump_data(self, match):

        networth_diff = {}
        for i in range(0, self.end_time, 40000):
            networth_diff[i] = self.get_networth_diff(i)
        networth_diff[self.end_time] = self.get_networth_diff(self.end_time)
        match.networth_diff = json.dumps(networth_diff)

        for player in match.player_set.all():
            for _, player_data in self.player_datas.items():
                if player_data.account_id == player.account_id:
                    player.networth = player_data.get_networth_at_time(self.end_time)
                    player.save()

    # helper functions
    def get_team_gold(self, team, time=None):
        total = 0
        for player_num, player_data in self.player_datas.items():
            if player_data.team == team:
                total += player_data.get_gold_at_time(time)
        return total

    def get_team_networth(self, team, time=None):
        total = 0
        for player_num, player_data in self.player_datas.items():
            if player_data.team == team:
                total += player_data.get_networth_at_time(time)
        return total

    def get_gold_diff(self, time=None):
        return self.get_team_gold(2, time) - self.get_team_gold(1, time)

    def get_networth_diff(self, time=None):
        return self.get_team_networth(1, time) - self.get_team_networth(2, time)

    # modifying functions
    def add_player(self, action):
        self.player_datas[action.player_num] = PlayerData(action.account_id, action.player_num)

    def remove_player(self, action):
        self.player_datas[action.player_num].items.clear()
        self.player_datas[action.player_num].gold_changes.clear()

    def update_player(self, action):
        self.player_datas[action.player_num].team = action.team

    def sell_item(self, action):

        # sell dced player items, distribute gold to team TODO handle disconnect
        if action.player_num == -1:
            for _, player_data in self.player_datas.items():
                if player_data.team == action.team:
                    player_data.earn_gold(action.time, action.value / 5)
            return

        self.player_datas[action.player_num].sell_item(action.time, action.item_code, action.value)

    def buy_item(self, action):
        self.player_datas[action.player_num].buy_item(action.time, action.item_code, action.value)

    def gold_earned(self, action):
        self.player_datas[action.player_num].earn_gold(action.time, action.value)

    def gold_lost(self, action):
        self.player_datas[action.player_num].lose_gold(action.time, action.value)


class PlayerConnectAction(LogAction):

    def __init__(self, line: str):
        super().__init__()
        self.player_num = int(parse_arg_val(line, "player"))
        self.account_id = int(parse_arg_val(line, "id"))

    def apply(self, match_data: MatchData):
        match_data.add_player(self)


# PLAYER_TERMINATED time:2504350 player:3
class PlayerTerminateAction(LogAction):

    def __init__(self, line: str):
        super().__init__()
        self.time = int(parse_arg_val(line, "time"))
        self.player_num = int(parse_arg_val(line, "player"))

    def apply(self, match_data: MatchData):
        match_data.remove_player(self)


# PLAYER_TEAM_CHANGE player:1 team:1
class PlayerTeamChangeAction(LogAction):

    def __init__(self, line: str):
        self.player_num = int(parse_arg_val(line, "player"))
        self.team = int(parse_arg_val(line, "team"))

    def apply(self, match_data: MatchData):
        match_data.update_player(self)


# ITEM_PURCHASE time:0 x:1796 y:1275 z:358 player:1 team:1 item:"Item_LoggersHatchet" cost:150
class ItemPurchaseAction(LogAction):

    def __init__(self, line: str):
        self.time = int(parse_arg_val(line, "time"))
        self.player_num = int(parse_arg_val(line, "player"))
        self.item_code = str(parse_arg_val(line, "item"))
        self.value = int(parse_arg_val(line, "cost"))

    def apply(self, match_data: MatchData):
        match_data.buy_item(self)


class ItemAssembleAction(LogAction):

    def __init__(self, line: str):
        self.time = int(parse_arg_val(line, "time"))
        self.player_num = int(parse_arg_val(line, "player"))
        self.item_code = str(parse_arg_val(line, "item"))

    def apply(self, match_data: MatchData):
        pass


# ITEM_SELL time:705300 x:1902 y:12566 z:128 player:6 team:2 item:"Item_Lifetube" value:850
class ItemSellAction(LogAction):

    def __init__(self, line: str):
        self.time = int(parse_arg_val(line, "time"))
        self.team = int(parse_arg_val(line, "team"))
        self.player_num = int(parse_arg_val(line, "player"))
        self.item_code = str(parse_arg_val(line, "item"))
        self.value = int(parse_arg_val(line, "value"))

    def apply(self, match_data: MatchData):
        match_data.sell_item(self)


# GOLD_EARNED time:843350 x:2112 y:12495 z:128 player:6 team:2 source:"Creep_LegionMelee" gold:46
class GoldEarnedAction(LogAction):

    def __init__(self, line: str):
        self.time = int(parse_arg_val(line, "time"))
        self.player_num = int(parse_arg_val(line, "player"))
        self.value = int(parse_arg_val(line, "gold"))

    def apply(self, match_data: MatchData):
        match_data.gold_earned(self)


# GOLD_LOST time:858450 x:8008 y:6468 z:0 player:7 team:1 source:"Hero_Tarot" owner:5 gold:223
class GoldLostAction(LogAction):

    def __init__(self, line: str):
        self.time = int(parse_arg_val(line, "time"))
        self.player_num = int(parse_arg_val(line, "player"))
        self.value = int(parse_arg_val(line, "gold"))

    def apply(self, match_data: MatchData):
        match_data.gold_lost(self)


# GOLD_LOST time:858450 x:8008 y:6468 z:0 player:7 team:1 source:"Hero_Tarot" owner:5 gold:223
class GameEndAction(LogAction):

    def __init__(self, line: str):
        self.time = int(parse_arg_val(line, "time"))

    def apply(self, match_data: MatchData):
        match_data.end_time = self.time
