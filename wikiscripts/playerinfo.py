from blaseball_mike.models import Team, Base
import requests


NAME_URL = 'https://api.blaseball-reference.com/v1/playerInfo?all=true&name='
ID_URL = 'https://api.blaseball-reference.com/v1/playerInfo?all=true&playerId='


class PlayerInfo(Base):
    player_lists = []
    checked_players = []

    def __init__(self):
        self.player_lists = []
        self.checked_players = []

    def get_player_team(self, name, season, day):
        player = self.get_player_info(name, season, day)
        print(player['team_id'])
        if player:
            if player['team_id'] == '40b9ec2a-cb43-4dbb-b836-5accb62e7c20':
                team = Team.load('b63be8c2-576a-4d6e-8daf-814f8bcea96f')
            else:
                team = Team.load(player['team_id'])
            if team and hasattr(team, 'full_name'):
                return f'[[{team.full_name}]]'
        return ''

    def match_name(self, name):
        return lambda player: player['player_name'] == name

    def match_name_and_date(self, name, season, day):
        return (lambda player: player['player_name'] == name and
                (player['season_from'] + 1 < season or
                (player['season_from'] + 1 == season and player['gameday_from'] + 1 < day)))

    def get_player_info_from_list(self, fn):
        return list(filter(fn, self.player_lists))

    def get_player_info(self, name, season, day):
        player_info = self.get_player_info_from_list(self.match_name_and_date(name, season, day))
        if len(player_info) > 0:
            return player_info.pop()
        else:
            full_player_info = self.get_player_info_from_list(self.match_name(name))
            if name not in self.checked_players:
                # print('could not find info for ' + name + '. downloading now...')
                new_player_info = requests.get(NAME_URL + name).json()
                self.checked_players.append(name)
                try:
                    self.player_lists = self.player_lists + new_player_info
                    return self.get_player_info(name, season, day)
                except Exception:
                    print('uhhh...')
                    return None
            elif len(full_player_info) > 0:
                return full_player_info.pop()  # fallback, I guess
            else:
                return None