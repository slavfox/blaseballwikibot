= Blaseball Wikibot =

This repo grabs some of the shims and scripts from pywikibot with the scripts that we use for the Blaseball Wiki. Questionable decisions have been made in order to support the wiki team.

== Pre-requisites ==

1. Setup a new account just for your robot on *both* https://www.blaseball.wiki/ and https://dev.blaseball.wiki/. Nes and I shared the OliverIsARobot account on Fandom, but this was partially because botting permissions were very locked down on that website. So we can keep track of whose bot edited what, create a new account just for your robot.
2. Ask an administrator (ask here with the username!) to update the account on blaseball.wiki with the right permissions. All new accounts on dev should already have the right permissions.
3. Create new bot passwords for the robots: https://www.blaseball.wiki/w/Special:BotPasswords and https://dev.blaseball.wiki/w/Special:BotPasswords
4. Make sure that you have Python 3.5+ and pip and the like

== Setup ==

1. ```pip install -r requirements.txt```
2. Create your own user-config.py and user-passwords based on the samples
3. run all scripts with the wrapper script like so: ```python pwb.py YOURSCRIPTHERE``` (this is *necessary* for anything in the script folder. This is not strictly necessary for any custom Blaseball scripts, but the wrapper performs login.)

== Blaseball Wiki Scripts ==

- events.py: updates 'Raw Event Log' with the latest events (we keep a log on the page to keep track of when it last ran.)
- infobox.py: iterates through the players of current teams. creates pages and updates the infoboxes (stats, soulscreams, etc.)