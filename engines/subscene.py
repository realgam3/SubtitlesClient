__author__ = 'RealGame (Tomer Zait)'

from re import compile, IGNORECASE, DOTALL
from urlparse import urljoin
from os import path, remove
from pycountry import languages

from engines.engine import SubtitleSite


class SubScene(SubtitleSite):
    def __init__(self, host_url):
        super(SubScene, self).__init__(host_url)
        self.__sub_url = None

    def __search_subtitles(self):
        res = self._session.get(urljoin(self.host_url, 'subtitles/release'),
                                params={'q': self.subtitle_release},
                                headers=self._headers)

        regex_search =  \
            r'<tr>\r\n' + \
            '\t+<td class="\w\d">\r\n' + \
            '\t+<a href="(?P<url>.*?)">\r\n' + \
            '\t+<div class="visited">\r\n' + \
            '\t+<span class=".*?">\r\n\t+(?P<lang>.*?)\r\n\t+</span>\r\n' + \
            '\t+<span>\r\n\t*(?P<release_name>.*?)\r\n\t+</span>\r\n' + \
            '\t+</div>\r\n.*?</tr>'

        regex_obj = compile(regex_search, flags=DOTALL)

        return [regex_res.groupdict() for regex_res in regex_obj.finditer(res.content)]

    def _get_subtitle_info(self):
        lang = languages.get(alpha2=self.subtitle_language).name
        to_search = self.strip_version(self.subtitle_release)

        sub_dict_list = self.__search_subtitles()
        for sub_dict in sub_dict_list:
            sub_regex = compile(self.strip_version(sub_dict['release_name']), flags=IGNORECASE)
            lang_regex = compile(sub_dict['lang'], flags=IGNORECASE)

            if sub_regex.match(to_search) and lang_regex.match(lang):
                self.__sub_url = sub_dict['url']
                return True
        return False

    def download_subtitle(self, subtitle_release, lang='en', test_mode=False):
        file_properties = self.get_file_properties(subtitle_release)
        self.subtitle_release = file_properties['release_name']
        self.subtitle_language = lang

        if self._get_subtitle_info():
            local_path = self.download_file(url=urljoin(self.host_url, self.__sub_url),
                                            session=self._session,
                                            base_dir=file_properties['base_dir'])
            if path.exists(local_path):
                if test_mode:
                    remove(local_path)
                return local_path
        return None
