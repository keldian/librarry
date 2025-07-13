import requests
import json
import os

def get_radarr_movies():
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

def extract_tmdb_ids(movies, shows):
    tmdb_ids = []
    for movie in movies:
        if movie.get('tmdbId'):
            tmdb_ids.append({"tmdb_id": movie['tmdbId']})
    for show in shows:
        if show.get('tmdbId'):
            tmdb_ids.append({"tmdb_id": show['tmdbId']})
    return tmdb_ids

def main():
    print("Starting sync process...")

    print("Fetching movies from Radarr...")
    movies = get_radarr_movies()
    print(f"Found {len(movies)} movies in Radarr")

    print("Fetching shows from Sonarr...")
    shows = get_sonarr_shows()
    print(f"Found {len(shows)} shows in Sonarr")

    print("Extracting tmdb_ids for StevenLu format...")
    tmdb_id_list = extract_tmdb_ids(movies, shows)
    print(f"Writing {len(tmdb_id_list)} tmdb_id entries to list.json...")

    with open('list.json', 'w') as f:
        json.dump(tmdb_id_list, f, indent=2)

    print("Sync complete!")

if __name__ == "__main__":
    main()