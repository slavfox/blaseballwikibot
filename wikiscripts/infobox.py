from blaseball_mike.models import Team, Player
import click
import pywikibot as pwb
from pywikibot.bot_choice import QuitKeyboardInterrupt
from pywikibot.tools.formatter import color_format
import wikitextparser as wtp
import sys


# i am tired of dealing with york's antics
def get_item_name(bat):
    if bat:
        if bat.text == 'Vibe Check':
            return '[[Legendary Items|Vibe Check]]'
        elif bat.text == 'The 2-Blood Blagonball':
            return '[[Blagonballs|The 2-Blood Blagonball]]'
        else:
            return bat.text
    else:
        return 'None'


def process_infobox(player, templates):
    true_template = [template for template in templates if template.normal_name() in 'Player'][0]

    def set_template(name, value):
        if value:
            true_template.set_arg(name, value, preserve_spacing=True)

    # get the stars from the template, or -1 if it can't figure it out
    def set_wiki_stars(name, value):
        wiki_stars = -1
        value_templates = []
        arg = true_template.get_arg(name)
        if arg and arg.value:
            value_templates = wtp.parse(arg.value).templates  # if values contain a template, this will grab them
        if len(value_templates) > 0 and len(value_templates[0].arguments) > 0:
            wiki_stars = value_templates[0].arguments[0].value
        if isinstance(wiki_stars, int) or wiki_stars.isnumeric():
            wiki_stars = float(wiki_stars)
        if wiki_stars != value:
            true_template.set_arg(name, f'{{{{Star Rating|{value}}}}}', preserve_spacing=True)

    set_wiki_stars('batting', player.batting_stars)
    set_wiki_stars('pitching', player.pitching_stars)
    set_wiki_stars('baserunning', player.baserunning_stars)
    set_wiki_stars('defense', player.defense_stars)
    set_template('blood', player.blood.text)
    set_template('coffee', player.coffee.text)
    set_template('ritual', player.ritual)
    set_template('fate', str(player.fate))
    set_template('soulscream', player.soulscream)
    set_template('uuid', player.id)

    return templates


def add_uuid(player, site, always, error_count, page_count):
    page = pwb.Page(site, player.id)
    if page.exists() is True:
        return (page_count, error_count, always)
    else:
        while True:
            result = page.put(f'#REDIRECT [[{player.name}]]', summary='Create UUID redirect', asynchronous=True)
            if result is None:
                print(f'Added UUID redirect for {player.name}.')
                return (page_count + 1, error_count, always)
            else:
                print(f'Error occurred while saving UUID redirect! Try {player.name} again.')
                return (page_count, error_count + 1, always)


def add_new(player, site, always, error_count, page_count):
    page = pwb.Page(site, player.name.replace(' ', '_'))

    name_split = player.name.split()
    name_split.pop(0)
    last_name = ' '.join(name_split)

    team = player.league_team.full_name

    text = f"""
<includeonly>
{{{{Template:New_Player_Header}}}} <!-- Remove this header and comment when adding community lore for the first time -->
{{{{Player
| title1={{{{{{PAGENAME}}}}}}
<!-- Use the filename with the file type, but without the File: or Image: prefix-->
| image1=
<!-- Photo credit -->
| caption1=

<!-- Records: Basic information -->
| aliases= <!-- IN GAME NAMES ONLY -->
| team=[[{team}]]
| former=
| status=Active
| dates= <!-- IRL dates active (ex. Jul 20 - Aug 31, 2020) -->
<!-- Records: Statistical Information -->
<!-- These are star ratings -->
| batting={{{{Star Rating|0}}}}
| pitching={{{{Star Rating|0}}}}
| baserunning={{{{Star Rating|0}}}}
| defense={{{{Star Rating|0}}}}
| modification=
<!-- These are taken from the pop-up box on clicking the player -->
| item=
| armor=
| evolution=
| ritual=
| coffee=
| blood=
| fate=
| soulscream=
<!-- For community lore info box fields, see Template:Player/doc & delete this note. -->
}}}}
'''{{{{PAGENAME}}}}''' is a (lineup player/pitcher) for the [[{team}]], and has been with the team since [[Season]], Day #.


== Official League Records ==
{last_name} joined the [[ILB]] as a (hitter/pitcher) for the [[{team}]] on [[Season]], Day # (after the [[incineration]] of [[Incinerated Player]]) (via the [[Season#Blessings | '''Blessing name''']] blessing).

<!-- When adding community lore about a player, add the template {{{{Community Lore}}}} at the top of the section and delete this note. -->


----
<references />
{{{{TeamNavSelector|$1}}}}
{{{{TeamCategorySelector|$1}}}}
<br />
<!-- Delete this note and whichever of the following categories do not apply: -->
[[Category:Players]]
[[Category:Lineup Players]]
[[Category:Pitchers]]
[[Category:Players who Replaced an Incinerated Player]]
</includeonly>
    """

    wtppage = wtp.parse(text)
    infobox = [element for idx, element in enumerate(wtppage.templates) if 'Player' in element.name]
    infobox = process_infobox(player, infobox)

    newtext = wtppage.string

    while True:
        # Let's put the changes.
        if not always:
            try:
                choice = pwb.input_choice(
                    'Do you want to accept these changes?',
                    [('Yes', 'y'), ('No', 'n'), ('All', 'a'),
                     ('open in Browser', 'b')], 'n')
            except QuitKeyboardInterrupt:
                sys.exit('User quit bot run.')

            if choice == 'a':
                always = True
            elif choice == 'n':
                return (page_count, error_count, always)
            elif choice == 'b':
                pwb.bot.open_webbrowser(page)

        if always or choice == 'y':
            result = page.put(newtext, summary='Create player experiment', asynchronous=True)
            if result is None:
                print(f'Created player page for {player.name}.')
                return (page_count + 1, error_count, always)
            else:
                print(f'Error occurred while creating player page! Try {player.name} again.')
                return (page_count, error_count + 1, always)


