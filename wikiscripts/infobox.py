from blaseball_mike.models import Team, Player
import click
import pywikibot as pwb
from pywikibot.bot_choice import QuitKeyboardInterrupt
from pywikibot.tools.formatter import color_format
import wikitextparser as wtp
import sys


# python pwb.py protect -cat:Shadows -edit:sysop -summary: "Locking Shadows Players"

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

    def set_modifications():
        playermods = player.perm_attr + player.seas_attr  # anything shorter and i don't care
        mod_text = [f'{{{{Modif|{element.value.lower()}}}}}' for idx, element in enumerate(playermods)]
        mod_text = '<br />'.join(mod_text)
        set_template('modifications', mod_text)

    set_modifications()
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
    set_template('armor', player.armor.text if player.armor else 'None')
    set_template('item', get_item_name(player.bat))

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


def add_new(player, site, always, error_count, page_count, team_name, role, is_shadowed):
    page = pwb.Page(site, player.name.replace(' ', '_'))

    name_split = player.name.split()
    name_split.pop(0)
    last_name = ' '.join(name_split)

    new_category = 'Shadows' if is_shadowed else f'{role}s'
    header = 'Shadows' if is_shadowed else 'New_Player_Header'

    text = f"""
{{{{Template:{header}}}}} <!-- Remove this header and comment when adding community lore for the first time -->
{{{{Player
| title1={{{{{{PAGENAME}}}}}}
<!-- Use the filename with the file type, but without the File: or Image: prefix-->
| image1=
<!-- Photo credit -->
| caption1=

<!-- Records: Basic information -->
| aliases= <!-- IN GAME NAMES ONLY -->
| team=[[{team_name}]]
| former=
| status=Active
| dates= <!-- IRL dates active (ex. Jul 20 - Aug 31, 2020) -->
<!-- Records: Statistical Information -->
<!-- These are star ratings -->
| batting={{{{Star Rating|{player.batting_stars}}}}}
| pitching={{{{Star Rating|{player.pitching_stars}}}}}
| baserunning={{{{Star Rating|{player.baserunning_stars}}}}}
| defense={{{{Star Rating|{player.defense_stars}}}}}
| modification=
<!-- These are taken from the pop-up box on clicking the player -->
| item=
| armor=
| evolution=
| ritual={player.ritual}
| coffee={player.coffee.text}
| blood={player.blood.text}
| fate={str(player.fate)}
| soulscream={player.soulscream}
| uuid={player.id}
<!-- For community lore info box fields, see Template:Player/doc & delete this note. -->
}}}}
'''{{{{PAGENAME}}}}''' is a {role} for the [[{team_name}]]{' in the [[Shadows]].' if is_shadowed else ', and has been with the team since [[Season]], Day #.'}

<!--
== Official League Records ==
{last_name} joined the [[ILB]] as a {role} for the [[{team_name}]] on [[Season]], Day #
(after the [[incineration]] of [[Incinerated Player]])
(via the [[Season#Blessings | '''Blessing name''']] blessing).
-->
<!-- When adding community lore about a player, add the template {{{{Community Lore}}}} at the top of the section and delete this note. -->

----
<references />
{{{{TeamNavSelector|{team_name}}}}}
{{{{TeamCategorySelector|{team_name}}}}}
<br />
<!-- Add categories as needed. You might want:
[[Category:Players who Replaced an Incinerated Player]]
-->
[[Category:Players]]
[[Category:{new_category}]]
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
            result = page.put(newtext, summary=f'Create \'{player.name}\' page', asynchronous=True)

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
def wiki_edit(player, site, always, error_count, page_count, team_name, role, is_shadowed):
    # create the UUID redirect
    (page_count, error_count, always) = add_uuid(player, site, always, error_count, page_count)

    page = pwb.Page(site, player.name.replace(' ', '_'))

    if (page.exists() is not True):
        # create the player page
        (page_count, error_count, always) = add_new(player, site, always, error_count, page_count, team_name, role, is_shadowed)
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
    always = False
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
            if team.stadium != None:
                for batter in team.lineup:
                    (page_count, error_count, always) = wiki_edit(batter, site, always, error_count, page_count, team.full_name, 'Batter', False)

                for pitcher in team.rotation:
                    (page_count, error_count, always) = wiki_edit(pitcher, site, always, error_count, page_count, team.full_name, 'Pitcher', False)

                for batter in team.bench:
                    (page_count, error_count, always) = wiki_edit(batter, site, always, error_count, page_count, team.full_name, 'Batter', True)

                for pitcher in team.bullpen:
                    (page_count, error_count, always) = wiki_edit(pitcher, site, always, error_count, page_count, team.full_name, 'Pitcher', True)

    print(f'Updated {page_count} pages. Error count: {error_count}.')


# To victory
if __name__ == '__main__':
    main()
