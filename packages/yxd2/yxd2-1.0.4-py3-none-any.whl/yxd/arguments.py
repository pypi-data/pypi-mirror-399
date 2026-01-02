from typing import Optional, Dict, Union, List
from .singleton import Singleton

'''
This modules refer to
Petter Kraabøl's Twitch-Chat-Downloader
https://github.com/PetterKraabol/Twitch-Chat-Downloader
(MIT License)
'''


class Arguments(metaclass=Singleton):
    """
    Arguments singleton
    """

    class Name:
        SETTINGS_FILE: str = 'settings_file'
        SETTINGS: str = 'settings'
        LOG: str = 'log'
        VERSION: str = 'version'
        OUTPUT: str = 'output_dir'
        VIDEO: str = 'video_id'
        BATCH_FILE: str = 'batch_file'
        SAVE_ERROR_DATA: bool = 'save_error_data'
        CHANNEL: str = 'channel'
        FIRST: str = 'first'
        SKIP_DUPLICATE: bool = 'skip_duplicate'
        API_KEY: str = 'api_key'
        PLAYLIST: str = 'playlist_id'
        SET_API: str = 'set_api'
        LINK_TO_SECTION: str = 'link_to_section'
        # Proxy settings
        PROXY_PROVIDER: str = 'proxy_provider'  # 'webshare' or 'dataimpulse'
        PROXY_USERNAME: str = 'proxy_username'
        PROXY_PASSWORD: str = 'proxy_password'
        PROXY_ENABLED: bool = 'proxy_enabled'
        PROXY_LOCATION: str = 'proxy_location'
        PROXY_API_KEY: str = 'proxy_api_key'
        # DataImpulse specific settings
        DATAIMPULSE_USERNAME: str = 'dataimpulse_username'
        DATAIMPULSE_PASSWORD: str = 'dataimpulse_password'
        DATAIMPULSE_LOCATION: str = 'dataimpulse_location'
        # Cookie file for authentication
        COOKIES: str = 'cookies'

    def __init__(self,
                 arguments: Optional[Dict[str, Union[str, bool, int]]] = None):
        """
        Initialize arguments
        :param arguments: Arguments from cli
        (Optional to call singleton instance without parameters)
        """

        if arguments is None:
            print('Error: arguments were not provided')
            exit()

        self.settings_file: str = arguments[Arguments.Name.SETTINGS_FILE]
        self.settings: str = arguments[Arguments.Name.SETTINGS]
        self.print_version: bool = arguments[Arguments.Name.VERSION]
        self.output: str = arguments[Arguments.Name.OUTPUT]
        if not (self.output.endswith('\\') or self.output.endswith('/')):
            self.output += '/'
        self.video_ids: List[int] = []
        self.channels: List[int] = []
        self.playlist_ids: List[int] = []
        self.save_error_data: bool = arguments[Arguments.Name.SAVE_ERROR_DATA]
        self.first: Optional[int] = arguments[Arguments.Name.FIRST]
        self.skip_duplicate: bool = arguments[Arguments.Name.SKIP_DUPLICATE]
        self.log: bool = arguments[Arguments.Name.LOG]
        self.link_to_section: str = arguments[Arguments.Name.LINK_TO_SECTION]
        # Optional or prompted arguments
        self.api_key: Optional[str] = arguments[Arguments.Name.API_KEY]
        self.set_api: Optional[str] = arguments[Arguments.Name.SET_API]
        # Proxy settings - ENABLED BY DEFAULT with DataImpulse
        self.proxy_provider: str = arguments.get(Arguments.Name.PROXY_PROVIDER, 'dataimpulse')  # Default: dataimpulse
        self.proxy_username: Optional[str] = arguments.get(Arguments.Name.PROXY_USERNAME)
        self.proxy_password: Optional[str] = arguments.get(Arguments.Name.PROXY_PASSWORD)
        self.proxy_enabled: bool = arguments.get(Arguments.Name.PROXY_ENABLED, True)  # Default: True (ENABLED)
        self.proxy_location: Optional[str] = arguments.get(Arguments.Name.PROXY_LOCATION)
        self.proxy_api_key: Optional[str] = arguments.get(Arguments.Name.PROXY_API_KEY)
        # DataImpulse specific settings
        self.dataimpulse_username: Optional[str] = arguments.get(Arguments.Name.DATAIMPULSE_USERNAME)
        self.dataimpulse_password: Optional[str] = arguments.get(Arguments.Name.DATAIMPULSE_PASSWORD)
        self.dataimpulse_location: Optional[str] = arguments.get(Arguments.Name.DATAIMPULSE_LOCATION)
        # Cookie file for authentication
        self.cookies: Optional[str] = arguments.get(Arguments.Name.COOKIES)
        # Videos
        if arguments[Arguments.Name.VIDEO]:
            self.video_ids = arguments[Arguments.Name.VIDEO].split(',')

        # Batch file - read video IDs from file
        if arguments.get(Arguments.Name.BATCH_FILE):
            batch_file = arguments[Arguments.Name.BATCH_FILE]
            try:
                with open(batch_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        # Extract video ID from URL or use as-is
                        if 'youtube.com/watch?v=' in line:
                            video_id = line.split('watch?v=')[1].split('&')[0]
                        elif 'youtu.be/' in line:
                            video_id = line.split('youtu.be/')[1].split('?')[0]
                        else:
                            video_id = line
                        if video_id and video_id not in self.video_ids:
                            self.video_ids.append(video_id)
                print(f"Loaded {len(self.video_ids)} video IDs from {batch_file}")
            except FileNotFoundError:
                print(f"Error: Batch file not found: {batch_file}")
                exit(1)
            except Exception as e:
                print(f"Error reading batch file: {e}")
                exit(1)

        if arguments[Arguments.Name.CHANNEL]:
            self.channels = arguments[Arguments.Name.CHANNEL].split(',')

        if arguments[Arguments.Name.PLAYLIST]:
            self.playlist_ids = arguments[Arguments.Name.PLAYLIST].split(',')
