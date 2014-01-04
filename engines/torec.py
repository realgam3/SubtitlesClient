__author__ = 'RealGame (Tomer Zait)'

from re import search, compile, IGNORECASE
from urlparse import urljoin
from os import path, remove
from math import floor
from random import random

from engine import SubtitleSite


class Torec(SubtitleSite):
    def __init__(self, host_url):
        super(Torec, self).__init__(host_url)
        self.__sub_dict = {
            'sub_id': -1,
            's': 1920,
            'code': None,
            'sh': 'yes',
            'guest': None,
            'timewaited': int(floor(random() * 7 + 12))
        }

    def __search_subtitles(self):
        res = self._session.post(url=urljoin(self.host_url, 'ssearch.asp'),
                                 data={'search': self.subtitle_release},
                                 headers=self._headers)

        r = compile('<td class="newd_table_titleLeft_BG"><div><a href="/sub\.asp\?sub_id=(.*?)">.*?</a></div></td>')
        regex_res = r.findall(res.content)
        if regex_res:
            self.__sub_dict['sub_id'] = regex_res[0]

    def _get_subtitle_info(self):
        self.__search_subtitles()

        res = self._session.get(url=urljoin(self.host_url, 'sub.asp'),
                                params={'sub_id': self.__sub_dict['sub_id']},
                                headers=self._headers)

        to_search = self.strip_version(self.subtitle_release)
        options = compile('<option value="(?P<code>.*?)" style=".*?">(?P<version>.*?)</option>')
        for option in options.finditer(res.content):
            sub_dict = option.groupdict()
            sub_version = compile(".*%s" % self.strip_version(sub_dict['version']), flags=IGNORECASE)

            if sub_version.match(to_search):
                self.__sub_dict['code'] = sub_dict['code']
                return True
        return False

    def __get_guest_code(self):
        data = {
            'sub_id': self.__sub_dict['sub_id'],
            's': self.__sub_dict['s']
        }
        res = self._session.post(url=urljoin(self.host_url, '/ajax/sub/guest_time.asp'),
                                 data=data,
                                 headers=self._headers)

        self.__sub_dict['guest'] = res.content
        if self.__sub_dict['guest'] != 'error':
            return True
        return False

    def __is_subtitle_ready(self):
        res_flag = (self._get_subtitle_info() and self.__get_guest_code())
        return res_flag

    def download_subtitle(self, subtitle_release, lang='he', test_mode=False):
        file_properties = self.get_file_properties(subtitle_release)
        self.subtitle_release = file_properties['release_name']
        self.subtitle_language = lang

        if self.__is_subtitle_ready():
            download_url = self._session.post(url=urljoin(self.host_url, '/ajax/sub/downloadun.asp'),
                                              data=self.__sub_dict,
                                              headers=self._headers).content

            if not search(".*?error '.*?'.*?", download_url):
                local_path = self.download_file(url=urljoin(self.host_url, download_url),
                                                session=self._session,
                                                base_dir=file_properties['base_dir'])
                if path.exists(local_path):
                    if test_mode:
                        remove(local_path)
                    return local_path
        return None
