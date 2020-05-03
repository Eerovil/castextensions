"""
Use Yle areena API to fetch media urls ready for playing with the chromecast
mediaplayer app.
"""


import requests
from random import randrange
from yledl import yledl

AREENA_URL = "https://external.api.yle.fi/v1/"


def monkeypatched(lines):
    yledl.retval = lines


yledl.print_lines = monkeypatched


class YleAreena:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_series_latest_id(self, series_id):
        data = self.api_call(
            (
                "programs/items.json?&"
                "series={series_id}&"
                "order=publication.starttime:desc&limit=1&"
                "type=program&"
                "availability=ondemand"
            ).format(series_id=series_id)
        )
        return data["data"][0]["id"]

    def get_series_random_id(self, series_id):
        data = self.api_call(
            (
                "programs/items.json?&"
                "series={series_id}&"
                "order=publication.starttime:asc&limit=10&"
                "type=program&"
                "availability=ondemand"
            ).format(series_id=series_id)
        )
        return data["data"][randrange(len(data["data"]) - 1)]["id"]

    def api_call(self, url):
        try:
            full_url = AREENA_URL + url + "&" + self.api_key
            print("full_url:", full_url)
            response = requests.get(full_url)
            return response.json()
        except Exception as e:
            print(e, response.content)

    @classmethod
    def get_program_url(self, program_id):
        print("Fetching url for program", program_id)
        yledl.main(["yledl", "--showurl", "https://areena.yle.fi/%s" % program_id])
        return yledl.retval[0]

    @classmethod
    def get_kaltura_id(self, program_id):
        """
        Dive into the yledl internals and fetch the kaltura player id.
        This can be used with Chromecast
        """
        from yledl.streamfilters import StreamFilters
        from yledl.http import HttpClient
        from yledl.localization import TranslationChooser
        from yledl.extractors import extractor_factory
        from yledl.titleformatter import TitleFormatter

        title_formatter = TitleFormatter()
        language_chooser = TranslationChooser('fin')
        httpclient = HttpClient(None)
        stream_filters = StreamFilters()

        url = 'https://areena.yle.fi/{}'.format(program_id)

        extractor = extractor_factory(url, stream_filters, language_chooser, httpclient)
        pid = extractor.program_id_from_url(url)

        info = extractor.program_info_for_pid(pid, url, title_formatter, None)

        return info.media_id.split('-')[-1]
