from blaseball_mike.models import Game, Team, Player
import pywikibot as pwb
import wikitextparser as wtp
import re

game_record = {'season': 1, 'day': 1}
name_re = r'\w[\w\'\-é ]+'
Player1_re = f'(?P<Player1>{name_re})'
Player2_re = f'(?P<Player2>{name_re})'
Team1_re = f'(?P<Team1>{name_re})'
Notes_re = f'(?P<Notes>{name_re})'
teams = Team.load_all()

outcomes_dict = {
    'Shelling': re.compile(f'{Player1_re} tasted the infinite and Shelled {Player2_re}!', re.IGNORECASE),
    'Incineration': re.compile(f'Rogue Umpire incinerated ({Team1_re} (?:pitch|hitt)er)?{Player1_re}!( Replaced by {Player2_re})?', re.IGNORECASE),
    'Shuffle': re.compile(f'The {Team1_re} (had several players|were completely|had their \\w+) shuffled in the Reverb!', re.IGNORECASE),
    'Feedback': re.compile(f'{Player1_re} and {Player2_re} switched teams in the feedback!', re.IGNORECASE),
    'Reverberating': re.compile(f'{Player1_re} is now Reverberating wildly!', re.IGNORECASE),
    'Blooddrain': re.compile(f'The Blooddrain gurgled! {Player1_re} siphoned some of {Player2_re}\'s {Notes_re} ability!', re.IGNORECASE),
    'Chain': re.compile(f'The Instability (?:chains|spreads) to the {name_re}\'s {Player1_re}!', re.IGNORECASE),
    'Hit By Pitch': re.compile(f'{Player1_re} hits {Player2_re} with a pitch! {name_re} is now {Notes_re}!', re.IGNORECASE),
    'Party': re.compile(f'{Player1_re} is Partying!', re.IGNORECASE),
    'Peanut': re.compile(f'({Team1_re} (?:pitch|hitt)er )?{Player1_re} swallowed a stray Peanut and had an? {Notes_re} reaction!', re.IGNORECASE),
    'Red Hot': re.compile(f'{Player1_re} is (no longer )?Red Hot', re.IGNORECASE),
    'Deshelling': re.compile(f'The Birds pecked {Player1_re} free!', re.IGNORECASE),
    'Big Peanut': re.compile(f'A Big Peanut crashes into the field, encasing {Player1_re}!', re.IGNORECASE),
    'Sun 2': re.compile(f'Sun 2 set a Win upon the {Team1_re}', re.IGNORECASE),
    'Black Hole': re.compile(f'The Black Hole swallowed a Win from the {Team1_re}!', re.IGNORECASE),
    'Elsewhere': re.compile(f'{Player1_re} (returned from|was swept) Elsewhere!', re.IGNORECASE)
}


def detect_type(outcome):
    for outcome_type in outcomes_dict.items():
        if outcome_type[1].search(outcome):
            return outcome_type[0]
    return 'Unknown'


def set_name_and_team(re_match, group_name, game, sample):
    if group_name in re_match.groupdict() and re_match.group(group_name) is not None:
        player = re_match.group(group_name)
        sample.set_arg(group_name, f'[[{player}]]')
        if sample.get_arg(f'{group_name}Team') is None:
            try:
                playerObj = Player.find_by_name(player)
                playerId = playerObj.id
                historicalPlayerObj = Player.load_by_gameday(playerId, game.season, game.day)
                if historicalPlayerObj is not None:
                    teamId = historicalPlayerObj.team_id
                    teamObj = Team.load(teamId)
                    print(f'{player}: Found historical team data: {teamObj.full_name}')
                    sample.set_arg(f'{group_name}Team', f'[[{teamObj.full_name}]]')
                elif playerObj.team_id is not None:
                    teamObj = Team.load(teamId)
                    print(f'{player}: Falling back to current team: {teamObj.full_name}')
                    sample.set_arg(f'{group_name}Team', f'maybe? [[{playerObj.league_team.full_name}]]')
                else:
                    print(f'Tried but failed to look up {player}')
                    sample.set_arg(f'{group_name}Team', 'Unknown')
            except:
                print(f'Failed to look up {player}')
                sample.set_arg(f'{group_name}Team', 'Unknown')


def set_team_from_string(re_match, group_name, sample):
    if group_name in re_match.groupdict() and re_match.group(group_name) is not None:
        team_name = re_match.group(group_name)
        if team_name == 'Dalé':
            team_name = 'Dale'
        elif team_name == 'Pies':  # blaseball-mike cannot tell the Pies and Spies apart
            team_name = 'Philly Pies'

        team = Team.load_by_name(team_name)

        if team is not None:
            sample.set_arg('Player1Team', f'[[{team.full_name}]]')
        else:
            print('Did not use team from string')


def set_notes(outcome, outcome_type, game, sample):
    if outcome_type != 'Unknown' and outcomes_dict[outcome_type].search(outcome):
        re_match = outcomes_dict[outcome_type].search(outcome)
        print(outcome)
        set_team_from_string(re_match, 'Team1', sample)
        set_team_from_string(re_match, 'Team2', sample)
        set_name_and_team(re_match, 'Player1', game, sample)
        set_name_and_team(re_match, 'Player2', game, sample)

        if 'Notes' in re_match.groupdict():
            sample.set_arg('Notes', re_match.group('Notes').capitalize())

        if outcome_type == 'Shuffle':
            if 'lineup' in outcome:
                sample.set_arg('Notes', 'Lineup')
            elif 'rotation' in outcome:
                sample.set_arg('Notes', 'Rotation')
            else:
                sample.set_arg('Notes', 'Full')
        elif outcome_type == 'Red Hot':
            if 'no longer' in outcome:
                sample.set_arg('Notes', 'Cooldown')
            else:
                sample.set_arg('Notes', 'Red Hot')
        elif outcome_type == 'Elsewhere':
            if 'returned from' in outcome:
                sample.set_arg('Notes', 'Returned')
            else:
                sample.set_arg('Notes', 'Swept Away')


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
    elif bool(games) and (games_all_ended or season != 13):
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
        page.put(page.text.replace(last_game.string, new_outcomes),
                 summary=f"Automated event update up to S{game_record['season']}G{game_record['game']}", minor=True)
    else:
        print('No need to update...')


def main():
    #  info.prefill_player_infos(teams)
    get_last_date()


# To victory
if __name__ == '__main__':
    main()
