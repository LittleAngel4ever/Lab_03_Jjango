import logging
from django.conf import settings


logger = logging.getLogger(__name__)

def get_top_tracks(limit=50):
    api_key = getattr(settings, 'SOUNDCHARTS_API_KEY', '').strip()
    if not api_key or api_key == 'your-demo-key':
        logger.info("API-ключ не задан, использую демо-данные.")
        return _get_demo_data(limit)

    try:
        real_data = _fetch_from_api(api_key, limit)
        if real_data:
            return real_data
    except Exception as e:
        logger.warning(f"Ошибка при запросе к Soundcharts API: {e}")

    logger.info("Не удалось получить реальные данные, использую демо.")
    return _get_demo_data(limit)

def _fetch_from_api(api_key, limit):
    """Пытается выполнить запрос к реальному API Soundcharts."""
    import requests
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    url = "https://api.soundcharts.com/v1/charts/top"
    headers = {
        "x-api-key": api_key,
        "Accept": "application/json",
        "User-Agent": "DjangoChart/1.0"
    }
    params = {"limit": limit, "country": "global"}

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=10,
        verify=False
    )
    response.raise_for_status()
    data = response.json()
    return _parse_api_response(data)

def _parse_api_response(data):
    """Парсит JSON-ответ Soundcharts API. Подстройте под реальную структуру."""
    tracks = []
    items = data.get('items', [])
    for item in items:
        tracks.append({
            'title': item.get('title', 'Unknown Title'),
            'artist': item.get('artist', {}).get('name', 'Unknown Artist'),
            'genre': _extract_genre(item),
            'release_year': _extract_year(item),
            'cover_image_url': item.get('imageUrl', ''),
            'lyrics': item.get('lyrics', 'Lyrics not available'),
            'artist_info': item.get('artist', {}).get('biography', ''),
        })
    return tracks

def _extract_genre(item):
    genres = item.get('genres', [])
    if genres:
        return genres[0].get('name', 'Unknown')
    return 'Unknown'

def _extract_year(item):
    date_str = item.get('releaseDate', '')
    if date_str and len(date_str) >= 4:
        return int(date_str[:4])
    return 2023

def _get_demo_data(limit):
    demo = []
    for i in range(1, limit + 1):
        demo.append({
            'title': f"Demo Track {i}",
            'artist': f"Artist {i//5}",
            'genre': ["Pop", "Rock", "Hip-Hop", "Electronic", "Jazz"][i % 5],
            'release_year': 2020 + (i % 4),
            'cover_image_url': f"https://loremflickr.com/300/300/music?random={i}",
            'lyrics': f"Demo lyrics for track {i}...",
            'artist_info': f"Biography of Artist {i//5}",
        })
    return demo
