from blaseball_mike.models import Team
import click
import pywikibot as pwb
import wikitextparser as wtp

# Turn a blaseball team id into the correct {{Template:}} call
def id_to_nav(id):
    switcher = {
    "8d87c468-699a-47a8-b40d-cfb73a5660ad": "CrabsNav",
    "3f8bbb15-61c0-4e3f-8e4a-907a5fb1565e": "FlowersNav",
    "a37f9158-7f82-46bc-908c-c9e2dda7c33b": "JazzHandsNav",
    "eb67ae5e-c4bf-46ca-bbbc-425cd34182ff": "MoistTalkersNav",
    "bfd38797-8404-4b38-8b82-341da28b1f83": "ShoeThievesNav",
    "ca3f1c8c-c025-4d8e-8eef-5be6accbeb16": "FirefightersNav",
    "b024e975-1c4a-4575-8936-a3754a08806a": "SteaksNav",
    "747b8e4a-7e50-4638-a973-ea7950a3e739": "TigersNav",
    "979aee4a-6d80-4863-bf1c-ee1a78e06024": "FridaysNav",
    "f02aeae2-5e6a-4098-9842-02d2273f25c7": "SunbeamsNav",
    "9debc64f-74b7-4ae1-a4d6-fce0144b6ea5": "SpiesNav",
    "adc5b394-8f76-416d-9ce9-813706877b84": "BreathMintsNav",
    "57ec08cc-0411-4643-b304-0e80dbc15ac7": "WildWingsNav",
    "b63be8c2-576a-4d6e-8daf-814f8bcea96f": "DaléNav",
    "36569151-a2fb-43c1-9df7-2df512424c82": "MillennialsNav",
    "23e4cbc1-e9cd-47fa-a35b-bfa06f726cb7": "PiesNav",
    "b72f3061-f573-40d7-832a-5ad475bd7909": "LoversNav",
    "105bc3ff-1320-4e37-8ef0-8d595cb95dd0": "GaragesNav",
    "878c1bf6-0d21-4659-bfee-916c8314d69c": "TacosNav",
    "7966eb04-efcc-499b-8f03-d13916330531": "MagicNav"
    }
    return switcher.get(id, "None")

def textify(team, roster):
    # Create a list of players from team
    lineup_list = [player.name for player in team.lineup]
    rotation_list = [player.name for player in team.rotation]

    # bench_list = [player.name for player in team.bench]
    # bullpen_list = [player.name for player in team.bullpen]

    # Output the roster in wikitext format
    if roster == "lineup":
        output_list = '[[' + ']] · [['.join(lineup_list) + ']]'
        return output_list

    elif roster == "rotation":
        output_list = '[[' + ']] · [['.join(rotation_list) + ']]'
        return output_list

    # elif roster == "bench":
    #     output_list = '[[' + ']] · [['.join(bench_list) + ']]'
    #     return output_list

    # elif roster == "bullpen":
    #     output_list = '[[' + ']] · [['.join(bullpen_list) + ']]'
    #     return output_list

    # elif roster == "full":
    # idk somehow do both

def wiki_edit(nav, roster, textified):
    # Fetch the correct Template from the wiki
    site = pwb.Site()
    page = pwb.Page(site, f'Template:{nav}')

    # Find the Navbox child
    text = wtp.parse(page.get()).templates[0].arguments[9].value

    # Find the correct string, replace, and post to wiki
    if roster == 'lineup':
        parsed = wtp.parse(text).templates[0].arguments[4].value
        page.put(page.text.replace(f"{parsed}", f"{textified}"), summary="Automated reverb update")

    elif roster == 'rotation':
        parsed = wtp.parse(text).templates[0].arguments[5].value
        page.put(page.text.replace(f"{parsed}", f"{textified}"), summary="Automated reverb update")

# Command line parsing
@click.command()
@click.option('--team', required=True, help="Team name")
@click.option('--roster', required=True, help="Which roster portion to adjust (lineup, rotation, or full)")
def main(team_name, roster):
    """Retrieves a given roster from the Blaseball API and parses it for writing to the team's Blasebal Wiki navigation box."""

    team_name = team
    # Load team from blaseball-mike
    team_obj = Team.load_by_name(team_name)
    change_level = roster
    # Turn team.id into the correct wiki nav page
    nav = id_to_nav(team_obj.id)
    # if nav = None something something error?
    # Wikitextify the team.lineup list for navbox use
    new_roster = textify(team_obj, change_level)
    # Edit the wiki using nav, --roster (change_level), and textify (new_roster)
    wiki_edit(nav, change_level, new_roster)


# To victory
if __name__ == '__main__':
    main()