import requests
from .arguments import Arguments


def get_webshare_quota():
    """
    Fetch WebShare bandwidth usage and quota from API.
    Returns dict with usage info or None if API key not set or request fails.
    """
    args = Arguments()

    if not args.proxy_api_key:
        return None

    try:
        headers = {
            'Authorization': f'Token {args.proxy_api_key}'
        }

        # Fetch bandwidth statistics
        response = requests.get(
            'https://proxy.webshare.io/api/v2/stats/',
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()

            # API returns a list directly
            if isinstance(data, list) and len(data) > 0:
                # Get the most recent stats (first item)
                stats = data[0]

                bandwidth_used_bytes = stats.get('bandwidth_total', 0)
                bandwidth_used_mb = bandwidth_used_bytes / (1024 * 1024)
                bandwidth_used_gb = bandwidth_used_mb / 1024

                return {
                    'bandwidth_used_bytes': bandwidth_used_bytes,
                    'bandwidth_used_mb': round(bandwidth_used_mb, 2),
                    'bandwidth_used_gb': round(bandwidth_used_gb, 3),
                    'requests_total': stats.get('requests_total', 0),
                    'requests_successful': stats.get('requests_successful', 0),
                    'requests_failed': stats.get('requests_failed', 0),
                }
            # Fallback for older API format with 'results' key
            elif isinstance(data, dict) and 'results' in data and len(data['results']) > 0:
                stats = data['results'][0]

                bandwidth_used_bytes = stats.get('bandwidth_total', 0)
                bandwidth_used_mb = bandwidth_used_bytes / (1024 * 1024)
                bandwidth_used_gb = bandwidth_used_mb / 1024

                return {
                    'bandwidth_used_bytes': bandwidth_used_bytes,
                    'bandwidth_used_mb': round(bandwidth_used_mb, 2),
                    'bandwidth_used_gb': round(bandwidth_used_gb, 3),
                    'requests_total': stats.get('requests_total', 0),
                    'requests_successful': stats.get('requests_successful', 0),
                    'requests_failed': stats.get('requests_failed', 0),
                }

        return None

    except Exception as e:
        # Silently fail if API request fails
        return None


def display_webshare_quota(quota_before=None, quota_after=None, session_bandwidth_mb=0.0):
    """
    Display WebShare bandwidth quota information.

    Note: WebShare API statistics are aggregated HOURLY, not in real-time.
    Local tracking provides immediate session statistics, while API shows hourly totals.

    Args:
        quota_before: Initial quota snapshot (may not reflect current hour)
        quota_after: Final quota snapshot (may not reflect current hour)
        session_bandwidth_mb: Locally tracked bandwidth (accurate and immediate)
    """
    if not quota_after:
        quota_after = get_webshare_quota()

    if not quota_after:
        return

    # Monthly limit (assuming 3 GB - user can adjust)
    monthly_limit_gb = 3.0
    monthly_limit_mb = monthly_limit_gb * 1024

    used_gb = quota_after['bandwidth_used_gb']
    used_mb = quota_after['bandwidth_used_mb']

    # Calculate projected usage based on local tracking (more accurate)
    # API stats are hourly aggregated, so local tracking is more current
    projected_used_mb = used_mb + session_bandwidth_mb
    projected_used_gb = projected_used_mb / 1024

    percent_used = (projected_used_gb / monthly_limit_gb) * 100
    remaining_gb = monthly_limit_gb - projected_used_gb
    remaining_mb = monthly_limit_mb - projected_used_mb

    print(f"\n{'='*70}")
    print(f"WebShare Monthly Quota Status")
    print(f"{'='*70}")
    print(f"  API reported (hourly): {used_mb:.2f} MB ({used_gb:.3f} GB)")

    if session_bandwidth_mb > 0:
        print(f"  Session usage:         +{session_bandwidth_mb:.2f} MB (locally tracked)")
        print(f"  Projected total:       {projected_used_mb:.2f} MB ({projected_used_gb:.3f} GB) - {percent_used:.1f}%")
        print(f"\n  Note: API stats update hourly. Session usage will appear in API")
        print(f"        within the next hour.")
    else:
        print(f"  Total used:            {used_mb:.2f} MB ({used_gb:.3f} GB) - {percent_used:.1f}%")

    print(f"\n  Remaining:             {remaining_mb:.2f} MB ({remaining_gb:.3f} GB)")
    print(f"  Monthly limit:         {monthly_limit_mb:.0f} MB ({monthly_limit_gb:.1f} GB)")

    # Calculate remaining videos (estimate)
    avg_mb_per_video = 1.2  # Based on 10-minute video
    videos_remaining = int(remaining_mb / avg_mb_per_video)
    print(f"\n  Estimated videos remaining: ~{videos_remaining} (avg 10-min videos)")
    print(f"{'='*70}\n")
