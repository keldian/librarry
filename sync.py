import requests
import json
import os
import sys
from datetime import datetime


def get_radarr_movies():
    """Fetch all movies from Radarr"""
    radarr_url = os.environ.get('RADARR_URL')
    api_key = os.environ.get('RADARR_API_KEY')

    if not radarr_url or not api_key:
        print("Warning: RADARR_URL and RADARR_API_KEY not set, skipping movies")
        return []

    radarr_url = radarr_url.rstrip('/')

    try:
        response = requests.get(
            f"{radarr_url}/api/v3/movie",
            params={'apikey': api_key},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching from Radarr: {e}")
        return []


def get_sonarr_shows():
    """Fetch all shows from Sonarr"""
    sonarr_url = os.environ.get('SONARR_URL')
    api_key = os.environ.get('SONARR_API_KEY')

    if not sonarr_url or not api_key:
        print("Warning: SONARR_URL and SONARR_API_KEY not set, skipping shows")
        return []

    sonarr_url = sonarr_url.rstrip('/')

    try:
        response = requests.get(
            f"{sonarr_url}/api/v3/series",
            params={'apikey': api_key},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching from Sonarr: {e}")
        return []


def convert_movies_to_items(movies):
    """Convert Radarr movies to list items"""
    items = []

    for movie in movies:
        # Only include movies that have been downloaded
        if not movie.get('hasFile', False):
            continue

        item = {
            "type": "movie",
            "movie": {
                "title": movie.get('title', 'Unknown'),
                "year": movie.get('year', 0),
                "ids": {}
            }
        }

        # Add available IDs
        if movie.get('tmdbId'):
            item["movie"]["ids"]["tmdb"] = movie['tmdbId']
        if movie.get('imdbId'):
            item["movie"]["ids"]["imdb"] = movie['imdbId']

        items.append(item)

    return items


def convert_shows_to_items(shows):
    """Convert Sonarr shows to list items"""
    items = []

    for show in shows:
        # Only include shows that have at least one episode downloaded
        if show.get('episodeFileCount', 0) == 0:
            continue

        item = {
            "type": "show",
            "show": {
                "title": show.get('title', 'Unknown'),
                "year": show.get('year', 0),
                "ids": {}
            }
        }

        # Add available IDs
        if show.get('tvdbId'):
            item["show"]["ids"]["tvdb"] = show['tvdbId']
        if show.get('imdbId'):
            item["show"]["ids"]["imdb"] = show['imdbId']
        if show.get('tmdbId'):
            item["show"]["ids"]["tmdb"] = show['tmdbId']

        items.append(item)

    return items


def create_combined_list(movie_items, show_items):
    """Create the final combined list"""
    all_items = movie_items + show_items

    return {
        "name": "My Media Library",
        "description": f"Auto-synced from Radarr and Sonarr on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "stats": {
            "movies": len(movie_items),
            "shows": len(show_items),
            "total": len(all_items)
        },
        "items": all_items
    }


def main():
    print("Starting sync process...")

    # Fetch from both services
    print("Fetching movies from Radarr...")
    movies = get_radarr_movies()
    print(f"Found {len(movies)} movies in Radarr")

    print("Fetching shows from Sonarr...")
    shows = get_sonarr_shows()
    print(f"Found {len(shows)} shows in Sonarr")

    # Convert to list items
    print("Converting movies to list format...")
    movie_items = convert_movies_to_items(movies)
    print(f"Added {len(movie_items)} downloaded movies")

    print("Converting shows to list format...")
    show_items = convert_shows_to_items(shows)
    print(f"Added {len(show_items)} shows with episodes")

    # Create the combined list (this replaces the entire list each time)
    print("Creating combined list...")
    combined_list = create_combined_list(movie_items, show_items)

    # Write the new list (overwrites the previous one completely)
    print("Writing list.json...")
    with open('list.json', 'w') as f:
        json.dump(combined_list, f, indent=2)

    print(f"Sync complete! Final list contains {combined_list['stats']['total']} items")
    print(f"  - Movies: {combined_list['stats']['movies']}")
    print(f"  - Shows: {combined_list['stats']['shows']}")


if __name__ == "__main__":
    main()