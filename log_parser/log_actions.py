import json
import sys
from abc import ABC, abstractmethod
from typing import Dict

from game_data.utils import is_ward, is_consumable, REV_WARD, OBS_WARD, is_boss
from log_parser.exceptions import UnexpectedPlayerException
from log_parser.utils import parse_arg_val
from match.models import Match

PLAYER_CONNECT = "PLAYER_CONNECT"
PLAYER_DISCONNECT = "PLAYER_DISCONNECT"
PLAYER_KICKED_AFK = "PLAYER_KICKED_AFK"
PLAYER_TERMINATED = "PLAYER_TERMINATED"
PLAYER_TEAM_CHANGE = "PLAYER_TEAM_CHANGE"
PLAYER_SELECT = "PLAYER_SELECT"
ITEM_ACTIVATE = "ITEM_ACTIVATE"
ITEM_PURCHASE = "ITEM_PURCHASE"
ITEM_ASSEMBLE = "ITEM_ASSEMBLE"
ITEM_SELL = "ITEM_SELL"
KILL = "KILL"
GOLD_EARNED = "GOLD_EARNED"
GOLD_LOST = "GOLD_LOST"
PLAYER_BUYBACK = "PLAYER_BUYBACK"
EXP_EARNED = "EXP_EARNED"
GAME_END = "GAME_END"
GAME_CONCEDE = "GAME_CONCEDE"


def parse_log_entry(line: str):
    args = line.split()
    if args[0] == PLAYER_CONNECT:
        if args[1].startswith("time"):
            return None
        return PlayerConnectAction(line)
    if args[0] == PLAYER_TERMINATED or args[0] == PLAYER_KICKED_AFK:
        return PlayerTerminateAction(line)
    if args[0] == PLAYER_TEAM_CHANGE:
        return PlayerTeamChangeAction(line)
    if args[0] == PLAYER_SELECT:
        return PlayerConfirmAction(line)
    if args[0] == ITEM_PURCHASE:
        return ItemPurchaseAction(line)
    if args[0] == ITEM_ASSEMBLE:
        return ItemAssembleAction(line)
    if args[0] == ITEM_ACTIVATE:
        return ItemActivateAction(line)
    if args[0] == ITEM_SELL:
        return ItemSellAction(line)
    if args[0] == KILL:
        return KillAction(line)
    if args[0] == GOLD_EARNED:
        if len(args) < 7:
            return None
        return GoldEarnedAction(line)
    if args[0] == EXP_EARNED:
        return ExpEarnedAction(line)
    if args[0] == GOLD_LOST:
        return GoldLostAction(line)
    if args[0] == PLAYER_BUYBACK:
        return PlayerBuybackAction(line)
    if args[0] == GAME_END:
        return GameEndAction(line, concede=False)
    if args[0] == GAME_END or args[0] == GAME_CONCEDE:
        return GameEndAction(line, concede=True)
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


class ExpChange:
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


class PlayerData:
    def __init__(self, account_id, player_num):
        super().__init__()
        self.account_id = account_id
        self.player_num = player_num
        self.team = None
        self.gold_changes = []
        self.exp_changes = []
        self.items = []
        self.active = False
        self.disconnect_time = None
        self.hero = None
        self.dewards = 0
        self.obs_wards = 0
        self.rev_wards = 0
        self.countered_wards = 0

    def confirm(self, hero):
        self.hero = hero
        self.active = True

    def deactivate(self, time):
        self.active = False
        self.disconnect_time = time

    def is_active(self):
        return self.active

    def get_gold_at_time(self, time=None):

        if self.disconnect_time and time > self.disconnect_time:
            return 0

        if time is None:
            time = sys.maxsize

        total = 600  # starting gold
        for gold_change in self.gold_changes:
            if gold_change.time > time:
                break
            total += gold_change.value
        return total + get_passive_gold_at_time(time)

    def get_networth_at_time(self, time=None):

        if self.disconnect_time and time > self.disconnect_time:
            return 0

        gold = self.get_gold_at_time(time=time)
        for item in self.items:
            if item.time > time:
                continue

            if not item.consumable:
                gold += item.value
        return gold

    def get_exp_at_time(self, time=None):
        if time is None:
            time = sys.maxsize

        total = 0
        for exp_change in self.exp_changes:
            if exp_change.time > time:
                break
            total += exp_change.value
        return total

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

    def earn_exp(self, time, value):
        self.exp_changes.append(ExpChange(time, value))

    def lose_gold(self, time, value):
        self.gold_changes.append(GoldChange(time, -value))

    def add_item(self, time, item_code):
        self.items.append(ItemData(time, item_code, 0, is_consumable(item_code)))

    def add_deward(self):
        self.dewards += 1

    def add_obs_ward(self):
        self.obs_wards += 1

    def add_rev_ward(self):
        self.rev_wards += 1

    def add_countered_ward(self):
        self.countered_wards += 1


