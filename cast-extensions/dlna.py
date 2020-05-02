import re
import upnpclient
import xml.etree.ElementTree as ET
from random import randrange


def find_dlna(dlna_server, expression, index=0):
    """
    Return a single url from dlna, title matching the regular expression `expression`.
    Will return the item at index `index`. Pass "random" for a random index.
    """
    res = [
        s for s in upnpclient.Device("http://{}/rootDesc.xml".format(dlna_server)).services
        if s.name == "ContentDirectory"
    ][0].Browse(
        ObjectID="2$8",
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
        if re.search(expression, item[0].text) is not None and count >= index:
            return item[3].text
        count += 1
