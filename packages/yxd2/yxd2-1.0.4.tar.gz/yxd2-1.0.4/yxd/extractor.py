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
from youtube_transcript_api.proxies import WebshareProxyConfig
# Import IP blocking errors
try:
    from youtube_transcript_api._errors import IpBlocked, RequestBlocked
except ImportError:
    # Fallback if these classes don't exist in older versions
    class IpBlocked(Exception):
        pass
    class RequestBlocked(Exception):
        pass

import time
import random
import requests
from .arguments import Arguments


class Extractor:
    def __init__(self, videi_id, callback=None):
        self.video_id = videi_id
        self.callback = callback
        self._proxy_config = None
        self._http_session = None
        self._setup_proxy()
        self._setup_http_session()

    def _setup_proxy(self):
        """Setup proxy if credentials are provided (WebShare or DataImpulse)"""
        args = Arguments()

        if not args.proxy_enabled:
            return

        # Determine which proxy provider to use
        if args.proxy_provider == 'dataimpulse':
            # Use DataImpulse credentials if provided, otherwise fall back to generic
            username = args.dataimpulse_username or args.proxy_username
            password = args.dataimpulse_password or args.proxy_password

            if username and password:
                # DataImpulse proxy - location filtering managed in dashboard
                # DON'T set session.proxies - let it read from environment for rotation
                import os
                proxy_url = f'http://{username}:{password}@gw.dataimpulse.com:823'
                os.environ['HTTP_PROXY'] = proxy_url
                os.environ['HTTPS_PROXY'] = proxy_url
                self._using_env_proxy = True
        else:
            # Default to WebShare
            if args.proxy_username and args.proxy_password:
                # Parse location filter if provided (e.g., "US,CA,GB")
                locations = None
                if args.proxy_location:
                    locations = [loc.strip().upper() for loc in args.proxy_location.split(',')]

                self._proxy_config = WebshareProxyConfig(
                    proxy_username=args.proxy_username,
                    proxy_password=args.proxy_password,
                    filter_ip_locations=locations,
                    retries_when_blocked=10,  # Retry 10 times with different IPs
                    domain_name='p.webshare.io',
                    proxy_port=80  # Use port 80 for minimal bandwidth (HTTP)
                )

    def _setup_http_session(self):
        """Setup optimized HTTP session for minimal bandwidth usage"""
        # Initialize bandwidth tracking
        self._bytes_sent = 0
        self._bytes_received = 0
        self._request_count = 0
        self._response_sizes = []

        if self._proxy_config or hasattr(self, '_using_env_proxy'):
            session = requests.Session()

            # DON'T set session.proxies for env proxy - requests will read from env vars
            # This allows rotation to work properly

            # Speed optimizations - keep-alive for faster connections
            session.headers.update({
                'Accept-Encoding': 'gzip, deflate',  # Enable compression
                'Connection': 'keep-alive',  # Keep connections open for speed
                'User-Agent': 'Mozilla/5.0',
            })

            # Faster connection pooling
            adapter = requests.adapters.HTTPAdapter(
                pool_connections=10,
                pool_maxsize=20,
                max_retries=0
            )
            session.mount('http://', adapter)
            session.mount('https://', adapter)

            # Add response hooks to track bandwidth
            original_send = session.send
            def tracking_send(request, **kwargs):
                self._request_count += 1

                # Track sent data (headers + body)
                sent_bytes = 0
                if request.body:
                    sent_bytes += len(request.body)
                # Estimate header size
                header_size = sum(len(k) + len(v) + 4 for k, v in request.headers.items())
                sent_bytes += header_size + len(request.method) + len(request.url) + 20
                self._bytes_sent += sent_bytes

                response = original_send(request, **kwargs)

                # Track received data
                received_bytes = 0
                if hasattr(response, 'content'):
                    received_bytes = len(response.content)
                    self._bytes_received += received_bytes
                    self._response_sizes.append(received_bytes)
                # Estimate response headers
                resp_header_size = sum(len(k) + len(v) + 4 for k, v in response.headers.items())
                self._bytes_received += resp_header_size + 20

                return response

            session.send = tracking_send
            self._http_session = session

    def extract(self) -> dict:
        # When using proxy, retries are handled by WebshareProxyConfig (10 retries)
        # For DataImpulse/env proxy, we handle retries manually
        max_retries = 1 if self._proxy_config else (10 if hasattr(self, '_using_env_proxy') else 3)

        for attempt in range(max_retries):
            # Create NEW session for each retry to force proxy rotation
            session_for_retry = None
            if hasattr(self, '_using_env_proxy'):
                import requests
                session_for_retry = requests.Session()
                # Session will pick up HTTP_PROXY/HTTPS_PROXY from environment
                session_for_retry.headers.update({
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'User-Agent': 'Mozilla/5.0',
                })

            try:
                # Create NEW API instance for each retry
                if self._proxy_config:
                    # WebShare with proxy config
                    api = Api(proxy_config=self._proxy_config, http_client=self._http_session)
                elif hasattr(self, '_using_env_proxy'):
                    # DataImpulse - create NEW session for this retry
                    api = Api(http_client=session_for_retry)
                else:
                    # No proxy
                    api = Api()
                transcript_list = api.list(video_id = self.video_id)
                for transcript in transcript_list:
                    result = transcript.fetch().snippets
                    # Close session after success
                    if session_for_retry:
                        session_for_retry.close()
                    return result

            except (IpBlocked, RequestBlocked) as err:
                # Close session to force new connection
                if session_for_retry:
                    try:
                        session_for_retry.close()
                    except:
                        pass

                # IP blocked - retry with new proxy
                if attempt < max_retries - 1:
                    wait_time = 1.0 + (attempt * 0.5)  # Longer wait: 1s, 1.5s, 2s, 2.5s...
                    print(f"IP blocked. Retrying with new proxy in {wait_time:.1f}s...")
                    time.sleep(wait_time)
                    continue  # Try next attempt with new IP
                else:
                    # Last attempt failed - raise to downloader for retry with delay
                    raise

            except (TranscriptsDisabled,
                    NoTranscriptFound,
                    CouldNotRetrieveTranscript,
                    VideoUnavailable,
                    NotTranslatable,
                    TranslationLanguageNotAvailable) as err:
                # These are not retryable errors - video doesn't have transcripts
                print(err.__class__)
                print("Transcripts unavailable.")
                return [{"error": 1}]

            except Exception as err:
                # Always close session on error
                if session_for_retry:
                    try:
                        session_for_retry.close()
                    except:
                        pass

                error_msg = str(err)
                error_type = type(err).__name__

                # Network/connection errors - always retry with new proxy
                if any(x in error_type for x in ['SSLError', 'ConnectionError', 'Timeout', 'ProxyError', 'HTTPError']):
                    if attempt < max_retries - 1:
                        wait_time = 1.0 + (attempt * 0.5)
                        print(f"Network error ({error_type}). Retrying with new proxy in {wait_time:.1f}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        # Last retry failed - skip this video
                        print(f"[NETWORK ERROR] Failed after {max_retries} attempts: {error_type}")
                        return [{"error": 3}]

                # IP blocking errors
                elif "429" in error_msg or "Too Many Requests" in error_msg or "blocked" in error_msg.lower():
                    if attempt < max_retries - 1:
                        wait_time = 1.0 + (attempt * 0.5)
                        print(f"Rate limited or blocked. Retrying in {wait_time:.1f}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print("[IP BLOCKED] Failed after retries")
                        return [{"error": 2}]

                # Any other error - retry anyway (might be transient)
                else:
                    if attempt < max_retries - 1:
                        wait_time = 1.0 + (attempt * 0.5)
                        print(f"[OUTER EXCEPTION] {error_type}: {str(err)[:60]}. Retrying in {wait_time:.1f}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        # Give up after all retries
                        print(f"[OUTER EXCEPTION] {error_type}: {str(err)[:80]}")
                        return [{"error": 3}]

        return [{"error": 3}]

    def get_bandwidth_stats(self):
        """Return bandwidth usage statistics in KB"""
        total_kb = (self._bytes_sent + self._bytes_received) / 1024
        sent_kb = self._bytes_sent / 1024
        received_kb = self._bytes_received / 1024

        # Calculate actual data vs overhead
        actual_data_kb = sum(self._response_sizes) / 1024
        overhead_kb = received_kb - actual_data_kb

        return {
            'total_kb': round(total_kb, 2),
            'sent_kb': round(sent_kb, 2),
            'received_kb': round(received_kb, 2),
            'actual_data_kb': round(actual_data_kb, 2),
            'overhead_kb': round(overhead_kb, 2),
            'request_count': self._request_count,
            'avg_response_kb': round(actual_data_kb / self._request_count, 2) if self._request_count > 0 else 0
        }

    def cancel(self):
        pass