class TeamData:
    def __init__(self):
        self.player_datas: Dict[int, PlayerData] = {}
        self.boss_kills = 0

    def add_player(self, player_data):
        self.player_datas[player_data.player_num] = player_data

    def get_player(self, player_num):
        for player in self.player_datas.values():
            if player.player_num == player_num:
                return player
        return None

    def get_players(self):
        return self.player_datas.values()

    def get_active_players(self):
        active_players = []
        for player_data in self.player_datas.values():
            if player_data.is_active():
                active_players.append(player_data)
        return active_players

    # helper functions
    def get_team_gold(self, time=None):
        total = 0
        for player_data in self.get_players():
            total += player_data.get_gold_at_time(time)
        return total

    def get_team_networth(self, time=None):
        total = 0
        for player_data in self.get_players():
            total += player_data.get_networth_at_time(time)
        return total

    def get_team_exp(self, time=None):
        total = 0.0
        for player_data in self.get_players():
            total += player_data.get_exp_at_time(time)
        return total

    def sell_dced_item(self, action):
        for player_data in self.get_active_players():
            player_data.earn_gold(
                action.time, action.value / self.num_of_active_players()
            )

    def num_of_active_players(self):
        return len(self.get_active_players())

    def add_boss_kill(self):
        self.boss_kills += 1


class MatchData:
    def __init__(self):
        self.player_buffer: Dict[int, PlayerData] = {}
        self.teams: Dict[int, TeamData] = {1: TeamData(), 2: TeamData()}
        self.end_time = 0
        self.concede = False

    # main function
    def dump_data(self, match):

        interval = 40000
        match.concede = self.concede
        match.boss_kills = {
            Match.TEAM_LEGION: self.teams[1].boss_kills,
            Match.TEAM_HELLBOURNE: self.teams[2].boss_kills,
        }
        networth_diff = {}
        for i in range(0, self.end_time, interval):
            networth_diff[i] = self.get_networth_diff(i)
        networth_diff[self.end_time] = self.get_networth_diff(self.end_time)
        match.networth_diff = json.dumps(networth_diff)

        exp_diff = {}
        for i in range(0, self.end_time, interval):
            exp_diff[i] = round(self.get_exp_diff(i))
        exp_diff[self.end_time] = round(self.get_exp_diff(self.end_time))
        match.exp_diff = json.dumps(exp_diff)

        for player in match.player_set.all():
            for team in self.teams.values():
                for player_data in team.get_players():
                    if player_data.account_id == player.account_id:

                        item_times = []

                        for item_data in player_data.items:
                            item_times.append(
                                {
                                    "item_time": item_data.time,
                                    "item_code": item_data.code,
                                }
                            )

                        player.item_times = json.dumps(item_times)

                        networth_time = {}
                        for i in range(0, self.end_time, interval):
                            networth_time[i] = player_data.get_networth_at_time(i)
                        networth_time[self.end_time] = player_data.get_networth_at_time(
                            self.end_time
                        )
                        player.networth_time = json.dumps(networth_time)

                        player.networth = player_data.get_networth_at_time(
                            self.end_time
                        )
                        player.dewards = player_data.dewards
                        player.obs_wards = player_data.obs_wards
                        player.rev_wards = player_data.rev_wards
                        player.uncountered_wards = (
                            player_data.rev_wards
                            + player_data.obs_wards
                            - player_data.countered_wards
                        )
                        player.save()

    def get_gold_diff(self, time=None):
        return self.teams[1].get_team_gold(time) - self.teams[2].get_team_gold(time)

    def get_networth_diff(self, time=None):
        return self.teams[1].get_team_networth(time) - self.teams[2].get_team_networth(
            time
        )

    def get_exp_diff(self, time=None):
        return self.teams[1].get_team_exp(time) - self.teams[2].get_team_exp(time)

    # modifying functions
    def add_player(self, action):
        self.player_buffer[action.player_num] = PlayerData(
            action.account_id, action.player_num
        )

    def update_player(self, action):
        if action.team == 0:  # spectator
            return
        player = self.player_buffer[action.player_num]
        player.team = action.team
        self.teams[action.team].add_player(player)

    def confirm_player(self, action):
        for team_num, team in self.teams.items():
            if player := team.get_player(action.player_num):
                player.confirm(action.hero)
                break

    # deactivate player and distribute gold to remaining teammates
    def remove_player(self, action):

        # distribute gold
        dc_current_gold = self.find_player(action.player_num).get_gold_at_time(
            action.time
        )
        team = self.find_team_by_player(action.player_num)

        for player_data in team.get_active_players():
            player_data.earn_gold(
                action.time, dc_current_gold / team.num_of_active_players()
            )
        team.player_datas[action.player_num].deactivate(action.time)

    def sell_item(self, action):
        if action.player_num == -1:  # -1 means item belongs to the terminated player
            self.teams[action.team].sell_dced_item(action)
            return

        self.find_player(action.player_num).sell_item(
            action.time, action.item_code, action.value
        )

    def buy_item(self, action):
        self.find_player(action.player_num).buy_item(
            action.time, action.item_code, action.value
        )

    def gold_earned(self, action):
        self.find_player(action.player_num).earn_gold(action.time, action.value)

    def gold_lost(self, action):
        self.find_player(action.player_num).lose_gold(action.time, action.value)

    def exp_earned(self, action):
        self.find_player(action.player_num).earn_exp(action.time, action.experience)

    def add_item_assemble(self, action):
        self.find_player(action.player_num).add_item(action.time, action.item_code)

    def find_player(self, player_num):
        for team in self.teams.values():
            if player := team.get_player(player_num):
                return player
        raise UnexpectedPlayerException("find_player = -1")

    def find_team_by_player(self, player_num):
        for team in self.teams.values():
            for num, player_data in team.player_datas.items():
                if num == player_num:
                    return team
        return None

    def add_deward(self, action):
        player_data = self.find_player(action.player_num)
        player_data.add_deward()

    def activate_item(self, action):
        if action.item_code == REV_WARD:
            self.find_player(action.player_num).add_rev_ward()
            return
        if action.item_code == OBS_WARD:
            self.find_player(action.player_num).add_obs_ward()
            return

    def ward_kill(self, action):
        owner = self.find_player(action.owner)
        owner.add_countered_ward()

    def boss_kill(self, action):
        self.teams[action.team].add_boss_kill()


