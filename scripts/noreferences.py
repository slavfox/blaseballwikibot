#!/usr/bin/python
"""
This script adds a missing references section to pages.

It goes over multiple pages, searches for pages where <references />
is missing although a <ref> tag is present, and in that case adds a new
references section.

These command line parameters can be used to specify which pages to work on:

&params;

Furthermore, the following command line parameters are supported:

-xml          Retrieve information from a local XML dump (pages-articles
              or pages-meta-current, see https://dumps.wikimedia.org).
              Argument can also be given as "-xml:filename".

-always       Don't prompt you for each replacement.

-quiet        Use this option to get less output

If neither a page title nor a page generator is given, it takes all pages from
the default maintenance category.

It is strongly recommended not to run this script over the entire article
namespace (using the -start) parameter, as that would consume too much
bandwidth. Instead, use the -xml parameter, or use another way to generate
a list of affected articles
"""
#
# (C) Pywikibot team, 2007-2020
#
# Distributed under the terms of the MIT license.
#
import re

from functools import partial

import pywikibot

from pywikibot import i18n, pagegenerators, textlib
from pywikibot.bot import ExistingPageBot, NoRedirectPageBot, SingleSiteBot
from pywikibot.pagegenerators import XMLDumpPageGenerator
from pywikibot.tools import remove_last_args

# This is required for the text that is shown when you run this script
# with the parameter -help.
docuReplacements = {
    '&params;': pagegenerators.parameterHelp,
}

# References sections are usually placed before further reading / external
# link sections. This dictionary defines these sections, sorted by priority.
# For example, on an English wiki, the script would place the "References"
# section in front of the "Further reading" section, if that existed.
# Otherwise, it would try to put it in front of the "External links" section,
# or if that fails, the "See also" section, etc.
placeBeforeSections = {
    'ar': [              # no explicit policy on where to put the references
        '?????????? ????????????',
        '???????? ????????',
        '??????????????'
    ],
    'arz': [              # no explicit policy on where to put the references
        '???????????? ????????????',
        '????????????',
        '?????? ????????'
    ],
    'ca': [
        'Bibliografia',
        'Bibliografia complement??ria',
        'Vegeu tamb??',
        'Enlla??os externs',
        'Enlla??os',
    ],
    'cs': [
        'Extern?? odkazy',
        'Pozn??mky',
    ],
    'da': [              # no explicit policy on where to put the references
        'Eksterne links'
    ],
    'de': [              # no explicit policy on where to put the references
        'Literatur',
        'Weblinks',
        'Siehe auch',
        'Weblink',      # bad, but common singular form of Weblinks
    ],
    'dsb': [
        'No??ki',
    ],
    'en': [              # no explicit policy on where to put the references
        'Further reading',
        'External links',
        'See also',
        'Notes'
    ],
    'eo': [
        'Eksteraj ligiloj',
        'Ekstera ligilo',
        'Eksteraj ligoj',
        'Ekstera ligo',
        'Rete'
    ],
    'es': [
        'Enlaces externos',
        'V??ase tambi??n',
        'Notas',
    ],
    'fa': [
        '?????????? ???? ??????????',
        '????????????',
        '???????????????? ????????????'
    ],
    'fi': [
        'Kirjallisuutta',
        'Aiheesta muualla',
        'Ulkoiset linkit',
        'Linkkej??',
    ],
    'fr': [
        'Liens externes',
        'Lien externe',
        'Voir aussi',
        'Notes'
    ],
    'he': [
        '?????? ????',
        '???????????? ??????????',
        '?????????????? ????????????????',
        '?????????? ????????????',
    ],
    'hsb': [
        'N????ki',
    ],
    'hu': [
        'K??ls?? hivatkoz??sok',
        'L??sd m??g',
    ],
    'it': [
        'Bibliografia',
        'Voci correlate',
        'Altri progetti',
        'Collegamenti esterni',
        'Vedi anche',
    ],
    'ja': [
        '????????????',
        '????????????',
        '???????????????',
    ],
    'ko': [              # no explicit policy on where to put the references
        '?????? ??????',
        '????????????',
        '?????? ??????',
        '????????????',
        '?????? ??????',
        '????????????'
        '?????? ??????',
        '????????????'
    ],
    'lt': [              # no explicit policy on where to put the references
        'Nuorodos'
    ],
    'nl': [              # no explicit policy on where to put the references
        'Literatuur',
        'Zie ook',
        'Externe verwijzingen',
        'Externe verwijzing',
    ],
    'pdc': [
        'Beweisunge',
        'Quelle unn Literatur',
        'Gwelle',
        'Gwuelle',
        'Auswenniche Gleecher',
        'Gewebbgleecher',
        'Guckt mol aa',
        'Seh aa',
    ],
    'pl': [
        '??r??d??a',
        'Bibliografia',
        'Zobacz te??',
        'Linki zewn??trzne',
    ],
    'pt': [
        'Liga????es externas',
        'Veja tamb??m',
        'Ver tamb??m',
        'Notas',
    ],
    'ru': [
        '????????????',
        '????????????????????',
    ],
    'sd': [
        '???????? ??????',
        '??????????',
        '?????????? ??????????',
    ],
    'sk': [
        'Pozri aj',
    ],
    'sr': [
        '???????? ????????????',
        '???????????????? ????????',
        '???????? ??????',
        '????????????????',
        '????????????????????',
    ],
    'szl': [
        'Przipisy',
        'P??ipisy',
    ],
    'th': [
        '???????????????????????????????????????',
        '?????????????????????????????????????????????',
        '?????????????????????',
        '????????????????????????',
    ],
    'ur': [              # no explicit policy on where to put the references
        '???????? ????????????',
        '?????????? ??????',
        '???????????? ??????????',
    ],
    'zh': [
        '????????????',
        '????????????',
        '????????????',
        '????????????',
    ],
}

