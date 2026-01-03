"""
Tracker list sources configuration.

Defines URLs for fetching public tracker lists from trusted sources.
"""

from typing import Dict, List

# Tracker list sources with URLs
TRACKER_SOURCES: Dict[str, str] = {
    # ngosang/trackerslist (most popular)
    "ngosang_best": "https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_best.txt",
    "ngosang_all": "https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_all.txt",
    "ngosang_http": "https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_all_http.txt",
    "ngosang_udp": "https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_all_udp.txt",
    # XIU2/TrackersListCollection
    "xiu2_best": "https://cf.trackerslist.com/best.txt",
    "xiu2_all": "https://cf.trackerslist.com/all.txt",
    "xiu2_http": "https://cf.trackerslist.com/http.txt",
    # newTrackon (stable trackers)
    "newtrackon": "https://newtrackon.com/api/stable",
}

# Profile -> source mapping
PROFILE_TRACKER_SOURCES: Dict[str, List[str]] = {
    "best": ["ngosang_best", "xiu2_best"],
    "all": ["ngosang_all", "xiu2_all"],
    "http_only": ["ngosang_http", "xiu2_http"],
    "stable": ["newtrackon", "ngosang_best"],
}


def get_sources_for_profile(profile: str) -> List[str]:
    """
    Get tracker source URLs for a given profile.

    Args:
        profile: Profile name (e.g., "best", "all")

    Returns:
        List of source URLs to fetch
    """
    source_keys = PROFILE_TRACKER_SOURCES.get(profile, ["ngosang_best"])
    return [TRACKER_SOURCES[key] for key in source_keys if key in TRACKER_SOURCES]
