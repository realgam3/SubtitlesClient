__author__ = 'RealGame (Tomer Zait)'

from re import findall, sub
from requests import Session
from os import path
from sys import exit, path as sys_path
from importlib import import_module
from abc import ABCMeta, abstractmethod


SUBTITLE_SITE_LIST = {
    'torec': {
        'class_name': 'Torec',
        'host_url': 'http://www.torec.net'
    },
    'subscenter': {
        'class_name': 'SubsCenter',
        'host_url': 'http://www.subscenter.org'
    },
    'subscene': {
        'class_name': 'SubScene',
        'host_url':  'http://www.subscene.com'
    }
}
DEFAULTS = {
    'test_release': 'Captain.America.The.First.Avenger.720p.Bluray.x264-MHD',
    'subtitle_language': 'he',
    'subtitle_engine': 'Torec'
}


class SubtitleSite(object):
    __metaclass__ = ABCMeta

    def __init__(self, host_url=None):
        super(SubtitleSite, self).__init__()
        self.host_url = host_url
        self.subtitle_release = None
        self.subtitle_language = None
        self._session = Session()
        self._headers = {
            'User-Agent': 'Subtitles Client'
        }

    @abstractmethod
    def _get_subtitle_info(self):
        pass

    @abstractmethod
    def download_subtitle(self, subtitle_release, lang=DEFAULTS['subtitle_language'], test_mode=False):
        pass

    def is_subtitle_exist(self, subtitle_release, lang=DEFAULTS['subtitle_language']):
        file_properties = self.get_file_properties(subtitle_release)
        self.subtitle_release = file_properties['release_name']
        self.subtitle_language = lang

        if self._get_subtitle_info():
            return True
        return False

    def test_engine(self):
        if self.download_subtitle(DEFAULTS['test_release'], test_mode=True):
            res = 'OK'
        else:
            res = 'ERROR'
        print "{class_name}: {res}".format(class_name=self.__class__.__name__, res=res)

    @staticmethod
    def class_factory(class_name):
        class_lower_name = class_name.lower()

        if class_lower_name in SUBTITLE_SITE_LIST.keys():
            sub_dict = SUBTITLE_SITE_LIST.get(class_lower_name)

            #Get subtitle dict items
            class_name = sub_dict.get('class_name')
            host_url = sub_dict.get('host_url')

            #Let us import outside the engines directory from string
            engines_path = path.dirname(__file__)
            if engines_path not in sys_path:
                sys_path.insert(0, engines_path)

            #Import dynamic class items
            subtitle_module = import_module(class_lower_name)
            subtitle_class = getattr(subtitle_module, class_name)

            return subtitle_class(host_url)

        print "Subtitles Site '{site_name}' Doesn't Exist!".format(site_name=class_name)
        exit(1)

    @staticmethod
    def download_file(url, params=None, headers=None, session=Session(), base_dir=''):
        r = session.get(url, params=params, headers=headers)

        #Get File Name & Save Path
        if 'Content-Disposition' in r.headers:
            local_filename = findall(r'filename=(.*)', r.headers['Content-Disposition'])[0]
        else:
            local_filename = path.basename(url)
        local_path = path.join(base_dir, local_filename)

        #Write The File
        with open(local_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                # filter out keep-alive new chunks
                if chunk:
                    f.write(chunk)
                    f.flush()
        return local_path

    @staticmethod
    def strip_version(release_version):
        return sub(r'[\.\-\s]', '', release_version).lower()

    @staticmethod
    def get_file_properties(full_path):
        #File Properties Dictionary
        properties = {
            'base_dir': '',
            'release_name': None
        }

        #If Is File Path
        if path.isfile(full_path):
            properties['base_dir'] = path.dirname(full_path)
            properties['release_name'] = path.splitext(path.basename(full_path))[0]
        #If Is Folder Path
        elif path.isdir(full_path):
            properties['base_dir'] = full_path
            properties['release_name'] = path.basename(full_path)
        #If Is Not File Or Folder Path
        else:
            properties['release_name'] = full_path

        return properties