# Titles of sections where a reference tag would fit into.
# The first title should be the preferred one: It's the one that
# will be used when a new section has to be created.
# Except for the first, others are tested as regexes.
referencesSections = {
    'wikipedia': {
        'ar': [             # not sure about which ones are preferred.
            '??????????',
            '??????????????',
            '??????????',
            '??????????????',
            '?????????? ????????????',
            '?????????? ????????????',
            '?????????????? ????????????????',
            '?????????????? ????????????????',
        ],
        'ary': [
            '????????????',
            '??????????',
        ],
        'arz': [
            '??????????',
            '??????????????',
            '??????????',
            '??????????????',
        ],
        'ca': [
            'Refer??ncies',
        ],
        'cs': [
            'Reference',
            'Pozn??mky',
        ],
        'da': [
            'Noter',
        ],
        'de': [             # see [[de:WP:REF]]
            'Einzelnachweise',
            'Anmerkungen',
            'Belege',
            'Endnoten',
            'Fu??noten',
            'Fu??-/Endnoten',
            'Quellen',
            'Quellenangaben',
        ],
        'dsb': [
            'No??ki',
        ],
        'en': [             # not sure about which ones are preferred.
            'References',
            'Footnotes',
            'Notes',
        ],
        'ru': [
            '????????????????????',
            '????????????',
            '??????????????????',
        ],
        'eo': [
            'Referencoj',
        ],
        'es': [
            'Referencias',
            'Notas',
        ],
        'fa': [
            '??????????',
            '????????'
        ],
        'fi': [
            'L??hteet',
            'Viitteet',
        ],
        'fr': [             # [[fr:Aide:Note]]
            'Notes et r??f??rences',
            'Notes? et r[??e]f[??e]rences?',
            'R[??e]f[??e]rences?',
            'Notes?',
            'Sources?',
        ],
        'he': [
            '?????????? ????????????',
        ],
        'hsb': [
            'N????ki',
        ],
        'hu': [
            'Forr??sok ??s jegyzetek',
            'Forr??sok',
            'Jegyzetek',
            'Hivatkoz??sok',
            'Megjegyz??sek',
        ],
        'is': [
            'Heimildir',
            'Tilv??sanir',
        ],
        'it': [
            'Note',
            'Riferimenti',
        ],
        'ja': [
            '??????',
            '?????????',
            '???????????????',
            '??????',
            '??????',
            '???',
        ],
        'ko': [
            '??????',
            '??????'
            '?????? ??? ?????? ??????'
            '?????? ??? ????????????',
            '?????? ??? ?????? ??????'
        ],
        'lt': [             # not sure about which ones are preferred.
            '??altiniai',
            'Literat??ra',
        ],
        'nl': [             # not sure about which ones are preferred.
            'Voetnoten',
            'Voetnoot',
            'Referenties',
            'Noten',
            'Bronvermelding',
        ],
        'pdc': [
            'Aamarrickunge',
        ],
        'pl': [
            'Przypisy',
            'Uwagi',
        ],
        'pt': [
            'Refer??ncias',
        ],
        'sd': [
            '??????????',
        ],
        'sk': [
            'Referencie',
        ],
        'sr': [
            '??????????????????',
            '????????????',
        ],
        'szl': [
            'Przipisy',
            'P??ipisy',
        ],
        'th': [
            '?????????????????????',
            '????????????????????????',
            '????????????????????????',
        ],
        'ur': [
            '?????????? ??????',
            '??????????',
        ],
        'zh': [
            '????????????',
            '????????????',
            '????????????',
            '????????????',
            '????????????',
            '????????????',
        ],
    },
}
# Header on Czech Wiktionary should be different (T123091)
referencesSections['wiktionary'] = dict(referencesSections['wikipedia'])
referencesSections['wiktionary'].update(cs=['pozn??mky', 'reference'])