def edit_existing(player, site, always, error_count, page_count):
    # Find the infobox??
    page = pwb.Page(site, player.name.replace(' ', '_'))

    pwbpage = page.get()
    wtppage = wtp.parse(page.get())
    infobox = [element for idx, element in enumerate(wtppage.templates) if 'Player' in element.name]
    infobox = process_infobox(player, infobox)

    newtext = wtppage.string
    text = pwbpage

    if text == newtext:
        print(f'skipping {player.name}')
        return (page_count, error_count, always)
    else:
        pwb.output(color_format(
            '\n\n>>> {lightpurple}{0}{default} <<<', page.title()))
        pwb.showDiff(text, newtext)

        while True:
            # Let's put the changes.
            if not always:
                try:
                    choice = pwb.input_choice(
                        'Do you want to accept these changes?',
                        [('Yes', 'y'), ('No', 'n'), ('All', 'a'),
                         ('open in Browser', 'b')], 'n')
                except QuitKeyboardInterrupt:
                    sys.exit('User quit bot run.')

                if choice == 'a':
                    always = True
                elif choice == 'n':
                    return (page_count, error_count, always)
                elif choice == 'b':
                    pwb.bot.open_webbrowser(page)

            if always or choice == 'y':
                result = page.put(newtext, summary='Update player infobox', asynchronous=True)
                if result is None:
                    return (page_count + 1, error_count, always)
                else:
                    print(f'Error occurred! Try {player.name} again.')
                    return (page_count, error_count + 1, always)


# for each player...
def wiki_edit(player, site, always, error_count, page_count):
    # create the UUID redirect
    (page_count, error_count, always) = add_uuid(player, site, always, error_count, page_count)

    page = pwb.Page(site, player.name.replace(' ', '_'))

    if (page.exists() is not True):
        # create the player page
        (page_count, error_count, always) = add_new(player, site, always, error_count, page_count)
    else:
        # try to edit the existing player
        (page_count, error_count, always) = edit_existing(player, site, always, error_count, page_count)
    return (page_count, error_count, always)


# Command line parsing
@click.command()
@click.option('--player_id', help='Player UUID')
@click.option('--player_ids', help='Player UUIDs...')
def main(player_id, player_ids):
    site = pwb.Site()
    always = True
    error_count = 0
    page_count = 0

    if (player_id):
        player = Player.load_one(player_id)  # Load player from blaseball-mike
        (page_count, error_count, always) = wiki_edit(player, site, always, error_count, page_count)

    elif (player_ids):
        ids_list = player_ids.split(',')
        for player_id in ids_list:
            player = Player.load_one(player_id)  # Load player from blaseball-mike
            (page_count, error_count, always) = wiki_edit(player, site, always, error_count, page_count)
    else:
        teams = Team.load_all()

        for team in teams.values():
            if team.card != -1:  # only counting teams in play because I'm lazy
                for batter in team.lineup:
                    (page_count, error_count, always) = wiki_edit(batter, site, always, error_count, page_count)

                for pitcher in team.rotation:
                    (page_count, error_count, always) = wiki_edit(pitcher, site, always, error_count, page_count)

    print(f'Updated {page_count} pages. Error count: {error_count}.')


# To victory
if __name__ == '__main__':
    main()