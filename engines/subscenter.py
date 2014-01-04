__author__ = 'RealGame (Tomer Zait)'

from re import match, search, IGNORECASE
from urlparse import urljoin
from os import path, remove
from json import loads

from engine import SubtitleSite


class SubsCenter(SubtitleSite):
    def __init__(self, host_url):
        super(SubsCenter, self).__init__(host_url)
        self.__subs_list = list()
        self.__sub_dict = dict()

    def __search_subtitles(self):
        res = self._session.get(url=urljoin(self.host_url, '/he/subtitle/search/'),
                                params={'q': self.subtitle_release},
                                headers=self._headers)

        regex_res = search('subtitles_groups = (?P<json>\{.*\})', res.content)
        if regex_res:
            return loads(regex_res.group('json'))

    def __create_subs_list(self, subs_dict):
        for item_key in subs_dict.keys():
            item = subs_dict.get(item_key)
            if type(item) == type(dict()):
                if 'key' in item.keys():
                    self.__subs_list.append(item)
                else:
                    self.__create_subs_list(item)

    def _get_subtitle_info(self):
        subs_dict = self.__search_subtitles()
        if subs_dict:
            self.__create_subs_list(subs_dict.get(self.subtitle_language))

            to_search = self.strip_version(self.subtitle_release)
            if self.__subs_list:
                for subtitle in self.__subs_list:
                    sub_version = self.strip_version(subtitle['subtitle_version'])
                    if match(sub_version, to_search, flags=IGNORECASE):
                        self.__sub_dict = subtitle
                        return True
        return False

    def download_subtitle(self, subtitle_release, lang='he', test_mode=False):
        file_properties = self.get_file_properties(subtitle_release)
        self.subtitle_release = file_properties['release_name']
        self.subtitle_language = lang

        if self._get_subtitle_info():
            sub_url = urljoin(self.host_url, '/subtitle/download/{lang}/{sub_id}/'.format(lang=lang,
                                                                                          sub_id=self.__sub_dict['id']))
            local_path = self.download_file(url=sub_url,
                                            params={'v': self.__sub_dict['subtitle_version'],
                                                    'key': self.__sub_dict['key']},
                                            session=self._session,
                                            base_dir=file_properties['base_dir'])
            if path.exists(local_path):
                if test_mode:
                    remove(local_path)
                return local_path
        return None
