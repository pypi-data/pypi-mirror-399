import os
import time
# from . import util
from .arguments import Arguments
from .exceptions import InvalidVideoIdException, NoContents, PatternUnmatchError, UnknownConnectionError
from .extractor import Extractor
from .html_archiver import HTMLArchiver
# from .util import extract_video_id
from .progressbar import ProgressBar
from .videoinfo2 import VideoInfo
from .youtube import channel
from .youtube import playlist
from json.decoder import JSONDecodeError
from pathlib import Path

from . import myutil as util

from youtube_transcript_api import (
    YouTubeTranscriptApi as Api,
    TranscriptsDisabled,
    NoTranscriptFound,
    CouldNotRetrieveTranscript,
    VideoUnavailable,
    NotTranslatable,
    TranslationLanguageNotAvailable,
    CookiePathInvalid,
)

# Import IP blocking errors for retry logic
try:
    from youtube_transcript_api._errors import IpBlocked, RequestBlocked
except ImportError:
    # Fallback if these classes don't exist in older versions
    class IpBlocked(Exception):
        pass
    class RequestBlocked(Exception):
        pass


import sys
import traceback
import re

SECTION_GROUP = ['streams', 'videos', 'shorts']

class Downloader:

    def __init__(self, dir_videos: set):
        self._dir_videos = dir_videos
        self._completed_videos = 0  # Track completed videos
        self._session_bandwidth_mb = 0.0  # Track bandwidth used in this session

    def _check_and_display_quota(self):
        """Display progress every 25 videos if proxy is enabled"""
        # Disabled - no bandwidth messages
        pass

    def video(self, video, splitter_string):
        is_complete = False
        try:
            video_id = util.extract_video_id(video.get('id'))
        except Exception as e:
            video_id = video.get("id")
            print(type(e), str(e))
        try:
            if not os.path.exists(Arguments().output):
                raise FileNotFoundError
            separated_path = str(Path(Arguments().output)) + os.path.sep
            path = util.checkpath(separated_path + video_id + '.html')
            # check if the video_id is already exists the output folder
            if video_id in self._dir_videos:
                # raise Exception(f"Video [{video_id}] is already exists in {os.path.dirname(path)}. Skip process.")
                print(
                    f"\nSkip the process...\n  The file for the video [{video_id}] already exists in {os.path.dirname(path)}.")

                return 'skip'

            skipmessage = None
            # Check if duration is None or empty string (common for shorts)
            if video.get("duration") is None or video.get("duration") == '':
                try:
                    info = VideoInfo(video.get("id"))
                    duration_seconds = info.get_duration()

                    # Convert seconds to "M:SS" or "H:MM:SS" format
                    if duration_seconds == 'LIVE':
                        video['duration'] = 'LIVE'
                    elif duration_seconds == 'UPCOMING':
                        video['duration'] = 'UPCOMING'
                    elif duration_seconds and duration_seconds > 0:
                        hours = duration_seconds // 3600
                        minutes = (duration_seconds % 3600) // 60
                        seconds = duration_seconds % 60
                        if hours > 0:
                            video['duration'] = f"{hours}:{minutes:02d}:{seconds:02d}"
                        else:
                            video['duration'] = f"{minutes}:{seconds:02d}"
                    else:
                        video['duration'] = None

                    # Also get published date if missing
                    if video.get("time_published") is None:
                        published_date = info.get_published_date()
                        if published_date:
                            video['time_published'] = published_date

                    if not video.get("duration"):
                        skipmessage = "Unable to retrieve transcript: Cannot retrieve the duration."
                except Exception as e:
                    print(f"Error getting duration via VideoInfo: {e}")
                    skipmessage = "Unable to retrieve transcript: Cannot retrieve the duration."

            elif video.get("duration") == 'LIVE':
                skipmessage = "Unable to retrieve transcript: This stream is live."

            elif video.get("duration") == 'UPCOMING':
                skipmessage = "Unable to retrieve transcript: This stream is upcoming."
                

            print(splitter_string)
            # Handle Unicode characters in title/channel name
            title = video.get('title', '')
            author = video.get('author', '')
            try:
                print(f"\n"
                      f"[title]    {title}\n"
                      f"[id]       {video_id}    [published] {video.get('time_published')}\n"
                      f"[channel]  {author}"
                      )
            except UnicodeEncodeError:
                # Fallback: encode with replacement for characters that can't be displayed
                print(f"\n[title]    {title.encode('ascii', 'replace').decode('ascii')}")
                print(f"[id]       {video_id}    [published] {video.get('time_published')}")
                print(f"[channel]  {author.encode('ascii', 'replace').decode('ascii')}")

            try:
                print(f"[path]     {path}  [duration] {video.get('duration')}")
            except UnicodeEncodeError:
                print(f"[path]     {path}  [duration] {video.get('duration', '').encode('ascii', 'replace').decode('ascii')}")
            if skipmessage:
                print(f"{skipmessage}\n")
                return

            duration = util.time_to_seconds(video["duration"])
            if duration == 0:
                # Check if it's an upcoming video or empty duration
                duration_str = str(video.get('duration', '')).lower()
                if duration_str in ['upcoming', 'live']:
                    print(f"Skipping {duration_str} video (not yet available)\n")
                elif duration_str == '':
                    print(f"Skipping video with empty duration (ID: {video_id})\n")
                return                        
            if video.get("error"):
                # error getting video info in parse()
                print(f"The video [{video_id}] may be private or deleted.")
                return False
            try:
                duration = util.time_to_seconds(video["duration"])
            except KeyError:
                return False
            pbar = ProgressBar(total=(duration * 1000), status="Extracting")

            ex = Extractor(video_id,
                           callback=pbar._disp)
            try:
                transcripts = ex.extract()
            finally:
                # ALWAYS close HTTP session to force new IP on next video
                if hasattr(ex, '_http_session') and ex._http_session:
                    try:
                        ex._http_session.close()
                    except:
                        pass  # Ignore close errors

            # Check if extraction failed
            if transcripts and len(transcripts) > 0 and isinstance(transcripts[0], dict) and transcripts[0].get("error"):
                error_code = transcripts[0].get("error")
                if error_code == 1:
                    print("Skipping video (no transcripts available)\n")
                elif error_code == 2:
                    print("Skipping video (IP blocked after retries)\n")
                else:
                    print("Skipping video (extraction error)\n")
                pbar.cancel()
                pbar.close()
                return False

            pbar.reset("#", "=", total=len(transcripts), status="Rendering  ")
            processor = HTMLArchiver(
                Arguments().output + video_id + '.html', callback=pbar._disp)
            processor.process(transcripts)
            processor.finalize()
            pbar.close()
            print("\nCompleted")

            # Minimal bandwidth tracking - only session total
            if Arguments().proxy_enabled:
                stats = ex.get_bandwidth_stats()
                total_mb = stats['total_kb'] / 1024
                self._session_bandwidth_mb += total_mb

            is_complete = True

            # Track completed videos and check quota
            self._completed_videos += 1
            self._check_and_display_quota()

            print()
            if pbar.is_cancelled():
                print("\nThe extraction process has been discontinued.\n")
                return False

            # No delays - proxy rotation handles everything

            return True

        except InvalidVideoIdException:
            print("Invalid Video ID or URL:", video_id)
        except NoContents as e:
            print('---' + str(e) + '---')
        except FileNotFoundError:
            print("The specified directory does not exist.:{}".format(
                Arguments().output))
            exit(0)
        except JSONDecodeError as e:
            print(e.msg)
            print("Cannot parse video information.:{}".format(video_id))
            if Arguments().save_error_data:
                util.save(e.doc, "ERR_JSON_DECODE", ".dat")
        except PatternUnmatchError as e:
            print("Cannot parse video information.:{}".format(video_id))
            if Arguments().save_error_data:
                util.save(str(e), "ERR_PATTERN_UNMATCH", ".dat")
        except KeyboardInterrupt:
            is_complete = "KeyboardInterrupt"
        except AttributeError as e:
            pass
        except Exception as e:
            error_type = type(e).__name__
            # Don't print scary traceback for common network errors
            if any(x in error_type for x in ['SSLError', 'ConnectionError', 'Timeout', 'ProxyError', 'HTTPError']):
                print(f"[NETWORK ERROR] {error_type}: Skipping video due to connection issue")
            elif 'RequestBlocked' in error_type or 'IpBlocked' in error_type:
                # Don't print long message for IP blocking - already handled
                print(f"[IP BLOCKED] Video skipped after all retry attempts")
            else:
                # Only show first line of error
                error_msg = str(e).split('\n')[0][:100]
                print(f"[OUTER EXCEPTION] {error_type}: {error_msg}")
                # Only print traceback for unexpected errors if flag is set
                if Arguments().save_error_data:
                    tb = traceback.extract_tb(sys.exc_info()[2])
                    trace = traceback.format_list(tb)
                    print('---- traceback ----')
                    for line in trace:
                        if '~^~' in line:
                            print(line.rstrip())
                        else:
                            text = re.sub(r'\n\s*', ' ', line.rstrip())
                            print(text)
                    print('-------------------')
        finally:
            clear_tasks()
            return is_complete

    def videos(self, video_ids):
        for i, video_id in enumerate(video_ids):
            if '[' in video_id or ']' in video_id:
                video_id = video_id.replace('[', '').replace(']', '')

            # Retry logic for IP blocked and outer exceptions
            max_retries = 3
            for retry_attempt in range(max_retries):
                try:
                    video = self.get_info(video_id)
                    if video.get("error"):
                        print("The video id is invalid :", video_id)
                        break  # Don't retry for invalid video IDs
                    splitter_string = f"\n{'-'*10} video:{i+1} of {min(len(video_ids),Arguments().first)} {'-'*10}"
                    ret = self.video(video,splitter_string)
                    if ret == 'skip':
                        break  # Don't retry for skipped videos

                    if ret == "KeyboardInterrupt":
                        self.cancel()
                        return

                    # Success - break retry loop
                    break

                except InvalidVideoIdException:
                    print(f"Invalid video id: {video_id}")
                    break  # Don't retry for invalid IDs
                except UnknownConnectionError:
                    print(f"Network Error has occured during processing:[{video_id}]")
                    break  # Don't retry for network errors
                except Exception as e:
                    error_type = str(type(e).__name__)
                    error_msg = str(e)

                    # Check if it's an IP blocked or retryable error
                    is_ip_blocked = "IpBlocked" in error_type or "RequestBlocked" in error_type
                    is_retryable = is_ip_blocked or "OUTER EXCEPTION" in error_msg

                    if is_retryable and retry_attempt < max_retries - 1:
                        print(f"[ERROR] {error_type}: {error_msg}")
                        print(f"[RETRY] Waiting 5 seconds before retry (attempt {retry_attempt + 2}/{max_retries})...")
                        import time
                        time.sleep(5)
                        # Force new session/IP for next attempt
                        continue
                    else:
                        # Last retry failed or non-retryable error
                        print("[OUTER EXCEPTION]" + str(type(e)), str(e))
                        break

    def channels(self, channels, tabs):
        if tabs is None:
            tabs = SECTION_GROUP
        else:
            tabs = [tabs]

        for i, ch in enumerate(channels):
            counter = 0  # Total counter across all sections
            channel_id = channel.get_channel_id(ch)
            processed_video_ids = set()  # Track processed video IDs to avoid duplicates

            for tab in tabs:
                # Get ALL videos from this section first
                all_videos_in_section = list(channel.get_videos(channel_id, tab=tab))

                for video in all_videos_in_section:
                    if counter >= Arguments().first:
                        break

                    # Skip if we already processed this video ID
                    video_id = video.get('id')
                    if video_id in processed_video_ids:
                        continue
                    processed_video_ids.add(video_id)

                    splitter_string = f"\n{'-'*10} channel: {i+1} of {len(channels)} / section: {tab} / video: {counter+1} of {Arguments().first} {'-'*10}"
                    ret = self.video(video, splitter_string)
                    if ret == 'skip':
                        continue
                    if ret == "KeyboardInterrupt":
                        self.cancel()
                        return
                    if ret:
                        counter += 1

    def playlist_ids(self, playlist_ids):
        stop=False
        for i, playlist_id in enumerate(playlist_ids):
            counter = 0
            page = 1
            video_list, num_pages, metadata = playlist.get_playlist_page_cli(playlist_id, page=str(page))

            while True:
                for video in video_list:
                    if counter > Arguments().first - 1:
                        stop=True
                        break
                    splitter_string = f"\n{'-'*10} playlist: {i+1} of {len(playlist_ids)} / video: {counter+1} of {Arguments().first} {'-'*10}"
                    ret = self.video(video, splitter_string)
                    if ret == 'skip':
                        continue
                    if ret == "KeyboardInterrupt":
                        self.cancel()
                        return
                    if ret:
                        counter += 1
                page += 1
                if stop or page > num_pages:
                    break
                video_list, num_pages, metadata = playlist.get_playlist_page_cli(playlist_id, page=str(page))

    def cancel(self, ex=None, pbar=None):
        '''Called when keyboard interrupted has occurred.
        '''
        print("\nKeyboard interrupted.\n")
        if ex:
            ex.cancel()
        if pbar:
            pbar.cancel()
        exit(0)

    def get_info(self, video_id):
        video = dict()
        for i in range(3):
            try:
                info = VideoInfo(video_id)
                break
            except PatternUnmatchError:
                time.sleep(2)
                continue
            except Exception as e:
                print("[OUTER EXCEPTION]" + str(type(e)), str(e))
                return {"error": True}    
        else:
            print(f"PatternUnmatchError:{video_id}")
            video['id'] = ""
            video['author'] = ""
            video['time_published'] = ""
            video['title'] = ""
            video['duration'] = ""
            video['error'] = True
            return video

        video['id'] = video_id
        video['author'] = str(info.get_channel_name())

        # Get published date
        published_date = info.get_published_date()
        video['time_published'] = published_date if published_date else "Unknown"

        video['title'] = str(info.get_title())

        # Convert duration from seconds to M:SS format
        duration_seconds = info.get_duration()
        if duration_seconds == 'LIVE':
            video['duration'] = 'LIVE'
        elif duration_seconds == 'UPCOMING':
            video['duration'] = 'UPCOMING'
        elif duration_seconds and duration_seconds > 0:
            hours = duration_seconds // 3600
            minutes = (duration_seconds % 3600) // 60
            seconds = duration_seconds % 60
            if hours > 0:
                video['duration'] = f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                video['duration'] = f"{minutes}:{seconds:02d}"
        else:
            video['duration'] = str(duration_seconds)

        return video
    
def clear_tasks():
    pass
