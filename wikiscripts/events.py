from blaseball_mike.models import Game, Team
import pywikibot as pwb
import wikitextparser as wtp
import re
from playerinfo import PlayerInfo


game_record = {'season': 1, 'day': 1}
name_re = r'\w[\w\'\-é ]+'
Player1_re = f'(?P<Player1>{name_re})'
Player2_re = f'(?P<Player2>{name_re})'
Team1_re = f'(?P<Team1>{name_re})'
Notes_re = f'(?P<Notes>{name_re})'
teams = Team.load_all()
info = PlayerInfo()

outcomes_dict = {
    'Incineration': re.compile(f'Rogue Umpire incinerated {name_re} (?:pitch|hitt)er {Player1_re}! Replaced by {Player2_re}'),
    'Shuffle': re.compile(f'The {Team1_re} (had several players|were completely|had their \\w+) shuffled in the Reverb!'),
    'Feedback': re.compile(f'{Player1_re} and {Player2_re} switched teams in the feedback!'),
    'Reverberating': re.compile(f'{Player1_re} is now Reverberating wildly!'),
    'Blooddrain': re.compile(f'The Blooddrain gurgled! {Player1_re} siphoned some of {Player2_re}\'s {Notes_re} ability!'),
    'Chain': re.compile(f'The Instability (?:chains|spreads) to the {name_re}\'s {Player1_re}!'),
    'Hit By Pitch': re.compile(f'{Player1_re} hits {Player2_re} with a pitch! {name_re} is now {Notes_re}!'),
    'Party': re.compile(f'{Player1_re} is Partying!'),
    'Peanut': re.compile(f'[\\w ]+ (?:pitch|hitt)er {Player1_re} swallowed a stray Peanut and had an? {Notes_re} reaction!'),
    'Red Hot': re.compile(f'{Player1_re} is (no longer )?Red Hot'),
    'Deshelling': re.compile(f'The Birds pecked {Player1_re} free!'),
    'Big Peanut': re.compile(f'A Big Peanut crashes into the field, encasing {Player1_re}!'),
    'Sun 2': re.compile(f'Sun 2 set a Win upon the {Team1_re}'),
    'Black Hole': re.compile(f'The Black Hole swallowed a Win from the {Team1_re}!')
}


def detect_type(outcome):
    for outcome_type in outcomes_dict.items():
        if outcome_type[1].search(outcome):
            return outcome_type[0]
    return 'Unknown'


def set_name(re_match, group_name, game, sample):
    if group_name in re_match.groupdict():
        player = re_match.group(group_name)
        sample.set_arg(group_name, f'[[{player}]]')
        team = info.get_player_team(player, game.season, game.day)
        # print(f'{player}: {team}')
        sample.set_arg(f'{group_name}Team', team)


def set_notes(outcome, outcome_type, game, sample):
    if outcome_type != 'Unknown' and outcomes_dict[outcome_type].search(outcome):
        re_match = outcomes_dict[outcome_type].search(outcome)
        print(outcome)
        set_name(re_match, 'Player1', game, sample)
        set_name(re_match, 'Player2', game, sample)

        if 'Notes' in re_match.groupdict():
            sample.set_arg('Notes', re_match.group('Notes').capitalize())

        if outcome_type == 'Shuffle':
            team_name = re_match.group('Team1')
            if team_name == 'Dalé':
                team_name = 'Dale'
            team = Team.load_by_name(team_name)
            sample.set_arg('Player1Team', f'[[{team.full_name}]]')
            if 'lineup' in outcome:
                sample.set_arg('Notes', 'Lineup')
            elif 'rotation' in outcome:
                sample.set_arg('Notes', 'Rotation')
            else:
                sample.set_arg('Notes', 'Full')
        elif outcome_type == 'Black Hole' or outcome_type == 'Sun 2':
            team_name = re_match.group('Team1')
            if team_name == 'Dalé':
                team_name = 'Dale'
            team = Team.load_by_name(team_name)
            sample.set_arg('Player1Team', f'[[{team.full_name}]]')
        elif outcome_type == 'Red Hot':
            if 'no longer' in outcome:
                sample.set_arg('Notes', 'Cooldown')
            else:
                sample.set_arg('Notes', 'Red Hot')


def get_wiki_template_string(game):
    template_strings = []
    for outcome in game.outcomes:
        sample = wtp.Template('{{Template:GameEvent}}')
        sample.set_arg('Outcome', outcome)
        sample.set_arg('Season', str(game.season))
        sample.set_arg('Day', str(game.day))
        sample.set_arg('Game', str(game.id))
        sample.set_arg('HomeTeam', f'[[{game.home_team.full_name}]]')
        sample.set_arg('AwayTeam', f'[[{game.away_team.full_name}]]')
        # idk process shit???
        outcome_type = detect_type(outcome)
        sample.set_arg('Type', outcome_type)
        set_notes(outcome, outcome_type, game, sample)
        template_strings.append(sample.string)
    template_strings.reverse()
    return template_strings


# get game, NOT zero indexed!
def get_game_outcomes(season, day):
    games = Game.load_by_day(season, day)
    games_all_ended = True in (game.finalized for uuid, game in games.items())

    print(f'Processing Season {season} Day {day}')

    if not bool(games) and day != 1:
        return get_game_outcomes(season + 1, 1)
    elif bool(games) and games_all_ended or season == 4:
        game_record['season'] = season
        game_record['day'] = day
        outcomes = [get_wiki_template_string(game) for uuid, game in games.items() if len(game.outcomes) > 0]
        flat_outcomes = [item for sublist in outcomes for item in sublist]
        return get_game_outcomes(season, day + 1) + flat_outcomes
    else:
        return []


def get_last_date():
    # Fetch the correct Template from the wiki
    site = pwb.Site()
    page = pwb.Page(site, 'Raw Event Log')

    # lol I made an empty template to hide some values
    last_game = wtp.parse(page.get()).templates[0]
    # i dont know how python works tbh
    game_record['season'] = int(last_game.arguments[0].value)
    game_record['day'] = int(last_game.arguments[1].value)

    outcomes = get_game_outcomes(game_record['season'], game_record['day'] + 1)

    new_last_updated = f'{{{{LastUpdated|Season={game_record["season"]}|Day={game_record["day"]}}}}}\n'
    new_outcomes = new_last_updated + "\n".join(outcomes)

    if (game_record['season'] != int(last_game.arguments[0].value) or game_record['day'] != int(last_game.arguments[1].value)):
        print(new_outcomes)
        page.put(page.text.replace(last_game.string, new_outcomes), summary="Automated event update...", minor=True)
    else:
        print('No need to update...')


def main():
    get_last_date()


# To victory
if __name__ == '__main__':
    main()
