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
    items = []
    for movie in movies:
        ids = {}
        if movie.get('tmdbId'):
            ids["tmdb"] = movie['tmdbId']
        if movie.get('imdbId'):
            ids["imdb"] = movie['imdbId']
        if ids:
            items.append({
                "type": "movie",
                "movie": {"ids": ids}
            })
    return items

def convert_shows_to_items(shows):
    items = []
    for show in shows:
        ids = {}
        if show.get('tvdbId'):
            ids["tvdb"] = show['tvdbId']
        if show.get('imdbId'):
            ids["imdb"] = show['imdbId']
        if show.get('tmdbId'):
            ids["tmdb"] = show['tmdbId']
        if ids:
            items.append({
                "type": "show",
                "show": {"ids": ids}
            })
    return items

def create_combined_list(movie_items, show_items):
    all_items = movie_items + show_items
    return {
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

    # Debug: Print first few items to check structure
    if movies:
        print("First movie sample:", json.dumps(movies[0], indent=2)[:500])
    if shows:
        print("First show sample:", json.dumps(shows[0], indent=2)[:500])

    # Convert to list items
    print("Converting movies to list format...")
    movie_items = convert_movies_to_items(movies)
    print(f"Added {len(movie_items)} movies")

    print("Converting shows to list format...")
    show_items = convert_shows_to_items(shows)
    print(f"Added {len(show_items)} shows")

    # Create the combined list (Trakt-compatible)
    print("Creating combined list...")
    combined_list = create_combined_list(movie_items, show_items)

    # Write the new list (overwrites the previous one completely)
    print("Writing list.json...")
    with open('list.json', 'w') as f:
        json.dump(combined_list, f, indent=2)

    print(f"Sync complete! Final list contains {len(combined_list['items'])} items")
    print(f"  - Movies: {len(movie_items)}")
    print(f"  - Shows: {len(show_items)}")


if __name__ == "__main__":
    main()