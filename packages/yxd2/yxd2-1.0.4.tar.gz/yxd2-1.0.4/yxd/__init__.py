import argparse
import os
import sys
from .arguments import Arguments
from .downloader import Downloader
from .settings2 import Settings
from .youtube import api
from pathlib import Path
from .youtube import util
try:
    from asyncio import CancelledError
except ImportError:
    from asyncio.futures import CancelledError

# Fix console encoding for Windows to support Unicode characters
if sys.platform == 'win32':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except:
        pass
'''
Most of CLI modules refer to
Petter Kraabøl's Twitch-Chat-Downloader
https://github.com/PetterKraabol/Twitch-Chat-Downloader
(MIT License)

WebShare Proxy Integration for IP Block Avoidance
==================================================

This tool now supports WebShare residential proxies to avoid YouTube IP blocking.

SETUP (One-time):
1. Create account at https://www.webshare.io
2. Purchase a "Residential Proxy" package (NOT "Proxy Server" or "Static Residential")
3. Get your credentials from https://dashboard.webshare.io/proxy/settings
4. Save credentials to yxd (run once):

   yxd -v VIDEO_ID --proxy-enabled --proxy-username YOUR_USERNAME --proxy-password YOUR_PASSWORD

USAGE:
Once credentials are saved, simply use --proxy-enabled:

   yxd -v VIDEO_ID --proxy-enabled
   yxd -c CHANNEL_URL --first 10 --proxy-enabled

BANDWIDTH OPTIMIZATION:
- Uses HTTP (port 80) instead of HTTPS to minimize bandwidth
- Automatically retries with new IP if blocked (10 retries)
- Prevents connection keep-alive for proper IP rotation
- Location filtering to reduce latency (optional):

  yxd -v VIDEO_ID --proxy-enabled --proxy-location "US,CA"

BENEFITS:
- Bypasses YouTube IP blocking
- Automatic IP rotation on each request
- Large residential IP pool reduces ban risk
- 2-4 second delays between videos still applied
- Minimal bandwidth usage optimization

See https://github.com/jdepoix/youtube-transcript-api#working-around-ip-bans

'''

__copyright__ = 'Copyright (C) 2020-2024 vb'
__version__ = '0.4.1'
__license__ = 'AGPLv3'
__author__ = 'vb'
__author_email__ = 'i@s.biz'
__url__ = "http://example.com"


