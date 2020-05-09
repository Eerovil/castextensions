import re
import upnpclient
import xml.etree.ElementTree as ET
from random import randrange


import logging


_LOGGER = logging.getLogger(__name__)


def find_dlna(dlna_server, expression, index=0, content_type="video/mp4"):
    """
    Return a single url from dlna, title matching the regular expression `expression`.
    Will return the item at index `index`. Pass "random" for a random index.
    """
    object_id = "2$8"
    index_url = 3
    if content_type[:5] == "audio":
        object_id = "1$4"
        index_url = 7
    res = [
        s for s in upnpclient.Device("http://{}/rootDesc.xml".format(dlna_server)).services
        if s.name == "ContentDirectory"
    ][0].Browse(
        ObjectID=object_id,
        BrowseFlag="BrowseDirectChildren",
        Filter="",
        StartingIndex=0,
        RequestedCount=100000,
        SortCriteria="",
    )["Result"]

    root = ET.fromstring(res)
    count = 0
    if not index:
        index = 0
    elif index == 'random':
        index = randrange(0, len(root))
    for item in root:
        _LOGGER.error(item[0].text)
        if re.search(expression, item[0].text) is not None and count >= index:
            return item[index_url].text
        count += 1