class PlayerConnectAction(LogAction):
    def __init__(self, line: str):
        super().__init__()
        self.player_num = int(parse_arg_val(line, "player"))
        self.account_id = int(parse_arg_val(line, "id"))

    def apply(self, match_data: MatchData):
        match_data.add_player(self)


# PLAYER_TERMINATED time:2504350 player:3
# PLAYER_KICKED_AFK time:1785900 player:1
class PlayerTerminateAction(LogAction):
    def __init__(self, line: str):
        super().__init__()
        self.time = int(parse_arg_val(line, "time") or 0)
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


# PLAYER_SELECT player:8 hero:"Hero_DrunkenMaster"
class PlayerConfirmAction(LogAction):
    def __init__(self, line: str):
        self.player_num = int(parse_arg_val(line, "player"))
        self.hero = str(parse_arg_val(line, "hero"))

    def apply(self, match_data: MatchData):
        match_data.confirm_player(self)


# ITEM_PURCHASE time:0 x:1796 y:1275 z:358 player:1 team:1 item:"Item_LoggersHatchet" cost:150
class ItemPurchaseAction(LogAction):
    def __init__(self, line: str):
        self.time = int(parse_arg_val(line, "time"))
        self.player_num = int(parse_arg_val(line, "player"))
        self.item_code = str(parse_arg_val(line, "item"))
        self.value = int(parse_arg_val(line, "cost"))

    def apply(self, match_data: MatchData):
        match_data.buy_item(self)


# ITEM_ASSEMBLE time:0 x:1953 y:8988 z:128 player:5 team:1 item:"Item_PowerSupply"
class ItemAssembleAction(LogAction):
    def __init__(self, line: str):
        self.time = int(parse_arg_val(line, "time"))
        self.player_num = int(parse_arg_val(line, "player"))
        self.item_code = str(parse_arg_val(line, "item"))

    def apply(self, match_data: MatchData):
        match_data.add_item_assemble(self)


