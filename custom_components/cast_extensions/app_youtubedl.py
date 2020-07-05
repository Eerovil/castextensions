import youtube_dl
from youtube_dl.utils import DownloadError, ExtractorError

import logging


_LOGGER = logging.getLogger(__name__)


DEFAULT_YTDL_OPTS = {"quiet": True, "no_warnings": True, 'logger': _LOGGER}


def youtubedl_get_media_url(content_type, media_url, ytdl_options=None):
    ydl = youtube_dl.YoutubeDL(dict(ytdl_options) if ytdl_options else DEFAULT_YTDL_OPTS)
    if content_type.startswith('audio') or content_type.startswith('music'):
        best_format = "bestaudio"
    else:
        best_format = "best"

    try:
        all_media_streams = ydl.extract_info(media_url, process=False)
    except DownloadError:
        # This exception will be logged by youtube-dl itself
        raise

    if 'entries' in all_media_streams:
        _LOGGER.warning("Playlists are not supported, "
                        "looking for the first video")
        try:
            selected_stream = next(all_media_streams['entries'])
        except StopIteration:
            _LOGGER.error("Playlist is empty")
            raise
    else:
        selected_stream = all_media_streams

    try:
        media_info = ydl.process_ie_result(selected_stream, download=False)
    except (ExtractorError, DownloadError):
        # This exception will be logged by youtube-dl itself
        raise

    format_selector = ydl.build_format_selector(best_format)

    try:
        best_quality_stream = next(format_selector(media_info))
    except (KeyError, StopIteration):
        best_quality_stream = media_info

    return best_quality_stream['url']
