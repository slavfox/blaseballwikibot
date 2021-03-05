# -*- coding: utf-8 -*-

#
# This is only an example. Don't use it.
#
# Refer the manual for its construction at:
# https://www.mediawiki.org/wiki/Manual:Pywikibot/fixes.py#Construction_of_a_fix

fixes['teamnav'] = {
    'regex': True,
    'msg': {
        '_default': 'simple nav selector',
    },
    'replacements': [
        (r'{{LoversNav}}', '{{TeamNavSelector|lovers}}'),
        (r'{{JazzHandsNav}}', '{{TeamNavSelector|jazz hands}}'),
        (r'{{TacosNav}}', '{{TeamNavSelector|tacos}}'),
        (r'{{MoistTalkersNav}}', '{{TeamNavSelector|moist talkers}}'),
        (r'{{BreathMintsNav}}', '{{TeamNavSelector|mints}}'),
        (r'{{SunbeamsNav}}', '{{TeamNavSelector|sunbeams}}'),
        (r'{{GaragesNav}}', '{{TeamNavSelector|garages}}'),
        (r'{{DaléNav}}', '{{TeamNavSelector|dale}}'),
        (r'{{FlowersNav}}', '{{TeamNavSelector|flowers}}'),
        (r'{{FridaysNav}}', '{{TeamNavSelector|fridays}}'),
        (r'{{SpiesNav}}', '{{TeamNavSelector|spies}}'),
        (r'{{CrabsNav}}', '{{TeamNavSelector|crabs}}'),
        (r'{{MillennialsNav}}', '{{TeamNavSelector|millenials}}'),
        (r'{{MagicNav}}', '{{TeamNavSelector|magic}}'),
        (r'{{TigersNav}}', '{{TeamNavSelector|Tigers}}'),
        (r'{{SteaksNav}}', '{{TeamNavSelector|steaks}}'),
        (r'{{WildWingsNav}}', '{{TeamNavSelector|wings}}'),
        (r'{{FirefightersNav}}', '{{TeamNavSelector|firefighters}}'),
        (r'{{PiesNav}}', '{{TeamNavSelector|pies}}'),
        (r'{{ShoeThievesNav}}', '{{TeamNavSelector|shoe thieves}}'),
        (r'{{Template:LoversNav}}', '{{TeamNavSelector|lovers}}'),
        (r'{{Template:JazzHandsNav}}', '{{TeamNavSelector|jazz hands}}'),
        (r'{{Template:TacosNav}}', '{{TeamNavSelector|tacos}}'),
        (r'{{Template:MoistTalkersNav}}', '{{TeamNavSelector|moist talkers}}'),
        (r'{{Template:BreathMintsNav}}', '{{TeamNavSelector|mints}}'),
        (r'{{Template:SunbeamsNav}}', '{{TeamNavSelector|sunbeams}}'),
        (r'{{Template:GaragesNav}}', '{{TeamNavSelector|garages}}'),
        (r'{{Template:DaléNav}}', '{{TeamNavSelector|dale}}'),
        (r'{{Template:FlowersNav}}', '{{TeamNavSelector|flowers}}'),
        (r'{{Template:FridaysNav}}', '{{TeamNavSelector|fridays}}'),
        (r'{{Template:SpiesNav}}', '{{TeamNavSelector|spies}}'),
        (r'{{Template:CrabsNav}}', '{{TeamNavSelector|crabs}}'),
        (r'{{Template:MillennialsNav}}', '{{TeamNavSelector|millenials}}'),
        (r'{{Template:MagicNav}}', '{{TeamNavSelector|magic}}'),
        (r'{{Template:TigersNav}}', '{{TeamNavSelector|Tigers}}'),
        (r'{{Template:SteaksNav}}', '{{TeamNavSelector|steaks}}'),
        (r'{{Template:WildWingsNav}}', '{{TeamNavSelector|wings}}'),
        (r'{{Template:FirefightersNav}}', '{{TeamNavSelector|firefighters}}'),
        (r'{{Template:PiesNav}}', '{{TeamNavSelector|pies}}'),
        (r'{{Template:ShoeThievesNav}}', '{{TeamNavSelector|shoe thieves}}'),
    ]
}

fixes['stars'] = {
    'regex': True,
    'msg': {
        '_default': 'star rating template replacement',
    },
    'replacements': [
        (r'★★★★★½', '{{Star Rating|5.5}}'),
        (r'★★★★★', '{{Star Rating|5}}'),
        (r'★★★★½', '{{Star Rating|4.5}}'),
        (r'★★★★', '{{Star Rating|4}}'),
        (r'★★★½', '{{Star Rating|3.5}}'),
        (r'★★★', '{{Star Rating|3}}'),
        (r'★★½', '{{Star Rating|2.5}}'),
        (r'★★', '{{Star Rating|2}}'),
        (r'★½', '{{Star Rating|1.5}}'),
        (r'★', '{{Star Rating|1}}'),
        (r'½', '{{Star Rating|0.5}}'),
    ]
}

fixes['infoboxstatus'] = {
    'regex': True,
    'msg': {
        '_default': 'player infobox status normalization',
    },
    'replacements': [
        (r'status=Alive', 'status=Active')
    ]
}

fixes['findbuggedbaserunning'] = {
    'regex': True,
    'msg': {
        '_default': 'fix bugged baserunning',
    },
    'replacements': [
        (r'\|baserunning=\(bugged\)', '{{Star Rating|0}}'),
        (r'\|baserunning=\(bugged\)', '{{Star Rating|0.5}}'),
        (r'\|baserunning=\(bugged\)', '{{Star Rating|1}}'),
        (r'\|baserunning=\(bugged\)', '{{Star Rating|1.5}}'),
        (r'\|baserunning=\(bugged\)', '{{Star Rating|2}}')
    ]
}

fixes['wexico'] = {
    'regex': True,
    'msg': {
        '_default': 'we\'re moving to wexico city guys',
    },
    'replacements': [
        (r'{{Template:WildWingsNav}}', '{{TeamNavSelector|wings}}'),
        (r'{{WildWingsNav}}', '{{TeamNavSelector|wings}}'),
        (r'\[\[Category:Mexico City Wild Wings\]\]', '{{TeamCategorySelector|wings}}'),
        (r'\[\[Category:Mexico City Wild Wings\]\]', '{{TeamCategorySelector|wings}}')
    ]
}

fixes['rumors'] = {
    'regex': True,
    'msg': {
        '_default': 'removing category from the cats',
    },
    'replacements': [
        (r'\[\[Category:Cats\]\]', '')
    ]
}

fixes['blaseball'] = {
    'regex': True,
    'msg': {
        '_default': 'term normalization',
    },
    'replacements': [
        (r'laseball', 'lase ball')
    ],
    'exceptions': {
        'inside-tags': [
            'comment',
            'header',
            'ref',
            'template',
            'gallery',
            'link'
        ]
    }
}