# ITEM_ACTIVATE time:304300 x:5559 y:7911 z:128 player:8 team:2 item:"Item_FlamingEye"
class ItemActivateAction(LogAction):
    def __init__(self, line: str):
        self.time = int(parse_arg_val(line, "time"))
        self.player_num = int(parse_arg_val(line, "player"))
        self.item_code = str(parse_arg_val(line, "item"))

    def apply(self, match_data: MatchData):
        if self.player_num == -1:
            return
        match_data.activate_item(self)


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


# KILL time:358900 x:5039 y:7559 z:530 player:5 team:1 target:"Gadget_FlamingEye" attacker:"Gadget_Item_ManaEye" owner:8
# KILL time:1096700 x:3740 y:7929 z:301 player:4 team:2 target:"Reborn_GolemBoss_Legion" attacker:"Hero_Bushwack"
class KillAction(LogAction):
    WARD_KILL_TYPE = "WARD_KILL_TYPE"
    DEFAULT_KILL_TYPE = "DEFAULT_KILL_TYPE"
    BOSS_KILL_TYPE = "BOSS_KILL_TYPE"

    def __init__(self, line: str):
        self.kill_type = KillAction.DEFAULT_KILL_TYPE
        self.target = str(parse_arg_val(line, "target"))
        if is_ward(self.target):
            self.kill_type = KillAction.WARD_KILL_TYPE
            self.owner = int(parse_arg_val(line, "owner"))
        if is_boss(self.target):
            self.kill_type = KillAction.BOSS_KILL_TYPE
            self.team = int(parse_arg_val(line, "team"))
            self.player = int(parse_arg_val(line, "player"))

    def apply(self, match_data: MatchData):
        if self.kill_type == KillAction.WARD_KILL_TYPE:
            match_data.ward_kill(self)
        if self.kill_type == KillAction.BOSS_KILL_TYPE:
            match_data.boss_kill(self)


# GOLD_EARNED time:843350 x:2112 y:12495 z:128 player:6 team:2 source:"Creep_LegionMelee" gold:46
# GOLD_EARNED time:884750 x:11011 y:4283 z:59 player:8 team:1 source:"Gadget_Item_ManaEye" owner:4 gold:50 WARD
class GoldEarnedAction(LogAction):
    def __init__(self, line: str):
        self.time = int(parse_arg_val(line, "time"))
        self.player_num = int(parse_arg_val(line, "player"))
        self.value = int(parse_arg_val(line, "gold"))
        self.source = str(parse_arg_val(line, "source"))

    def apply(self, match_data: MatchData):
        match_data.gold_earned(self)
        if is_ward(self.source):
            match_data.add_deward(self)


# EXP_EARNED time:32300 x:7512 y:7345 z:-120 player:7 team:1 experience:20.47 source:"Creep_HellbourneMelee"
# EXP_EARNED time:98950 x:13983 y:1672 z:128 player:5 team:2 experience:25.00 source:"Hero_Fairy" owner:0
class ExpEarnedAction(LogAction):
    def __init__(self, line: str):
        self.time = int(parse_arg_val(line, "time"))
        self.player_num = int(parse_arg_val(line, "player"))
        self.experience = float(parse_arg_val(line, "experience"))

    def apply(self, match_data: MatchData):
        match_data.exp_earned(self)


# GOLD_LOST time:858450 x:8008 y:6468 z:0 player:7 team:1 source:"Hero_Tarot" owner:5 gold:223
class GoldLostAction(LogAction):
    def __init__(self, line: str):
        self.time = int(parse_arg_val(line, "time"))
        self.player_num = int(parse_arg_val(line, "player"))
        self.value = int(parse_arg_val(line, "gold"))

    def apply(self, match_data: MatchData):
        match_data.gold_lost(self)


# PLAYER_BUYBACK time:1598100 player:9 cost:896 team:1
class PlayerBuybackAction(LogAction):
    def __init__(self, line: str):
        self.time = int(parse_arg_val(line, "time"))
        self.player_num = int(parse_arg_val(line, "player"))
        self.value = int(parse_arg_val(line, "cost"))

    def apply(self, match_data: MatchData):
        match_data.gold_lost(self)


# GOLD_LOST time:858450 x:8008 y:6468 z:0 player:7 team:1 source:"Hero_Tarot" owner:5 gold:223
class GameEndAction(LogAction):
    def __init__(self, line: str, concede: bool):
        self.time = int(parse_arg_val(line, "time"))
        self.concede = concede

    def apply(self, match_data: MatchData):
        match_data.end_time = self.time
        match_data.concede = self.concede