# Templates which include a <references /> tag. If there is no such template
# on your wiki, you don't have to enter anything here.
referencesTemplates = {
    'wikipedia': {
        'ar': ['??????????', '??????????????', '?????? ??????????????',
               '?????? ??????????????', '?????????? ??????????', 'Reflist'],
        'ary': ['??????????', '??????????????', '??????????????',
                'Reflist', 'Refs'],
        'arz': ['??????????', '??????????', '??????????????', '?????? ??????????????',
                'Reflist', 'Refs'],
        'be': ['????????????', '????????????????????', 'Reflist', '???????? ????????????',
               '??????????????'],
        'be-tarask': ['????????????'],
        'ca': ['Refer??ncies', 'Reflist', 'Listaref', 'Refer??ncia',
               'Referencies', 'Refer??ncies2',
               'Amaga', 'Amaga ref', 'Amaga Ref', 'Amaga Ref2', 'Ap??ndix'],
        'da': ['Reflist'],
        'dsb': ['Referency'],
        'en': ['Reflist', 'Refs', 'FootnotesSmall', 'Reference',
               'Ref-list', 'Reference list', 'References-small', 'Reflink',
               'Footnotes', 'FootnotesSmall'],
        'eo': ['Referencoj'],
        'es': ['Listaref', 'Reflist', 'muchasref'],
        'fa': ['Reflist', 'Refs', 'FootnotesSmall', 'Reference',
               '????????????', '??????????????????? ', '???????????? ??', '??????????????',
               '?????????? ??????????'],
        'fi': ['Viitteet', 'Reflist'],
        'fr': ['R??f??rences', 'Notes', 'References', 'Reflist'],
        'he': ['?????????? ????????????', '????????'],
        'hsb': ['Referency'],
        'hu': ['reflist', 'forr??sok', 'references', 'megjegyz??sek'],
        'is': ['reflist'],
        'it': ['References'],
        'ja': ['Reflist', '???????????????'],
        'ko': ['??????', 'Reflist'],
        'lt': ['Reflist', 'Ref', 'Litref'],
        'nl': ['Reflist', 'Refs', 'FootnotesSmall', 'Reference',
               'Ref-list', 'Reference list', 'References-small', 'Reflink',
               'Referenties', 'Bron', 'Bronnen/noten/referenties', 'Bron2',
               'Bron3', 'ref', 'references', 'appendix',
               'Noot', 'FootnotesSmall'],
        'pl': ['Przypisy', 'Przypisy-lista', 'Uwagi'],
        'pt': ['Notas', 'ref-section', 'Refer??ncias', 'Reflist'],
        'ru': ['Reflist', 'Ref-list', 'Refs', 'Sources',
               '????????????????????', '???????????? ????????????????????',
               '????????????', '????????????'],
        'sd': ['Reflist', 'Refs', 'Reference',
               '??????????'],
        'sr': ['Reflist', '??????????????????', '????????????', '??????????????'],
        'szl': ['Przipisy', 'P??ipisy'],
        'th': ['???????????????????????????????????????'],
        'ur': ['Reflist', 'Refs', 'Reference',
               '?????????? ??????', '??????????'],
        'zh': ['Reflist', 'RefFoot', 'NoteFoot'],
    },
}