def main():

    parser = argparse.ArgumentParser(description=f'yxd v{__version__}')
    parser.add_argument('-v', f'--{Arguments.Name.VIDEO}', type=str,
                        help='Video ID (or URL that includes Video ID).'
                        'You can specify multiple video IDs by '
                        'separating them with commas without spaces.\n'
                        'If ID starts with a hyphen (-), enclose the ID in square brackets.')
    parser.add_argument('-a', f'--{Arguments.Name.BATCH_FILE.replace("_", "-")}', type=str,
                        help='File containing video URLs or IDs (one per line)')
    parser.add_argument('-c', f'--{Arguments.Name.CHANNEL}', type=str,
                        help='Channel ID (or URL of channel page)')
    parser.add_argument('-f', f'--{Arguments.Name.FIRST}', type=int,
                        default=1000, help='Download chat from the last n VODs')
    parser.add_argument('-o', f'--{Arguments.Name.OUTPUT}', type=str,
                        help='Output directory (end with "/"). default="./"', default='./')
    parser.add_argument('-p', f'--{Arguments.Name.PLAYLIST}', type=str,
                        help='Playlist ID ("PL-")')
    parser.add_argument('-l',  f'--{Arguments.Name.LINK_TO_SECTION}', type=str,
                        help='Specify a link to a section of the channel page. Option: "streams", "videos", "shorts", "playlists".If omitted, data in all sections are covered.')
    parser.add_argument('-e', f'--{Arguments.Name.SAVE_ERROR_DATA}', action='store_true',
                        help='Save error data when error occurs(".dat" file)')
    parser.add_argument('-s', f'--{Arguments.Name.SKIP_DUPLICATE}', action='store_true',
                        help='Skip already extracted videos. This option is valid only when `-o` option is specified.')
    parser.add_argument(f'--{Arguments.Name.API_KEY.replace("_", "-")}', type=str, help='YouTube API key')
    parser.add_argument(f'--{Arguments.Name.SET_API}', action='store_true',
                        help='Set new API key')
    parser.add_argument(f'--{Arguments.Name.SETTINGS}', action='store_true', help='Print settings file location')
    parser.add_argument(f'--{Arguments.Name.SETTINGS_FILE.replace("_", "-")}', type=str,
                        # default=str(Path.home()) + '/.config/ycd/settings.json',
                        default=str(Path.home()) + '/.config/ycd/settings.json',
                        help='Use a custom settings file')
    parser.add_argument(f'--{Arguments.Name.LOG}', action='store_true', help='Save log file')
    parser.add_argument(f'--{Arguments.Name.VERSION}', action='store_true',
                        help='Show version')
    # Proxy arguments (WebShare and DataImpulse) - ENABLED BY DEFAULT
    parser.add_argument(f'--{Arguments.Name.PROXY_PROVIDER.replace("_", "-")}', type=str,
                        default='dataimpulse', choices=['webshare', 'dataimpulse'],
                        help='Proxy provider to use: "webshare" or "dataimpulse" (default: dataimpulse)')
    parser.add_argument(f'--{Arguments.Name.PROXY_ENABLED.replace("_", "-")}', action='store_true',
                        default=True,
                        help='Enable residential proxy (enabled by default)')
    parser.add_argument('--no-proxy', action='store_true',
                        help='Disable proxy')
    parser.add_argument(f'--{Arguments.Name.PROXY_USERNAME.replace("_", "-")}', type=str,
                        help='Proxy username (WebShare or DataImpulse, stored in settings if provided)')
    parser.add_argument(f'--{Arguments.Name.PROXY_PASSWORD.replace("_", "-")}', type=str,
                        help='Proxy password (WebShare or DataImpulse, stored in settings if provided)')
    parser.add_argument(f'--{Arguments.Name.PROXY_LOCATION.replace("_", "-")}', type=str,
                        help='Proxy location filter (e.g., "US,CA,GB" for USA, Canada, UK)')
    parser.add_argument(f'--{Arguments.Name.PROXY_API_KEY.replace("_", "-")}', type=str,
                        help='WebShare API key for bandwidth tracking (get from https://proxy.webshare.io/userapi/keys/)')
    # DataImpulse specific arguments
    parser.add_argument(f'--{Arguments.Name.DATAIMPULSE_USERNAME.replace("_", "-")}', type=str,
                        help='DataImpulse proxy username (stored in settings if provided)')
    parser.add_argument(f'--{Arguments.Name.DATAIMPULSE_PASSWORD.replace("_", "-")}', type=str,
                        help='DataImpulse proxy password (stored in settings if provided)')
    parser.add_argument(f'--{Arguments.Name.DATAIMPULSE_LOCATION.replace("_", "-")}', type=str,
                        help='DataImpulse proxy location filter (e.g., "US,CA,GB")')
    parser.add_argument(f'--{Arguments.Name.COOKIES}', type=str,
                        help='Path to cookies file (Netscape format) for accessing Members Only content')
    parsed_args = parser.parse_args()
    args_dict = parsed_args.__dict__

    # Handle --no-proxy flag
    if args_dict.get('no_proxy'):
        args_dict[Arguments.Name.PROXY_ENABLED] = False

    Arguments(args_dict)

    Settings(Arguments().settings_file,
             reference_filepath=f'{os.path.dirname(os.path.abspath(__file__))}/settings.reference.json.py')

    if not Settings().config.get('EULA', None) or not Settings().config.get('EULA', None) == 'agreed':
        print()
        print("!!CAUTION!!\n"
        "The use of this tool is at your own risk.\n"
        "The author of this program is not responsible for any damage \n"
        "caused by this tool or bugs or specifications\n"
        "or other incidental actions.\n"
        "You will be deemed to have agreed to the items listed in the LICENSE.\n"
        "Type `yes` if you agree with the above.\n")
        while True:
            ans = input()
            if ans == 'yes':
                Settings().config['EULA'] = "agreed"
                Settings().save()
                break
            elif ans == "":
                continue
            else:
                return

    # Print version
    if Arguments().print_version:
        print(f'v{__version__}')
        return

    # set api key
    if Arguments().set_api:
        if Settings().config.get('api_key', None):
            loop = True
            while loop:
                print(f"Change API Key:\n   [current key] {Settings().config.get('api_key', None)}")
                typed_apikey = ""
                while typed_apikey == "":
                    typed_apikey = input(f"Type new API Key:").strip()
                t= ""
                while not t:
                    t = input("Change OK? (y/n) ")
                    if t == "Y" or t == "y":
                        if api.check_validation(typed_apikey):
                            Settings().config['api_key'] = typed_apikey
                            Settings().save()
                            print("Changed the API key.")
                            loop = False
                            break
                        else:
                            print("[Error!] The entered API key is NOT valid or exceeds quota limit. Please try again or enter other key.\n")
                            q = input("...press any key to continue. (or press 'q' to quit)...")
                            if q == "Q" or q == "q":
                                loop = False
                                break
                    elif t == "N" or t == "n":
                        loop = False
                        break
                    else:
                        t = ""
        return


    if Arguments().api_key or Settings().config.get('api_key', None):
        Settings().config['api_key'] = Arguments().api_key or Settings().config.get('api_key', None)
    else:
        for i in range(3):
            typed_apikey = input('Enter YouTube API key: ').strip()
            if api.check_validation(typed_apikey):
                print("Confirmed the entered YouTube API key.")
                Settings().config['api_key'] = typed_apikey
                break
            print("The entered API key is NOT valid or exceeds quota limit. Please try again or enter other key.")
            print(f"--number of attempts:{3-i-1} remaining--")
            print()
        else:
            print("Unable to determine the valid YouTube API key, or you have exceeded the available quota.")
            print("(CANNOT support any inquiries about the YouTube API.)")
            return

    # Handle proxy setup with interactive prompt if needed
    if Arguments().proxy_enabled:
        # Save proxy provider to settings
        if Arguments().proxy_provider:
            Settings().config['proxy_provider'] = Arguments().proxy_provider
        elif Settings().config.get('proxy_provider'):
            Arguments().proxy_provider = Settings().config.get('proxy_provider')
        else:
            Arguments().proxy_provider = 'webshare'  # Default

        # Set default location if not specified
        if not Arguments().proxy_location and not Settings().config.get('proxy_location'):
            Arguments().proxy_location = "FI,EE,SE,LV,NO,DK"
            Settings().config['proxy_location'] = "FI,EE,SE,LV,NO,DK"

        # Handle API key for bandwidth tracking (WebShare only)
        if Arguments().proxy_api_key:
            Settings().config['proxy_api_key'] = Arguments().proxy_api_key
        elif Settings().config.get('proxy_api_key'):
            Arguments().proxy_api_key = Settings().config.get('proxy_api_key')

        # Handle DataImpulse specific credentials
        if Arguments().proxy_provider == 'dataimpulse':
            # Check if DataImpulse credentials are provided via CLI
            if Arguments().dataimpulse_username and Arguments().dataimpulse_password:
                Settings().config['dataimpulse_username'] = Arguments().dataimpulse_username
                Settings().config['dataimpulse_password'] = Arguments().dataimpulse_password
                if Arguments().dataimpulse_location:
                    Settings().config['dataimpulse_location'] = Arguments().dataimpulse_location
            # Check if credentials exist in settings
            elif Settings().config.get('dataimpulse_username') and Settings().config.get('dataimpulse_password'):
                Arguments().dataimpulse_username = Settings().config.get('dataimpulse_username')
                Arguments().dataimpulse_password = Settings().config.get('dataimpulse_password')
                if not Arguments().dataimpulse_location and Settings().config.get('dataimpulse_location'):
                    Arguments().dataimpulse_location = Settings().config.get('dataimpulse_location')
            # No credentials found - prompt user interactively
            else:
                print("\n" + "="*70)
                print("DataImpulse Proxy Setup Required")
                print("="*70)
                print("\nTo avoid YouTube IP blocking, yxd can use DataImpulse residential proxies.")
                print("\nIf you don't have a DataImpulse account yet:")
                print("  1. Sign up at: https://dataimpulse.com")
                print("  2. Purchase a residential proxy package")
                print("  3. Get your credentials from your DataImpulse dashboard")
                print("\nYour credentials will be saved securely for future use.")
                print("="*70 + "\n")

                # Prompt for username
                proxy_username = ""
                while not proxy_username:
                    proxy_username = input("Enter DataImpulse Proxy Username: ").strip()
                    if not proxy_username:
                        print("Username cannot be empty. Please try again.")

                # Prompt for password
                proxy_password = ""
                while not proxy_password:
                    proxy_password = input("Enter DataImpulse Proxy Password: ").strip()
                    if not proxy_password:
                        print("Password cannot be empty. Please try again.")

                # Set default location filter to Finland and closest countries
                proxy_location = "FI,EE,SE,LV,NO,DK"
                print("\n[Default] Proxy locations set to Finland and nearby countries:")
                print("  FI (Finland), EE (Estonia), SE (Sweden), LV (Latvia), NO (Norway), DK (Denmark)")
                print("  This minimizes latency and bandwidth usage.")

                # Save to settings
                Arguments().dataimpulse_username = proxy_username
                Arguments().dataimpulse_password = proxy_password
                if proxy_location:
                    Arguments().dataimpulse_location = proxy_location
                    Settings().config['dataimpulse_location'] = proxy_location

                Settings().config['dataimpulse_username'] = proxy_username
                Settings().config['dataimpulse_password'] = proxy_password

                print("\n" + "="*70)
                print("✅ DataImpulse credentials saved successfully!")
                print("   They will be automatically used in future runs with --proxy-enabled --proxy-provider dataimpulse")
                print("="*70 + "\n")
        else:
            # WebShare proxy handling (default)
            # Check if credentials are provided via CLI
            if Arguments().proxy_username and Arguments().proxy_password:
                Settings().config['proxy_username'] = Arguments().proxy_username
                Settings().config['proxy_password'] = Arguments().proxy_password
            # Check if credentials exist in settings
            elif Settings().config.get('proxy_username') and Settings().config.get('proxy_password'):
                # Load from settings
                Arguments().proxy_username = Settings().config.get('proxy_username')
                Arguments().proxy_password = Settings().config.get('proxy_password')
                if not Arguments().proxy_location and Settings().config.get('proxy_location'):
                    Arguments().proxy_location = Settings().config.get('proxy_location')
            # No credentials found - prompt user interactively
            else:
                print("\n" + "="*70)
                print("WebShare Proxy Setup Required")
                print("="*70)
                print("\nTo avoid YouTube IP blocking, yxd can use WebShare residential proxies.")
                print("\nIf you don't have a WebShare account yet:")
                print("  1. Sign up at: https://www.webshare.io")
                print("  2. Purchase a 'Residential Proxy' package")
                print("  3. Get your credentials from: https://dashboard.webshare.io/proxy/settings")
                print("\nYour credentials will be saved securely for future use.")
                print("="*70 + "\n")

                # Prompt for username
                proxy_username = ""
                while not proxy_username:
                    proxy_username = input("Enter WebShare Proxy Username: ").strip()
                    if not proxy_username:
                        print("Username cannot be empty. Please try again.")

                # Prompt for password
                proxy_password = ""
                while not proxy_password:
                    proxy_password = input("Enter WebShare Proxy Password: ").strip()
                    if not proxy_password:
                        print("Password cannot be empty. Please try again.")

                # Set default location filter to Finland and closest countries
                proxy_location = "FI,EE,SE,LV,NO,DK"  # Finland + 5 closest countries
                print("\n[Default] Proxy locations set to Finland and nearby countries:")
                print("  FI (Finland), EE (Estonia), SE (Sweden), LV (Latvia), NO (Norway), DK (Denmark)")
                print("  This minimizes latency and bandwidth usage.")

                # Save to settings
                Arguments().proxy_username = proxy_username
                Arguments().proxy_password = proxy_password
                if proxy_location:
                    Arguments().proxy_location = proxy_location
                    Settings().config['proxy_location'] = proxy_location

                Settings().config['proxy_username'] = proxy_username
                Settings().config['proxy_password'] = proxy_password

                print("\n" + "="*70)
                print("✅ WebShare credentials saved successfully!")
                print("   They will be automatically used in future runs with --proxy-enabled")
                print("="*70 + "\n")

    # Load saved proxy credentials even if not using proxy (for display purposes)
    elif Settings().config.get('proxy_username') and Settings().config.get('proxy_password'):
        if not Arguments().proxy_username:
            Arguments().proxy_username = Settings().config.get('proxy_username')
        if not Arguments().proxy_password:
            Arguments().proxy_password = Settings().config.get('proxy_password')

    Settings().save()
    # Scan folder
    dir_videos = set()
    if Arguments().output:
        path = Arguments().output
    else:
        path = "./"
    if not os.path.exists(path):
        print(f"Directory not found:{path}")
        return
    if Arguments().skip_duplicate:
        print("Scanning output dirctory...")
        dir_videos.update([f[:11] for f in os.listdir(
            path) if os.path.isfile(os.path.join(path, f)) and f[-5:]=='.html'] )

    # Extract
    if Arguments().video_ids or Arguments().channels or Arguments().playlist_ids:
        try:
            # Create single downloader instance to track total videos across all operations
            downloader = Downloader(dir_videos)

            if Arguments().video_ids:
                downloader.videos(Arguments().video_ids)

            if Arguments().channels:
                if Arguments().link_to_section:
                    arg = str.lower(Arguments().link_to_section)
                    if not arg in ( "streams","shorts","videos","playlists"):
                        print("Error:\n The argument `-l (--link_to_section)` must be one of the following strings:\n"
                              ' "streams" / "videos" / "shorts" /  "playlists"\n')
                        return
                downloader.channels(Arguments().channels,tabs=Arguments().link_to_section)

            if Arguments().playlist_ids:
                downloader.playlist_ids(Arguments().playlist_ids)

            # Final stats disabled - too verbose
            # if Arguments().proxy_enabled:
            #     print(f"\n{'='*70}")
            #     print(f"All downloads complete! Total: {downloader._completed_videos} videos")
            #     print(f"Session bandwidth used: {downloader._session_bandwidth_mb:.2f} MB ({downloader._session_bandwidth_mb / 1024:.3f} GB)")
            #     print(f"{'='*70}\n")

            return
        except CancelledError:
            print('Cancelled')
            return
        except util.FetchError as e:
            print(e)
            print('Error:The specified Channel_ID or Playlist_ID may not exist.')
    else:
        parser.print_help()    
