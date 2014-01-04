#!/usr/bin/env python
#-*- coding:utf-8 -*-
########################################################
# Name: Subtitles Client
# Site: http://RealGame.co.il
__author__ = 'RealGame (Tomer Zait)'
__license__ = 'GPL v3'
__version__ = '1.0'
__email__ = 'realgam3@gmail.com'
########################################################

from os import path
from docopt import docopt

from engines.engine import SubtitleSite, SUBTITLE_SITE_LIST, DEFAULTS


__doc__ = \
"""
Subtitles Client

Usage:
  {prog} download <releases_path>... [--lang=<language> | --engine=<subtitle_site>...]
  {prog} exist <releases_path>... [--lang=<language> | --engine=<subtitle_site>...]
  {prog} test [<engines>...]
  {prog} (-h | --help)
  {prog} (-v | --version)

Options:
  -h --help                 Show this screen.
  -v --version              Show version.
  --lang=<language>         Subtitle Language (Alpha2) [default: {def_language}].
  --engine=<subtitle_site>  Subtitle Site              [default: {def_engine}].
""".format(prog=path.basename(__file__),
           def_language=DEFAULTS['subtitle_language'],
           def_engine=DEFAULTS['subtitle_engine'])


def download_subtitles(releases, engines=[DEFAULTS['subtitle_engine']], lang=DEFAULTS['subtitle_language']):
    if releases:
        for release in releases:
            for engine in engines:
                subtitle_release = SubtitleSite.get_file_properties(release)['release_name']
                print "[{engine: ^15}] Trying To Download Subtitles For: '{release}'".format(engine=engine,
                                                                                             release=subtitle_release)
                sub_obj = SubtitleSite.class_factory(engine)
                subtitle_path = sub_obj.download_subtitle(release, lang)
                if subtitle_path:
                    print "{0:17} Download Success: ({file_path}).\n".format("", file_path=subtitle_path)
                else:
                    print "{0:17} Subtitles Not Found.\n".format("")


def is_subtitles_exist(releases, engines=[DEFAULTS['subtitle_engine']], lang=DEFAULTS['subtitle_language']):
    if releases:
        for release in releases:
            for engine in engines:
                subtitle_release = SubtitleSite.get_file_properties(release)['release_name']

                sub_obj = SubtitleSite.class_factory(engine)
                exist_flag = sub_obj.is_subtitle_exist(release, lang)
                res = "Exist"
                if not exist_flag:
                    res = "Does Not " + res
                print "[{engine: ^15}] '{release}' - {res}.".format(engine=engine,
                                                                    release=subtitle_release,
                                                                    res=res)


def test_engines(engines):
    if not engines:
        engines = SUBTITLE_SITE_LIST.keys()

    for engine_key in engines:
        t = SubtitleSite.class_factory(engine_key)
        t.test_engine()


def main():
    args = docopt(__doc__, help=True, version='Subtitles Client %s' % __version__)
    
    if args['download']:
        download_subtitles(args['<releases_path>'], args['--engine'], args['--lang'])
    elif args['exist']:
        is_subtitles_exist(args['<releases_path>'], args['--engine'], args['--lang'])
    elif args['test']:
        test_engines(args['<engines>'])


if __name__ == "__main__":
    main()