# Text to be added instead of the <references /> tag.
# Define this only if required by your wiki.
referencesSubstitute = {
    'wikipedia': {
        'ar': '{{??????????}}',
        'ary': '{{??????????}}',
        'arz': '{{??????????}}',
        'be': '{{????????????}}',
        'da': '{{reflist}}',
        'dsb': '{{referency}}',
        'fa': '{{????????????}}',
        'fi': '{{viitteet}}',
        'fr': '{{r??f??rences}}',
        'he': '{{?????????? ????????????}}',
        'hsb': '{{referency}}',
        'hu': '{{Forr??sok}}',
        'pl': '{{Przypisy}}',
        'ru': '{{????????????????????}}',
        'sd': '{{??????????}}',
        'sr': '{{reflist}}',
        'szl': '{{Przipisy}}',
        'th': '{{???????????????????????????????????????}}',
        'ur': '{{?????????? ??????}}',
        'zh': '{{reflist}}',
    },
}

# Sites where no title is required for references template
# as it is already included there
noTitleRequired = ['be', 'szl']

maintenance_category = 'Q6483427'

_ref_regex = re.compile('</ref>', re.IGNORECASE)
_references_regex = re.compile('<references.*?/>', re.IGNORECASE)


def _match_xml_page_text(text) -> bool:
    """Match page text."""
    text = textlib.removeDisabledParts(text)
    return _ref_regex.search(text) and not _references_regex.search(text)


XmlDumpNoReferencesPageGenerator = partial(
    XMLDumpPageGenerator, text_predicate=_match_xml_page_text)


class NoReferencesBot(SingleSiteBot, ExistingPageBot, NoRedirectPageBot):

    """References section bot."""

    @remove_last_args(['gen'])
    def __init__(self, **kwargs) -> None:
        """Initializer."""
        self.available_options.update({
            'verbose': True,
        })
        super().__init__(**kwargs)

        self.refR = _ref_regex
        self.referencesR = _references_regex
        self.referencesTagR = re.compile('<references>.*?</references>',
                                         re.IGNORECASE | re.DOTALL)
        try:
            self.referencesTemplates = referencesTemplates[
                self.site.family.name][self.site.code]
        except KeyError:
            self.referencesTemplates = []
        try:
            self.referencesText = referencesSubstitute[
                self.site.family.name][self.site.code]
        except KeyError:
            self.referencesText = '<references />'

    def lacksReferences(self, text) -> bool:
        """Check whether or not the page is lacking a references tag."""
        oldTextCleaned = textlib.removeDisabledParts(text)
        if self.referencesR.search(oldTextCleaned) or \
           self.referencesTagR.search(oldTextCleaned):
            if self.opt.verbose:
                pywikibot.output('No changes necessary: references tag found.')
            return False

        if self.referencesTemplates:
            templateR = '{{(' + '|'.join(self.referencesTemplates) + ')'
            if re.search(templateR, oldTextCleaned, re.IGNORECASE):
                if self.opt.verbose:
                    pywikibot.output(
                        'No changes necessary: references template found.')
                return False

        if not self.refR.search(oldTextCleaned):
            if self.opt.verbose:
                pywikibot.output('No changes necessary: no ref tags found.')
            return False

        if self.opt.verbose:
            pywikibot.output('Found ref without references.')
        return True

    def addReferences(self, oldText) -> str:
        """
        Add a references tag into an existing section where it fits into.

        If there is no such section, creates a new section containing
        the references tag. Also repair malformed references tags.
        Set the edit summary accordingly.

        @param oldText: page text to be modified
        @type oldText: str
        @return: The modified pagetext
        """
        # Do we have a malformed <reference> tag which could be repaired?
        # Set the edit summary for this case
        self.comment = i18n.twtranslate(self.site, 'noreferences-fix-tag')

        # Repair two opening tags or an opening and an empty tag
        pattern = re.compile(r'< *references *>(.*?)'
                             r'< */?\s*references */? *>', re.DOTALL)
        if pattern.search(oldText):
            pywikibot.output('Repairing references tag')
            return re.sub(pattern, r'<references>\1</references>', oldText)
        # Repair single unclosed references tag
        pattern = re.compile(r'< *references *>')
        if pattern.search(oldText):
            pywikibot.output('Repairing references tag')
            return re.sub(pattern, '<references />', oldText)

        # Is there an existing section where we can add the references tag?
        # Set the edit summary for this case
        self.comment = i18n.twtranslate(self.site, 'noreferences-add-tag')
        for section in i18n.translate(self.site, referencesSections):
            sectionR = re.compile(r'\r?\n=+ *%s *=+ *\r?\n' % section)
            index = 0
            while index < len(oldText):
                match = sectionR.search(oldText, index)
                if match:
                    if textlib.isDisabled(oldText, match.start()):
                        pywikibot.output(
                            'Existing {0} section is commented out, skipping.'
                            .format(section))
                        index = match.end()
                    else:
                        pywikibot.output('Adding references tag to existing'
                                         '{0} section...\n'.format(section))
                        templates_or_comments = re.compile(
                            r'^((?:\s*(?:\{\{[^\{\}]*?\}\}|<!--.*?-->))*)',
                            flags=re.DOTALL)
                        new_text = (
                            oldText[:match.end() - 1]
                            + templates_or_comments.sub(
                                r'\1\n{0}\n'.format(self.referencesText),
                                oldText[match.end() - 1:]))
                        return new_text
                else:
                    break

        # Create a new section for the references tag
        for section in i18n.translate(self.site, placeBeforeSections):
            # Find out where to place the new section
            sectionR = re.compile(r'\r?\n(?P<ident>=+) *%s *(?P=ident) *\r?\n'
                                  % section)
            index = 0
            while index < len(oldText):
                match = sectionR.search(oldText, index)
                if match:
                    if textlib.isDisabled(oldText, match.start()):
                        pywikibot.output(
                            'Existing {0} section is commented out, '
                            "won't add the references in front of it."
                            .format(section))
                        index = match.end()
                    else:
                        pywikibot.output(
                            'Adding references section before {0} section...\n'
                            .format(section))
                        index = match.start()
                        ident = match.group('ident')
                        return self.createReferenceSection(oldText, index,
                                                           ident)
                else:
                    break
        # This gets complicated: we want to place the new references
        # section over the interwiki links and categories, but also
        # over all navigation bars, persondata, and other templates
        # that are at the bottom of the page. So we need some advanced
        # regex magic.
        # The strategy is: create a temporary copy of the text. From that,
        # keep removing interwiki links, templates etc. from the bottom.
        # At the end, look at the length of the temp text. That's the position
        # where we'll insert the references section.
        catNamespaces = '|'.join(self.site.namespaces.CATEGORY)
        categoryPattern = r'\[\[\s*(%s)\s*:[^\n]*\]\]\s*' % catNamespaces
        interwikiPattern = r'\[\[([a-zA-Z\-]+)\s?:([^\[\]\n]*)\]\]\s*'
        # won't work with nested templates
        # the negative lookahead assures that we'll match the last template
        # occurrence in the temp text.
        # FIXME:
        # {{commons}} or {{commonscat}} are part of Weblinks section
        # * {{template}} is mostly part of a section
        # so templatePattern must be fixed
        templatePattern = r'\r?\n{{((?!}}).)+?}}\s*'
        commentPattern = r'<!--((?!-->).)*?-->\s*'
        metadataR = re.compile(r'(\r?\n)?(%s|%s|%s|%s)$'
                               % (categoryPattern, interwikiPattern,
                                  templatePattern, commentPattern), re.DOTALL)
        tmpText = oldText
        while True:
            match = metadataR.search(tmpText)
            if match:
                tmpText = tmpText[:match.start()]
            else:
                break
        pywikibot.output(
            'Found no section that can be preceded by a new references '
            'section.\nPlacing it before interwiki links, categories, and '
            'bottom templates.')
        index = len(tmpText)
        return self.createReferenceSection(oldText, index)

    def createReferenceSection(self, oldText, index, ident='==') -> str:
        """Create a reference section and insert it into the given text.

        @param oldText: page text that is going to be be amended
        @type oldText: str
        @param index: the index of oldText where the reference section should
            be inserted at
        @type index: int
        @param ident: symbols to be inserted before and after reference section
            title
        @type ident: str
        @return: the amended page text with reference section added
        """
        if self.site.code in noTitleRequired:
            ref_section = '\n\n%s\n' % self.referencesText
        else:
            ref_section = '\n\n{ident} {title} {ident}\n{text}\n'.format(
                title=i18n.translate(self.site, referencesSections)[0],
                ident=ident, text=self.referencesText)
        return oldText[:index].rstrip() + ref_section + oldText[index:]

    def skip_page(self, page):
        """Check whether the page could be processed."""
        if page.isDisambig():
            pywikibot.output('Page {} is a disambig; skipping.'
                             .format(page.title(as_link=True)))
            return True

        if self.site.sitename == 'wikipedia:en' and page.isIpEdit():
            pywikibot.warning(
                'Page {} is edited by IP. Possible vandalized'
                .format(page.title(as_link=True)))
            return True

        return super().skip_page(page)

    def treat_page(self) -> None:
        """Run the bot."""
        page = self.current_page
        try:
            text = page.text
        except pywikibot.LockedPage:
            pywikibot.warning('Page {} is locked?!'
                              .format(page.title(as_link=True)))
            return

        if self.lacksReferences(text):
            self.put_current(self.addReferences(text), summary=self.comment)


def main(*args) -> None:
    """
    Process command line arguments and invoke bot.

    If args is an empty list, sys.argv is used.

    @param args: command line arguments
    @type args: str
    """
    options = {}
    gen = None

    # Process global args and prepare generator args parser
    local_args = pywikibot.handle_args(args)
    genFactory = pagegenerators.GeneratorFactory()

    for arg in local_args:
        opt, _, value = arg.partition(':')
        if opt == '-xml':
            xmlFilename = value or i18n.input('pywikibot-enter-xml-filename')
            gen = XmlDumpNoReferencesPageGenerator(xmlFilename)
        elif opt == '-always':
            options['always'] = True
        elif opt == '-quiet':
            options['verbose'] = False
        else:
            genFactory.handle_arg(arg)

    gen = genFactory.getCombinedGenerator(gen, preload=True)
    if not gen:
        site = pywikibot.Site()
        cat = site.page_from_repository(maintenance_category)
        if cat:
            gen = cat.articles(namespaces=genFactory.namespaces or [0])

    if gen:
        bot = NoReferencesBot(generator=gen, **options)
        bot.run()
    else:
        pywikibot.bot.suggest_help(missing_generator=True)


if __name__ == '__main__':
    main()
